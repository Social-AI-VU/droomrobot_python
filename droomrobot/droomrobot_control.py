from os.path import abspath, join

from droomrobot.bloedafname4 import Bloedafname4
from droomrobot.bloedafname6 import Bloedafname6
from droomrobot.bloedafname9 import Bloedafname9
from droomrobot.droomrobot_script import ScriptId, InteractionPart
from droomrobot.kapinductie4 import Kapinductie4
from droomrobot.kapinductie6 import Kapinductie6
from droomrobot.sonde4 import Sonde4
from droomrobot.sonde6 import Sonde6
from sonde9 import Sonde9
from kapinductie9 import Kapinductie9


class DroomrobotControl:

    def __init__(self, mini_ip, mini_id, mini_password, redis_ip,
                 google_keyfile_path, sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                 google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE",
                 openai_key_path=None, default_speaking_rate=1.0,
                 computer_test_mode=False):
        self.mini_ip = mini_ip
        self.mini_id = mini_id
        self.mini_password = mini_password
        self.redis_ip = redis_ip
        self.google_keyfile_path = google_keyfile_path
        self.sample_rate_dialogflow_hertz = sample_rate_dialogflow_hertz
        self.dialogflow_language = dialogflow_language
        self.google_tts_voice_name = google_tts_voice_name
        self.google_tts_voice_gender = google_tts_voice_gender
        self.openai_key_path = openai_key_path
        self.default_speaking_rate = default_speaking_rate
        self.computer_test_mode = computer_test_mode

        self.interaction_script = None

    def run_script(self, participant_id: str, script_id: ScriptId, interaction_part: InteractionPart, user_model: dict):
        # Select class based on script_id and child_age
        script_class_map = {
            ScriptId.SONDE: [Sonde4, Sonde6, Sonde9],
            ScriptId.KAPINDUCTIE: [Kapinductie4, Kapinductie6, Kapinductie9],
            ScriptId.BLOEDAFNAME: [Bloedafname4, Bloedafname6, Bloedafname9],
        }

        def select_age_index(age):
            if age <= 6:
                return 0
            elif 6 < age <= 9:
                return 1
            else:
                return 2

        try:
            if script_id not in script_class_map:
                print(f"[Error] Unsupported script_id: {script_id}")
                return

            age_index = select_age_index(user_model['child_age'])
            script_class = script_class_map[script_id][age_index]

            # Shared constructor kwargs
            constructor_kwargs = {
                'mini_ip': self.mini_ip,
                'mini_id': self.mini_id,
                'mini_password': self.mini_password,
                'redis_ip': self.redis_ip,
                'google_keyfile_path': self.google_keyfile_path,
                'openai_key_path': self.openai_key_path,
                'default_speaking_rate': self.default_speaking_rate,
                'computer_test_mode': self.computer_test_mode,
            }

            # Instantiate the appropriate script
            self.interaction_script = script_class(**constructor_kwargs)

            # Run the script
            self.interaction_script.run(
                participant_id=participant_id,
                interaction_part=interaction_part,
                user_model=user_model
            )

        except KeyboardInterrupt:
            print("[Interrupted] Closing connection to droomrobot...")
            if self.interaction_script:
                self.interaction_script.stop()
            print("Closed.")

        except Exception as e:
            print(f"[Error] Exception while running script: {e}")

    def pause(self):
        if self.interaction_script:
            self.interaction_script.pause()

    def resume(self):
        if self.interaction_script:
            self.interaction_script.resume()

    def stop(self):
        if self.interaction_script:
            self.interaction_script.stop()


if __name__ == '__main__':
    droomrobot_control = DroomrobotControl(mini_ip="192.168.178.111", mini_id="00167", mini_password="alphago",
                                           redis_ip="192.168.178.84",
                                           google_keyfile_path=abspath(
                                               join("../conf", "dialogflow", "google_keyfile.json")),
                                           openai_key_path=abspath(join("../conf", "openai", ".openai_env")),
                                           default_speaking_rate=0.8, computer_test_mode=False)

    droomrobot_control.run_script(participant_id='9999',
                                  script_id=ScriptId.SONDE,
                                  interaction_part=InteractionPart.INTRODUCTION,
                                  user_model={
                                      'child_name': 'Bas',
                                      'child_age': 10})
