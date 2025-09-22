import base64
import queue
from json import dumps, loads
from threading import Thread

import pyaudio
import websockets
from sic_framework import AudioRequest

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


class ElevenLabsTTS:
    def __init__(self, speaker, elevenlabs_key, voice_id, model_id, sample_rate=22050):
        self.speaker = speaker
        self.elevenlabs_key = elevenlabs_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.sample_rate = sample_rate
        self.websocket = None

    async def connect(self):
        uri = (
            f"wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream-input"
            f"?model_id={self.model_id}"
            f"&output_format=pcm_{self.sample_rate}"
            f"&inactivity_timeout=180"
        )
        self.websocket = await websockets.connect(uri)
        # f"&auto_mode=true"

        # Send initial config once
        await self.websocket.send(dumps({
            "text": " ",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "use_speaker_boost": False,
                "chunk_length_schedule": [50, 120, 160, 290]
            },
            "auto_mode": True,
            "xi_api_key": self.elevenlabs_key,
        }))

    async def disconnect(self):
        if self.websocket:
            await self.websocket.send(dumps({"text": ""}))  # end marker
            self.websocket = None

    async def speak(self, text):
        # Reconnect if no active connection.
        if not self.websocket or self.websocket.closed:
            await self.connect()

        # Send sentence
        await self.websocket.send(dumps({"text": text, "flush": True}))

        try:
            message = await self.websocket.recv()
            data = loads(message)

            if data.get("audio"):
                audio_bytes = base64.b64decode(data["audio"])
                self.speaker.request(AudioRequest(audio_bytes, self.sample_rate))
        except websockets.exceptions.ConnectionClosedOK:
            # Normal closure (1000), nothing to worry about
            print("WebSocket closed cleanly by server.")
            self.websocket = None
        except websockets.exceptions.ConnectionClosedError as e:
            # Abnormal closure
            print(f"WebSocket closed with error: {e}")
            self.websocket = None
        except Exception as e:
            # Catch-all for JSON parsing or other issues
            print(f"recv response failure: {e}")
            self.websocket = None
