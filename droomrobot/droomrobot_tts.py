import asyncio
import base64
import logging
import os
import hashlib
import string
import threading
import wave
from json import dumps, loads, load, dump
from pathlib import Path

import websockets

from enum import Enum


class TTSService(Enum):
    GOOGLE = 1
    ELEVENLABS = 2


class TTSConf:

    def __init__(self, speaking_rate):
        self.speaking_rate = speaking_rate


class GoogleTTSConf(TTSConf):

    def __init__(self, speaking_rate=1.0, google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE"):
        super().__init__(speaking_rate)
        self.google_tts_voice_name = google_tts_voice_name
        self.google_tts_voice_gender = google_tts_voice_gender


class ElevenLabsTTSConf(TTSConf):
    def __init__(self, speaking_rate=None, voice_id='yO6w2xlECAQRFP6pX7Hw', model_id='eleven_flash_v2_5'):
        super().__init__(None if speaking_rate == 1.0 else speaking_rate)
        self.voice_id = voice_id
        self.model_id = model_id


class ElevenLabsTTS:
    def __init__(self, elevenlabs_key, voice_id, model_id, sample_rate=22050, speaking_rate=None):
        self.elevenlabs_key = elevenlabs_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.sample_rate = sample_rate
        self.websocket = None
        self.speaking_rate = max(0.7, min(speaking_rate, 1.2)) if speaking_rate else speaking_rate
        self.lock = asyncio.Lock()
        # Development logging
        self.logger = logging.getLogger("droomrobot")

    async def connect(self):
        uri = (
            f"wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream-input"
            f"?model_id={self.model_id}"
            f"&output_format=pcm_{self.sample_rate}"
            f"&inactivity_timeout=180"
            f"&auto_mode=false"
        )
        self.websocket = await websockets.connect(uri)

        voice_settings = {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "use_speaker_boost": False,
                "chunk_length_schedule": [120, 160, 250, 290]}
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

    async def drain_socket(self):
        try:
            while True:
                await asyncio.wait_for(self.websocket.recv(), timeout=0.2)
                self.logger.warning("[TTS] Had to drain the websocket.")
        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
            pass

    async def speak(self, text):
        async with self.lock:
            # Reconnect if no active connection.
            if not self.websocket or self.websocket.closed:
                self.logger.warning("[TTS] Websocket not connected. Initiating reconnect.")
                await self.connect()
            if not await self.ping_connection():
                self.logger.warning("[TTS] Websocket not connected. Initiating reconnect.")
                await self.connect()

            await self.drain_socket()
            # Send sentence
            await self.websocket.send(dumps({"text": text, "flush": True}))

            audio_chunks = []
            while True:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
                    data = loads(message)

                    if data.get("audio"):
                        audio_chunks.append(base64.b64decode(data["audio"]))

                    if data.get("isFinal"):
                        if audio_chunks:
                            return b"".join(audio_chunks)
                        return None

                except asyncio.TimeoutError:
                    if audio_chunks:
                        return b"".join(audio_chunks)

                    self.logger.error('[TTS] No audio received from Elevenlabs')
                    self.websocket = None
                    return None

                except websockets.exceptions.ConnectionClosedOK:
                    # Normal closure (1000), nothing to worry about
                    self.logger.warning("[TTS] WebSocket closed cleanly by server.")
                    self.websocket = None
                    return b"".join(audio_chunks) if audio_chunks else None
                except websockets.exceptions.ConnectionClosedError as e:
                    # Abnormal closure
                    self.logger.error(f"[TTS] WebSocket closed with error: {e}")
                    self.websocket = None
                    return b"".join(audio_chunks) if audio_chunks else None
                except Exception as e:
                    # Catch-all for JSON parsing or other issues
                    self.logger.error(f"[TTS] Other failure in elevenlabs tts: {e}")
                    self.websocket = None
                    return b"".join(audio_chunks) if audio_chunks else None

class TTSCacher:

    def __init__(self, tts_cache_dir='tts_cache', tts_cache_map_file_name='tts_cache_map.json', subfolder_depth=2):
        root = Path(__file__).parent.resolve()
        self.tts_cache_dir = root / tts_cache_dir
        self.tts_cache_map_file = self.tts_cache_dir / tts_cache_map_file_name
        self.subfolder_depth = subfolder_depth

        self.tts_cache = self._load_cache()

        # Serializes save_audio_file and _save_cache so concurrent writers
        # (e.g. live say() racing with a background pregen) don't collide
        # on the same .wav file or corrupt the JSON cache map.
        self._write_lock = threading.Lock()

    @staticmethod
    def normalize_text(text: str) -> str:
        """Lowercase, strip, remove punctuation for consistent caching"""
        text = text.strip().lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        return text

    def make_tts_key(self, text: str, voice_conf: TTSConf) -> str:
        """Generate a hash key based on text + TTS parameters"""
        if isinstance(voice_conf, GoogleTTSConf):
            payload = {
                "text": self.normalize_text(text),
                'tts_service': "GOOGLE",
                "speaking_rate": voice_conf.speaking_rate,
                "setting_1": voice_conf.google_tts_voice_name,
                "setting_2": voice_conf.google_tts_voice_gender,
            }
        elif isinstance(voice_conf, ElevenLabsTTSConf):
            payload = {
                "text": self.normalize_text(text),
                'tts_service': "ELEVENLABS",
                "speaking_rate": voice_conf.speaking_rate,
                "setting_1": voice_conf.model_id,
                "setting_2": voice_conf.voice_id,
            }
        else:
            raise ValueError(f'Voice Conf {voice_conf} is not supported.')

        # Sort keys to ensure deterministic JSON
        canonical = dumps(payload, sort_keys=True)
        return hashlib.md5(canonical.encode("utf-8")).hexdigest()

    def save_audio_file(self, tts_key: str, audio_bytes: bytes, sample_rate: int, sample_width: int = 2, channels: int = 1):
        """Write the wav for `tts_key` and register it in the cache map.

        Safe to call from multiple threads — a single lock serializes
        callers, and a second caller for the same key short-circuits
        once it sees the first writer already cached it. The wav itself
        is written atomically (temp file + rename) so a partial write
        can never produce a half-written .wav on disk."""
        subfolder_name = tts_key[:self.subfolder_depth]
        subfolder = self.tts_cache_dir / subfolder_name
        filename = subfolder / f"{tts_key}.wav"

        with self._write_lock:
            # If another writer beat us to it, don't redo the work — the
            # bytes are already on disk and registered.
            if tts_key in self.tts_cache and filename.exists():
                return

            try:
                os.makedirs(subfolder, exist_ok=True)

                tmp_filename = subfolder / (
                    f"{tts_key}.{os.getpid()}.{threading.get_ident()}.tmp.wav"
                )
                with wave.open(str(tmp_filename), "wb") as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(sample_width)  # 2 bytes = 16-bit
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_bytes)

                # Atomic publish — readers either see the old file (if
                # any) or the complete new one, never a half-written wav.
                os.replace(str(tmp_filename), str(filename))

                self.tts_cache[tts_key] = f"{subfolder_name}/{tts_key}.wav"
                self._save_cache_locked()
            except Exception as e:
                # Don't let a transient FS error (permission, brief lock,
                # antivirus, etc.) crash the script. Worst case we miss
                # the cache once and regenerate next time.
                print(f"[TTS] save_audio_file failed for {tts_key}: {e!r}")
                # Best-effort cleanup of any leftover temp file.
                try:
                    if 'tmp_filename' in locals() and tmp_filename.exists():
                        tmp_filename.unlink()
                except Exception:
                    pass

    def load_audio_file(self, tts_key):
        if tts_key in self.tts_cache:
            # Cached audio exists, play it
            audio_file = self.tts_cache[tts_key]
            audio_path = Path(audio_file)
            if not audio_path.is_absolute():
                audio_path = self.tts_cache_dir / audio_path
            if os.path.exists(audio_path):
                return str(audio_path)
            else:
                # Stale map entry; drop it under the write lock so we
                # don't race with a save_audio_file() that's mid-flight.
                with self._write_lock:
                    if tts_key in self.tts_cache:
                        del self.tts_cache[tts_key]
                        self._save_cache_locked()
        return None

    def _load_cache(self) -> dict:
        if os.path.exists(self.tts_cache_map_file):
            with open(self.tts_cache_map_file, "r") as f:
                return load(f)
        return {}

    def _save_cache(self):
        with self._write_lock:
            self._save_cache_locked()

    def _save_cache_locked(self):
        """Caller must already hold self._write_lock. Writes via temp file
        + rename so an interrupted dump can never leave the JSON map
        truncated (which would orphan every cached wav)."""
        tmp = self.tts_cache_map_file.with_suffix(
            self.tts_cache_map_file.suffix + f".{os.getpid()}.{threading.get_ident()}.tmp"
        )
        try:
            with open(tmp, "w") as f:
                dump(self.tts_cache, f, indent=2)
            os.replace(str(tmp), str(self.tts_cache_map_file))
        except Exception as e:
            print(f"[TTS] _save_cache failed: {e!r}")
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
