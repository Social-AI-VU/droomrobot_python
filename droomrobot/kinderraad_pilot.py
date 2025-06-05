from enum import Enum
from os.path import abspath, join

from sonde9 import Sonde9
from kapinductie9 import Kapinductie9
from core import InteractionPart


class ScriptId(Enum):
    SONDE = 1
    KAPINDUCTIE = 2


class PilotManager:

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

    def run_pilot(self, participant_id: str, script_id: ScriptId, interaction_part: InteractionPart,
                  child_name: str, child_age: int, droomplek='raceauto', kleur='blauw'):

        if script_id == ScriptId.SONDE:
            pilot_script = Sonde9(mini_ip=self.mini_ip, mini_id=self.mini_id, mini_password=self.mini_password,
                                  redis_ip=self.redis_ip, google_keyfile_path=self.google_keyfile_path,
                                  openai_key_path=self.openai_key_path,
                                  default_speaking_rate=self.default_speaking_rate,
                                  computer_test_mode=self.computer_test_mode)
            pilot_script.run(participant_id=participant_id, interaction_part=interaction_part, child_name=child_name,
                             child_age=child_age, droomplek=droomplek, kleur=kleur)

        elif script_id == ScriptId.KAPINDUCTIE:
            pilot_script = Kapinductie9(mini_ip=self.mini_ip, mini_id=self.mini_id, mini_password=self.mini_password,
                                        redis_ip=self.redis_ip, google_keyfile_path=self.google_keyfile_path,
                                        openai_key_path=self.openai_key_path,
                                        default_speaking_rate=self.default_speaking_rate,
                                        computer_test_mode=self.computer_test_mode)
            pilot_script.run(participant_id=participant_id, interaction_part=interaction_part, child_name=child_name,
                             child_age=child_age, droomplek=droomplek)

        else:
            print("[Error] Script type not supported")



if __name__ == '__main__':
    pilot_manager = PilotManager(mini_ip="192.168.1.37", mini_id="00167", mini_password="alphago",
                                 redis_ip="192.168.1.180",
                                 google_keyfile_path=abspath(join("../conf", "dialogflow", "google_keyfile.json")),
                                 openai_key_path=abspath(join("../conf", "openai", ".openai_env")),
                                 default_speaking_rate=0.8, computer_test_mode=False)

    pilot_manager.run_pilot(participant_id='9999',
                            script_id=ScriptId.SONDE,
                            interaction_part=InteractionPart.INTRODUCTION,
                            child_name='Bas',
                            child_age=10,
                            droomplek='waterglijbaan',
                            kleur='regenboogkleur')
