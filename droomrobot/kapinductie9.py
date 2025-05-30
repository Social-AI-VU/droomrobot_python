from enum import Enum
from os.path import abspath, join
from time import sleep

from sic_framework.services.openai_gpt.gpt import GPTRequest

from core import Droomrobot, AnimationType, InteractionPart


class Kapinductie9:

    def __init__(self, mini_ip, mini_id, mini_password, redis_ip,
                 google_keyfile_path, sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                 google_tts_voice_name="nl-NL-Standard-D", google_tts_voice_gender="FEMALE",
                 openai_key_path=None, default_speaking_rate=1.0,
                 computer_test_mode=False):

        self.droomrobot = Droomrobot(mini_ip, mini_id, mini_password, redis_ip,
                                     google_keyfile_path, sample_rate_dialogflow_hertz, dialogflow_language,
                                     google_tts_voice_name, google_tts_voice_gender,
                                     openai_key_path, default_speaking_rate,
                                     computer_test_mode)

    def run(self, participant_id: str, interaction_part: InteractionPart, child_name: str, child_age: int,
            droomplek='strand'):
        self.user_model = {
            'child_name': child_name,
            'child_age': child_age,
        }

        self.droomrobot.start_logging(participant_id, {
            'participant_id': participant_id,
            'interaction_part': interaction_part,
            'child_age': child_age,
        })
        if interaction_part == InteractionPart.INTRODUCTION:
            self.introductie(child_name, child_age)
        elif interaction_part == InteractionPart.INTERVENTION:
            self.interventie(child_name, droomplek)
        else:
            print("[Error] Interaction part not recognized")
        self.droomrobot.stop_logging()

    def introductie(self, child_name: str, child_age: int):
        self.droomrobot.animate(AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        self.droomrobot.animate(AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        self.droomrobot.say(f'Hallo, ik ben de droomrobot!')
        self.droomrobot.say('Wat fijn dat ik je mag helpen vandaag.')
        self.droomrobot.say('Wat is jouw naam?')
        sleep(3)
        self.droomrobot.say(f'{child_name}, wat een leuke naam.')
        self.droomrobot.say('En hoe oud ben je?')
        sleep(3)
        self.droomrobot.say(
            f'{str(child_age)} jaar. Oh wat goed, dan ben je al oud genoeg om mijn speciale trucje te leren.')
        self.droomrobot.say(
            'Ik heb namelijk een truukje dat bij heel veel kinderen goed werkt om alles in het ziekenhuis makkelijker te maken.')
        self.droomrobot.say('Die truuk werkt bij veel kinderen heel goed.')
        self.droomrobot.say('Ik ben dan ook benieuwd hoe goed het bij jou gaat werken.')
        self.droomrobot.say('Jij kunt jezelf helpen door je lichaam en hoofd te ontspannen.')
        self.droomrobot.say('Ik ga je wat vertellen over deze truuk.')
        self.droomrobot.say('let maar goed op, dan ga jij het ook leren.')
        self.droomrobot.say(
            'we gaan samen een reis maken in je fantasie, wat ervoor zorgt dat jij je fijn, rustig en sterk voelt.')
        self.droomrobot.say(
            'Met je fantasie kun je aan iets fijns denken terwijl je hier bent, als een soort droom. En het grappige is dat als je denkt aan iets fijns, dat jij je dan ook fijner gaat voelen.')
        self.droomrobot.say('Ik zal het even voor doen.')
        self.droomrobot.say('Ik ga in mijn droomreis het liefst in gedachten naar de wolken, lekker relaxed zweven.')
        # self.droomrobot.say('Kijk maar eens in mijn ogen, daar zie je wat ik bedoel.')
        # self.droomrobot.say('Cool hé.')
        self.droomrobot.say('Maar het hoeft niet de wolken te zijn. Iedereen heeft een eigen fijne plek.')
        self.droomrobot.say('Laten we nu samen bedenken wat jouw fijne plek is.')
        self.droomrobot.say('Je kan bijvoorbeeld in gedachten naar het strand, het bos of de ruimte.')

        # droomplek = self.droomrobot.ask_entity_llm('Naar welke plek zou jij graag willen?')
        droomplek = self.droomrobot.ask_entity('Naar welke plek zou jij graag willen?',
                                               {'droomplek': 1},
                                               'droomplek',
                                               'droomplek')
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
        droomplek_lidwoord = self.droomrobot.get_article(droomplek)

        # SAMEN OEFENEN
        self.droomrobot.say(
            'Laten we alvast gaan oefenen om samen een mooie droomreis te maken, zodat het je zometeen gaat helpen als je onder narcose gaat.')
        self.droomrobot.say('Ga even lekker zitten zoals jij dat fijn vindt.')
        sleep(1)
        zit_goed = self.droomrobot.ask_yesno("Zit je zo goed?")
        if 'yes' in zit_goed:
            self.droomrobot.say('En nu je lekker bent gaan zitten.')
        else:
            self.droomrobot.say('Het zit vaak het lekkerste als je stevig gaat zitten.')
            self.droomrobot.say('met beide benen op de grond.')
            sleep(1)
            self.droomrobot.say('Als je goed zit.')
        self.droomrobot.say('mag je je ogen dicht doen.')
        self.droomrobot.say('en dan gaan we beginnen met de droomreis.')
        self.droomrobot.say('En terwijl je nu zo lekker zit mag je je handen op je buik doen en rustig gaan ademhalen')

        self.droomrobot.say('Adem rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')
        self.droomrobot.say(
            'En voel maar dat je buik en je handen iedere keer rustig omhoog en omlaag gaan terwijl je zo lekker aan het ademhalen bent.')

        if droomplek:
            if 'strand' in droomplek:
                self.strand_oefenen(child_name, child_age)
            elif 'bos' in droomplek:
                self.bos_oefenen(child_name, child_age)
            elif 'ruimte' in droomplek:
                self.ruimte_oefenen(child_name, child_age)

        self.droomrobot.say(
            'en wat zo fijn is, is dat iedere keer als je het nodig hebt, je weer terug kan gaan in gedachten naar deze fijne plek')
        self.droomrobot.say(
            'Je hoeft alleen maar diep in en uit te ademen. Ik ben benieuwd hoe goed dit je zometeen gaat helpen.')
        self.droomrobot.say('Nu je genoeg geoefend hebt mag je je ogen weer lekker opendoen.')
        self.droomrobot.say(
            f'Wanneer je zometeen aan de beurt bent ga ik je helpen om weer naar {droomplek_lidwoord} {droomplek} te gaan in gedachten. Je hebt super goed geoefend, dus je kan verrast zijn hoe goed het zometeen gaat!')
        self.droomrobot.say(f'Tot straks, {child_name}.')

    def interventie(self, child_name: str, droomplek: str):
        ### INTERVENTIE
        self.droomrobot.animate(AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        self.droomrobot.animate(AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        self.droomrobot.say('Wat fijn dat ik je weer mag helpen, we gaan weer samen een droomreis maken.')
        self.droomrobot.say(
            'Omdat je net al zo goed hebt geoefend, zul je zien dat het nu nog beter en makkelijker gaat.')
        self.droomrobot.say(
            'Je mag je nu lekker ontspannen en je ogen dicht doen zodat je helemaal kunt genieten van de rust en zodat het truukje nog beter werkt.')
        sleep(1)
        self.droomrobot.say(
            'Luister goed naar mijn stem en merk maar dat andere geluiden in het ziekenhuis veel stiller worden.')
        self.droomrobot.say('Ga maar rustig ademen zoals je dat gewend bent.')
        self.droomrobot.say('Adem rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')

        if droomplek:
            if 'strand' in droomplek:
                self.strand_interventie(child_name)
            elif 'bos' in droomplek:
                self.bos_interventie(child_name)
            elif 'ruimte' in droomplek:
                self.ruimte_interventie(child_name)

        ### AFSCHEID
        ## geen afscheid want het kind slaapt?

    '''
        self.droomrobot.say('Wat heb je jezelf goed geholpen om alles makkelijker te maken.')
        ging_goed = self.ask_opinion_llm("Hoe goed is het gegaan?")
        if 'positive' in ging_goed:
            self.droomrobot.say('Wat fijn! Je hebt jezelf echt goed geholpen.')
        else:
            self.droomrobot.say('Ik vind dat je echt goed je best hebt gedaan.')
            self.droomrobot.say('En kijk welke stapjes je allemaal al goed gelukt zijn.')
            self.droomrobot.say('Je hebt goed geluisterd naar mijn stem.')
        
        self.droomrobot.say('En weet je wat nu zo fijn is, hoe vaker je deze droomreis oefent, hoe makkelijker het wordt.')
        self.droomrobot.say('Je kunt dit ook zonder mij oefenen.')
        self.droomrobot.say('Je hoeft alleen maar je ogen dicht te doen en terug te denken aan jouw plek in gedachten.')
        self.droomrobot.say('Ik ben benieuwd hoe goed je het de volgende keer gaat doen. Je doet het op jouw eigen manier, en dat is precies goed.')
    '''

    def strand(self, child_name: str, child_age: int):
        self.droomrobot.say('Ah, het strand! Ik kan de golven bijna horen en het zand onder mijn voeten voelen.')
        self.droomrobot.say('Weet je wat ik daar graag doe? Een zandkasteel bouwen met een vlag er op.')
        motivation = self.droomrobot.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat zou jij op het strand willen doen?', child_age,
                                                                motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Je kan van alles doen op het strand he! Zo fijn.")

    def bos(self, child_name: str, child_age: int):
        self.droomrobot.say('Het bos, wat een rustige plek! Ik hou van de hoge bomen en het zachte mos op de grond.')
        self.droomrobot.say(
            'Weet je wat ik daar graag doe? Ik zoek naar dieren die zich verstoppen, zoals vogels of eekhoorns.')
        motivation = self.droomrobot.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat zou jij in het bos willen doen?', child_age,
                                                                motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Je kan van alles doen in het bos, zo fijn.")

    def ruimte(self, child_name: str, child_age: int):
        self.droomrobot.say(
            'De ruimte, wat een avontuurlijke plek! Ik stel me voor dat ik in een raket zit en langs de sterren vlieg.')
        self.droomrobot.say(
            'Weet je wat ik daar graag zou doen? Zwaaien naar de planeten en zoeken naar aliens die willen spelen.')
        motivation = self.droomrobot.ask_open(f'Wat zou jij in de ruimte willen doen {child_name}?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat zou jij in de ruimte willen doen?', child_age,
                                                                motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Je kan van alles doen in de ruimte, zo fijn.")

    def nieuwe_droomplek(self, droomplek: str, child_name: str, child_age: int):
        gpt_response = self.droomrobot.gpt.request(
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
        self.droomrobot.say(gpt_response.response)
        motivation = self.droomrobot.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.droomrobot.personalize(
                f'Wat zou jij op jouw droomplek {droomplek} willen doen?', child_age, motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")

    def droomplek_not_recognized(self, child_name: str, child_age: int):
        self.droomrobot.say('Oh sorry ik begreep je even niet.')
        self.droomrobot.say('Weetje wat. Ik vind het stand echt super leuk.')
        self.droomrobot.say('Laten we naar het strand gaan als droomplek.')
        self.strand(child_name, child_age)

    def strand_oefenen(self, child_name: str, child_age: int):
        self.droomrobot.say(
            'En terwijl je zo rustig aan het ademhalen bent mag je gaan voorstellen dat je op het strand bent.')
        self.droomrobot.say('Kijk maar eens in gedachten om je heen wat je allemaal op die mooie plek ziet.')
        self.droomrobot.say('Misschien ben je er alleen, of is er iemand bij je.')
        self.droomrobot.say('Kijk maar welke mooie kleuren je allemaal om je heen ziet.')
        self.droomrobot.say('Misschien wel groen of paars of regenboog kleuren.')
        self.droomrobot.say('En merk maar hoe fijn jij je op deze plek voelt.')
        self.droomrobot.say('Luister maar lekker naar de golven van de zee.')
        self.droomrobot.play_audio('resources/audio/ocean_waves.wav')
        self.droomrobot.say(
            'Misschien is het er heerlijk warm of lekker koel. Voel de zonnestralen maar op je gezicht.')
        self.droomrobot.say('En op deze plek kan je alles doen waar je zin in hebt.')
        self.droomrobot.say('Misschien ga je een zandkaasteel bouwen, of spring je over de golven heen.')
        motivation = self.droomrobot.ask_open(f'Wat ga jij op het strand doen?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat ga jij op het strand doen?', child_age,
                                                                motivation)
            self.droomrobot.say(personalized_response)
        self.droomrobot.say("Wat je ook doet, merk maar hoe fijn het is om dat daar te doen!")

    def bos_oefenen(self, child_name: str, child_age: int):
        self.droomrobot.say(
            'En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in een prachtig bos bent.')
        self.droomrobot.say('Kijk maar eens om je heen wat je allemaal op die mooie plek ziet.')
        self.droomrobot.say('Misschien zie je grote bomen, of kleine bloemen die zachtjes in de wind bewegen.')
        self.droomrobot.say('En merk maar hoe fijn jij je op deze plek voelt.')
        self.droomrobot.say('Luister maar naar het geluid van de vogeltjes die fluiten.')
        self.droomrobot.play_audio('resources/audio/forest-sounds.wav')
        self.droomrobot.say(
            'Misschien is het er lekker fris, of voel je de zonnestralen door de bomen schijnen. Voel maar de zachte warmte op je gezicht.')
        self.droomrobot.say('En op deze plek kun je alles doen waar je zin in hebt.')
        self.droomrobot.say('Misschien ga je een boom beklimmen, of op zoek naar dieren.')
        motivation = self.droomrobot.ask_open(f'Wat ga jij in het bos doen?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat ga jij in het bos doen?', child_age,
                                                                motivation)
            self.droomrobot.say(personalized_response)
        self.droomrobot.say("Merk maar hoe fijn het is om dat daar te doen!")

    def ruimte_oefenen(self, child_name: str, child_age: int):
        self.droomrobot.say(
            'En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in de ruimte bent, hoog boven de aarde.')
        self.droomrobot.say('Misschien ben je er alleen, of is er iemand bij je.')
        self.droomrobot.say('Kijk maar eens om je heen, wat zie je daar allemaal?')
        self.droomrobot.say(
            'Misschien zie je de aarde heel klein worden, helemaal onder je, alsof je heel hoog in de lucht vliegt.')
        self.droomrobot.say('Misschien zie je sterren die heel fel schijnen, in verschillende kleuren.')
        self.droomrobot.say('Je voelt je heel rustig en veilig in de ruimte, want er is zoveel te ontdekken.')
        self.droomrobot.say('De ruimte is eindeloos, vol met geheimen en wonderen.')
        self.droomrobot.say('Misschien zie je wel regenbogen of ontdek je een speciale wereld.')
        motivation = self.droomrobot.ask_open(f'Wat ga jij doen in de ruimte?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat ga jij doen in de ruimte?', child_age,
                                                                motivation)
            self.droomrobot.say(personalized_response)
        self.droomrobot.say("Misschien zie je sterren die heel fel schijnen, in verschillende kleuren.")
        self.droomrobot.say('Oooooh, merk maar hoe fijn het is om dat daar te doen!')

    def strand_interventie(self, child_name: str):
        self.droomrobot.say('Stel je maar voor dat je weer op het strand bent, op die fijne plek.')
        self.droomrobot.say(
            'Kijk maar weer naar alle mooie kleuren die om je heen zijn en merk hoe fijn je je voelt op deze plek.')
        self.droomrobot.say('Luister maar naar alle fijne geluiden op het strand.')
        self.droomrobot.play_audio('resources/audio/ocean_waves.wav')
        self.droomrobot.say('Het zand onder je voeten is heerlijk zacht.')
        self.droomrobot.say('Als je je tenen beweegt, voel je hoe lekker het zand voelt.')
        self.droomrobot.say('En terwijl je nu zo lekker op het strand bent, zie je een mooie schommel staan.')
        self.droomrobot.say('Precies in de kleur die jij mooi vindt.')
        self.droomrobot.say('Je mag naar de schommel toe gaan en lekker gaan schommelen.')
        self.droomrobot.say('Voel maar hoe makkelijk de schommel met je mee beweegt, heen. en weer. heen. en weer.')
        self.droomrobot.say('De schommel gaat precies zo hoog als dat jij het fijn vindt.')
        self.droomrobot.say('Jij hebt namelijk alle controle.')
        self.droomrobot.say('Het kan ook een lekker kriebel gevoel in je buik geven.')
        self.droomrobot.say(
            'En terwijl je zo lekker aan het schommelen bent, voel je de zachte warme wind op je gezicht.')
        self.droomrobot.say(
            'Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt op het strand.')
        self.droomrobot.say('Je hoort de golven van de zee, terwijl je lekker blijft schommelen.')
        self.droomrobot.say('De zon is net als een warme zachte deken die over je heen gaat.')
        self.droomrobot.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        self.droomrobot.say('Steeds lichter. steeds rustiger. helemaal ontspannen.')

    def bos_interventie(self, child_name: str):
        self.droomrobot.say('Stel je maar voor dat je weer in het bos bent, op die fijne plek.')
        self.droomrobot.say(
            'Kijk maar weer naar alle mooie kleuren die om je heen zijn en merk hoe fijn je je voelt op deze plek.')
        self.droomrobot.say('Luister maar naar alle fijne geluiden in het bos.')
        self.droomrobot.play_audio('resources/audio/forest-sounds.wav')
        self.droomrobot.say('De grond onder je voeten is zacht en bedekt met een klein laagje mos.')
        self.droomrobot.say('Voel maar hoe lekker het is om op deze plek te staan.')
        self.droomrobot.say(
            'En terwijl je nu zo lekker in het bos bent, zie je een mooie schommel tussen twee grote bomen hangen.')
        self.droomrobot.say('Precies in de kleur die jij mooi vindt.')
        self.droomrobot.say('Je mag naar de schommel toe gaan en lekker gaan schommelen.')
        self.droomrobot.say('Voel maar hoe makkelijk de schommel met je mee beweegt, heen en weer, heen en weer.')
        self.droomrobot.say('De schommel gaat precies zo hoog als dat jij het fijn vindt.')
        self.droomrobot.say('Jij hebt namelijk alle controle.')
        self.droomrobot.say('Het kan ook een lekker kriebelend gevoel in je buik geven.')
        self.droomrobot.say('En terwijl je zo lekker aan het schommelen bent, voel je de frisse lucht op je gezicht.')
        self.droomrobot.say(
            'Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt in het bos.')
        self.droomrobot.say('Je hoort de vogels zachtjes fluiten.')
        self.droomrobot.say('De zon is net als een warme zachte deken die over je heen gaat.')
        self.droomrobot.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        self.droomrobot.say('Steeds lichter, steeds rustiger, helemaal ontspannen.')

    def ruimte_interventie(self, child_name: str):
        self.droomrobot.say('Stel je maar voor dat je weer in de ruimte bent, boven de aarde, omgeven door de sterren.')
        self.droomrobot.say(
            'Kijk maar naar de sterren die glinsteren, voel maar hoe rustig het is in deze uitgestrekte ruimte.')
        self.droomrobot.say('Luister naar het zachte geluid van je ademhaling en de stilte om je heen.')
        self.droomrobot.say('Je mag naar het ruimteschip toe zweven en er lekker in gaan zitten.')
        self.droomrobot.say('In het ruimteschip krijg je een ruimtekapje op.')
        self.droomrobot.say('Het voelt heerlijk zacht tegen je gezicht en het zal je beschermen.')
        self.droomrobot.say(
            'Het houdt je helemaal veilig, zodat je nergens anders aan hoeft te denken dan aan je avontuur in de ruimte.')
        self.droomrobot.say(
            'En terwijl je in het ruimteschip zit, voel je hoe het ruimteschip met je meebeweegt, zacht en langzaam.')
        self.droomrobot.say(
            'Je hebt alle controle over waar je naartoe wilt, je kunt naar de sterren vliegen of verder weg gaan, het maakt niet uit.')
        self.droomrobot.say('Voel de rust om je heen, terwijl je door de ruimte zweeft.')
        self.droomrobot.say(
            'Nu zweef je rustig langs een prachtige planeet die helemaal van kleur is, misschien wel in een fel blauw, of paars, of misschien zie je wel ringen om de planeet heen.')
        self.droomrobot.say('Jij voelt je veilig en rustig, als een astronaut in je eigen avontuur.')
        self.droomrobot.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker in de ruimte zweeft.')
        self.droomrobot.say('Steeds lichter, steeds rustiger, helemaal ontspannen.')
