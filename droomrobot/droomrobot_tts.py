import asyncio
import base64
import logging
from json import dumps, loads

import websockets
from sic_framework import AudioRequest

from enum import Enum


class Voice(Enum):
    GOOGLE = 1
    ELEVENLABS = 2


class VoiceConf:

    def __init__(self, speaking_rate):
        self.speaking_rate = speaking_rate


class GoogleVoiceConf(VoiceConf):

    def __init__(self, speaking_rate=1.0, google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE"):
        super().__init__(speaking_rate)
        self.google_tts_voice_name = google_tts_voice_name
        self.google_tts_voice_gender = google_tts_voice_gender


class ElevenLabsVoiceConf(VoiceConf):
    def __init__(self, speaking_rate=None, voice_id='yO6w2xlECAQRFP6pX7Hw', model_id='eleven_flash_v2_5'):
        super().__init__(speaking_rate)
        self.voice_id = voice_id
        self.model_id = model_id


class ElevenLabsTTS:
    def __init__(self, speaker, elevenlabs_key, voice_id, model_id, sample_rate=22050, speaking_rate=None):
        self.speaker = speaker
        self.elevenlabs_key = elevenlabs_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.sample_rate = sample_rate
        self.websocket = None
        self.speaking_rate = max(0.7, min(speaking_rate, 1.2)) if speaking_rate else speaking_rate
        # Development logging
        self.logger = logging.getLogger("droomrobot")

    async def connect(self):
        uri = (
            f"wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream-input"
            f"?model_id={self.model_id}"
            f"&output_format=pcm_{self.sample_rate}"
            f"&inactivity_timeout=180"
        )
        self.websocket = await websockets.connect(uri)

        voice_settings = {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "use_speaker_boost": False,
                "chunk_length_schedule": [50, 120, 160, 290]}
        if self.speaking_rate is not None:
            voice_settings["speed"] = self.speaking_rate

        # Send initial config once
        await self.websocket.send(dumps({
            "text": " ",
            "voice_settings": voice_settings,
            "auto_mode": True,
            "xi_api_key": self.elevenlabs_key,
        }))

    async def disconnect(self):
        if self.websocket:
            try:
                await self.websocket.send(dumps({"text": ""}))  # end marker
                await self.websocket.close()
            except Exception as e:
                self.logger.error(f"[TTS] Error while closing websocket: {e}")
            finally:
                self.websocket = None

    async def ping_connection(self):
        try:
            await self.websocket.ping()
            return True
        except:
            return False

    async def speak(self, text):
        # Reconnect if no active connection.
        if not self.websocket or self.websocket.closed:
            self.logger.warning("[TTS] Websocket not connected. Initiating reconnect.")
            await self.connect()
        if not await self.ping_connection():
            self.logger.warning("[TTS] Websocket not connected. Initiating reconnect.")
            await self.connect()

        # Send sentence
        await self.websocket.send(dumps({"text": text, "flush": True}))

        while True:
            try:
                message = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
                data = loads(message)

                if data.get("audio"):
                    audio_bytes = base64.b64decode(data["audio"])
                    self.speaker.request(AudioRequest(audio_bytes, self.sample_rate))
                    break

                if data.get("isFinal"):
                    break
            except asyncio.TimeoutError:
                self.logger.error('[TTS] No audio received from Elevenlabs')
                self.websocket = None
                break
            except websockets.exceptions.ConnectionClosedOK:
                # Normal closure (1000), nothing to worry about
                self.logger.warning("[TTS] WebSocket closed cleanly by server.")
                self.websocket = None
                break
            except websockets.exceptions.ConnectionClosedError as e:
                # Abnormal closure
                self.logger.error(f"[TTS] WebSocket closed with error: {e}")
                self.websocket = None
                break
            except Exception as e:
                # Catch-all for JSON parsing or other issues
                self.logger.error(f"[TTS] Other failure in elevenlabs tts: {e}")
                self.websocket = None
                break
