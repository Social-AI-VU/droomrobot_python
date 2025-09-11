from os.path import abspath, join

from droomrobot.core import Droomrobot, InteractionConf


class TTSTest:
    def __init__(self, mini_ip, mini_id, mini_password, redis_ip,
                 google_keyfile_path, sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                 dialogflow_timeout=None,
                 google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE", default_speaking_rate=1.0,
                 openai_key_path=None, computer_test_mode=False):
        self.mini_id = mini_id
        self.droomrobot = Droomrobot(mini_ip=mini_ip, mini_id=mini_id, mini_password=mini_password, redis_ip=redis_ip,
                                     google_keyfile_path=google_keyfile_path,
                                     sample_rate_dialogflow_hertz=sample_rate_dialogflow_hertz,
                                     dialogflow_language=dialogflow_language, dialogflow_timeout=dialogflow_timeout,
                                     google_tts_voice_name=google_tts_voice_name,
                                     google_tts_voice_gender=google_tts_voice_gender,
                                     default_speaking_rate=default_speaking_rate,
                                     openai_key_path=openai_key_path,
                                     computer_test_mode=computer_test_mode)

    def speak(self):
        self.droomrobot.say("Normaal")
        self.droomrobot.say("Hallo, ik ben de droomrobot.")

        self.droomrobot.set_interaction_conf(InteractionConf(amplified=True))
        self.droomrobot.say("Versterkt")
        self.droomrobot.say("Hallo, ik ben de droomrobot.")


if __name__ == '__main__':
    test = TTSTest(mini_ip="192.168.178.251", mini_id="00041", mini_password="mini", redis_ip="192.168.178.84",
                   google_keyfile_path=abspath(join("../../conf", "dialogflow", "google_keyfile.json")),
                   computer_test_mode=False)
    test.speak()
