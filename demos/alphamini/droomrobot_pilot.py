import json
from os.path import abspath, join
from os import environ


import numpy as np
from sic_framework.core.message_python2 import AudioRequest
from sic_framework.devices.alphamini import Alphamini
from sic_framework.devices.common_mini.mini_speaker import MiniSpeakersConf
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

from sic_framework.devices.common_mini.mini_animation import MiniActionRequest

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

7. pip install --upgrade -e .[dialogflow,google-tts,openai-gpt,alphamini]
8. run: conf/redis/redis-server.exe conf/redis/redis.conf
9. run in new terminal: run-dialogflow 
10. run in new terminal: run-google-tts
11. run in new terminal: run-gpt
12. add in the main: the ip address, id, and password of the alphamini and the ip-address of the redis server (= ip address of you laptop)
13. Run this script
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
        print("SETUP OPENAI COMPLETE \n")

        # set up the config for dialogflow
        dialogflow_conf = DialogflowConf(keyfile_json=json.load(open(google_keyfile_path)),
                                         sample_rate_hertz=sample_rate_dialogflow_hertz, language=dialogflow_language)

        # initiate Dialogflow object
        self.dialogflow = Dialogflow(ip="localhost", conf=dialogflow_conf)
        # flag to signal when the app should listen (i.e. transmit to dialogflow)
        self.request_id = np.random.randint(10000)

        print("SETUP DIALOGFLOW COMPLETE \n")

        # setup the tts service
        self.google_tts_voice_name = google_tts_voice_name
        self.google_tts_voice_gender = google_tts_voice_gender
        self.tts = Text2Speech(conf=Text2SpeechConf(keyfile=google_keyfile_path))
        init_reply = self.tts.request(GetSpeechRequest(text="Ik ben aan het initializeren",
                                                  voice_name=self.google_tts_voice_name,
                                                  ssml_gender=self.google_tts_voice_gender))
        print("TTS INITIALIZED \n")

        self.mini = Alphamini(
            ip="10.0.0.155",
            mini_id="00199",
            mini_password="alphago",
            redis_ip="10.0.0.107",
            speaker_conf=MiniSpeakersConf(sample_rate=init_reply.sample_rate),
        )
        print("SETUP MINI COMPLETE \n")

        # connect the output of DesktopMicrophone as the input of DialogflowComponent
        self.dialogflow.connect(self.mini.mic)
        self.dialogflow.register_callback(on_dialog)

        print("SETUP MIC COMPLETE \n")

    def say(self, text):
            reply = self.tts.request(GetSpeechRequest(text=text,
                                                    voice_name=self.google_tts_voice_name,
                                                    ssml_gender=self.google_tts_voice_gender))
            self.mini.speaker.request(AudioRequest(reply.waveform, reply.sample_rate))


    def personalize(self, robot_input, user_age, user_input):
        gpt_response = self.gpt.request(
            GPTRequest(f'Je bent een sociale robot die praat met een kind van {str(user_age)} jaar oud.'
                        f'Het kind ligt in het ziekenhuis.'
                        f'Jij bent daar om het kind af te leiden met een leuk gesprek.'
                        f'Als robot heb je zojuist het volgende gevraagd: {robot_input}'
                        f'Het kind reageerde met het volgende: "{user_input}"'
                        f'Genereer nu een passende reactie in 1 zin, zet het gesprek voort, dus stel ook een vraag daarna.'))
        return gpt_response.response


    def run(self):
        input = self.say("Hallo, ik ben de droomrobot en ik ben hier voor jou. Wat is jouw lievelingsdier?")
        history = []
        try:
            for i in range(100000):
                transcript = ""
                reply = self.dialogflow.request(GetIntentRequest(self.request_id), timeout=50)

                print(reply.intent)
                if reply.intent == "Default Fallback Intent" or reply.intent == None:
                    input = self.personalize(input, 8, transcript)
                else:
                    input = reply.fulfillment_message

                reply = self.tts.request(
                    GetSpeechRequest(
                        text=input,
                        voice_name=self.google_tts_voice_name,
                        ssml_gender=self.google_tts_voice_gender
                    )
                )
                self.mini.speaker.request(AudioRequest(reply.waveform, reply.sample_rate))
        # MANUAL END OF CONVERSATION
        except KeyboardInterrupt:
            print("Stop the dialogflow component 2.")
            self.dialogflow.stop()





        
        

def on_dialog(message):
        if message.response:
            if message.response.recognition_result.is_final:
                print("Transcript:", message.response.recognition_result.transcript)
                global transcript
                transcript = message.response.recognition_result.transcript 

        
if __name__ == '__main__':
    droomrobot = Droomrobot(mini_ip="10.0.0.155", mini_id="00199", mini_password="alphago", redis_ip="10.0.0.107",
                            google_keyfile_path=abspath(join("..", "..", "conf", "dialogflow", "google_tts_keyfile.json")),
                            openai_key_path=abspath(join("..", "..", "conf", "openai", ".openai_env")))
    droomrobot.run()
