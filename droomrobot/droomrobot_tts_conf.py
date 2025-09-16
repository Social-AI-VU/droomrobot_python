from enum import Enum


class Voice(Enum):
    GOOGLE = 1
    ELEVENLABS = 2


class VoiceConf:

    def __init__(self, default_speaking_rate=1.0):
        self.default_speaking_rate = default_speaking_rate


class GoogleVoiceConf(VoiceConf):

    def __init__(self, default_speaking_rate=1.0, google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE"):
        super().__init__(default_speaking_rate)
        self.google_tts_voice_name = google_tts_voice_name
        self.google_tts_voice_gender = google_tts_voice_gender


class ElevenLabsVoiceConf(VoiceConf):
    def __init__(self, default_speaking_rate=1.0, voice_id='yO6w2xlECAQRFP6pX7Hw', model_id='eleven_flash_v2_5'):
        super().__init__(default_speaking_rate)
        self.voice_id = voice_id
        self.model_id = model_id
