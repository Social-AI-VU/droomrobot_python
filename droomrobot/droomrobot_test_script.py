import json
from os import environ
from os.path import abspath, join

import numpy as np
from sic_framework.core.message_python2 import AudioMessage, AudioRequest
from sic_framework.services.text2speech.text2speech_service import Text2Speech, Text2SpeechConf, GetSpeechRequest, SpeechResult
from sic_framework.devices.alphamini import Alphamini
from sic_framework.devices.common_mini.mini_speaker import MiniSpeakersConf

from sic_framework.services.openai_gpt.gpt import GPT, GPTConf, GPTRequest
from dotenv import load_dotenv

from sic_framework.devices.desktop import Desktop
from sic_framework.services.dialogflow.dialogflow import (
    Dialogflow,
    DialogflowConf,
    GetIntentRequest,
)

"""
This is an example script for the droomrobot project.

IMPORTANT
First, you need to set-up Google Cloud Console with dialogflow and Google TTS:

1. Dialogflow: https://socialrobotics.atlassian.net/wiki/spaces/CBSR/pages/2205155343/Getting+a+google+dialogflow+key 
2. TTS: https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/ 
3. Create a keyfile as instructed in (1) and save it conf/dialogflow/google_keyfile.json

Second, you need an openAI key:
4. Generate your personal openai api key here: https://platform.openai.com/api-keys
5. Either add your openai key to your systems variables or
create a .openai_env file in the conf/openai folder and add your key there like this:
OPENAI_API_KEY="your key"

Third, the redis server, Dialogflow, Google TTS and OpenAI gpt service need to be running:

6. pip install --upgrade social-interaction-cloud[dialogflow,google-tts,openai-gpt,alphamini]
7. run: conf/redis/redis-server.exe conf/redis/redis.conf
8. run in new terminal: run-dialogflow 
9. run in new terminal: run-google-tts
10. run in new terminal: run-gpt
11. Run this script
"""


class Droomrobot:
    def __init__(self, mini_ip, mini_id, mini_password, redis_ip,
                 google_keyfile_path, sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                 google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE",
                 openai_key_path=None):
        # Generate your personal openai api key here: https://platform.openai.com/api-keys
        # Either add your openai key to your systems variables (and comment the next line out) or
        # create a .openai_env file in the conf/openai folder and add your key there like this:
        # OPENAI_API_KEY="your key"
        if openai_key_path:
            load_dotenv(openai_key_path)

        # Setup GPT client
        conf = GPTConf(openai_key=environ["OPENAI_API_KEY"])
        self.gpt = GPT(conf=conf)



        # set up the config for dialogflow
        dialogflow_conf = DialogflowConf(keyfile_json=json.load(open(google_keyfile_path)),
                                         sample_rate_hertz=sample_rate_dialogflow_hertz, language=dialogflow_language)

        # initiate Dialogflow object
        self.dialogflow = Dialogflow(ip="localhost", conf=dialogflow_conf)

        # set-up desktop client
        self.desktop = Desktop()

        # connect the output of DesktopMicrophone as the input of DialogflowComponent
        self.dialogflow.connect(self.desktop.mic)

        # flag to signal when the app should listen (i.e. transmit to dialogflow)
        self.can_listen = True
        self.request_id = np.random.randint(10000)
        self.is_yesno = False


        # Initialize TTS
        self.google_tts_voice_name = google_tts_voice_name
        self.google_tts_voice_gender = google_tts_voice_gender
        self.tts = Text2Speech(conf=Text2SpeechConf(keyfile=google_keyfile_path))
        init_reply = self.tts.request(GetSpeechRequest(text="Ik ben aan het initializeren",
                                                  voice_name=self.google_tts_voice_name,
                                                  ssml_gender=self.google_tts_voice_gender))

        self.mini = Alphamini(ip=mini_ip, mini_id=mini_id, mini_password=mini_password, redis_ip=redis_ip,
                              speaker_conf=MiniSpeakersConf(sample_rate=init_reply.sample_rate))

    def say(self, text):
        reply = self.tts.request(GetSpeechRequest(text=text,
                                                  voice_name=self.google_tts_voice_name,
                                                  ssml_gender=self.google_tts_voice_gender))
        self.mini.speaker.request(AudioRequest(reply.waveform, reply.sample_rate))

    def ask_yesno(self, question, max_attempts=2):
        attempts = 0
        while attempts < max_attempts:
            # ask question
            tts_reply = self.tts.request(GetSpeechRequest(text=question,
                                                          voice_name=self.google_tts_voice_name,
                                                          ssml_gender=self.google_tts_voice_gender))
            self.mini.speaker.request(AudioRequest(tts_reply.waveform, tts_reply.sample_rate))

            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id, {'answer_yesno': 1}))

            print("The detected intent:", reply.intent)

            # return answer
            if reply.intent:
                if "yesno_yes" in reply.intent:
                    return "yes"
                elif "yesno_no" in reply.intent:
                    return "no"
                elif "yesno_dontknow" in reply.intent:
                    return "dontknow"
            attempts += 1
        return None

    def ask_entity(self, question, context, target_intent, target_entity, max_attempts=2):
        attempts = 0

        while attempts < max_attempts:
            # ask question
            tts_reply = self.tts.request(GetSpeechRequest(text=question,
                                                          voice_name=self.google_tts_voice_name,
                                                          ssml_gender=self.google_tts_voice_gender))
            self.mini.speaker.request(AudioRequest(tts_reply.waveform, tts_reply.sample_rate))

            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id, context))

            print("The detected intent:", reply.intent)

            # Return entity
            if reply.intent:
                if target_intent in reply.intent:
                    if reply.response.query_result.parameters and target_entity in reply.response.query_result.parameters:
                        return reply.response.query_result.parameters[target_entity]
            attempts += 1
        return None

    def ask_open(self, question, max_attempts=2):
        attempts = 0

        while attempts < max_attempts:
            # ask question
            tts_reply = self.tts.request(GetSpeechRequest(text=question,
                                                          voice_name=self.google_tts_voice_name,
                                                          ssml_gender=self.google_tts_voice_gender))
            self.mini.speaker.request(AudioRequest(tts_reply.waveform, tts_reply.sample_rate))

            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id))

            print("The detected intent:", reply.intent)

            # Return entity
            if reply.response.query_result.query_text:
                return reply.response.query_result.query_text
            attempts += 1
        return None

    def personalize(self, robot_input, user_age, user_input):
        gpt_response = self.gpt.request(
            GPTRequest(f'Je bent een sociale robot die praat met een kind van {str(user_age)} jaar oud.'
                       f'Het kind ligt in het ziekenhuis.'
                       f'Jij bent daar om het kind af te leiden met een leuk gesprek.'
                       f'Als robot heb je zojuist het volgende gevraagd: {robot_input}'
                       f'Het kind reageerde met het volgende: "{user_input}"'
                       f'Genereer nu een passende reactie in 1 zin.'))
        return gpt_response.response

    def run(self):
        # self.say("Hallo, ik ben de droomrobot en ik ben hier voor jou.")
        likes_animals = self.ask_yesno("Hou je van dieren?")
        print(likes_animals)
        if "yes" in likes_animals:
            lievelingsdier = self.ask_entity("Wat is jouw lievelingsdier?", {'animals': 1},
                                              'animals', 'animals')
            print(lievelingsdier)

            if lievelingsdier:
                open_question = f"Wat vind je zo leuk aan een {lievelingsdier}?"
                lievelingsdier_motivation = self.ask_open(open_question)
                print(lievelingsdier_motivation)

                if lievelingsdier_motivation:
                    personalized_response = self.personalize(open_question,7, lievelingsdier_motivation)
                    print(personalized_response)

                    if personalized_response:
                        self.say(personalized_response)


if __name__ == '__main__':
    droomrobot = Droomrobot(mini_ip="192.168.178.111", mini_id="00167", mini_password="alphago", redis_ip="192.168.178.84",
                            google_keyfile_path=abspath(join("..", "conf", "dialogflow", "google_keyfile.json")),
                            openai_key_path=abspath(join("..", "conf", "openai", ".openai_env")))
    droomrobot.run()
