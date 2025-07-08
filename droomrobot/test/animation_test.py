from os.path import abspath, join
from time import sleep

from droomrobot.core import Droomrobot, AnimationType

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
        speaking_acts = [
            "speakingAct1",
            "speakingAct2",
            "speakingAct3",
            "speakingAct4",
            "speakingAct5",
            "speakingAct6",
            "speakingAct7",
            "speakingAct8",
            "speakingAct9",
            "speakingAct10",
            "speakingAct11",
            "speakingAct12",
            "speakingAct13",
            "speakingAct14",
            "speakingAct15",
            "speakingAct16",
            "speakingAct17"
        ]

        for animation in speaking_acts:
            try:
                self.droomrobot.say(f"Volgende is {animation}")
                self.droomrobot.animate(AnimationType.ACTION, animation)
                sleep(1)
            except Exception as e:
                print(e)

        self.droomrobot.say('Klaar')


if __name__ == '__main__':
    droomrobot = AnimationTest(mini_ip="192.168.178.111", mini_id="00167", mini_password="alphago",
                               redis_ip="192.168.178.84",
                               google_keyfile_path=abspath(join("../../conf", "dialogflow", "google_keyfile.json")),
                               openai_key_path=abspath(join("../../conf", "openai", ".openai_env")),
                               default_speaking_rate=0.8, computer_test_mode=False)
    droomrobot.run()
