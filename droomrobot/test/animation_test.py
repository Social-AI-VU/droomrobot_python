from os.path import abspath, join
import os
from core import Droomrobot, AnimationType

"""
Demo: Animation with alphamini.

"""


class AnimationTest:
    def __init__(self, mini_ip, mini_id, mini_password, redis_ip,
                 google_keyfile_path, sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                 google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE",
                 openai_key_path=None, default_speaking_rate=1.0,
                 computer_test_mode=False):
            self.mini_id = mini_id
            self.droomrobot = Droomrobot(mini_ip, mini_id, mini_password, redis_ip,
                                     google_keyfile_path, sample_rate_dialogflow_hertz, dialogflow_language,
                                     google_tts_voice_name, google_tts_voice_gender,
                                     openai_key_path, default_speaking_rate,
                                     computer_test_mode)

    def run(self):
        self.droomrobot.animate(AnimationType.ACTION, "random_short4") ## Wave right hand
        self.droomrobot.animate(AnimationType.EXPRESSION, "emo_007") ## Smile
        os._exit(0)

if __name__ == '__main__':
    droomrobot = AnimationTest(mini_ip="10.0.0.125", mini_id="00041", mini_password="mini",
                                 redis_ip="10.0.0.109",
                                 google_keyfile_path=abspath(join("../conf", "dialogflow", "google_keyfile.json")),
                                 openai_key_path=abspath(join("../conf", "openai", ".openai_env")),
                                 default_speaking_rate=0.8, computer_test_mode=False)
    droomrobot.run()
