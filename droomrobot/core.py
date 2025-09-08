import asyncio
import json
import logging
import queue
import wave
from enum import Enum
from os import environ, fsync
from os.path import exists
from pathlib import Path
import random as rand
from threading import Thread, Event
from time import sleep, strftime

import numpy as np
import mini.mini_sdk as MiniSdk
from mini import MouthLampColor, MouthLampMode
from mini.apis.api_action import PlayAction
from mini.apis.api_expression import SetMouthLamp, PlayExpression
from sic_framework.core.message_python2 import AudioRequest
from sic_framework.devices.alphamini import Alphamini
from sic_framework.devices.common_mini.mini_speaker import MiniSpeakersConf
from sic_framework.devices.desktop import Desktop
from sic_framework.services.dialogflow.dialogflow import (
    Dialogflow,
    DialogflowConf,
    GetIntentRequest,
)
from sic_framework.services.text2speech.text2speech_service import (
    GetSpeechRequest,
    Text2Speech,
    Text2SpeechConf,
)
from sic_framework.services.openai_gpt.gpt import GPT, GPTConf, GPTRequest
from dotenv import load_dotenv

"""
Demo: AlphaMini recognizes user intent and replies using Dialogflow/Text-to-Speech and an LLM.

IMPORTANT
First, you need to set-up Google Cloud Console with dialogflow and Google TTS:

1. Dialogflow: https://socialrobotics.atlassian.net/wiki/spaces/CBSR/pages/2205155343/Getting+a+google+dialogflow+key 
2. TTS: https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/ 
2a. note: you need to set-up a paid account with a credit card. You get $300,- free tokens, which is more then enough
for testing this agent. So in practice it will not cost anything.
3. Create a keyfile as instructed in (1) and save it conf/dialogflow/google_keyfile.json
3a. note: never share the keyfile online. 

Secondly you need to configure your dialogflow agent.
4. In your empty dialogflow agent do the following things:
4a. remove all default intents
4b. go to settings -> import and export -> and import the resources/droomrobot_dialogflow_agent.zip into your
dialogflow agent. That gives all the necessary intents and entities that are part of this example (and many more)

Thirdly, you need an openAI key:
5. Generate your personal openai api key here: https://platform.openai.com/api-keys
6. Either add your openai key to your systems variables or
create a .openai_env file in the conf/openai folder and add your key there like this:
OPENAI_API_KEY="your key"

Forth, the redis server, Dialogflow, Google TTS and OpenAI gpt service need to be running:

7. pip install --upgrade social_interaction_cloud[dialogflow,google-tts,openai-gpt,alphamini]
8. run: conf/redis/redis-server.exe conf/redis/redis.conf
9. run in new terminal: run-dialogflow 
10. run in new terminal: run-google-tts
11. run in new terminal: run-gpt
12. add in the main: the ip address, id, and password of the alphamini and the ip-address of the redis server (= ip address of you laptop)
13. Run this script
"""


class AnimationType(Enum):
    ACTION = 1
    EXPRESSION = 2


class InteractionConf:

    def __init__(self, speaking_rate=None, sleep_time=0, animated=True, max_attempts=2):
        self.speaking_rate = speaking_rate
        self.sleep_time = sleep_time
        self.animated = animated
        self.max_attempts = max_attempts

    @staticmethod
    def apply_config_defaults(config_attr, param_names):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                config = getattr(self, config_attr)
                for name in param_names:
                    if kwargs.get(name) is None:
                        kwargs[name] = getattr(config, name)
                return func(self, *args, **kwargs)

            return wrapper

        return decorator


class Droomrobot:
    def __init__(self, mini_ip, mini_id, mini_password, redis_ip,
                 google_keyfile_path, sample_rate_dialogflow_hertz=44100, dialogflow_language="nl", dialogflow_timeout=None,
                 google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE", default_speaking_rate=1.0,
                 openai_key_path=None,
                 computer_test_mode=False):

        print("\n SETTING UP BASIC PROCESSING")
        # Development logging
        self.logger = logging.getLogger("droomrobot")

        # Data logging
        self._log_queue = None
        self._log_thread = None

        # Interaction configuration
        self.interaction_conf = InteractionConf()
        print('complete')

        print("\n SETTING UP OPENAI")
        # Generate your personal openai api key here: https://platform.openai.com/api-keys
        # Either add your openai key to your systems variables (and comment the next line out) or
        # create a .openai_env file in the conf/openai folder and add your key there like this:
        # OPENAI_API_KEY="your key"
        if openai_key_path:
            load_dotenv(openai_key_path)

        # Setup GPT client
        conf = GPTConf(openai_key=environ["OPENAI_API_KEY"])
        self.gpt = GPT(conf=conf)
        print('Complete')

        print("\n SETTING UP DIALOGFLOW")
        # set up the config for dialogflow
        dialogflow_conf = DialogflowConf(keyfile_json=json.load(open(google_keyfile_path)),
                                         sample_rate_hertz=sample_rate_dialogflow_hertz,
                                         language=dialogflow_language,
                                         timeout=dialogflow_timeout)

        # initiate Dialogflow object
        self.dialogflow = Dialogflow(ip="localhost", conf=dialogflow_conf)
        # flag to signal when the app should listen (i.e. transmit to dialogflow)
        self.request_id = np.random.randint(10000)
        print('Complete')

        print("\n SETTING UP TTS")
        # setup the tts service
        self.google_tts_voice_name = google_tts_voice_name
        self.google_tts_voice_gender = google_tts_voice_gender
        self.tts = Text2Speech(conf=Text2SpeechConf(keyfile=google_keyfile_path,
                                                    speaking_rate=default_speaking_rate))
        init_reply = self.tts.request(GetSpeechRequest(text="Ik ben aan het initializeren",
                                                       voice_name=self.google_tts_voice_name,
                                                       ssml_gender=self.google_tts_voice_gender))
        print('Complete')

        if not computer_test_mode:
            print("\n SETTING UP ALPHAMINI")
            print("Connecting to SIC on alphamini")
            self.mini_id = mini_id
            self.mini = Alphamini(
                ip=mini_ip,
                mini_id=self.mini_id,
                mini_password=mini_password,
                redis_ip=redis_ip,
                speaker_conf=MiniSpeakersConf(sample_rate=init_reply.sample_rate),
                bypass_install=True
            )
            self.speaker = self.mini.speaker
            self.mic = self.mini.mic
            self.device_name = "alphamini"

            print("Connecting to miniSDK")
            # Create asyncio event loop to keep connection open to miniSDK.
            self.animation_futures = []
            self.background_loop = asyncio.new_event_loop()
            self.background_thread = Thread(target=self._start_loop, daemon=True)
            self.background_thread.start()
            self.mini_api = None
            future = asyncio.run_coroutine_threadsafe(self._connect_once(), self.background_loop)
            try:
                future.result()
                self.animate(AnimationType.ACTION, "009")  # Wake up
                self.animate(AnimationType.EXPRESSION, "codemao20")  # Blink
            except Exception as e:
                self.logger.error("Failed to connect to mini device", exc_info=e)

        else:
            print("\n SETTING UP COMPUTER")
            desktop = Desktop()
            self.speaker = desktop.speakers
            self.mic = desktop.mic
            self.device_name = "computer"
        print("Complete")

        print("\n SETTING UP MIC CONNECTION")
        # connect the output of Minimicrophone as the input of DialogflowComponent
        self.dialogflow.connect(self.mic)
        self.dialogflow.register_callback(self._on_dialog)
        print("Complete and ready for interaction!")

    def start_logging(self, log_id, init_data: dict):
        folder = Path("logs")
        folder.mkdir(parents=True, exist_ok=True)
        log_path = folder / f"{log_id}.log"
        self._log_queue = queue.Queue()
        self._log_thread = Thread(target=self.log_writer, args=(log_path,), daemon=True)
        self._log_thread.start()

        timestamp = strftime("%Y-%m-%d %H:%M:%S")
        self._log_queue.put(f'[{timestamp}] ### START NEW LOG ###')
        self._log_queue.put(', '.join(f"{k}: {v}" for k, v in init_data.items()))

    def stop_logging(self):
        if self._log_queue:
            self._log_queue.put(None)
        if self._log_thread:
            self._log_thread.join()

    def log_writer(self, log_path):
        with open(log_path, 'a', encoding='utf-8') as f:
            while True:
                item = self._log_queue.get()
                if item is None:
                    break  # Exit signal
                f.write(item + '\n')
                f.flush()

    def log_utterance(self, speaker, text):
        if self._log_queue:
            timestamp = strftime("%Y-%m-%d %H:%M:%S")
            self._log_queue.put(f"[{timestamp}] {speaker}: {text}")

    def log_recognition_result(self, recognition_result):
        if self._log_queue:
            timestamp = strftime("%Y-%m-%d %H:%M:%S")
            self._log_queue.put(f"[{timestamp}] recognition result: {recognition_result}")

    @InteractionConf.apply_config_defaults('interaction_conf', ['speaking_rate', 'sleep_time', 'animated'])
    def say(self, text, speaking_rate=None, sleep_time=None, animated=None):
        if speaking_rate:
            reply = self.tts.request(GetSpeechRequest(text=text,
                                                      voice_name=self.google_tts_voice_name,
                                                      ssml_gender=self.google_tts_voice_gender,
                                                      speaking_rate=speaking_rate))
        else:
            reply = self.tts.request(GetSpeechRequest(text=text,
                                                      voice_name=self.google_tts_voice_name,
                                                      ssml_gender=self.google_tts_voice_gender))

        self.speaker.request(AudioRequest(reply.waveform, reply.sample_rate))
        if animated:
            self.animate(AnimationType.EXPRESSION, self._random_speaking_eye_expression(), run_async=True)
            self.animate(AnimationType.ACTION, self._random_speaking_act(), run_async=True)
        self.log_utterance(speaker='robot', text=text)
        if sleep_time and sleep_time > 0:
            sleep(sleep_time)

    def play_audio(self, audio_file):
        with wave.open(audio_file, 'rb') as wf:
            # Get parameters
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()

            # Ensure format is 16-bit (2 bytes per sample)
            if sample_width != 2:
                raise ValueError("WAV file is not 16-bit audio. Sample width = {} bytes.".format(sample_width))

            self.speaker.request(AudioRequest(wf.readframes(n_frames), framerate))
            self.log_utterance(speaker='robot', text=f'plays {audio_file}')

    @InteractionConf.apply_config_defaults('interaction_conf', ['max_attempts', 'speaking_rate', 'animated'])
    def ask_yesno(self, question, max_attempts=None, speaking_rate=None, animated=None):
        attempts = 0
        while attempts < max_attempts:
            # ask question
            self.say(question, speaking_rate=speaking_rate, animated=animated)

            self.set_mouth_lamp(MouthLampColor.GREEN, MouthLampMode.NORMAL)
            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id, {'answer_yesno': 1}))
            self.set_mouth_lamp(MouthLampColor.WHITE, MouthLampMode.BREATH)
            print("The detected intent:", reply.intent)

            # return answer
            if reply.intent:
                self.log_recognition_result(f'context: answer_yesno, recognized_intent: {str(reply.intent)}')
                if "yesno_yes" in reply.intent:
                    return "yes"
                elif "yesno_no" in reply.intent:
                    return "no"
                elif "yesno_dontknow" in reply.intent:
                    return "dontknow"

            self.log_recognition_result(f'context: answer_yesno, recognized_intent: None')
            attempts += 1
        self.log_recognition_result(f'context: answer_yesno, intent recognition failed')
        return None

    @InteractionConf.apply_config_defaults('interaction_conf', ['max_attempts', 'speaking_rate', 'animated'])
    def ask_entity(self, question, context, target_intent, target_entity, max_attempts=None, speaking_rate=None, animated=None):
        attempts = 0

        while attempts < max_attempts:
            # ask question
            self.say(question, speaking_rate=speaking_rate, animated=animated)
            self.set_mouth_lamp(MouthLampColor.GREEN, MouthLampMode.NORMAL)
            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id, context))
            self.set_mouth_lamp(MouthLampColor.WHITE, MouthLampMode.BREATH)
            print("The detected intent:", reply.intent)

            # Return entity
            if reply.intent:
                if target_intent in reply.intent:
                    if reply.response.query_result.parameters and target_entity in reply.response.query_result.parameters:
                        result_entity = reply.response.query_result.parameters[target_entity]
                        self.log_recognition_result(f'context: {context}, target_intent: {target_intent}, '
                                                    f'target_entity: {target_entity}, recognized_entity: {str(result_entity)}')
                        return result_entity
            attempts += 1
            self.log_recognition_result(f'context: {context}, target_intent: {target_intent}, '
                                        f'target_entity: {target_entity}, recognized_intent: None')

        self.log_recognition_result(f'context: {context}, intent recognition failed')
        return None

    @InteractionConf.apply_config_defaults('interaction_conf', ['max_attempts', 'speaking_rate', 'animated'])
    def ask_open(self, question, max_attempts=None, speaking_rate=None, animated=None):
        attempts = 0

        while attempts < max_attempts:
            # ask question
            self.say(question, speaking_rate=speaking_rate, animated=animated)

            self.set_mouth_lamp(MouthLampColor.GREEN, MouthLampMode.NORMAL)
            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id))
            self.set_mouth_lamp(MouthLampColor.WHITE, MouthLampMode.BREATH)

            print("The detected intent:", reply.intent)

            # Return entity
            if reply.response.query_result.query_text:
                return reply.response.query_result.query_text
            attempts += 1
        return None

    @InteractionConf.apply_config_defaults('interaction_conf', ['speaking_rate', 'animated'])
    def ask_fake(self, question, duration, speaking_rate=None, animated=None):
        self.say(question, speaking_rate=speaking_rate, animated=animated)
        self.set_mouth_lamp(MouthLampColor.GREEN, MouthLampMode.NORMAL)
        sleep(duration)
        self.set_mouth_lamp(MouthLampColor.WHITE, MouthLampMode.BREATH)

    @InteractionConf.apply_config_defaults('interaction_conf', ['max_attempts', 'speaking_rate', 'animated'])
    def ask_entity_llm(self, question, strict=False, max_attempts=None, speaking_rate=None, animated=None):
        attempts = 0

        while attempts < max_attempts:
            # ask question
            self.say(question, speaking_rate=speaking_rate, animated=animated)

            self.set_mouth_lamp(MouthLampColor.GREEN, MouthLampMode.NORMAL)
            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id))
            self.set_mouth_lamp(MouthLampColor.WHITE, MouthLampMode.BREATH)

            strict_instruction = ''
            if strict:
                strict_instruction = (f'Zorg ervoor dat de entity gerelateerd aan de vraag. '
                                      f'Is dat niet het geval return dan "none"'
                                      f'Bijvoorbeeld als de reactie is "lust er iemand nog koffie"'
                                      f'dan is "koffie" niet gerelateerd aan de vraag.')
            # Return entity
            if reply.response.query_result.query_text:
                print(f'transcript is {reply.response.query_result.query_text}')
                gpt_response = self.gpt.request(
                    GPTRequest(f'Je bent een sociale robot die praat met een kind tussen de 6 en 9 jaar oud. '
                               f'De robot stelt een vraag over een interesse van het kind.'
                               f'Jouw taak is om de key entity er uit te filteren'
                               f'Bijvoorbeeld bij de vraag: "wat is je lievelingsdier?" '
                               f'en de reactie "mijn lievelingsdier is een hond" '
                               f'filter je alleen "hond" als key entity uit. '
                               f'{strict_instruction}'
                               # f'of bijvoorbeeld "wat is je superkracht?" en de reactie '
                               # f'is "mijn superkracht is heel hard rennen"'
                               # f'filter je "heel hard rennen" er uit.'
                               f'Als robot heb je net het volgende gevraagt {question}'
                               f'Dit is de reactie van het kind {reply.response.query_result.query_text}'
                               f'Return alleen de key entity string terug (of none).'))
                print(f'response is {gpt_response.response}')

                self.log_recognition_result(f'llm extracted entity: {gpt_response.response}')
                if gpt_response.response != 'none':
                    return gpt_response.response
            attempts += 1
        self.log_recognition_result('llm extracted entity: None')
        return None

    @InteractionConf.apply_config_defaults('interaction_conf', ['max_attempts', 'speaking_rate', 'animated'])
    def ask_opinion_llm(self, question, max_attempts=None, speaking_rate=None, animated=None):
        attempts = 0

        while attempts < max_attempts:
            # ask question
            self.say(question, speaking_rate=speaking_rate, animated=animated)

            self.set_mouth_lamp(MouthLampColor.GREEN, MouthLampMode.NORMAL)
            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id))
            self.set_mouth_lamp(MouthLampColor.WHITE, MouthLampMode.BREATH)

            # Return entity
            if reply.response.query_result.query_text:
                print(f'transcript is {reply.response.query_result.query_text}')
                gpt_response = self.gpt.request(
                    GPTRequest(f'Je bent een sociale robot die praat met een kind tussen de 6 en 9 jaar oud. '
                               f'De robot stelt een vraag over een interesse van het kind.'
                               f'Jouw taak is om de mening van het kind er uit te filteren'
                               f'Bijvoorbeeld bij de vraag: "hoe goed is het gegaan?" '
                               f'en de reactie "het ging niet zo goed" '
                               f'filter je "negative" als opinion er uit. '
                               # f'of bijvoorbeeld "wat is je superkracht?" en de reactie '
                               # f'is "mijn superkracht is heel hard rennen"'
                               # f'filter je "heel hard rennen" er uit.'
                               f'Als robot heb je net het volgende gevraagt {question}'
                               f'Dit is de reactie van het kind {reply.response.query_result.query_text}'
                               f'Return alleen de opinion string (positive/negative) terug.'))
                print(f'response is {gpt_response.response}')
                self.log_recognition_result(f'llm extracted sentiment: {gpt_response.response}')
                return gpt_response.response
            attempts += 1
        self.log_recognition_result('llm extracted sentiment: None')
        return None

    def get_article(self, word):
        gpt_response = self.gpt.request(
            GPTRequest(
                f'Retourneer het lidwoord van {word}. Retouneer alleen het lidwoord zelf bijv. "de" of "het" en geen andere informatie.'))
        return gpt_response.response

    def get_adjective(self, word):
        gpt_response = self.gpt.request(
            GPTRequest(
                f'Retourneer het bijvoeglijk naamwoord van {word}. Retourneer alleen het bijvoeglijk naamwoord zelf bijv. "groene" of "zachte" en geen andere informatie.'))
        return gpt_response.response

    def personalize(self, robot_input, user_age, user_input):
        gpt_response = self.gpt.request(
            GPTRequest(f'Je bent een sociale robot die praat met een kind van {str(user_age)} jaar oud.'
                       f'Het kind ligt in het ziekenhuis.'
                       f'Jij bent daar om het kind af te leiden met een leuk gesprek.'
                       f'Als robot heb je zojuist het volgende gevraagd: {robot_input}'
                       f'Het kind reageerde met het volgende: "{user_input}"'
                       f'Genereer nu een passende reactie in 1 zin. '
                       f'Het mag geen vraag zijn. De woordenschat en het taalniveau moeten op B2 niveau zijn.'))
        return gpt_response.response

    def generate_funny_response(self, user_age, context, user_input):
        gpt_response = self.gpt.request(
            GPTRequest(f'Je bent een sociale robot die praat met een kind van {str(user_age)} jaar oud.'
                       f'Het kind ligt in het ziekenhuis.'
                       f'Jij bent daar om het kind af te leiden met een leuk gesprek.'
                       f'Dit is de context van het gesprek: {context}'
                       f'Het kind reageerde met het volgende: "{user_input}"'
                       f'Genereer nu een grappige reactie in één of twee zinnen. '
                       f'Het mag geen vraag zijn. De woordenschat en het taalniveau moeten op B2 niveau zijn.'))
        return gpt_response.response

    def generate_question(self, user_age, robot_input, user_input):
        gpt_response = self.gpt.request(
            GPTRequest(f'Je bent een sociale robot die praat met een kind van {str(user_age)} jaar oud.'
                       f'Het kind ligt in het ziekenhuis.'
                       f'Jij bent daar om het kind af te leiden met een leuk gesprek.'
                       f'Als robot heb je zojuist het volgende gevraagd: {robot_input}'
                       f'Het kind reageerde met het volgende: "{user_input}"'
                       f'Genereer nu 1 passende vervolgvraag. '
                       f'De woordenschat en het taalniveau moeten op B2 niveau zijn.'))
        return gpt_response.response

    def animate(self, animation_type: AnimationType, animation_id: str, run_async=False):
        try:
            future = asyncio.run_coroutine_threadsafe(
                self._animation_action(animation_id, animation_type),
                self.background_loop
            )
        except Exception as e:
            self.logger.error(f'Animation {animation_id} failed: {e}', exc_info=e)
            return

        self.animation_futures.append(future)

        if not run_async:
            future.result()

    async def _animation_action(self, action_name, animation_type):
        try:
            if animation_type == AnimationType.ACTION:
                action: PlayAction = PlayAction(action_name=action_name)
                await action.execute()
            elif animation_type == AnimationType.EXPRESSION:
                action: PlayExpression = PlayExpression(express_name=action_name)
                await action.execute()
        except Exception as e:
            self.logger.error(f'Animation action {action_name} failed {e}', exc_info=e)

    def set_mouth_lamp(self, color: MouthLampColor, mode: MouthLampMode, duration=-1, breath_duration=1000,
                       run_async=False):
        if 'computer' in self.device_name:
            print(f"Set mouth lamp: {color} {mode} {duration} {breath_duration}")
        else:
            future = asyncio.run_coroutine_threadsafe(self._mouth_lamp_expression(color, mode, duration, breath_duration),
                                                      self.background_loop)
            self.animation_futures.append(future)

            if not run_async:
                future.result()

    async def _mouth_lamp_expression(self, color: MouthLampColor, mode: MouthLampMode, duration=-1, breath_duration=1000):
        if mode == MouthLampMode.BREATH:
            mouth_lamp_action: SetMouthLamp = SetMouthLamp(color=color, mode=MouthLampMode.BREATH,
                                                           breath_duration=breath_duration)
        else:
            mouth_lamp_action: SetMouthLamp = SetMouthLamp(color=color, mode=MouthLampMode.NORMAL, duration=duration)
        await mouth_lamp_action.execute()

    def disconnect(self):
        if self.device_name == 'alphamini':
            for fut in self.animation_futures:
                fut.cancel()

            # Disconnect from miniSDK
            future = asyncio.run_coroutine_threadsafe(self._disconnect_alphamini_api(), self.background_loop)
            future.result()
            # Schedule loop shutdown
            if self.background_loop.is_running():
                self.background_loop.call_soon_threadsafe(self.background_loop.stop)
            # Wait for the thread to finish
            self.background_thread.join()

    def _on_dialog(self, message):
        if message.response:
            transcript = message.response.recognition_result.transcript
            print("Transcript:", transcript)
            if message.response.recognition_result.is_final:
                self.log_utterance(speaker='child', text=transcript)

    def _start_loop(self):
        asyncio.set_event_loop(self.background_loop)
        self.background_loop.run_forever()

    async def _connect_once(self):
        if not self.mini_api:
            self.mini_api = await MiniSdk.get_device_by_name(self.mini_id, 10)
            await MiniSdk.connect(self.mini_api)

    @staticmethod
    async def _disconnect_alphamini_api():
        await MiniSdk.release()

    @staticmethod
    def _get_user_model_file_path(participant_id: str):
        folder = Path("user_models")
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"user_model_{participant_id}.json"

    def load_user_model(self, participant_id: str):
        file_path = self._get_user_model_file_path(participant_id)
        if exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        else:
            return {}

    def save_user_model(self, participant_id: str, user_model: dict):
        file_path = self._get_user_model_file_path(participant_id)
        with open(file_path, "w") as f:
            json.dump(user_model, f, indent=4)
            f.flush()  # flush internal buffers
            fsync(f.fileno())  # flush OS buffers to disk

    def set_interaction_conf(self, interaction_conf: InteractionConf):
        self.interaction_conf = interaction_conf

    def reset_interaction_conf(self):
        self.interaction_conf = InteractionConf()

    @staticmethod
    def _random_speaking_act():
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
        return rand.choice(speaking_acts)

    @staticmethod
    def _random_speaking_eye_expression():
        speaking_expressions = [
                "codemao1", "codemao2", "codemao3", "codemao4", "codemao5",
                "codemao6", "codemao7", "codemao8", "codemao9", "codemao10",
                "codemao11", "codemao12", "codemao13", "codemao14", "codemao15",
                "codemao16", "codemao17", "codemao18", "codemao19", "codemao20"]
        return rand.choice(speaking_expressions)