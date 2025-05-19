from os.path import abspath, join

from bloedafname4 import Bloedafname4
from bloedafname6 import Bloedafname6
from bloedafname9 import Bloedafname9
from core import InteractionPart, ChildGender


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

    def run_pilot(self, participant_id: str, script_id: int, interaction_part: InteractionPart,
                  child_name: str, child_age: int, child_gender: ChildGender):

        if script_id == 4:
            pilot_script = Bloedafname4(mini_ip=self.mini_ip, mini_id=self.mini_id, mini_password=self.mini_password,
                                        redis_ip=self.redis_ip, google_keyfile_path=self.google_keyfile_path,
                                        openai_key_path=self.openai_key_path,
                                        default_speaking_rate=self.default_speaking_rate,
                                        computer_test_mode=self.computer_test_mode)

        elif script_id == 6:
            pilot_script = Bloedafname6(mini_ip=self.mini_ip, mini_id=self.mini_id, mini_password=self.mini_password,
                                        redis_ip=self.redis_ip, google_keyfile_path=self.google_keyfile_path,
                                        openai_key_path=self.openai_key_path,
                                        default_speaking_rate=self.default_speaking_rate,
                                        computer_test_mode=self.computer_test_mode)

        else:
            pilot_script = Bloedafname9(mini_ip=self.mini_ip, mini_id=self.mini_id, mini_password=self.mini_password,
                                        redis_ip=self.redis_ip, google_keyfile_path=self.google_keyfile_path,
                                        openai_key_path=self.openai_key_path,
                                        default_speaking_rate=self.default_speaking_rate,
                                        computer_test_mode=self.computer_test_mode)

        pilot_script.run(participant_id=participant_id, interaction_part=interaction_part, child_name=child_name,
                         child_age=child_age, child_gender=child_gender)


if __name__ == '__main__':
    pilot_manager = PilotManager(mini_ip="192.168.178.111", mini_id="00167", mini_password="alphago",
                                 redis_ip="192.168.178.84",
                                 google_keyfile_path=abspath(join("../conf", "dialogflow", "google_keyfile.json")),
                                 openai_key_path=abspath(join("../conf", "openai", ".openai_env")),
                                 default_speaking_rate=0.8, computer_test_mode=False)

    pilot_manager.run_pilot(participant_id='9996',
                            script_id=9,
                            interaction_part=InteractionPart.INTERVENTION,
                            child_name='Bas',
                            child_age=8,
                            child_gender=ChildGender.BOY)
