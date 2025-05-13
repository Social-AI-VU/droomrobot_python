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
        self.say(f'{str(child_age)} jaar. Oh wat goed, dan kan ik je een truukje leren om alles in het ziekenhuis makkelijker te maken.')
        self.say('Dat truukje werkt bij veel kinderen heel goed.')
        self.say('Ik ben benieuwd hoe goed het bij jou gaat werken.')
        self.say('Jij kunt namelijk heel makkelijk jezelf helpen in het ziekenhuis door je lichaam en hoofd te ontspannen.')
        self.say('Ik ga je wat meer vertellen over het truukje wat ik kan.')
        self.say('Let maar goed op, dan kan jij het ook leren.')
        self.say('We gaan samen een reis maken in je fantasie wat ervoor zorgt dat jij je fijn, rustig en sterk voelt.')
        self.say('Met je fantasie kun je aan iets fijns denken terwijl je hier bent, als een soort droom.')
        self.say('Ik zal het trucje even voor doen.')
        self.say('Ik ga in mijn droomreis het liefst in gedachten naar de wolken.')
        # self.say('Kijk maar eens in mijn ogen, daar zie je wat ik bedoel.') 
        # self.say('Cool hé')
        self.say('En wat nu zo handig is aan dit truukje is dat het je ook kan helpen met het sonde inbrengen.')

        self.say('Door ergens anders aan te denken, zoals iets dat jij leuk vind, richt je je aandacht daarop in plaats van de sonde.')
        self.say('Dat maakt het vaker minder ongemakkelijk, en kan het fijner laten voelen.')
        self.say('Wat goed helpt is om je voor te stellen dat je in een raceauto door een tunnel scheurt, of van een waterglijvbaan gaat, of als dolfijn door het water beweegt.')
        self.say('Welke lijkt jij het leukste?')
        

        # droomplek = self.ask_entity('Wat zou jij willen doen? Je kan kiezen uit raceauto, waterpretpark of dolfijn.',
        #                             {'droom_plek': 1},
        #                             'droom_plek',
        #                             'droom_plek')

        droomplek = self.ask_entity_llm('De waterglijvaan, de race-auto of dolfijn?') ## wellicht "kies uit raceauto racen, naar een waterpretpark of als dolfijn in de zee zwemmen"

        if droomplek:
            if 'raceauto' in droomplek:
                self.raceauto(child_name, child_age)
            elif 'waterpretpark' in droomplek:
                self.waterpretpark(child_name, child_age)
            elif 'dolfijn' in droomplek:
                self.dolfijn(child_name, child_age)
            # else:
            #     self.nieuwe_droomplek(droomplek, child_name, child_age)
        else:
            droomplek = 'raceauto'  # default
            self.droomplek_not_recognized(child_name, child_age)
        droomplek_lidwoord = self.get_article(droomplek)

        # SAMEN OEFENEN
        self.say('Laten we alvast gaan oefenen om samen een ontspannen reis te maken, zodat het je zometeen gaat helpen bij het inbrengen van de sonde.')
        self.say('De sonde is een dun zacht buiksje dat heel makkelijk door je neus naar binnen kan om jou te helpen je beter te voelen.')
        self.say('Ga even lekker zitten zoals jij dat prettig vindt.')
        sleep(1)
        zit_goed = self.ask_yesno("Zit je zo goed?")
        if 'yes' in zit_goed:
            self.say('En nu je lekker bent gaan zitten.')
        else:
            self.say('Het helpt vaak als je je benen een beetje ontspant.')
            self.say('probeer maar een fijne houding te vinden.')
            sleep(1)
            self.say('Als je goed zit.')
        self.say('mag je je ogen dicht doen.')
        self.say('dat maakt het makkelijker om je te concenteren.')
        self.say('En terwijl je nu zo zit, leg je rustig je handen op je buik doen en adem je kalm in en uit.')

        self.say('Adem rustig in.')
        self.play_audio('resources/audio/breath_in.wav')
        self.say('en rustig uit.')
        self.play_audio('resources/audio/breath_out.wav')
        self.say('Voel hoe je buik zachtjes op en neer beweegt bij iedere ademhaling.')

        if droomplek:
            if 'raceauto' in droomplek:
                kleur = self.raceauto_oefenen(child_name, child_age)
            elif 'waterpretpark' in droomplek:
                kleur = self.waterpretpark_oefenen(child_name, child_age)
            elif 'dolfijn' in droomplek:
                kleur = self.dolfijn_oefenen(child_name, child_age)

        self.say('En wat zo fijn is, is dat iedere keer als je het nodig hebt je weer terug kan gaan naar deze fijne plek.')
        self.say('Je hoeft alleen maar een paar keer diep in en uit te ademen.')
        self.say('Ik ben benieuwd hoe goed dit je zometeen gaat helpen.')
        self.say('Als je genoeg geoefend hebt, mag je je ogen weer lekker open doen.')
        self.say(f'Ik vind {kleur} een hele mooie kleur, die heb je goed gekozen.')

        if droomplek:
            if 'raceauto' in droomplek:
                self.say('Als je zometeen aan de beurt bent, ga ik je helpen om weer naar de racebaan te gaan in gedachten.')
            elif 'waterpretpark' in droomplek:
                self.say('Als je zometeen aan de beurt bent, ga ik je helpen om weer naar het waterpretpark te gaan in gedachten.')
            elif 'dolfijn' in droomplek:
                self.say('Als je zometeen aan de beurt bent, ga ik je helpen om weer naar de zee te gaan in gedachten.')
        
        ## INTERVENTIE
        sleep(5)
        self.say('Wat fijn dat ik je weer mag helpen, we gaan weer samen een reis door je fantasie maken.')
        self.say('Omdat je net al zo goed hebt geoefend zul je zien dat het nu nog beter en makkelijker gaat.')
        self.say('Je mag weer goed gaan zitten en je ogen dicht doen zodat deze droomreis nog beter werkt.')
        self.say('Luister maar weer goed naar mijn stem en merk maar dat andere geluiden in het ziekenhuis veel stiller worden.')
        self.say('Ga maar rustig ademen zoals je dat gewend bent, met je handen op je buik.')

        self.say('Adem rustig in.')
        self.play_audio('resources/audio/breath_in.wav')
        self.say('en rustig uit.')
        self.play_audio('resources/audio/breath_out.wav')

        if droomplek:
            if 'raceauto' in droomplek:
                self.raceauto_interventie(child_name, child_age, kleur)
            elif 'waterpretpark' in droomplek:
                self.waterpretpark_interventie(child_name, child_age, kleur)
            elif 'dolfijn' in droomplek:
                self.dolfijn_interventie(child_name, child_age, kleur)
        
        ## AFSCHEID/OUTRO
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

        
        
    def raceauto(self, child_name: str, child_age: int):
        self.say('De raceauto, die vind ik ook het leukste!')
        self.say('Ik vind het fijn dat je zelf kan kiezen hoe snel of rustig je gaat rijden.')
        motivation = self.ask_open(f'Hou jij van snel rijden of rustig?')
        if motivation:
            personalized_response = self.personalize('Hou jij van snel rijden of rustig?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Oke, super.")
        ## maar wat als het kind rustig zegt.
        self.say('Wat mij altijd goed helpt is om in gedachten te denken dat de sonde een race auto is die lekker snel en makkelijk door een tunnel rijdt.')


    def waterpretpark(self, child_name: str, child_age: int):
        self.say('Wat leuk, het waterpretpark!')
        self.say('Gelukkig kan ik tegen water zodat ik met je mee kan gaan.')
        motivation = self.ask_open(f'Ga jij het liefste snel of rustig van de waterglijbaan?')
        if motivation:
            personalized_response = self.personalize('Ga jij het liefste snel of rustig van de waterglijbaan?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Oke, super.")
        self.say('Wat mij altijd goed helpt is om in gedachten te denken dat de sonde door een waterglijbaan gaat, lekker snel en makkelijk.')


    def dolfijn(self, child_name: str, child_age: int):
        self.say('Dat vind ik dol fijn.')
        self.say('Ik vind het altijd heerlijk om door het water te zwemmen op zoek naar schatten onder water.')
        motivation = self.ask_open(f'Hou jij van snel of rustig zwemmen?')
        if motivation:
            personalized_response = self.personalize('Hou jij van snel of rustig zwemmen?', child_age, motivation)
            self.say(personalized_response)
        else:
            self.say("Oke, super.")
        self.say('Wat mij altijd goed helpt is om in gedachten te denken dat de sonde een dolfijn is die heel makkelijk en snel door het water beweegt, op zoek naar een schat.')

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
        self.say('Dus laten we met de raceauto racen.')
        self.raceauto(child_name, child_age)

    def raceauto_oefenen(self, child_name: str, child_age: int):
        self.say('En terwijl je zo rustig aan het ademhalen bent mag je je gaan voorstellen dat je op een plek met een racebaan bent.')
        self.say('En op die plek staat een mooie raceauto, speciaal voor jou!')
        self.say('Kijk maar eens hoe jouw speciale raceauto eruit ziet.')
        sleep(1)
        kleur = self.ask_entity_llm('Welke kleur heeft jouw raceauto?')
        self.say(f"Wat goed, die mooie {kleur} raceauto gaat jou vandaag helpen.")
        self.say('Ga maar in de raceauto zitten, en voel maar hoe fijn je je daar voelt.')
        sleep(1)
        self.say('De motor ronkt.')
        self.play_audio('resources/audio/vroomvroom.wav') 
        self.say('Je voelt het stuur in je handen. Je zit vast met een stevige gordel, helemaal klaar voor de start.')
        self.say('Ga maar lekker een rondje rijden in je speciale auto en voel maar hoe makkelijk dat gaat.')
        self.say('Jij hebt alles onder controle.')
        return kleur

    def dolfijn_oefenen(self, child_name: str, child_age: int):
        self.say('En terwijl je zo rustig aan het ademhalen bent, mag je je gaan voorstellen dat je een dolfijn bent die aan het zwemmen is.')
        self.say('Je bent in een mooie, blauwe zee.')
        self.say('Kijk maar eens om je heen wat je allemaal kan zien.')
        self.say('Welke kleuren er allemaal zijn en hoe het er voelt.')
        sleep(2)
        self.say('Misschien is het water warm en zacht, of fris en koel.')
        self.say('Je voelt hoe je licht wordt, alsof je zweeft.')
        kleur = self.ask_entity_llm('Wat voor kleur dolfijn ben je?')
        self.say(f'Aah, een {kleur} dolfijn! Die zijn extra krachtig.')
        self.say('Je zult wellicht zien dat als je om je heen kijkt dat je dan de zonnenstralen door het water ziet schijnen.')
        sleep(1)
        self.say('Er zwemmen vrolijke vissen om je heen.')
        self.say('Ga maar lekker op avontuur in die onderwaterwereld en kijk wat je allemaal kan vinden.')
        sleep(2)
        return kleur
    
    def waterpretpark_oefenen(self, child_name: str, child_age: int):
        self.say('En terwijl je zo rustig aan het ademhalen bent mag je je gaan voorstellen dat je in een waterpretpark bent.')
        self.say('Het is een lekker warme dag en je voelt de zon op je gezicht.')
        self.say('Om je heen hoor je het spetterende water en vrolijke stemmen.')
        self.say('En voor je zie je de grootste, gaafste waterglijbanen die je ooit hebt gezien!')
        self.say('Kijk maar eens om je heen welke glijbanen je allemaal ziet en welke kleuren de glijbanen hebben.')
        kleur = self.ask_entity_llm('Welke kleur heeft de glijbaan waar je vanaf wilt gaan?')
        self.say(f'Wat goed! Die mooie {kleur} glijbaan gaat jou vandaag helpen.')
        self.say('Je loopt langzaam de trap op naar de top van de glijbaan')
        self.say('Merk maar dat je je bij iedere stap fijner en rustiger voelt.')
        self.say('Misschien voel je een beetje kriebels in je buik dat is helemaal oké!')
        self.say('Dat betekent dat je er klaar voor bent.')
        self.say('Bovenaan ga je zitten.')
        self.say('Je voelt het koele water om je heen.')
        self.say('Je plaatst je handen naast je.')
        self.say('Adem diep in')
        sleep(2)
        self.say('en klaar voor de start!')
        self.say('Ga maar rustig naar beneden met de glijbaan en merk maar hoe rustig en soepel dat gaat.')
        return kleur
    
    def raceauto_interventie(self, child_name: str, child_age: int, kleur: str):
        self.say(f'Stel je maar weer voor dat je op de racebaan staat met jouw {kleur} raceauto!')
        sleep(3)
        self.say('Je auto rijdt op een rechte weg.')
        self.say('Je rijdt precies zo snel als jij fijn vindt en je hebt alles onder controle, waardoor je je sterk voelt.')
        self.say('De auto heeft speciale zachte banden die over de speciale weg heen rijden.')
        self.say('Kijk maar wat voor mooie kleur de speciale weg heeft.')
        self.say('Je kunt je zelfs voorstellen dat de weg glitters heeft om je extra kracht te geven.')
        self.say('Voor je zie je een tunnel. Het is een speciale tunnel, precies groot genoeg voor jouw auto.')
        self.say('Je weet dat als je rustig blijft rijden, je er soepel doorheen komt.')
        self.say('De tunnel heeft precies de juiste vorm, je hoeft alleen maar ontspannen door te blijven rijden.')
        self.say('En in de tunnel zitten prachtige lichtjes en hele mooie kleuren.')
        self.say('Kijk maar eens wat voor mooie kleuren jij allemaal in de tunnel ziet.')
        self.say('En jij blijft rustig doorrijden. Precies zo snel als jij fijn vindt, je hebt alles onder controle.')
        self.say('Misschien voelt het soms even gek of kriebelt het een beetje in de tunnel, net als wanneer je met je auto over een hobbel in de weg rijdt.')
        self.say('Maar jij weet: als je rustig blijft ademen en je blik op de weg houdt, kom je er zo doorheen.')
        self.say('Je auto glijdt soepel verder en verder.')
        self.say('En steeds dieper de tunnel in. En jij blijft heerlijk in je auto zitten.')
        self.say('En je stuurt de auto met de juiste snelheid, precies wat goed is voor jou. En voel maar dat jij dit heel goed kan.')
        self.say('En de verpleegkundige zal je vertellen wanneer je bij het einde van de tunnel bent.')

        ## outro
        self.say('Wow! Jij bent door de tunnel gereden als een echte coureur!')
        self.say('De finishvlag wappert voor je en het publiek juicht.')
        self.say('Wat een geweldige race!')
        self.say('Je hebt dit zo goed gedaan.')
        self.say('Je auto staat nu stil op de eindstreep en je mag lekker even ontspannen.')
        self.say('Misschien voel je nog een klein beetje de weg onder je trillen, maar dat is oké.')
        self.say('Je hebt alles onder controle en je bent een echte racekampioen!')
        self.say('Nu mag je je ogen weer open doen.')
    
    def waterpretpark_interventie(self, child_name: str, child_age: int, kleur: str):
        self.say('Stel je je maar weer voor dat je in het waterpretpark bent.')
        self.say(f'Je gaat weer de trap op van jouw {kleur} glijbaan, die je net al zo goed geoefend hebt.')
        self.say('Bij iedere stap voel je weer dat je lichaam zich goed voelt en je er kracht van krijgt.')
        self.say('Hoor het geluid van het water maar.')
        self.play_audio('resources/audio/splashing_water.wav')

        self.say('Boven aan ga je weer zitten en adem je weer rustig in.')
        self.play_audio('resources/audio/breath_in.wav')
        self.say('En uit.')
        self.play_audio('resources/audio/breath_out.wav')

        self.say('Je plaatst je handen naast je ademt diep in en klaar voor de start!')
        self.say('Daar ga je! Je duwt jezelf zachtjes af en voelt hoe je begint te glijden.')
        self.say('Eerst heel langzaam.')
        self.say('En dan iets sneller.')
        self.say('Precies zoals jij dat fijn vindt!')
        self.say('Je voelt het water langs je glijden, net als een zachte golf die je meevoert.')
        self.say('Misschien voel je dat je soms tegen de zijkant aan komt, dat is gewoon een bocht in de glijbaan! Heel normaal!')
        self.say('Misschien heeft het water in je glijbaan wel een speciale kleur en glitters, zodat het je extra kan helpen.')
        self.say('Je blijft lekker glijden, met het water dat je moeiteloos omlaag laat gaan. Soms gaat het even iets sneller, dan weer iets rustiger.')
        self.say('Misschien voel je een klein raar kriebeltje, alsof een waterstraaltje even tegen je neus spat.')
        self.say('Maar dat is oké, want jij weet dat je bijna beneden bent.')
        self.say('Je ademt rustig in en uit, net als de zachte golfjes om je heen.')
        self.say('Je komt lager en lager.')
        self.say('En nog een bocht.')
        self.say('De verpleegkundige vertelt je wanneer je bij de laatste bocht bent.')
        self.say('Je voelt jezelf soepel door de tunnel van de glijbaan glijden.')

        ## outro
        self.play_audio('resources/sounds/splash.wav')
        self.say('Daar plons je in het zwembad, precies zoals je wilde!')
        self.say('Je voelt je licht en ontspannen. Wat een gave rit!')
        self.say('Het lekkere water heeft je geholpen en het is je gelukt.')
        self.say('En weet je wat? Jij bent echt een supergoede glijbaan-avonturier!')
        self.say('Je hebt laten zien dat je rustig kunt blijven, en dat je overal soepel doorheen kunt glijden.')
        self.say('Je mag jezelf een high vijf geven want jij bent een echte waterkampioen! En doe je ogen maar weer open.')

    def dolfijn_interventie(self, child_name: str, child_age: int, kleur: str):
        self.say(f'Stel je je maar weer voor dat je een {kleur} dolfijn in de zee bent.')
        self.say('Kijk maar weer om je heen wat je allemaal ziet.')
        self.say('De visjes om je heen en de mooie kleuren.')
        self.say('Merk maar hoe soepel je je door het water heen beweegt, en hoe fijn je je voelt op die plek.')
        self.say('Als je goed kijkt zie je in de verte een oude schatkist op de oceaanbodem.')
        self.say('Dat is jouw missie van vandaag: je gaat ernaartoe zwemmen als een echte dolfijn.')
        self.say('Je beweegt je lichaam soepel, net als een dolfijn.')
        self.say('Eerst rustig.')
        self.say('En dan iets sneller.')
        self.say('Je voelt hoe het water je zachtjes verder en lager brengt.')
        self.say('Elke keer dat je inademt, voel je de frisse zeelucht vullen met energie.')
        self.say('Als je uitademt, laat je alle spanning los.')
        self.say('Heel ontspannen, net als een dolfijn die rustig door het water glijdt.')
        self.say('En terwijl je zwemt zie je een onderwatergrot.')
        self.say('Het is een geheime doorgang en de ingang is precies groot genoeg voor jou.')
        self.say('Je weet dat als je soepel en rustig zwemt, je er moeiteloos doorheen glijdt.')
        self.say('Je voelt misschien een zacht gevoel bij je neus of keel.')
        self.say('Dat is gewoon een klein zeewierplantje dat je even aanraakt en dat jou extra kracht geeft. Heel normaal!')
        self.say('Jij blijft rustig zwemmen door de grot, met een bochtje en weer verder.')
        self.say('Soms voel je een klein golfje langs je neus, net als een dolfijn die door een stroomversnelling zwemt!')
        self.say('En je weet dat als je rustig blijft bewegen dat je er gemakkelijk doorheen gaat.')
        self.say('De verpleegkundige vertelt je wanneer je bij de schat bent.')
        self.say('Je zwemt soepel verder.')
        self.say('Kijk maar of je al iets van de schat kunt zien!')

        ## outro
        self.say('Je bent bij de uitgang van de grot en ja hoor, je ziet de schat!')
        self.say('De kist ligt op de bodem, glinsterend tussen het koraal.')
        self.say('Je strekt je vinnen uit en je hebt hem. Het zit vol met gouden munten en juwelen.')
        self.say('Je hebt het geweldig gedaan! Je hebt laten zien hoe rustig en sterk je bent, als een echte dolfijn.')
        self.say('Zwem maar weer rustig omhoog en open je ogen zodat je weer hier in de ruimte bent.')

    def on_dialog(self, message):
        if message.response:
            if message.response.recognition_result.is_final:
                print("Transcript:", message.response.recognition_result.transcript)
                self.transcript = message.response.recognition_result.transcript


if __name__ == '__main__':
    droomrobot = Droomrobot(mini_ip="172.20.10.11", mini_id="00199", mini_password="alphago",
                            redis_ip="172.20.10.10",
                            google_keyfile_path=abspath(join("..", "conf", "dialogflow", "google_keyfile.json")),
                            openai_key_path=abspath(join("..", "conf", "openai", ".openai_env")),
                            default_speaking_rate=0.8, computer_test_mode=False)
    droomrobot.run('Tessa', 8)
