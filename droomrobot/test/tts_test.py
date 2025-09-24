from os.path import abspath, join

from droomrobot.core import Droomrobot, InteractionConf
from droomrobot.droomrobot_tts import GoogleVoiceConf, ElevenLabsVoiceConf, VoiceConf


class TTSTest:
    def __init__(self, mini_ip, mini_id, mini_password, redis_ip,
                 google_keyfile_path, sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                 dialogflow_timeout=None,
                 voice_conf: VoiceConf = GoogleVoiceConf(),
                 openai_key_path=None, computer_test_mode=False):
        self.mini_id = mini_id
        self.droomrobot = Droomrobot(mini_ip=mini_ip, mini_id=mini_id, mini_password=mini_password, redis_ip=redis_ip,
                                     google_keyfile_path=google_keyfile_path,
                                     sample_rate_dialogflow_hertz=sample_rate_dialogflow_hertz,
                                     dialogflow_language=dialogflow_language, dialogflow_timeout=dialogflow_timeout,
                                     voice_conf=voice_conf,
                                     env_path=openai_key_path,
                                     computer_test_mode=computer_test_mode)

    def test_amplification(self):
        self.droomrobot.say("Normaal")
        self.droomrobot.say("Hallo, ik ben de droomrobot.")

        self.droomrobot.set_interaction_conf(InteractionConf(amplified=True))
        self.droomrobot.say("Versterkt")
        self.droomrobot.say("Hallo, ik ben de droomrobot.")

    def speak(self):
        self.droomrobot.say("Hallo, ik ben de droomrobot.")
        self.droomrobot.ask_fake("Hoe heet jij?")
        self.droomrobot.say("Mike, wat een leuke naam!")
        self.droomrobot.ask_open("Wat vind jij leuk om te doen?")
        self.droomrobot.say("Dat klikt leuk zeg.")
        self.droomrobot.disconnect()


if __name__ == '__main__':
    # voice_conf = GoogleVoiceConf()
    voice_conf = ElevenLabsVoiceConf()
    test = TTSTest(mini_ip="192.168.178.251", mini_id="00041", mini_password="mini", redis_ip="192.168.178.84",
                   google_keyfile_path=abspath(join("../../conf", "dialogflow", "google_keyfile.json")),
                   openai_key_path=abspath(join("../../conf", "openai", ".openai_env")),
                   voice_conf=voice_conf,
                   computer_test_mode=False)
    test.speak()
