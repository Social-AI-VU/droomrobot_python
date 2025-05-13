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
                    GPTRequest(f'Je bent een sociale robot die praat met een kind tussen de 9 en 12 jaar oud. '
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
                    GPTRequest(f'Je bent een sociale robot die praat met een kind tussen de 9 en 12 jaar oud. '
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
        self.say('Die truuk werkt bij veel kinderen heel goed.')
        self.say('Ik ben dan ook benieuwd hoe goed het bij jou gaat werken.')
        self.say('Jij kunt jezelf helpen door je lichaam en hoofd te ontspannen.')
        self.say('Ik ga je wat vertellen over deze truuk.')
        self.say('let maar goed op, dan ga jij het ook leren.')
        self.say('we gaan samen een reis maken in je fantasie, wat ervoor zorgt dat jij je fijn, rustig en sterk voelt.')
        self.say('Met je fantasie kun je aan iets fijns denken terwijl je hier bent, als een soort droom. En het grappige is dat als je denkt aan iets fijns, dat jij je dan ook fijner gaat voelen.')
        self.say('Ik zal het even voor doen.')
        self.say('Ik ga in mijn droomreis het liefst in gedachten naar de wolken, lekker relaxed zweven.')
        # self.say('Kijk maar eens in mijn ogen, daar zie je wat ik bedoel.')
        # self.say('Cool hé.')
        self.say('Maar het hoeft niet de wolken te zijn. Iedereen heeft een eigen fijne plek.')
        self.say('Laten we nu samen bedenken wat jouw fijne plek is.')
        self.say('Je kan bijvoorbeeld in gedachten naar het strand, het bos of de ruimte.')

        # droomplek = self.ask_entity('Wat is een plek waar jij je fijn voelt? Het strand, het bos, de speeltuin of de ruimte?',
        #                             {'droom_plek': 1},
        #                             'droom_plek',
        #                             'droom_plek')
        # self.mini.animation.request(MiniActionRequest("018"))

        droomplek = self.ask_entity_llm('Naar welke plek zou jij graag willen?')

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
        self.say('Laten we alvast gaan oefenen om samen een mooie droomreis te maken, zodat het je zometeen gaat helpen als je onder narcose gaat.')
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
        self.say('en dan gaan we beginnen met de droomreis.')
        self.say('En terwijl je nu zo lekker zit mag je je handen op je buik doen en rustig gaan ademhalen')

        self.say('Adem rustig in.')
        self.play_audio('resources/audio/breath_in.wav')
        self.say('en rustig uit.')
        self.play_audio('resources/audio/breath_out.wav')
        self.say('En voel maar dat je buik en je handen iedere keer rustig omhoog en omlaag gaan terwijl je zo lekker aan het ademhalen bent.')

        if droomplek:
            if 'strand' in droomplek:
                self.strand_oefenen(child_name, child_age)
            elif 'bos' in droomplek:
                self.bos_oefenen(child_name, child_age)
            elif 'ruimte' in droomplek:
                self.ruimte_oefenen(child_name, child_age)

        self.say('en wat zo fijn is, is dat iedere keer als je het nodig hebt, je weer terug kan gaan in gedachten naar deze fijne plek')
        self.say('Je hoeft alleen maar diep in en uit te ademen. Ik ben benieuwd hoe goed dit je zometeen gaat helpen.')
        self.say('Nu je genoeg geoefend hebt mag je je ogen weer lekker opendoen.')
        self.say(f'Wanneer je zometeen aan de beurt bent ga ik je helpen om weer naar {droomplek_lidwoord} {droomplek} te gaan in gedachten. Je hebt super goed geoefend, dus je kan verrast zijn hoe goed het zometeen gaat!')

        ### INTERVENTIE
        sleep(5)
        self.say('Wat fijn dat ik je weer mag helpen, we gaan weer samen een droomreis maken.')
        self.say('Omdat je net al zo goed hebt geoefend, zul je zien dat het nu nog beter en makkelijker gaat.')
        self.say('Je mag je nu lekker ontspannen en je ogen dicht doen zodat je helemaal kunt genieten van de rust en zodat het truukje nog beter werkt.')
        sleep(1)
        self.say('Luister goed naar mijn stem en merk maar dat andere geluiden in het ziekenhuis veel stiller worden.')
        self.say('Ga maar rustig ademen zoals je dat gewend bent.')
        self.say('Adem rustig in.')
        self.play_audio('resources/audio/breath_in.wav')
        self.say('en rustig uit.')
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
        self.say('Ah, het strand! Ik kan de golven bijna horen en het zand onder mijn voeten voelen.')
        self.say('Weet je wat ik daar graag doe? Een zandkasteel bouwen met een vlag er op.')
        motivation = self.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.personalize('Wat zou jij op het strand willen doen?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Je kan van alles doen op het strand he! Zo fijn.")


    def bos(self, child_name: str, child_age: int):
        self.say('Het bos, wat een rustige plek! Ik hou van de hoge bomen en het zachte mos op de grond.')
        self.say('Weet je wat ik daar graag doe? Ik zoek naar dieren die zich verstoppen, zoals vogels of eekhoorns.')
        motivation = self.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.personalize('Wat zou jij in het bos willen doen?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Je kan van alles doen in het bos, zo fijn.")

    def ruimte(self, child_name: str, child_age: int):
        self.say('De ruimte, wat een avontuurlijke plek! Ik stel me voor dat ik in een raket zit en langs de sterren vlieg.')
        self.say('Weet je wat ik daar graag zou doen? Zwaaien naar de planeten en zoeken naar aliens die willen spelen.')
        motivation = self.ask_open(f'Wat zou jij in de ruimte willen doen {child_name}?')
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
        self.say('Kijk maar eens in gedachten om je heen wat je allemaal op die mooie plek ziet.')
        self.say('Misschien ben je er alleen, of is er iemand bij je.')
        self.say('Kijk maar welke mooie kleuren je allemaal om je heen ziet.')
        self.say('Misschien wel groen of paars of regenboog kleuren.')
        self.say('En merk maar hoe fijn jij je op deze plek voelt.')
        self.say('Luister maar lekker naar de golven van de zee.')
        self.play_audio('resources/audio/ocean_waves.wav')
        self.say('Misschien is het er heerlijk warm of lekker koel. Voel de zonnestralen maar op je gezicht.')
        self.say('En op deze plek kan je alles doen waar je zin in hebt.')
        self.say('Misschien ga je een zandkaasteel bouwen, of spring je over de golven heen.')
        motivation = self.ask_open(f'Wat ga jij op het strand doen?')
        if motivation:
            personalized_response = self.personalize('Wat ga jij op het strand doen?', child_age,
                                                     motivation)
            self.say(personalized_response)
        self.say("Wat je ook doet, merk maar hoe fijn het is om dat daar te doen!")
    
    def bos_oefenen(self, child_name: str, child_age: int):
        self.say('En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in een prachtig bos bent.')
        self.say('Kijk maar eens om je heen wat je allemaal op die mooie plek ziet.')
        self.say('Misschien zie je grote bomen, of kleine bloemen die zachtjes in de wind bewegen.')
        self.say('En merk maar hoe fijn jij je op deze plek voelt.')
        self.say('Luister maar naar het geluid van de vogeltjes die fluiten.')
        self.play_audio('resources/audio/forest-sounds.wav')
        self.say('Misschien is het er lekker fris, of voel je de zonnestralen door de bomen schijnen. Voel maar de zachte warmte op je gezicht.')
        self.say('En op deze plek kun je alles doen waar je zin in hebt.')
        self.say('Misschien ga je een boom beklimmen, of op zoek naar dieren.')
        motivation = self.ask_open(f'Wat ga jij in het bos doen?')
        if motivation:
            personalized_response = self.personalize('Wat ga jij in het bos doen?', child_age,
                                                     motivation)
            self.say(personalized_response)
        self.say("Merk maar hoe fijn het is om dat daar te doen!")
    
    def ruimte_oefenen(self, child_name: str, child_age: int):
        self.say('En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in de ruimte bent, hoog boven de aarde.')
        self.say('Misschien ben je er alleen, of is er iemand bij je.')
        self.say('Kijk maar eens om je heen, wat zie je daar allemaal?')
        self.say('Misschien zie je de aarde heel klein worden, helemaal onder je, alsof je heel hoog in de lucht vliegt.')
        self.say('Misschien zie je sterren die heel fel schijnen, in verschillende kleuren.')
        self.say('Je voelt je heel rustig en veilig in de ruimte, want er is zoveel te ontdekken.')
        self.say('De ruimte is eindeloos, vol met geheimen en wonderen.')
        self.say('Misschien zie je wel regenbogen of ontdek je een speciale wereld.')
        motivation = self.ask_open(f'Wat ga jij doen in de ruimte?')
        if motivation:
            personalized_response = self.personalize('Wat ga jij doen in de ruimte?', child_age,
                                                     motivation)
            self.say(personalized_response)
        self.say("Misschien zie je sterren die heel fel schijnen, in verschillende kleuren.")
        self.say('Oooooh, merk maar hoe fijn het is om dat daar te doen!')

    def strand_interventie(self, child_name: str, child_age: int):
        self.say('Stel je maar voor dat je weer op het strand bent, op die fijne plek.')
        self.say('Kijk maar weer naar alle mooie kleuren die om je heen zijn en merk hoe fijn je je voelt op deze plek.')
        self.say('Luister maar naar alle fijne geluiden op het strand.')
        self.play_audio('resources/sounds/ocean_waves.wav')
        self.say('Het zand onder je voeten is heerlijk zacht.')
        self.say('Als je je tenen beweegt, voel je hoe lekker het zand voelt.')
        self.say('En terwijl je nu zo lekker op het strand bent, zie je een mooie schommel staan.')
        self.say('Precies in de kleur die jij mooi vindt.')
        self.say('Je mag naar de schommel toe gaan en lekker gaan schommelen.')
        self.say('Voel maar hoe makkelijk de schommel met je mee beweegt, heen en weer, heen en weer.')
        self.say('De schommel gaat precies zo hoog als dat jij het fijn vindt.')
        self.say('Jij hebt namelijk alle controle.')
        self.say('Het kan ook een lekker kriebelend gevoel in je buik geven.')
        self.say('En terwijl je zo lekker aan het schommelen bent, voel je de zachte warme wind op je gezicht.')
        self.say('Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt op het strand.')
        self.say('Je hoort de golven van de zee, terwijl je lekker blijft schommelen.')
        self.say('De zon is net als een warme zachte deken die over je heen gaat.')
        self.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        self.say('Steeds lichter, steeds rustiger, helemaal ontspannen.')
    
    def bos_interventie(self, child_name: str, child_age: int):
        self.say('Stel je maar voor dat je weer in het bos bent, op die fijne plek.')
        self.say('Kijk maar weer naar alle mooie kleuren die om je heen zijn en merk hoe fijn je je voelt op deze plek.')
        self.say('Luister maar naar alle fijne geluiden in het bos.')
        self.play_audio('resources/audio/forest-sounds.wav')
        self.say('De grond onder je voeten is zacht en bedekt met een klein laagje mos.')
        self.say('Voel maar hoe lekker het is om op deze plek te staan.')
        self.say('En terwijl je nu zo lekker in het bos bent, zie je een mooie schommel tussen twee grote bomen hangen.')
        self.say('Precies in de kleur die jij mooi vindt.')
        self.say('Je mag naar de schommel toe gaan en lekker gaan schommelen.')
        self.say('Voel maar hoe makkelijk de schommel met je mee beweegt, heen en weer, heen en weer.')
        self.say('De schommel gaat precies zo hoog als dat jij het fijn vindt.')
        self.say('Jij hebt namelijk alle controle.')
        self.say('Het kan ook een lekker kriebelend gevoel in je buik geven.')
        self.say('En terwijl je zo lekker aan het schommelen bent, voel je de frisse lucht op je gezicht.')
        self.say('Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt in het bos.')
        self.say('Je hoort de vogels zachtjes fluiten.')
        self.say('De zon is net als een warme zachte deken die over je heen gaat.')
        self.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        self.say('Steeds lichter, steeds rustiger, helemaal ontspannen.')
        
    def ruimte_interventie(self, child_name: str, child_age: int):
        self.say('Stel je maar voor dat je weer in de ruimte bent, boven de aarde, omgeven door de sterren.')
        self.say('Kijk maar naar de sterren die glinsteren, voel maar hoe rustig het is in deze uitgestrekte ruimte.')
        self.say('Luister naar het zachte geluid van je ademhaling en de stilte om je heen.')
        self.say('Je mag naar het ruimteschip toe zweven en er lekker in gaan zitten.')
        self.say('In het ruimteschip krijg je een ruimtekapje op.')
        self.say('Het voelt heerlijk zacht tegen je gezicht en het zal je beschermen.')
        self.say('Het houdt je helemaal veilig, zodat je nergens anders aan hoeft te denken dan aan je avontuur in de ruimte.')
        self.say('En terwijl je in het ruimteschip zit, voel je hoe het ruimteschip met je meebeweegt, zacht en langzaam.')
        self.say('Je hebt alle controle over waar je naartoe wilt, je kunt naar de sterren vliegen of verder weg gaan, het maakt niet uit.')
        self.say('Voel de rust om je heen, terwijl je door de ruimte zweeft.')
        self.say('Nu zweef je rustig langs een prachtige planeet die helemaal van kleur is, misschien wel in een fel blauw, of paars, of misschien zie je wel ringen om de planeet heen.')
        self.say('Jij voelt je veilig en rustig, als een astronaut in je eigen avontuur.')
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
    droomrobot.run('Tessa', 11)
