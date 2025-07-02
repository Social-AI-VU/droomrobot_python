import abc
from enum import Enum

from droomrobot.core import Droomrobot


class ScriptId(Enum):
    SONDE = 1
    KAPINDUCTIE = 2
    BLOEDAFNAME = 3


class InteractionPart(Enum):
    INTRODUCTION = 1
    INTERVENTION = 2


class DroomrobotScript:

    def __init__(self, mini_ip, mini_id, mini_password, redis_ip,
                 google_keyfile_path, sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                 google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE",
                 openai_key_path=None, default_speaking_rate=1.0,
                 computer_test_mode=False):

        self.droomrobot = Droomrobot(mini_ip, mini_id, mini_password, redis_ip,
                                     google_keyfile_path, sample_rate_dialogflow_hertz, dialogflow_language,
                                     google_tts_voice_name, google_tts_voice_gender,
                                     openai_key_path, default_speaking_rate,
                                     computer_test_mode)
        self.participant_id = None
        self.user_model = None
        self.script_id = None

    @abc.abstractmethod
    def run(self, participant_id: str, interaction_part: InteractionPart, user_model_addendum: dict):

        self.participant_id = participant_id
        self.user_model = self.droomrobot.load_user_model(participant_id=participant_id)
        self.user_model.update(user_model_addendum)

        if 'droomplek' in self.user_model:
            self.user_model['droomplek_lidwoord'] = self.droomrobot.get_article(self.user_model['droomplek'])

        self.droomrobot.start_logging(participant_id, {
            'participant_id': participant_id,
            'script_id': self.script_id.name,
            'interaction_part': interaction_part,
            'child_age': self.user_model['child_age']
        })

    def pause(self):
        if self.droomrobot:
            self.droomrobot.pause()

    def resume(self):
        if self.droomrobot:
            self.droomrobot.resume()

    def stop(self):
        self.droomrobot.stop_logging()
        self.droomrobot.disconnect()
