from os.path import abspath, join

from droomrobot.core import AnimationType, Droomrobot
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext, InteractionSession


class ScriptTest(DroomrobotScript):

    def __init__(self, droomrobot: Droomrobot, interaction_context=InteractionContext.BLOEDAFNAME) -> None:
        super(ScriptTest, self).__init__(droomrobot=droomrobot, interaction_context=interaction_context)

    def prepare(self, participant_id: str, session: InteractionSession, user_model_addendum: dict = False):
        super().prepare(participant_id, session, user_model_addendum)
        self._test()

    def _test(self):
        self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True)
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        self.add_move(self.droomrobot.say, 'Hallo, ik ben de droomrobot!')


if __name__ == '__main__':
    droomrobot = Droomrobot(mini_ip="192.168.178.111", mini_id="00167", mini_password="alphago",
                            redis_ip="192.168.178.84",
                            google_keyfile_path=abspath(join("../../conf", "dialogflow", "google_keyfile.json")),
                            openai_key_path=abspath(join("../../conf", "openai", ".openai_env")),
                            sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                            dialogflow_timeout=10.0,
                            google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE",
                            default_speaking_rate=1.0,
                            computer_test_mode=False)

    script_test = ScriptTest(droomrobot)
    script_test.prepare(participant_id='999', session=InteractionSession.INTRODUCTION, user_model_addendum={})
    script_test.run()
