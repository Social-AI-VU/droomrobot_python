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
                 google_tts_voice_name="nl-NL-Chirp3-HD-Leda", google_tts_voice_gender="FEMALE",
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
                                                  speaking_rate=speaking_rate,
                                                  ))
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
                    GPTRequest(f'Je bent een sociale robot die praat met een kind tussen de 4 en 6 jaar oud. '
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
                    GPTRequest(f'Je bent een sociale robot die praat met een kind tussen de 4 en 6 jaar oud. '
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
        self.say('het is een truukje dat kinderen helpt om zich fijn en sterk te voelen in het ziekenhuis.')
        self.say('Ik ben benieuwd hoe goed het bij jou gaat werken.')
        self.say('We gaan samen iets leuks bedenken dat jou gaat helpen.')
        self.say('Nu ga ik je wat meer vertellen over het truukje wat ik kan.')
        self.say('Let maar goed op, ik ga je iets bijzonders leren.')
        self.say('Ik kan jou meenemen op een droomreis!')
        self.say('Een droomreis is een truukje waarbij je aan iets heel leuks denkt.')
        self.say('Dat helpt je om rustig en sterk te blijven.')
        self.say('jij mag kiezen waar je heen wilt in gedachten.')
        self.say('Je kan kiezen uit het strand, het bos of de ruimte.')

        # droomplek = self.ask_entity('Wat is een plek waar jij je fijn voelt? Het strand, het bos, de speeltuin of de ruimte?',
        #                             {'droom_plek': 1},
        #                             'droom_plek',
        #                             'droom_plek')
        # self.mini.animation.request(MiniActionRequest("018"))

        droomplek = self.ask_entity_llm('Waar wil je naartoe?')

        if droomplek:
            if 'strand' in droomplek:
                self.strand(child_name, child_age)
            elif 'bos' in droomplek:
                self.bos(child_name, child_age)
            elif 'ruimte' in droomplek:
                self.ruimte(child_name, child_age)
            # else:
            #     self.nieuwe_droomplek(droomplek, child_name, child_age)
        else:
            droomplek = 'strand'  # default
            self.droomplek_not_recognized(child_name, child_age)
        droomplek_lidwoord = self.get_article(droomplek)

        # SAMEN OEFENEN
        self.say('Laten we samen gaan oefenen.')
        self.say('Ga even lekker zitten zoals jij dat fijn vindt.')
        sleep(1)
        zit_goed = self.ask_yesno("Zit je zo goed?")
        if 'yes' in zit_goed:
            self.say('En nu je lekker bent gaan zitten.')
        else:
            self.say('Het zit vaak het lekkerste als je je benen lekker slap maakt, net als spaghetti.')
            self.say('ga maar eens kijke hoe goed dat zit.')
            sleep(1)
            self.say('als je goed zit.')
        self.say('mag je je ogen dicht doen.')
        self.say('dan werkt het truukje het beste.')
        self.say('leg nu je handen op je buik.')

        self.say('Adem rustig in.')
        self.play_audio('resources/audio/breath_in.wav')
        self.say('en rustig uit.')
        self.play_audio('resources/audio/breath_out.wav')
        self.say('En voel maar dat je buik rustig op en neer beweegt.')

        if droomplek:
            if 'strand' in droomplek:
                self.strand_oefenen(child_name, child_age)
            elif 'bos' in droomplek:
                self.bos_oefenen(child_name, child_age)
            elif 'ruimte' in droomplek:
                self.ruimte_oefenen(child_name, child_age)

        self.say('Weet je wat zo fijn is? Je kunt altijd teruggaan naar deze mooie plekken in je hoofd.')
        self.say('Je hoeft alleen maar rustig in en uit te ademen.')
        self.say('Ik ben benieuwd hoe goed dit je zometeen gaat helpen.')
        self.say('als je klaar bent, mag je je ogen weer open doen.')
        self.say(f'Straks ga ik je helpen om weer terug te gaan naar {droomplek_lidwoord} {droomplek} te gaan in gedachten. Je hebt super goed geoefend, dus je kan verrast zijn hoe goed het zometeen gaat!')

        ### INTERVENTIE
        sleep(5)
        self.say('Wat fijn dat ik je  mag helpen, we gaan weer samen op een mooie droomreis.')
        self.say('Omdat je net al zo goed hebt geoefend, zal het nu nog makkelijker gaan.')
        self.say('Ga maar lekker zitten zoals jij dat fijn vindt.')
        sleep(1)
        self.say('Sluit je ogen maar, dan werkt de droomreis het allerbeste en kan je in gedachten op reis gaan.')
        self.say('En je mag ze altijd even op doen en als je wilt weer dicht.')
        self.say('Luister goed naar mijn stem, en merk maar dat alle andere geluiden in het ziekenhuis steeds zachter worden.')
        self.say('Leg je handen op je buik.')
        self.say('en adem heel goed in.')
        self.play_audio('resources/audio/breath_in.wav')
        self.say('en weer heel goed uit.')
        self.play_audio('resources/audio/breath_out.wav')

        if droomplek:
            if 'strand' in droomplek:
                self.strand_interventie(child_name, child_age)
            elif 'bos' in droomplek:
                self.bos_interventie(child_name, child_age)
            elif 'ruimte' in droomplek:
                self.ruimte_interventie(child_name, child_age)

        ### AFSCHEID
        ## geen afscheid want het kind slaapt?
      '''
        self.say('Wat heb je jezelf goed geholpen om alles makkelijker te maken.')
        ging_goed = self.ask_opinion_llm("Hoe goed is het gegaan?")
        if 'positive' in ging_goed:
            self.say('Wat fijn! Je hebt jezelf echt goed geholpen.')
        else:
            self.say('Ik vind dat je echt goed je best hebt gedaan.')
            self.say('En kijk welke stapjes je allemaal al goed gelukt zijn.')
            self.say('Je hebt goed geluisterd naar mijn stem.')
        
        self.say('En weet je wat nu zo fijn is, hoe vaker je deze droomreis oefent, hoe makkelijker het wordt.')
        self.say('Je kunt dit ook zonder mij oefenen.')
        self.say('Je hoeft alleen maar je ogen dicht te doen en terug te denken aan jouw plek in gedachten.')
        self.say('Ik ben benieuwd hoe goed je het de volgende keer gaat doen. Je doet het op jouw eigen manier, en dat is precies goed.')
        '''


    def strand(self, child_name: str, child_age: int):
        self.say('Wat is het fijn op het strand, Ik voel het warme zand en hoor de golven zachtjes ruisen.')
        self.say('Weet je wat ik daar graag doe? Grote zandkastelen bouwen en schelpjes zoeken.')
        motivation = self.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.personalize('Wat zou jij op het strand willen doen?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Er is zoveel leuks te doen op het strand.")


    def bos(self, child_name: str, child_age: int):
        self.say('Het bos, wat een rustige plek! De bomen zijn hoog en soms hoor ik de vogeltjes fluiten.')
        self.say('Weet je wat ik daar graag doe? Takjes verzamelen en speuren naar eekhoorntjes.')
        motivation = self.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.personalize('Wat zou jij in het bos willen doen?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Je kan van alles doen in het bos, zo fijn.")

    def ruimte(self, child_name: str, child_age: int):
        self.say('De ruimte is heel bijzonder, ik stel me voor dat ik in een raket zit en langs de sterren vlieg.')
        self.say('Weet je wat ik daar graag doe? Naar de planeten zwaaien en kijken of ik grappige mannetjes zie.')
        motivation = self.ask_open('Wat zou jij willen doen in de ruimte?')
        if motivation:
            personalized_response = self.personalize('Wat zou jij in de ruimte willen doen?', child_age,
                                                     motivation)
            self.say(personalized_response)
        else:
            self.say("Je kan van alles doen in de ruimte, zo fijn.")

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

    def strand_oefenen(self, child_name: str, child_age: int):
        self.say('En terwijl je zo rustig aan het ademhalen bent mag je gaan voorstellen dat je op het strand bent.')
        self.say('Kijk maar in je hoofd om je heen. Wat zie je allemaal?')
        self.say('Misschien zie je het zand, de zee of een mooie schelp.')
        self.say('Ben je daar alleen, of is er iemand bij je?')
        self.say('Kijk maar welke mooie kleuren je allemaal om je heen ziet.')
        self.say('Misschien wel groen of paars of andere kleuren.')
        self.say('En merk maar hoe fijn jij je op deze plek voelt.')
        self.say('Luister maar lekker naar de golven van de zee.')
        self.play_audio('resources/audio/ocean_waves.wav')
        self.say('Misschien voel je de warme zon op je gezicht, of is het een beetje koel.')
        self.say('Hier kun je alles doen wat je leuk vindt.')
        self.say('Misschien bouw je een groot zandkasteel, of spring je over de golven.')
        motivation = self.ask_open(f'Wat ga jij op het strand doen?')
        if motivation:
            personalized_response = self.personalize('Wat ga jij op het strand doen?', child_age,
                                                     motivation)
            self.say(personalized_response)
        self.say("Wat je ook doet, merk maar hoe fijn het is om dat daar te doen!")
    
    def bos_oefenen(self, child_name: str, child_age: int):
        self.say('En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in een prachtig bos bent.')
        self.say('Kijk maar eens om je heen wat je allemaal op die mooie plek ziet.')
        self.say('Misschien zie je hoe bomen, groene blaadjes of een klein diertje.')
        self.say('En merk maar hoe fijn jij je op deze plek voelt.')
        self.say('Luister maar naar de vogels die zingen.')
        self.play_audio('resources/audio/forest-sounds.wav')
        self.say('Misschien voel je de frisse lucht, of schijnt de zon door de bomen op je gezicht.')
        self.say('Hier kun je alles doen wat je leuk vindt.')
        self.say('Misschien klim je in een boom, of zoek je naar dieren.')
        motivation = self.ask_open(f'Wat ga jij doen in het bos?')
        if motivation:
            personalized_response = self.personalize('Wat ga jij in het bos doen?', child_age,
                                                     motivation)
            self.say(personalized_response)
        self.say("Merk maar hoe fijn het is om dat te doen!")
    
    def ruimte_oefenen(self, child_name: str, child_age: int):
        self.say('En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in de ruimte bent, heel hoog in de lucht.')
        self.say('Misschien ben je er alleen, of is er iemand bij je.')
        self.say('Kijk maar eens om je heen, wat zie je daar allemaal?')
        self.say('Misschien zie je de aarde heel klein worden.')
        self.say('Misschien zie je sterren die heel fel schijnen, in verschillende kleuren.')
        self.say('Je voelt je heel rustig en veilig in de ruimte, want er is zoveel te ontdekken.')
        self.say('De ruimte is zo groot, vol met leuke plekken.')
        self.say('Misschien zie je wel regenbogen of ontdek je een speciale ster met grappige dieren er op.')
        motivation = self.ask_open(f'Wat ga jij doen in de ruimte?')
        if motivation:
            personalized_response = self.personalize('Wat ga jij doen in de ruimte?', child_age,
                                                     motivation)
            self.say(personalized_response)
        #self.say("Misschien zie je sterren die heel fel schijnen, in verschillende kleuren.")
        self.say('Oooooh, merk maar hoe fijn het is om dat daar te doen!')

    def strand_interventie(self, child_name: str, child_age: int):
        self.say('Stel je maar voor dat je weer op het strand bent, op die fijne plek.')
        self.say('Wat zie je daar allemaal? Misschien een grote zee en zacht zand.')
        self.say('Luister maar naar alle fijne geluiden op het strand.')
        self.play_audio('resources/sounds/ocean_waves.wav')
        self.say('Voel het zand maar onder je voeten. Het is lekker zacht en warm.')
        self.say('Als je je tenen beweegt, voel je hoe lekker het zand voelt.')
        self.say('En terwijl je nu zo lekker op het strand bent, zie je een mooie schommel staan.')
        self.say('Die heeft precies jouw lievelingskleur.')
        self.say('Je mag op de schommel gaan zitten.')
        self.say('Voel maar hoe je zachtjes heen en weer gaat.')
        self.say('Voel maar hoe makkelijk de schommel doet wat jij wil, heen en weer, heen en weer.')
        self.say('De schommel gaat precies zo hoog als jij fijn vindt.')
        self.say('Jij bent de baas.')
        self.say('Het kan ook een lekker kriebelend gevoel in je buik geven.')
        self.say('En terwijl je zo lekker aan het schommelen bent, voel je de zachte warme wind op je gezicht.')
        self.say('Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt op het strand.')
        self.say('Je hoort de golven van de zee, terwijl je lekker blijft schommelen.')
        self.say('De zon is net als een warme zachte deken die over je heen gaat.')
        self.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        self.say('Steeds lichter, steeds rustiger, helemaal ontspannen.')
    
    def bos_interventie(self, child_name: str, child_age: int):
        self.say('Stel je maar voor dat je weer in het bos bent, op die fijne plek.')
        self.say('Kijk maar weer naar alle mooie kleuren die om je heen zijn en hoe fijn je je voelt op deze plek.')
        self.say('Luister maar naar alle rustige geluiden in het bos.')
        self.play_audio('resources/audio/forest-sounds.wav')
        self.say('De grond onder je voeten is lekker zacht.')
        self.say('Voel maar hoe fijn het is om hier te zijn.')
        self.say('Kijk, daar hangt een schommel tussen de bomen.')
        self.say('Het is precies jouw lievelingskleur.')
        self.say('Je mag op de schommel gaan zitten. Voel maar hoe je zachtjes heen en weer gaat.')
        self.say('Voel maar hoe makkelijk de schommel doet wat jij wil, heen en weer, heen en weer.')
        self.say('De schommel gaat precies zo hoog als dat jij fijn vindt.')
        self.say('Jij bent de baas.')
        self.say('Het kan ook een lekker kriebelend gevoel in je buik geven.')
        self.say('En terwijl je zo lekker aan het schommelen bent, voel je de frisse lucht op je gezicht.')
        self.say('Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt in het bos.')
        self.say('Je hoort de vogels zachtjes fluiten.')
        self.say('De zon is net als een warme zachte deken die over je heen gaat.')
        self.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        self.say('Steeds lichter, steeds rustiger, helemaal ontspannen.')
        
    def ruimte_interventie(self, child_name: str, child_age: int):
        self.say('Stel je maar voor dat je weer in de ruimte bent, heel hoog in de lucht.')
        self.say('Wat zie je daar allemaal? Misschien sterren die twinkelen en planeten in mooie kleuren.')
        self.say('Voel maar hoe rustig het is om hier te zweven.')
        self.say('Kijk daar is een ruimteschip! Je mag erin gaan zitten.')
        self.say('Het voelt zacht en veilig. Jij bent de baas.')
        self.say('Het ruimteschip zweeft langzaam met je mee.')
        self.say('In het ruimteschip krijg je een ruimtekapje op.')
        self.say('Het voelt heerlijk zacht tegen je gezicht en het zal je beschermen.')
        self.say('Het houdt je helemaal veilig, zodat je nergens anders aan hoeft te denken dan aan je avontuur in de ruimte.')
        self.say('En terwijl je in het ruimteschip zit, voel je hoe het ruimteschip langzaam met je mee zweeft.')
        self.say('Jij kunt kiezen waar je naartoe wilt zweven, naar de sterren of verder weg.')
        self.say('Voel de rust om je heen, terwijl je door de ruimte zweeft')
        self.say('Kijk, daar is een mooie planeet! Misschien is hij blauw, paars of heeft hij ringen.')
        self.say('Je voelt je veilig en stoer als een echte astronaut.')
        self.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker in de ruimte zweeft.')
        self.say('Steeds lichter, steeds rustiger, helemaal ontspannen.')





    def on_dialog(self, message):
        if message.response:
            if message.response.recognition_result.is_final:
                print("Transcript:", message.response.recognition_result.transcript)
                self.transcript = message.response.recognition_result.transcript


if __name__ == '__main__':
    droomrobot = Droomrobot(mini_ip="10.0.0.155", mini_id="00199", mini_password="alphago",
                            redis_ip="10.0.0.107",
                            google_keyfile_path=abspath(join("..", "conf", "dialogflow", "google_keyfile.json")),
                            openai_key_path=abspath(join("..", "conf", "openai", ".openai_env")),
                            default_speaking_rate=0.8, computer_test_mode=False)
    droomrobot.run('Tessa', 5)
