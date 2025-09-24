from os.path import abspath, join

from droomrobot.core import AnimationType, Droomrobot
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext, InteractionSession
from droomrobot.droomrobot_tts import GoogleVoiceConf, ElevenLabsVoiceConf


class ScriptTest(DroomrobotScript):

    def __init__(self, droomrobot: Droomrobot, interaction_context=InteractionContext.BLOEDAFNAME) -> None:
        super(ScriptTest, self).__init__(droomrobot=droomrobot, interaction_context=interaction_context)

    def prepare(self, participant_id: str, session: InteractionSession, user_model_addendum: dict = False,
                audio_amplified: bool = False):
        super().prepare(participant_id, session, user_model_addendum, audio_amplified)
        self._test()

    def _test(self):
        self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True)
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        self.add_move(self.droomrobot.say, 'Hallo, ik ben de droomrobot!')
        self.add_move(self.droomrobot.ask_fake, "Hoe heet jij?", 2)
        self.add_move(self.droomrobot.say, "Mike, wat een leuke naam!")
        self.add_move(self.droomrobot.ask_open, "Wat vind jij leuk om te doen?")
        self.add_move(self.droomrobot.say, "Dat klikt leuk zeg.")


if __name__ == '__main__':
    droomrobot = Droomrobot(mini_ip="192.168.178.251", mini_id="00041", mini_password="mini",
                            redis_ip="192.168.178.84",
                            google_keyfile_path=abspath(join("../../conf", "dialogflow", "google_keyfile.json")),
                            env_path=abspath(join("../../conf", "openai", ".openai_env")),
                            sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                            dialogflow_timeout=10.0,
                            voice_conf=ElevenLabsVoiceConf(),
                            computer_test_mode=False)

    script_test = ScriptTest(droomrobot)
    script_test.prepare(participant_id='999', session=InteractionSession.INTRODUCTION, user_model_addendum={})
    script_test.run()
    droomrobot.disconnect()
