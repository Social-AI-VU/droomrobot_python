import logging
import sys
import tkinter as tk
from json import load, JSONDecodeError
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from threading import Thread
from os.path import abspath, join

from droomrobot.droomrobot_script import InteractionContext, InteractionSession
from droomrobot_control import DroomrobotControl


class TextRedirector:
    def __init__(self, text_widget, tag):
        self.text_widget = text_widget
        self.tag = tag

    def write(self, message):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", message)
        self.text_widget.configure(state="disabled")
        self.text_widget.see("end")

    def flush(self):
        self.text_widget.update_idletasks()


class DroomrobotGUI:
    def __init__(self, root):
        # Logging
        self.logger = logging.getLogger("droomrobot")
        self.logger.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, or CRITICAL

        # Avoid adding multiple handlers if re-running in an interactive environment
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        self.root = root
        self.root.title("Droomrobot Controller")
        self.advanced_fields = []

        # === Containers ===
        self.connect_frame = ttk.Frame(root)
        self.full_control_frame = ttk.Frame(root)

        self.connect_frame.grid(row=0, column=0, sticky="nsew")
        self.full_control_frame.grid(row=0, column=0, sticky="nsew")
        self.full_control_frame.grid_remove()

        # Console Frame (hidden by default)
        self.console_visible = False
        self.console_frame = ttk.LabelFrame(root, text="Console Output")
        self.console_frame.grid(row=99, column=0, padx=10, pady=10, sticky="ew")  # high row number to place it last
        self.console_frame.grid_remove()

        # Console toggle button
        self.console_toggle_btn = ttk.Button(root, text="Show Console ⯈", command=self.toggle_console)
        self.console_toggle_btn.grid(row=98, column=0, padx=10, pady=(5, 0), sticky="w")

        # Console text widget
        self.console = ScrolledText(self.console_frame, height=10, state="disabled", wrap="word")
        self.console.pack(fill="both", expand=True)

        # Redirect stdout/stderr
        sys.stdout = TextRedirector(self.console, "stdout")
        sys.stderr = TextRedirector(self.console, "stderr")

        # === Setup (Connect) Screen ===
        # Load them from config file
        config = self.load_config()
        self.mini_ip = tk.StringVar(value=config.get("mini_ip", "192.168.178.111"))
        self.mini_id = tk.StringVar(value=config.get("mini_id", "00167"))
        self.mini_password = tk.StringVar(value=config.get("mini_password", "alphago"))
        self.redis_ip = tk.StringVar(value=config.get("redis_ip", "192.168.178.84"))
        self.google_keyfile = tk.StringVar(value=config.get("google_keyfile", "../conf/dialogflow/google_keyfile.json"))
        self.openai_keyfile = tk.StringVar(value=config.get("openai_keyfile", "../conf/openai/.openai_env"))
        self.dialogflow_timeout = tk.StringVar(value=str(config.get("dialogflow_timeout", "15.0")))
        self.default_speaking_rate = tk.StringVar(value=str(config.get("default_speaking_rate", "0.9")))
        self.debug_mode = tk.BooleanVar(value=config.get("debug_mode", False))
        self.audio_amplified = tk.BooleanVar(value=config.get("versterkt", False))

        setup_frame = ttk.LabelFrame(self.connect_frame, text="Robot Setup")
        setup_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(setup_frame, text="Mini IP").grid(row=0, column=0)
        ttk.Entry(setup_frame, textvariable=self.mini_ip).grid(row=0, column=1)

        ttk.Label(setup_frame, text="Mini ID").grid(row=1, column=0)
        ttk.Entry(setup_frame, textvariable=self.mini_id).grid(row=1, column=1)

        ttk.Label(setup_frame, text="Mini Password").grid(row=2, column=0)
        ttk.Entry(setup_frame, textvariable=self.mini_password, show='*').grid(row=2, column=1)

        ttk.Label(setup_frame, text="Redis IP").grid(row=3, column=0)
        ttk.Entry(setup_frame, textvariable=self.redis_ip).grid(row=3, column=1)

        # --- Advanced Settings Toggle ---
        self.connect_advanced_visible = tk.BooleanVar(value=False)
        toggle_button = ttk.Button(
            setup_frame,
            text="▸ Advanced Settings",
            command=self.toggle_connect_advanced_settings,
            style="TButton"
        )
        toggle_button.grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.connect_advanced_button = toggle_button

        # --- Advanced Frame (Initially Hidden) ---
        self.connect_advanced_frame = ttk.Frame(setup_frame)
        self.connect_advanced_frame.grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.connect_advanced_frame.grid_remove()  # Start hidden

        # Populate advanced frame
        ttk.Label(self.connect_advanced_frame, text="Google Keyfile Path").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.connect_advanced_frame, textvariable=self.google_keyfile, width=50).grid(row=0, column=1)

        ttk.Label(self.connect_advanced_frame, text="OpenAI Keyfile Path").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.connect_advanced_frame, textvariable=self.openai_keyfile, width=50).grid(row=1, column=1)

        ttk.Label(self.connect_advanced_frame, text="Dialogflow Timeout").grid(row=2, column=0, sticky="w")
        ttk.Entry(self.connect_advanced_frame, textvariable=self.dialogflow_timeout, width=10).grid(row=2, column=1,
                                                                                                    sticky="w")
        ttk.Label(self.connect_advanced_frame, text="Speaking Rate").grid(row=3, column=0, sticky="w")
        ttk.Entry(self.connect_advanced_frame, textvariable=self.default_speaking_rate, width=10).grid(row=3, column=1,
                                                                                              sticky="w")
        ttk.Checkbutton(
            self.connect_advanced_frame,
            text="No robot debug mode",
            variable=self.debug_mode
        ).grid(row=4, column=0, columnspan=2, sticky="w")

        self.connect_btn = ttk.Button(self.connect_frame, text="Connect", command=self.handle_connect)
        self.connect_btn.grid(row=1, column=0, pady=10)

        self.progress = ttk.Progressbar(self.connect_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, pady=(5, 10), sticky="ew")
        self.progress.grid_remove()  # Hide initially

        # === Full Control View ===

        # Interaction Frame
        self.participant_id = tk.StringVar()
        self.child_name = tk.StringVar()
        self.child_age = tk.IntVar()
        self.priklocatie = tk.StringVar(value="arm")
        try:
            context_enum = InteractionContext[config.get("context")]
        except KeyError:
            context_enum = InteractionContext.SONDE
        self.context = tk.StringVar(value=context_enum.name)

        try:
            session_enum = InteractionSession[config.get("session")]
        except KeyError:
            session_enum = InteractionSession.INTRODUCTION
        self.session = tk.StringVar(value=session_enum.name)

        interaction_frame = ttk.LabelFrame(self.full_control_frame, text="Interaction Parameters")
        interaction_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(interaction_frame, text="Participant ID").grid(row=0, column=0)
        ttk.Entry(interaction_frame, textvariable=self.participant_id).grid(row=0, column=1)

        ttk.Label(interaction_frame, text="Voornaam").grid(row=1, column=0)
        ttk.Entry(interaction_frame, textvariable=self.child_name).grid(row=1, column=1)

        ttk.Label(interaction_frame, text="Leeftijd").grid(row=2, column=0)
        ttk.Entry(interaction_frame, textvariable=self.child_age).grid(row=2, column=1)

        ttk.Label(interaction_frame, text="Context").grid(row=3, column=0)
        context_combo = ttk.Combobox(
            interaction_frame,
            textvariable=self.context,
            values=[e.name for e in InteractionContext]
        )
        context_combo.grid(row=3, column=1)
        context_combo.bind("<<ComboboxSelected>>", self.on_interaction_context_change)


        ttk.Label(interaction_frame, text="Onderdeel").grid(row=4, column=0)
        ttk.Combobox(interaction_frame, textvariable=self.session,
                     values=[e.name for e in InteractionSession]).grid(row=4, column=1)

        ttk.Label(interaction_frame, text="Versterkt").grid(row=5, column=0)
        ttk.Checkbutton(interaction_frame, variable=self.audio_amplified).grid(row=5, column=1, sticky="w")

        self.priklocatie_label = ttk.Label(interaction_frame, text="Priklocatie")
        self.priklocatie_entry = ttk.Entry(interaction_frame, textvariable=self.priklocatie)

        # Place them but hidden initially
        self.priklocatie_label.grid(row=6, column=0)
        self.priklocatie_entry.grid(row=6, column=1)
        self.priklocatie_label.grid_remove()
        self.priklocatie_entry.grid_remove()

        # Advanced Settings
        self.advanced_visible = False
        self.advanced_frame = ttk.LabelFrame(self.full_control_frame, text="Advanced Settings")
        self.toggle_button = ttk.Button(self.full_control_frame, text="Show Advanced Settings ⯈", command=self.toggle_advanced)
        self.toggle_button.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")
        self.advanced_frame.grid(row=3, column=0, padx=10, sticky="ew")
        self.advanced_frame.grid_remove()

        header_frame = ttk.Frame(self.advanced_frame)
        ttk.Label(header_frame, text="Key", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 40))
        ttk.Label(header_frame, text="Value", font=("Segoe UI", 9, "bold")).pack(side="left")
        header_frame.pack(anchor="w", pady=(5, 0))

        self.advanced_fields_container = ttk.Frame(self.advanced_frame)
        self.advanced_fields_container.pack(anchor="w")
        self.add_advanced_field()

        self.add_field_button = ttk.Button(self.advanced_frame, text="Add Field", command=self.add_advanced_field)
        self.add_field_button.pack(anchor="w", pady=(5, 5))

        self.dance_button = ttk.Button(self.advanced_frame, text="💃 Let Robot Dance", command=self.dance)
        self.dance_button.pack(anchor="w", pady=(5, 10))

        # --- Say Command (Robot Speak) ---
        say_frame = ttk.Frame(self.advanced_frame)
        say_frame.pack(anchor="w", pady=(5, 10))

        ttk.Label(say_frame, text="Say:").pack(side="left")

        self.say_text = tk.StringVar()
        ttk.Entry(say_frame, textvariable=self.say_text, width=40).pack(side="left", padx=(5, 5))

        self.say_button = ttk.Button(say_frame, text="🗣️ Speak", command=self.say_text_command, state="disabled")
        self.say_button.pack(side="left")

        # Control Buttons
        button_frame = ttk.Frame(self.full_control_frame)
        button_frame.grid(row=4, column=0, pady=10)

        self.start_btn = ttk.Button(button_frame, text="Start", command=self.start_script)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = ttk.Button(button_frame, text="Pause", command=self.pause_script, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.resume_btn = ttk.Button(button_frame, text="Resume", command=self.resume_script, state="disabled")
        self.resume_btn.grid(row=0, column=2, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_script, state="disabled")
        self.stop_btn.grid(row=0, column=3, padx=5)

        self.disconnect_btn = ttk.Button(button_frame, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_btn.grid(row=0, column=4, padx=5)

        # Phase control (hidden initially)
        style = ttk.Style()
        style.configure("CurrentPhase.TButton", background="#b6e7b0", foreground="black", relief="sunken")

        self.phase_frame = ttk.LabelFrame(self.full_control_frame, text="Script Phases")
        self.phase_frame.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        self.phase_frame.grid_remove()

        self.phase_buttons = {}
        self.droomrobot_control = None
        self.script_thread = None

        # Ensure priklocatie field visibility matches initial context
        self.on_interaction_context_change()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        # Stop and disconnect robot control gracefully
        if self.droomrobot_control:
            self.droomrobot_control.stop()
            self.droomrobot_control.disconnect()

        # Wait for script thread to finish if alive
        if self.script_thread and self.script_thread.is_alive():
            self.script_thread.join(timeout=2)

        # Destroy the Tkinter window
        self.root.destroy()

        # Force exit after short delay
        self.root.after(100, lambda: sys.exit(0))

    def toggle_advanced(self):
        if self.advanced_visible:
            self.advanced_frame.grid_remove()
            self.toggle_button.config(text="Show Advanced Settings ⯈")
        else:
            self.advanced_frame.grid()
            self.toggle_button.config(text="Hide Advanced Settings ⯆")
        self.advanced_visible = not self.advanced_visible

    def toggle_connect_advanced_settings(self):
        visible = self.connect_advanced_visible.get()
        if visible:
            self.connect_advanced_frame.grid_remove()
            self.connect_advanced_button.config(text="▸ Advanced Settings")
        else:
            self.connect_advanced_frame.grid()
            self.connect_advanced_button.config(text="▼ Advanced Settings")
        self.connect_advanced_visible.set(not visible)

    def add_advanced_field(self, key_default="", val_default=""):
        key_var = tk.StringVar(value=key_default)
        val_var = tk.StringVar(value=val_default)
        frame = ttk.Frame(self.advanced_fields_container)
        ttk.Entry(frame, textvariable=key_var, width=15).pack(side="left", padx=(0, 5))
        ttk.Entry(frame, textvariable=val_var, width=15).pack(side="left", padx=(0, 5))

        def remove():
            frame.destroy()
            self.advanced_fields.remove((key_var, val_var))

        ttk.Button(frame, text="❌", width=2, command=remove).pack(side="left")
        frame.pack(anchor="w", pady=2)
        self.advanced_fields.append((key_var, val_var))

    def on_interaction_context_change(self, event=None):
        if self.context.get() == "BLOEDAFNAME":
            self.priklocatie_label.grid(row=6, column=0)
            self.priklocatie_entry.grid(row=6, column=1)
        else:
            self.priklocatie_label.grid_remove()
            self.priklocatie_entry.grid_remove()

    def collect_user_model(self):
        user_model = {
            "child_name": self.child_name.get(),
            "child_age": self.child_age.get(),
        }
        if self.context.get() == "BLOEDAFNAME":
            user_model["priklocatie"] = self.priklocatie.get()
        for key_var, val_var in self.advanced_fields:
            key = key_var.get().strip()
            val = val_var.get().strip()
            if key:
                user_model[key] = val
        return user_model

    def handle_connect(self):
        def connect_thread():
            try:
                self.connect_btn.config(text="Connecting...", state="disabled")
                self.progress.grid()
                self.progress.start()

                self.connect()

                self.progress.stop()
                self.progress.grid_remove()

                self.connect_btn.config(text="Connected ✅")
                self.connect_frame.grid_remove()
                self.full_control_frame.grid(row=0, column=0, sticky="nsew")
            except Exception as e:
                self.progress.stop()
                self.progress.grid_remove()
                self.connect_btn.config(text="Retry Connect", state="normal")
                print("Connection failed:", e)

        Thread(target=connect_thread, daemon=True).start()

    def switch_to_connect_view(self):
        # Hide all interaction-related widgets
        self.full_control_frame.grid_remove()

        # Disable interaction control buttons
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.disconnect_btn.config(state="disabled")

        # Show connect view
        self.connect_frame.grid(row=0, column=0, sticky="nsew")
        self.connect_btn.config(state="normal", text="Connect")
        self.connect_btn.grid(row=1, column=0, pady=10)

        self.root.update()

    def connect(self):
        self.droomrobot_control = DroomrobotControl()
        self.droomrobot_control.connect(
            mini_ip=self.mini_ip.get(),
            mini_id=self.mini_id.get(),
            mini_password=self.mini_password.get(),
            redis_ip=self.redis_ip.get(),
            google_keyfile_path=abspath(self.google_keyfile.get()),
            dialogflow_timeout=self.float_validation(self.dialogflow_timeout.get(), "Dialogflow timeout"),
            default_speaking_rate=self.float_validation(self.default_speaking_rate.get(), "Speaking rate"),
            openai_key_path=abspath(self.openai_keyfile.get()),
            computer_test_mode=self.debug_mode.get()
        )

        # After connecting successfully, show interaction controls
        self.toggle_button.grid()
        self.console_toggle_btn.grid()
        self.disconnect_btn.config(state="normal")
        self.start_btn.config(state="normal")
        self.say_button.config(state="normal")

    def disconnect(self):
        if self.droomrobot_control:
            self.droomrobot_control.disconnect()
            self.droomrobot_control = None
        self.switch_to_connect_view()
        print("Disconnected from robot.")

    def start_script(self):
        participant_id = self.participant_id.get()
        user_model = self.collect_user_model()
        context = InteractionContext[self.context.get()]
        session = InteractionSession[self.session.get()]
        audio_amplified = self.audio_amplified.get()

        def run():
            self.droomrobot_control.start(participant_id, context, session, user_model, audio_amplified)

        self.script_thread = Thread(target=run)
        self.script_thread.start()

        self.wait_for_phase_data()

        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")

    def pause_script(self):
        if self.droomrobot_control:
            self.droomrobot_control.pause()
            self.pause_btn.config(state="disabled")
            self.resume_btn.config(state="normal")

    def resume_script(self):
        if self.droomrobot_control:
            self.droomrobot_control.resume()
            self.pause_btn.config(state="normal")
            self.resume_btn.config(state="disabled")

    def stop_script(self):
        # Step 1: Update GUI immediately
        self.stop_btn.config(text="Stopping...", state="disabled")
        self.root.update_idletasks()

        # Step 2: Start background thread to stop things
        Thread(target=self._stop_script_thread, daemon=True).start()

    def _stop_script_thread(self):
        try:
            # Stop and disconnect robot control gracefully
            if self.droomrobot_control:
                self.droomrobot_control.stop()

            # Wait for script thread to finish if alive
            if self.script_thread and self.script_thread.is_alive():
                self.script_thread.join(timeout=5)
        except Exception as e:
            self.logger.error("Error stopping script", exc_info=e)
        finally:
            # Step 3: Update GUI safely in the main thread
            self.root.after(0, self._reset_gui_after_stop)

    def _reset_gui_after_stop(self):
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(text="Stop", state="disabled")

    def toggle_console(self):
        if self.console_visible:
            self.console_frame.grid_remove()
            self.console_toggle_btn.config(text="Show Console ⯈")
        else:
            self.console_frame.grid()
            self.console_toggle_btn.config(text="Hide Console ⯆")
        self.console_visible = not self.console_visible

    def show_phase_buttons(self):
        # Always clear previous buttons
        for widget in self.phase_frame.winfo_children():
            widget.destroy()
        self.phase_buttons = {}

        # Get current script phases
        script = self.droomrobot_control.interaction_script
        phases = script.phases
        current = script.current_phase

        # If no phases, hide the frame and return
        if not phases:
            self.phase_frame.grid_remove()
            return

        # Otherwise, display new buttons
        for idx, name in enumerate(phases):
            is_current = idx == current
            btn = ttk.Button(
                self.phase_frame,
                text=name,
                command=lambda phase_name=name: self.next_phase(phase_name),
                state="disabled" if is_current else "normal",
                style="CurrentPhase.TButton" if is_current else "TButton"
            )
            btn.pack(side="left", padx=5, pady=5)
            self.phase_buttons[name] = btn

        self.phase_frame.grid()

    def next_phase(self, phase_name):
        for phase, btn in self.phase_buttons.items():
            if phase == phase_name:
                btn.config(state="disabled", style="CurrentPhase.TButton")
            else:
                btn.config(state="normal", style="TButton")
        self.droomrobot_control.interaction_script.next_phase(phase_name)
        self.resume_script()

    def wait_for_phase_data(self, retries_left=15):  # 15 retries × 200ms = 3 seconds
        script = self.droomrobot_control.interaction_script
        if script and script.phases:
            self.show_phase_buttons()
        elif retries_left > 0:
            self.root.after(200, lambda: self.wait_for_phase_data(retries_left - 1))
        else:
            # No phases detected after retries, hide any old phase UI
            self.phase_frame.grid_remove()
            self.phase_buttons = {}

    def dance(self):
        if self.droomrobot_control:
            try:
                self.droomrobot_control.dance()
            except Exception as e:
                self.logger.error("Dance failed:", exc_info=e)
        else:
            self.logger.warning("Robot is not connected.")

    def say_text_command(self):
        if self.droomrobot_control:
            text = self.say_text.get().strip()
            if text:
                try:
                    self.droomrobot_control.say(text)
                except Exception as e:
                    self.logger.error("Say command failed:", exc_info=e)
            else:
                self.logger.warning("No text entered to speak.")
        else:
            self.logger.warning("Robot is not connected.")


    def load_config(self, path=abspath(join("../conf", "droomrobot", "default_settings.json"))):
        try:
            with open(path, "r") as f:
                return load(f)
        except (FileNotFoundError, JSONDecodeError) as e:
            self.logger.error(f"Error loading config: {e}", exc_info=e)
            return {}

    def float_validation(self, value, name=""):
        try:
            return float(value)
        except ValueError:
            self.logger.warning(f"Warning: Invalid input for '{name}'.")
            return


# --- Run GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DroomrobotGUI(root)
    root.mainloop()
