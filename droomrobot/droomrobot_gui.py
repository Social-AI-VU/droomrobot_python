import sys
import tkinter as tk
from tkinter import ttk
from threading import Thread

from droomrobot.droomrobot_script import ScriptId, InteractionPart
from droomrobot_control import DroomrobotControl  # Import inside if needed
from os.path import abspath


class DroomrobotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Droomrobot Controller")

        self.advanced_fields = []

        # Interaction Frame
        interaction_frame = ttk.LabelFrame(root, text="Interaction Parameters")
        interaction_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.participant_id = tk.StringVar()
        self.child_name = tk.StringVar()
        self.child_age = tk.IntVar()

        self.script_id = tk.StringVar(value=ScriptId.SONDE.name)
        self.interaction_part = tk.StringVar(value=InteractionPart.INTRODUCTION.name)

        ttk.Label(interaction_frame, text="Participant ID").grid(row=0, column=0)
        ttk.Entry(interaction_frame, textvariable=self.participant_id).grid(row=0, column=1)

        ttk.Label(interaction_frame, text="Voornaam").grid(row=1, column=0)
        ttk.Entry(interaction_frame, textvariable=self.child_name).grid(row=1, column=1)

        ttk.Label(interaction_frame, text="Leeftijd").grid(row=2, column=0)
        ttk.Entry(interaction_frame, textvariable=self.child_age).grid(row=2, column=1)

        ttk.Label(interaction_frame, text="Context").grid(row=3, column=0)
        ttk.Combobox(interaction_frame, textvariable=self.script_id, values=[e.name for e in ScriptId]).grid(row=3, column=1)

        ttk.Label(interaction_frame, text="Onderdeel").grid(row=4, column=0)
        ttk.Combobox(interaction_frame, textvariable=self.interaction_part, values=[e.name for e in InteractionPart]).grid(row=4, column=1)

        # Setup Frame
        setup_frame = ttk.LabelFrame(root, text="Robot Setup")
        setup_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.mini_ip = tk.StringVar(value="192.168.178.111")
        self.mini_id = tk.StringVar(value="00167")
        self.mini_password = tk.StringVar(value="alphago")
        self.redis_ip = tk.StringVar(value="192.168.178.84")
        self.google_keyfile = tk.StringVar(value="../conf/dialogflow/google_keyfile.json")
        self.openai_keyfile = tk.StringVar(value="../conf/openai/.openai_env")

        ttk.Label(setup_frame, text="Mini IP").grid(row=0, column=0, sticky="w")
        ttk.Entry(setup_frame, textvariable=self.mini_ip).grid(row=0, column=1)

        ttk.Label(setup_frame, text="Mini ID").grid(row=1, column=0, sticky="w")
        ttk.Entry(setup_frame, textvariable=self.mini_id).grid(row=1, column=1)

        ttk.Label(setup_frame, text="Mini Password").grid(row=2, column=0, sticky="w")
        ttk.Entry(setup_frame, textvariable=self.mini_password, show='*').grid(row=2, column=1)

        ttk.Label(setup_frame, text="Redis IP").grid(row=3, column=0, sticky="w")
        ttk.Entry(setup_frame, textvariable=self.redis_ip).grid(row=3, column=1)

        # Toggle button for advanced settings
        self.advanced_visible = False
        self.advanced_frame = ttk.Frame(self.root)
        self.toggle_button = ttk.Button(self.root, text="Show Advanced Settings ⯈", command=self.toggle_advanced)
        self.toggle_button.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")
        self.advanced_frame.grid(row=3, column=0, padx=10, sticky="ew")
        self.advanced_frame.grid_remove()  # Hidden by default

        # Header labels
        header_frame = ttk.Frame(self.advanced_frame)
        ttk.Label(header_frame, text="Key", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 40))
        ttk.Label(header_frame, text="Value", font=("Segoe UI", 9, "bold")).pack(side="left")
        header_frame.pack(anchor="w", pady=(5, 0))

        # Field container
        self.advanced_fields_container = ttk.Frame(self.advanced_frame)
        self.advanced_fields_container.pack(anchor="w")

        # Initial key-value pairs
        self.add_advanced_field()

        # Add field button
        self.add_field_button = ttk.Button(self.advanced_frame, text="Add Field", command=self.add_advanced_field)
        self.add_field_button.pack(anchor="w", pady=(5, 5))

        # Control Buttons
        button_frame = ttk.Frame(root)
        button_frame.grid(row=4, column=0, pady=10)

        self.start_btn = ttk.Button(button_frame, text="Start", command=self.start_script)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = ttk.Button(button_frame, text="Pause", command=self.pause_script, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.resume_btn = ttk.Button(button_frame, text="Resume", command=self.resume_script, state="disabled")
        self.resume_btn.grid(row=0, column=2, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_script, state="disabled")
        self.stop_btn.grid(row=0, column=3, padx=5)

        self.droomrobot_control = None
        self.script_thread = None

        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())

    def toggle_advanced(self):
        if self.advanced_visible:
            self.advanced_frame.grid_remove()
            self.toggle_button.config(text="Show Advanced Settings ⯈")
        else:
            self.advanced_frame.grid()
            self.toggle_button.config(text="Hide Advanced Settings ⯆")
        self.advanced_visible = not self.advanced_visible

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

    def collect_user_model(self):
        user_model = {
            "child_name": self.child_name.get(),
            "child_age": self.child_age.get(),
        }

        for key_var, val_var in self.advanced_fields:
            key = key_var.get().strip()
            val = val_var.get().strip()
            if key:
                user_model[key] = val

        return user_model

    def start_script(self):
        # Create DroomrobotControl instance
        self.droomrobot_control = DroomrobotControl(
            mini_ip=self.mini_ip.get(),
            mini_id=self.mini_id.get(),
            mini_password=self.mini_password.get(),
            redis_ip=self.redis_ip.get(),
            google_keyfile_path=abspath(self.google_keyfile.get()),
            openai_key_path=abspath(self.openai_keyfile.get()),
            default_speaking_rate=0.8,
            computer_test_mode=False
        )

        participant_id = self.participant_id.get()
        user_model = self.collect_user_model()

        script_id = ScriptId[self.script_id.get()]
        interaction_part = InteractionPart[self.interaction_part.get()]

        # Run in background thread
        def run():
            self.droomrobot_control.run_script(
                participant_id=participant_id,
                script_id=script_id,
                interaction_part=interaction_part,
                user_model=user_model
            )

        self.script_thread = Thread(target=run)
        self.script_thread.start()

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
        if self.droomrobot_control:
            self.droomrobot_control.stop()
            self.script_thread.join()

        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")

        self.root.quit()  # Ends the mainloop
        self.root.destroy()  # Closes the window
        sys.exit(0)


# --- Run GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DroomrobotGUI(root)
    root.mainloop()
