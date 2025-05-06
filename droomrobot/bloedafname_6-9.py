import json
import wave
from os.path import abspath, join
from os import environ
from time import sleep

import numpy as np
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


class Droomrobot:
    def __init__(self, mini_ip, mini_id, mini_password, redis_ip,
                 google_keyfile_path, sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                 google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE",
                 openai_key_path=None, default_speaking_rate=1.0,
                 computer_test_mode=False):
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
        self.transcript = ""

        print("SETUP DIALOGFLOW COMPLETE \n")

        # setup the tts service
        self.google_tts_voice_name = google_tts_voice_name
        self.google_tts_voice_gender = google_tts_voice_gender
        self.tts = Text2Speech(conf=Text2SpeechConf(keyfile=google_keyfile_path,
                                                    speaking_rate=default_speaking_rate))
        init_reply = self.tts.request(GetSpeechRequest(text="Ik ben aan het initializeren",
                                                       voice_name=self.google_tts_voice_name,
                                                       ssml_gender=self.google_tts_voice_gender))
        print("TTS INITIALIZED \n")

        if not computer_test_mode:
            self.mini_id = mini_id
            self.mini = Alphamini(
                ip=mini_ip,
                mini_id=self.mini_id,
                mini_password=mini_password,
                redis_ip=redis_ip,
                speaker_conf=MiniSpeakersConf(sample_rate=init_reply.sample_rate),
            )
            self.speaker = self.mini.speaker
            self.mic = self.mini.mic
            print("SETUP MINI COMPLETE \n")
        else:
            desktop = Desktop()
            self.speaker = desktop.speakers
            self.mic = desktop.mic
            print("SETUP COMPUTER COMPLETE \n")
    
        # connect the output of Minimicrophone as the input of DialogflowComponent
        self.dialogflow.connect(self.mic)
        self.dialogflow.register_callback(self.on_dialog)

        print("SETUP MIC COMPLETE \n")
            

    def say(self, text, speaking_rate=1.0):
        reply = self.tts.request(GetSpeechRequest(text=text,
                                                  voice_name=self.google_tts_voice_name,
                                                  ssml_gender=self.google_tts_voice_gender,
                                                  speaking_rate=speaking_rate))
        self.speaker.request(AudioRequest(reply.waveform, reply.sample_rate))

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

    def ask_yesno(self, question, max_attempts=2):
        attempts = 0
        while attempts < max_attempts:
            # ask question
            tts_reply = self.tts.request(GetSpeechRequest(text=question,
                                                          voice_name=self.google_tts_voice_name,
                                                          ssml_gender=self.google_tts_voice_gender))
            self.speaker.request(AudioRequest(tts_reply.waveform, tts_reply.sample_rate))

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
            self.speaker.request(AudioRequest(tts_reply.waveform, tts_reply.sample_rate))

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
            self.speaker.request(AudioRequest(tts_reply.waveform, tts_reply.sample_rate))

            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id))

            print("The detected intent:", reply.intent)

            # Return entity
            if reply.response.query_result.query_text:
                return reply.response.query_result.query_text
            attempts += 1
        return None

    def ask_entity_llm(self, question, max_attempts=2):
        attempts = 0

        while attempts < max_attempts:
            # ask question
            tts_reply = self.tts.request(GetSpeechRequest(text=question,
                                                          voice_name=self.google_tts_voice_name,
                                                          ssml_gender=self.google_tts_voice_gender))
            self.speaker.request(AudioRequest(tts_reply.waveform, tts_reply.sample_rate))

            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id))

            # Return entity
            if reply.response.query_result.query_text:
                print(f'transcript is {reply.response.query_result.query_text}')
                gpt_response = self.gpt.request(
                    GPTRequest(f'Je bent een sociale robot die praat met een kind tussen de 6 en 9 jaar oud. '
                               f'De robot stelt een vraag over een interesse van het kind.'
                               f'Jouw taak is om de key entity er uit te filteren'
                               f'Bijvoorbeeld bij de vraag: "wat is je lievelingsdier?" '
                               f'en de reactie "mijn lievelingsdier is een hond" '
                               f'filter je "hond" als key entity uit. '
                               # f'of bijvoorbeeld "wat is je superkracht?" en de reactie '
                               # f'is "mijn superkracht is heel hard rennen"'
                               # f'filter je "heel hard rennen" er uit.'
                               f'Als robot heb je net het volgende gevraagt {question}'
                               f'Dit is de reactie van het kind {reply.response.query_result.query_text}'
                               f'Return alleen de key entity string terug.'))
                print(f'response is {gpt_response.response}')
                return gpt_response.response
            attempts += 1
        return None

    def ask_opinion_llm(self, question, max_attempts=2):
        attempts = 0

        while attempts < max_attempts:
            # ask question
            tts_reply = self.tts.request(GetSpeechRequest(text=question,
                                                          voice_name=self.google_tts_voice_name,
                                                          ssml_gender=self.google_tts_voice_gender))
            self.speaker.request(AudioRequest(tts_reply.waveform, tts_reply.sample_rate))

            # listen for answer
            reply = self.dialogflow.request(GetIntentRequest(self.request_id))

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
                return gpt_response.response
            attempts += 1
        return None

    def get_article(self, word):
        gpt_response = self.gpt.request(
            GPTRequest(f'Retourneer het lidwoord van {word}. Retouneer alleen het lidwoord zelf bijv. "de" of "het" en geen andere informatie.'))
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



    def run(self, child_name: str, child_age: int, robot_name: str="Hero"):

        # INTRODUCTIE
        self.say(f'Hallo, ik ben {robot_name} de droomrobot!')
        self.say('Wat fijn dat ik je mag helpen vandaag.')
        self.say('Wat is jouw naam?')
        sleep(3)
        self.say(f'{child_name}, wat een leuke naam.')
        self.say('En hoe oud ben je?')
        sleep(3)
        self.say(f'{str(child_age)} jaar. Oh wat goed, dan ben je al oud genoeg om mijn speciale trucje te leren.')
        self.say('Ik heb namelijk een truukje dat bij heel veel kinderen goed werkt om alles in het ziekenhuis makkelijker te maken.')
        self.say('Ik ben benieuwd hoe goed het bij jou gaat werken.')
        self.say('We gaan samen een verhaal maken dat jou helpt om je fijn, rustig en sterk te voelen.')
        self.say('We gaan het samen doen, op jouw eigen manier.')
        self.say('Het heet een droomreis.')
        self.say('Met een droomreis kun je aan iets fijns denken terwijl je hier bent.')
        self.say('Dat helpt je om rustig en sterk te blijven.')
        #self.say('Ik zal het trucje even voor doen.')
        #self.say('Ik ga het liefst in gedachten naar de wolken.')
        #self.say('Kijk maar eens in mijn ogen, daar zie je wat ik bedoel.')
        #self.say('cool he.')
        #self.say('Maar het hoeft niet de wolken te zijn. Iedereen heeft een eigen fijne plek.')
        self.say('Laten we nu samen bedenken wat jouw fijne plek is.')
        self.say('Je kan bijvoorbeeld in gedachten naar het strand, het bos, de speeltuin of de ruimte.')

        # droomplek = self.ask_entity('Wat is een plek waar jij je fijn voelt? Het strand, het bos, de speeltuin of de ruimte?',
        #                             {'droom_plek': 1},
        #                             'droom_plek',
        #                             'droom_plek')

        droomplek = self.ask_entity_llm('Wat is een plek waar jij je fijn voelt?')

        if droomplek:
            if 'strand' in droomplek:
                self.strand(child_name, child_age)
            elif 'bos' in droomplek:
                self.bos(child_name, child_age)
            elif 'speeltuin' in droomplek:
                self.speeltuin(child_name, child_age)
            elif 'ruimte' in droomplek:
                self.ruimte(child_name, child_age)
            else:
                self.nieuwe_droomplek(droomplek, child_name, child_age)
        else:
            droomplek = 'strand'  # default
            self.droomplek_not_recognized(child_name, child_age)
        droomplek_lidwoord = self.get_article(droomplek)

        # SAMEN OEFENEN
        self.say('Laten we alvast een keer oefenen om samen een mooie droomreis te maken.')
        self.say('Ga even lekker zitten zoals jij dat fijn vindt.')
        sleep(1)
        zit_goed = self.ask_yesno("Zit je zo goed?")
        if 'yes' in zit_goed:
            self.say('En nu je lekker bent gaan zitten.')
        else:
            self.say('Het zit vaak het lekkerste als je stevig gaat zitten.')
            self.say('met beide benen op de grond.')
            sleep(1)
            self.say('Als je goed zit.')
        self.say('mag je je ogen dicht doen.')
        self.say('dan werkt het truukje het beste.', speaking_rate=0.8)
        sleep(1)
        self.say('Stel je voor, dat je op een hele fijne mooie plek bent... in je eigen gedachten.', speaking_rate=0.7)
        sleep(1)
        self.say(f'Misschien is het weer {droomplek_lidwoord} {droomplek}, of een nieuwe droomwereld', speaking_rate=0.7)
        sleep(1)
        self.say('Kijk maar eens om je heen, wat je allemaal op die mooie plek ziet.', speaking_rate=0.7)
        sleep(1)
        self.say('Misschien ben je er alleen... of is er iemand bij je.', speaking_rate=0.7)
        sleep(1)
        self.say('Kijk maar welke mooie kleuren je allemaal om je heen ziet.', speaking_rate=0.7)
        sleep(1)
        self.say('Misschien wel groen... of paars... of regenboog kleuren.', speaking_rate=0.7)
        sleep(1)
        self.say('En merk maar hoe fijn jij je op deze plek voelt.', speaking_rate=0.7)
        sleep(1)
        self.say('En stel je dan nu voor, dat je in jouw droomreis een superheld bent.', speaking_rate=0.7)
        sleep(1)
        self.say('Met een speciale kracht.', speaking_rate=0.7)
        sleep(1)
        self.say('Jij mag kiezen.', speaking_rate=0.7)
        sleep(1)
        superkracht = self.ask_entity_llm('Welke kracht kies je vandaag?')
        if superkracht:
            superkracht_question = self.generate_question(child_age, "Welke superkracht zou je willen?", superkracht)
            superkracht_child_response = self.ask_open(superkracht_question)
            superkracht_robot_response = self.personalize(superkracht_question, child_age, superkracht_child_response)
            self.say(superkracht_robot_response, speaking_rate=0.7)
            sleep(1)
            self.say(f'Laten we samen oefenen hoe je jouw superkracht {superkracht} kunt activeren.', speaking_rate=0.7)
        else:
            self.say('Laten we samen oefenen hoe je die kracht kunt activeren.', speaking_rate=0.7)
        sleep(1)
        self.say('Adem diep in door je neus.', speaking_rate=0.7)
        self.play_audio('resources/audio/breath_in.wav')
        self.say('en blaas langzaam uit door je mond.', speaking_rate=0.7)
        self.play_audio('resources/audio/breath_out.wav')
        self.say('Goed zo, dat gaat al heel goed.', speaking_rate=0.7)
        sleep(1)
        self.say('En terwijl je zo goed aan het ademen bent, stel je voor dat er een klein, warm lichtje op je arm verschijnt.', speaking_rate=0.7)
        sleep(1)
        self.say('Dat lichtje is magisch en laadt jouw kracht op.', speaking_rate=0.7)
        sleep(1)
        self.say('Stel je eens voor hoe dat lichtje eruit ziet.', speaking_rate=0.7)
        sleep(1)
        self.say('Is het geel, blauw of misschien jouw lievelingskleur?', speaking_rate=0.7)
        sleep(1)
        kleur = self.ask_entity_llm('Welke kleur heeft jouw lichtje?')
        sleep(1)
        self.say(f'{kleur}, wat goed.', speaking_rate=0.7)
        sleep(1)
        self.say('Merk maar eens hoe dat lichtje je een heel fijn, krachtig gevoel geeft.', speaking_rate=0.7)
        sleep(1)
        self.say('En hoe jij nu een superheld bent met jouw superkracht en alles aankan.', speaking_rate=0.7)
        sleep(1)
        self.say('En iedere keer als je het nodig hebt, kun je zoals je nu geleerd hebt, een paar keer diep in en uit ademen.', speaking_rate=0.7)
        sleep(1)
        self.say('Hartstikke goed, ik ben benieuwd hoe goed het lichtje je zometeen gaat helpen.', speaking_rate=0.7)
        sleep(1)
        self.say('Als je genoeg geoefend hebt, mag je je ogen weer lekker open doen en zeggen, het lichtje gaat mij helpen.', speaking_rate=0.7)
        sleep(3)

        oefenen_goed = self.ask_yesno('Ging het oefenen goed?')
        if 'yes' in oefenen_goed:
            experience = self.ask_open('Wat fijn. Wat vond je goed gaan?')
            if experience:
                personalized_response = self.personalize('Wat fijn. Wat vond je goed gaan?', child_age, experience)
                self.say(personalized_response)
            else:
                self.say("Wat knap van jou.")
            self.say(f'Ik vind {kleur} een hele mooie kleur, die heb je goed gekozen.')
        else:
            experience = self.ask_open('Wat ging er nog niet zo goed?')
            if experience:
                personalized_response = self.personalize('Wat ging er nog niet zo goed?', child_age, experience)
                self.say(personalized_response)
            else:
                pass
            self.say(f'Gelukkig wordt het steeds makkelijker als je het vaker oefent.')
        self.say('Ik ben benieuwd hoe goed het zometeen gaat.')
        self.say('Je zult zien dat dit je gaat helpen.')
        self.say('Als je zometeen aan de beurt bent ga ik je helpen om het lichtje weer samen aan te zetten zodat je weer die superheld bent.')

        ### INTERVENTIE
        sleep(5)
        self.say('Wat fijn dat ik je weer mag helpen, we gaan weer samen een droomreis maken.')
        self.say('Omdat je net al zo goed hebt geoefend, zul je zien dat het nu nog beter en makkelijker gaat.')
        self.say('Je mag weer goed gaan zitten en je ogen dicht doen zodat deze droomreis nog beter voor jou werkt.')
        sleep(1)
        self.say('Luister maar weer goed naar mijn stem... en merk maar dat andere geluiden in het ziekenhuis... veel stiller worden.', speaking_rate=0.8)
        sleep(1)
        self.say('Ga maar rustig ademen... zoals je dat gewend bent.', speaking_rate=0.7)
        sleep(1)
        self.say('Adem rustig in.', speaking_rate=0.7)
        self.play_audio('resources/audio/breath_in.wav')
        self.say('en rustig uit.', speaking_rate=0.7)
        self.play_audio('resources/audio/breath_out.wav')
        sleep(1)
        self.say(f'Stel je maar voor... dat je bij {droomplek_lidwoord} {droomplek} bent.', speaking_rate=0.7)
        sleep(1)
        self.say('Kijk maar weer naar alle mooie kleuren die om je heen zijn... en merk hoe fijn je je voelt op deze plek.', speaking_rate=0.7)
        sleep(1)
        self.say('Luister maar naar alle fijne geluiden op die plek.', speaking_rate=0.7)
        sleep(1)
        # Sound should be here but this is not possible with the LLM generated content
        self.say('Nu gaan we je superkracht weer activeren... zoals je dat geleerd hebt.', speaking_rate=0.7)
        sleep(1)
        self.say('Adem in via je neus.', speaking_rate=0.7)
        self.play_audio('resources/audio/breath_in.wav')
        self.say('en blaas rustig uit via je mond.', speaking_rate=0.7)
        self.play_audio('resources/audio/breath_out.wav')
        sleep(1)
        self.say('En kijk maar hoe je krachtige lichtje weer op je arm verschijnt... in precies de goede kleur die je nodig hebt.', speaking_rate=0.7)
        sleep(1)
        self.say('Zie het lichtje steeds sterker en krachtiger worden.', speaking_rate=0.7)
        sleep(1)
        self.say('Zodat jij weer een superheld wordt... en jij jezelf kan helpen.', speaking_rate=0.7)
        sleep(1)
        self.say('En als je het nodig hebt, stel je voor dat je lichtje nog helderder gaat schijnen.', speaking_rate=0.7)
        sleep(1)
        self.say('Dat betekent dat jouw kracht helemaal wordt opgeladen.', speaking_rate=0.7)
        sleep(1)
        self.say('Als het nodig is, kan je de kracht nog groter maken door met je tenen te wiebelen.', speaking_rate=0.7)
        sleep(1)
        self.say('Het geeft een veilige en zachte gloed om je te helpen.', speaking_rate=0.7)
        sleep(1)
        self.say('Als je iets voelt op je arm, dan is dat een teken dat je superkrachten volledig werken.', speaking_rate=0.7)
        sleep(1)
        self.say('Adem diep in.', speaking_rate=0.7)
        self.play_audio('resources/audio/breath_in.wav')
        self.say('en blaas uit.', speaking_rate=0.7)
        self.play_audio('resources/audio/breath_out.wav')
        sleep(1)
        self.say('Merk maar hoe goed jij jezelf kan helpen, je bent echt een superheld.', speaking_rate=0.7)
        sleep(3)

        ### AFSCHEID
        #TODO: add bloedprikken_outro_6
        self.say('Wat heb je jezelf goed geholpen om alles makkelijker te maken.')
        ging_goed = self.ask_opinion_llm("Hoe goed is het gegaan?")
        if 'positive' in ging_goed:
            self.say('Wat fijn! je hebt jezelf echt goed geholpen.')
        else:
            self.say('Dat geeft niets.')
            self.say('Je hebt goed je best gedaan.')
            self.say('En kijk welke stapjes je allemaal al goed gelukt zijn.')
        self.say('je kon al goed een' f'{kleur} lichtje uitzoeken.') #weet niet of het zo goed gaat met '
        self.say('En weet je wat nu zo fijn is, hoe vaker je dit truukje oefent, hoe makkelijker het wordt.')
        self.say('Je kunt dit ook zonder mij oefenen.')
        self.say('Je hoeft alleen maar je ogen dicht te doen en aan je lichtje te denken.')
        self.say('Dan word jij weer een superheld met extra kracht.')
        self.say('Ik ben benieuwd hoe goed je het de volgende keer gaat doen.')
        self.say('Je doet het op jouw eigen manier, en dat is precies goed.')
        self.say('Ik ga nu een ander kindje helpen, net zoals ik jou nu heb geholpen.')
        self.say('Misschien zien we elkaar de volgende keer!')



    def strand(self, child_name: str, child_age: int):
        self.say('Ah, het strand! Ik kan de golven bijna horen en het zand onder mijn voeten voelen.')
        self.say('Weet je wat ik daar graag doe? Een zandkasteel bouwen met een vlag er op.')
        motivation = self.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.personalize('Wat zou jij op het strand willen doen?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Oke, super.")


    def bos(self, child_name: str, child_age: int):
        self.say('Het bos, wat een rustige plek! Ik hou van de hoge bomen en het zachte mos op de grond.')
        self.say('Weet je wat ik daar graag doe? Ik zoek naar dieren die zich verstoppen, zoals vogels of eekhoorns.')
        motivation = self.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.personalize('Wat zou jij in het bos willen doen?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Oke, super.")

    def speeltuin(self, child_name: str, child_age: int):
        self.say('De speeltuin, wat een vrolijke plek! Ik hou van de glijbaan en de schommel.')
        self.say('Weet je wat ik daar graag doe? Heel hoog schommelen, bijna tot aan de sterren.')
        motivation = self.ask_open(f'Wat vind jij het leukste om te doen in de speeltuin {child_name}?')
        if motivation:
            personalized_response = self.personalize('Wat vind jij het leukste om te doen in de speeltuin?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Oke, super.")

    def ruimte(self, child_name: str, child_age: int):
        self.say('De ruimte, wat een avontuurlijke plek! Ik stel me voor dat ik in een raket zit en langs de sterren vlieg.')
        self.say('Weet je wat ik daar graag zou doen? Zwaaien naar de planeten en zoeken naar aliens die willen spelen.')
        motivation = self.ask_open(f'Wat zou jij in de ruimte willen doen {child_name}?')
        if motivation:
            personalized_response = self.personalize('Wat zou jij in de ruimte willen doen?', child_age,
                                                     motivation)
            self.say(personalized_response)
        else:
            self.say("Oke, super.")

    def nieuwe_droomplek(self, droomplek: str, child_name: str, child_age: int):
        gpt_response = self.gpt.request(
            GPTRequest(f'Je bent een sociale robot die praat met een kind van {str(child_age)} jaar oud.'
                       f'Het kind ligt in het ziekenhuis.'
                       f'Jij bent daar om het kind af te leiden met een leuk gesprek. '
                       f'Gebruik alleen positief taalgebruik.'
                       f'Het gesprek gaat over een fijne plek voor het kind en wat je daar kunt doen.'
                       f'Jouw taak is het genereren van twee zinnen over die plek.'
                       f'De eerste zin is een observatie die de plek typeert'
                       f'De tweede zin gaat over wat de robot leuk zou vinden om te doen op die plek.'
                       f'Bijvoorbeeld als de fijne plek de speeltuin is zouden dit de twee zinnen kunnen zijn.'
                       f'"De speeltuin, wat een vrolijke plek! Ik hou van de glijbaan en de schommel."'
                       f'Weet je wat ik daar graag doe? Heel hoog schommelen, bijna tot aan de sterren."'
                       f'De fijne plek voor het kind is "{droomplek}"'
                       f'Genereer nu de twee zinnen (observatie en wat de robot zou doen op die plek). '))
        self.say(gpt_response.response)
        motivation = self.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.personalize(f'Wat zou jij op jouw droomplek {droomplek} willen doen?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Oke, super.")

    def droomplek_not_recognized(self, child_name: str, child_age: int):
        self.say('Oh sorry ik begreep je even niet.')
        self.say('Weetje wat. Ik vind het stand echt super leuk.')
        self.say('Laten we naar het strand gaan als droomplek.')
        self.strand(child_name, child_age)

    def on_dialog(self, message):
        if message.response:
            if message.response.recognition_result.is_final:
                print("Transcript:", message.response.recognition_result.transcript)
                self.transcript = message.response.recognition_result.transcript


if __name__ == '__main__':
    droomrobot = Droomrobot(mini_ip="10.0.0.144", mini_id="00010", mini_password="alphago",
                            redis_ip="10.0.0.141",
                            google_keyfile_path=abspath(join("..", "conf", "dialogflow", "google_keyfile.json")),
                            openai_key_path=abspath(join("..", "conf", "openai", ".openai_env")),
                            default_speaking_rate=0.8, computer_test_mode=False)
    droomrobot.run('Tessa', 8)