from os.path import abspath, join
from time import sleep

from sic_framework.services.openai_gpt.gpt import GPTRequest

from droomrobot import Droomrobot, AnimationType


class Sonde4:
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

    def run(self, child_name: str, child_age: int, robot_name: str = "Hero"):

        # INTRODUCTIE
        self.droomrobot.say(f'Hallo, ik ben {robot_name} de droomrobot!')
        self.droomrobot.say('Wat fijn dat ik je mag helpen vandaag.')
        self.droomrobot.say('Wat is jouw naam?')
        sleep(3)
        self.droomrobot.say(f'Hoi {child_name}, wat leuk je te ontmoeten.')
        self.droomrobot.say('En hoe oud ben je?')
        sleep(3)
        self.droomrobot.say(f'{str(child_age)} jaar. Oh wat goed, dan ben je al oud genoeg om mijn speciale trucje te leren.')
        self.droomrobot.say(
            'Het is een truukje dat kinderen helpt om zich fijn en sterk te voelen in het ziekenhuis.')
        self.droomrobot.say('Ik ben benieuwd hoe goed het bij jou gaat werken.')
        self.droomrobot.say('We gaan samen iets leuks bedenken dat jou gaat helpen.')
        self.droomrobot.say('Nu ga ik je wat meer vertellen over het trucje wat ik kan.')
        self.droomrobot.say('Let maar goed op, ik ga je iets bijzonders leren.')
        self.droomrobot.say('Ik kan jou meenemen op een droomreis!')
        self.droomrobot.say('Een droomreis is een trucje waarbij je aan iets heel leuks denkt.')
        self.droomrobot.say('Dat helpt je om rustig en sterk te blijven.')
        self.droomrobot.say('Ik ga je laten zien hoe het werkt.')
        # self.say('Kijk maar eens goed in mijn ogen.')
        # self.say('Cool hé')
        self.droomrobot.say('Nu mag jij kiezen waar je heen wilt in gedachten.')

        # droomplek = self.ask_entity('Wat zou jij willen doen? Je kan kiezen uit raceauto, waterpretpark of dolfijn.',
        #                             {'droom_plek': 1},
        #                             'droom_plek',
        #                             'droom_plek')

        droomplek = self.droomrobot.ask_entity_llm(
            'Je kan kiezen uit raceauto, waterpretpark of dolfijn.')  ## wellicht "kies uit raceauto racen, naar een waterpretpark of als dolfijn in de zee zwemmen"

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
        droomplek_lidwoord = self.droomrobot.get_article(droomplek)

        # SAMEN OEFENEN
        self.droomrobot.say(
            'Oke, laten we samen gaan oefenen.')
        self.droomrobot.say('Ga even lekker zitten zoals jij dat fijn vindt.')
        sleep(1)
        zit_goed = self.droomrobot.ask_yesno("Zit je goed zo?")
        if 'yes' in zit_goed:
            self.droomrobot.say('En nu je lekker bent gaan zitten.')
        else:
            self.droomrobot.say('Het zit vaak het lekkerste als je je benen lekker slap maakt, net als spaghetti.')
            self.droomrobot.say('Ga maar eens kijken hoe goed dat zit.')
            sleep(1)
            self.droomrobot.say('Als je goed zit.')

        self.droomrobot.say('Leg je nu je handen op je buik en adem rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('En adem rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')
        self.droomrobot.say(
            'Voel maar hoe je buik rustig op en neer beweegt.')

        if droomplek:
            if 'raceauto' in droomplek:
                kleur, kleur_adjective = self.raceauto_oefenen(child_name, child_age)
            elif 'waterpretpark' in droomplek:
                kleur, kleur_adjective = self.waterpretpark_oefenen(child_name, child_age)
            elif 'dolfijn' in droomplek:
                kleur, kleur_adjective = self.dolfijn_oefenen(child_name, child_age)

        self.droomrobot.say(
            'En weet je wat fijn is? Als je dit rustige gevoel later weer nodig hebt, kun je er altijd naar terug.')
        self.droomrobot.say('Je hoeft alleen maar rustig diep in en uit te ademen, en daar ben je weer.')
        self.droomrobot.say('Ik ben benieuwd hoe goed het je zometeen gaat helpen.')
        self.droomrobot.say('Als je klaar bent met oefenen, mag je je ogen weer open doen.')
        self.droomrobot.say(f'Ik vind {kleur} een hele mooie kleur, die heb je goed gekozen.')

        if droomplek:
            if 'raceauto' in droomplek:
                self.droomrobot.say(
                    'Als je straks aan de beurt bent ga ik je vragen om in gedachten terug te gaan naar de racebaan.')
            elif 'waterpretpark' in droomplek:
                self.droomrobot.say(
                    'Als je straks aan de beurt bent ga ik je vragen om in gedachten terug te gaan naar het waterpretpark.')
            elif 'dolfijn' in droomplek:
                self.droomrobot.say('Als je straks aan de beurt bent ga ik je vragen om in gedachten terug te gaan naar de zee.')

        ## INTERVENTIE
        sleep(5)
        self.droomrobot.say('Wat fijn dat ik je mag helpen! We gaan samen weer op een mooie droomreis.')
        self.droomrobot.say('Omdat je net al zo goed hebt geoefend, zal het nu nog makkelijker gaan.')
        self.droomrobot.say('Ga maar lekker zitten zoals jij dat fijn vindt.')
        sleep(1)
        self.droomrobot.say('Sluit je ogen maar, dan werkt de droomreis het allerbeste.')
        self.droomrobot.say(
            'Luister goed naar mijn stem. Alle andere geluiden in het ziekenhuis worden steeds zachter..')
        self.droomrobot.say('Leg je handen op je buik en adem rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en weer rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')

        if droomplek:
            if 'raceauto' in droomplek:
                self.raceauto_interventie(child_name, child_age, kleur_adjective)
            elif 'waterpretpark' in droomplek:
                self.waterpretpark_interventie(child_name, child_age, kleur_adjective)
            elif 'dolfijn' in droomplek:
                self.dolfijn_interventie(child_name, child_age, kleur_adjective)

        ## AFSCHEID/OUTRO
        self.droomrobot.say('Wat heb je jezelf goed geholpen om alles makkelijker te maken.')
        ging_goed = self.droomrobot.ask_opinion_llm("Hoe goed is het gegaan?")
        if 'positive' in ging_goed:
            self.droomrobot.say('Wat fijn! Je hebt jezelf echt goed geholpen.')
        else:
            self.droomrobot.say('Ik vind dat je echt goed je best hebt gedaan.')
            self.droomrobot.say('En kijk welke stapjes je allemaal al goed gelukt zijn.')
            self.droomrobot.say('Je hebt supergoed naar mijn stem geluisterd.')

        self.droomrobot.say('En weet je wat nu zo fijn is, hoe vaker je deze droomreis oefent, hoe makkelijker het wordt.')
        self.droomrobot.say('Je kunt dit ook zonder mij oefenen.')
        self.droomrobot.say('Je hoeft alleen maar je ogen dicht te doen en terug te denken aan jouw plek in gedachten.')
        self.droomrobot.say(
            'Ik ben benieuwd hoe goed je het de volgende keer gaat doen. Je doet het op jouw eigen manier, en dat is precies goed.')

    def raceauto(self, child_name: str, child_age: int):
        self.droomrobot.say('Een raceauto, die is stoer!')
        self.droomrobot.say('Jij mag zelf kiezen hoe snel of langzaam hij rijdt.')
        motivation = self.droomrobot.ask_open(f'Rijd jij graag snel of liever langzaam?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Rijd jij graag snel of liever langzaam?', child_age, motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")
        ## maar wat als het kind rustig zegt.
        self.droomrobot.say(
            'Weet je wat mij helpt? Ik stem me voor dat de sonde een raceauto is die snel en soepel door een tunnel rijdt!')

    def waterpretpark(self, child_name: str, child_age: int):
        self.droomrobot.say('Wauw, een waterglijbaan!')
        self.droomrobot.say('Ik hou van spetteren in het water.')
        motivation = self.droomrobot.ask_open(f'Glij jij liever snel of langzaam naar beneden?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Glij jij liever snel of langzaam naar beneden?',
                                                     child_age, motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")
        self.droomrobot.say(
            'Wat mij helpt, is denken dat de sonde net als een waterglijbaan is: hij glijdt zo naar beneden, makkelijk en snel!')

    def dolfijn(self, child_name: str, child_age: int):
        self.droomrobot.say('Een dolfijn, die vind ik zo leuk!')
        self.droomrobot.say('Ze zwemmen snel en zoeken naar schatten onder water.')
        motivation = self.droomrobot.ask_open(f'Zwem jij graag snel of rustig?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Zwem jij graag snel of rustig?', child_age, motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")
        self.droomrobot.say(
            'Ik stel me voor dat de sonde een dolfijn is die makkelijk door het water zwemt, op zoek naar een schat!')

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
            personalized_response = self.droomrobot.personalize(f'Wat zou jij op jouw droomplek {droomplek} willen doen?',
                                                     child_age, motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")

    def droomplek_not_recognized(self, child_name: str, child_age: int):
        self.droomrobot.say('Oh sorry ik begreep je even niet.')
        self.droomrobot.say('Dus laten we met de raceauto racen.')
        self.raceauto(child_name, child_age)

    def raceauto_oefenen(self, child_name: str, child_age: int):
        self.droomrobot.say(
            'Terwijl je zo rustig ademt, stel je je voor dat je op een racebaan bent.')
        self.droomrobot.say('En op die plek staat een mooie raceauto, speciaal voor jou!')
        self.droomrobot.say('Daar staat een supermooie raceauto, helemaal voor jou!')
        sleep(1)
        kleur = self.droomrobot.ask_entity_llm('Kijk maar goed, welke kleur heeft jouw raceauto?')
        kleur_adjective = self.droomrobot.get_adjective(kleur)
        self.droomrobot.say(f"Wat goed, die mooie {kleur_adjective} raceauto gaat jou vandaag helpen.")
        self.droomrobot.say('Stap maar in, en voel hoe fijn het is.')
        sleep(1)
        self.droomrobot.say('Luister maar naar de motor, die maakt een stoer geluid.')
        self.droomrobot.play_audio('resources/audio/vroomvroom.wav')
        self.droomrobot.say('Voel het stuur in je handen. De gordel zit stevig om je heen.')
        self.droomrobot.say('En nu mag je gaan rijden in je speciale auto, en voel maar hoe makkelijk dat gaat.')
        self.droomrobot.say('Je raceauto gaat makkelijk en snel over de baan.')
        self.droomrobot.say('Jij stuurt precies zoals jij wilt.')
        self.droomrobot.say('Jij hebt alles onder controle.')
        return kleur, kleur_adjective

    def dolfijn_oefenen(self, child_name: str, child_age: int):
        self.droomrobot.say(
            'Terwijl je rustig ademt, stel je voor dat je een dolfijn bent die lekker aan het zwemmen is.')
        self.droomrobot.say('Je zwemt in een mooie, blauwe zee.')
        self.droomrobot.say('Kijk maar eens om je heen wat je allemaal ziet.')
        self.droomrobot.say('Welke kleuren zie je in het water?')
        sleep(2)
        self.droomrobot.say('Voelt het water warm en zacht, of juist een beetje fris en koel.')
        self.droomrobot.say('Je voelt je licht, alsof je zweeft in het water.')
        kleur = self.droomrobot.ask_entity_llm('Welke kleur dolfijn ben jij?')
        kleur_adjective = self.droomrobot.get_adjective(kleur)
        self.droomrobot.say(f'Wauw, een {kleur_adjective} dolfijn! Die zijn extra krachtig.')
        self.droomrobot.say(
            'Kijk maar eens goed, je ziet misschien zonnestralen door het water schijnen.')
        sleep(1)
        self.droomrobot.say('Om je heen zwemmen vrolijke visjes.')
        self.droomrobot.say('Ga maar lekker op avontuur en ontdek wat er allemaal te zien is in de zee.')
        sleep(2)
        return kleur, kleur_adjective

    def waterpretpark_oefenen(self, child_name: str, child_age: int):
        self.droomrobot.say(
            'Terwijl je rustig ademt, stel je voor dat je in een waterpretpark bent.')
        self.droomrobot.say('Het is een lekkere warme dag en je voelt de zon op je gezicht.')
        self.droomrobot.say('Om je heen hoor je het water spetteren en kinderen lachen.')
        self.droomrobot.say('En kijk eens voor je, daar staan de allergaafste waterglijbanen die je ooit hebt gezien!')
        self.droomrobot.say('Er zijn allemaal verschillende, en ze hebben mooie kleuren.')
        kleur = self.droomrobot.ask_entity_llm('Welke kleur heeft de glijbaan waar jij vanaf wilt gaan?')
        kleur_adjective = self.droomrobot.get_adjective(kleur)
        self.droomrobot.say(f'Wat goed! Die mooie {kleur_adjective} glijbaan gaat jou vandaag helpen.')
        self.droomrobot.say('Je loopt de trap op, stap voor stap, steeds hoger.')
        self.droomrobot.say('Voel maar hoe fijn en rustig je je bij elke stap voelt.')
        self.droomrobot.say('Misschien voel je een beetje kriebels in je buik, dat is helemaal oké!')
        self.droomrobot.say('Dat betekent dat je er klaar voor bent.')
        self.droomrobot.say('Bovenaan ga je zitten.')
        self.droomrobot.say('Voel het koele water om je heen.')
        self.droomrobot.say('Zet je handen naast je neer.')
        self.droomrobot.say('Adem diep in')
        sleep(2)
        self.droomrobot.say('en klaar voor de start!')
        self.droomrobot.say('Glij maar rustig naar beneden, en voel hoe makkelijk en fijn dat gaat.')
        return kleur, kleur_adjective

    def raceauto_interventie(self, child_name: str, child_age: int, kleur_adjective: str):
        self.droomrobot.say(f'Stel je voor, je staat op de racebaan met jouw mooie {kleur_adjective} raceauto!')
        sleep(3)
        self.droomrobot.say('Je auto rijdt op een rechte weg.')
        self.droomrobot.say(
            'Je mag zelf kiezen hoe snel of rustig je rijdt, precies zoals jij dat fijn vindt.')
        self.droomrobot.say('Jij weet precies hoe jij wilt rijden, waardoor je je sterk voelt.')
        self.droomrobot.say('De wielen van de auto zijn lekker zacht, en rollen makkelijk over de weg.')
        self.droomrobot.say('Kijk eens, welke kleur heeft jouw speciale racebaan?')
        self.droomrobot.say('Misschien zitten er glitters op de weg, die jou extra sterk maken.')
        self.droomrobot.say('En daar, voor je, een tunnel! Een hele speciale tunnel, precies groot genoeg voor jouw auto.')
        self.droomrobot.say('Je rijdt er rustig naartoe, en als je rustig blijft rijden, dan ga je er soepel doorheen.')
        self.droomrobot.say('De tunnel is precies groot genoeg.')
        self.droomrobot.say('De tunnel is mooi en kleurrijk, met lichtjes, die zachtjes schijnen.')
        self.droomrobot.say('Kijk maar eens welke mooie kleuren jij allemaal in de tunnel ziet.')
        self.droomrobot.say('Je blijft lekker doorrijden, zo snel als jij fijn vindt.')
        self.droomrobot.say(
            'Misschien voelt het even gek of een beetje kriebelig, net als over een hobbeltje rijden.')
        self.droomrobot.say('Maar jij weet: als je rustig blijft ademen, rijd je er heel makkelijk doorheen.')
        self.droomrobot.say('Je auto glijdt soepel verder en verder.')
        self.droomrobot.say('Merk maar hoe veilig jij je in je eigen auto voelt.')
        self.droomrobot.say(
            'En jij blijft heerlijk zitten in je auto, je hebt alles onder controle!')
        self.droomrobot.say('De verpleegkundige vertelt je wanneer je bij het einde van de tunnel bent.')

        ## outro
        self.droomrobot.say('Wow! Jij bent als een supersnelle coureur door de tunnel gereden!')
        self.droomrobot.say('Kijk eens, daar is de finishvlag, hij wappert speciaal voor jou!')
        self.droomrobot.say('Hoor je het publiek juichen?')
        self.droomrobot.say('Ze klappen voor jou, omdat je het zo goed hebt gedaan!')
        self.droomrobot.say('Je auto is nu veilig gestopt op de finishlijn.')
        self.droomrobot.say('Pfoe, wat een gave race.')
        self.droomrobot.say('Misschien voel je nog een klein beetje het trillen van de weg, maar dat is helemaal oké.')
        self.droomrobot.say('Jij bent een echte racekampioen!')
        self.droomrobot.say('Nu mag je je ogen weer open doen.')

    def waterpretpark_interventie(self, child_name: str, child_age: int, kleur_adjective: str):
        self.droomrobot.say('Stel je voor, je bent weer in het waterpretpark.')
        self.droomrobot.say(f'Je loopt langzaam de trap op van jouw {kleur_adjective} glijbaan, net als daarnet.')
        self.droomrobot.say('Je hebt dit al goed geoefend, waardoor het makkelijker gaat.')
        self.droomrobot.say('Bij elke stap voel je hoe sterk en fijn je je voelt.')
        self.droomrobot.say('Luister maar naar het spetterende water om je heen!')
        self.droomrobot.play_audio('resources/audio/splashing_water.wav')

        self.droomrobot.say('Boven aan ga je lekker zitten. Je ademt rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('En rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')

        self.droomrobot.say('Je zet je handen weer naast je neer. Dan zet je je zachtjes af, en daar ga je!')
        self.droomrobot.say('Voel hoe je rustig begint te glijden.')
        self.droomrobot.say('Eerst heel langzaam.')
        self.droomrobot.say('Dan een beetje sneller.')
        self.droomrobot.say('Precies zoals jij dat fijn vindt!')
        self.droomrobot.say('Het zachte water glijdt langs je heen, net als een zachte golf die je meeneemt.')
        self.droomrobot.say(
            'Soms voel je dat je even tegen de zijkant aankomt, dat is gewoon een bocht in de glijbaan! Heel normaal!')
        self.droomrobot.say(
            'Misschien heeft het water wel glitters, of een speciale kleur, om jou extra kan helpen.')
        self.droomrobot.say(
            'Je blijft lekker glijden, soms wat sneller, soms wat rustiger. Het gaat helemaal vanzelf.')
        self.droomrobot.say('Misschien voel je even een klein kriebeltje, alsof een waterstraaltje tegen je neus spat.')
        self.droomrobot.say('Je ademt rustig in en uit, net als de zachte golfjes om je heen.')
        self.droomrobot.say('Je komt lager en lager.')
        self.droomrobot.say('Nog een bocht, en nog één.')
        self.droomrobot.say('De verpleegkundige vertelt je wanneer je bij de laatste bocht bent.')
        self.droomrobot.say('Je glijdt soepel verder, en je kan dit heel goed!')

        ## outro
        self.droomrobot.play_audio('resources/sounds/splash.wav')
        self.droomrobot.say('Daar plons je in het zwembad, precies zoals je wilde!')
        self.droomrobot.say('Wat een supercoole rit was dat!')
        self.droomrobot.say('Jij bent helemaal beneden gekomen, goed gedaan!')
        self.droomrobot.say('Het zachte water heeft je geholpen, en jij hebt het helemaal zelf gedaan.')
        self.droomrobot.say('En weet je wat? Jij bent echt een supergoede glijbaan-avonturier!')
        self.droomrobot.say('Je hebt laten zien hoe knap jij bent, en hoe goed je overal doorheen kunt glijden.')
        self.droomrobot.say(
            'Geef jezelf maar een high five, en doe je ogen maar weer open.')

    def dolfijn_interventie(self, child_name: str, child_age: int, kleur_adjective: str):
        self.droomrobot.say(f'Stel je je maar weer voor dat je een {kleur_adjective} dolfijn in de zee bent.')
        self.droomrobot.say('Kijk maar eens goed om je heen.')
        self.droomrobot.say('Je ziet vrolijke visjes om je heen zwemmen, en overal zijn prachtige kleuren!')
        self.droomrobot.say('Voel maar hoe je soepel door het water glijdt, net als een echte dolfijn!')
        self.droomrobot.say('Het voelt heel fijn en rustig hier in de zee.')
        self.droomrobot.say('Kijk daar, in de verte! Op de bodem van de oceaan ligt een oude schatkist!')
        self.droomrobot.say('Dat is jouw missie vandaag: je mag ernaartoe zwemmen!')
        self.droomrobot.say('Je beweegt je lichaam net als een echte dolfijn.')
        self.droomrobot.say('Eerst heel rustig.')
        self.droomrobot.say('En dan iets sneller.')
        self.droomrobot.say('Het zachte water helpt je naar beneden.')
        self.droomrobot.say('Adem maar rustig in, en voel hoe de frisse zeelucht je energie geeft.')
        self.droomrobot.say('En als je uitademt, laat je alle spanningen los.')
        self.droomrobot.say('Heel ontspannen, net als een dolfijn, die rustig zwemt.')
        self.droomrobot.say('Ooh, kijk! Daar is een onderwatergrot, een geheime doorgang!')
        self.droomrobot.say('De ingang is precies groot genoeg voor jou.')
        self.droomrobot.say('Je zwemt heel soepel naar binnen.')
        self.droomrobot.say('Misschien voel je een zacht kriebeltje bij je neus of keel.')
        self.droomrobot.say(
            'Dat is gewoon een klein zeewierplantje dat je extra kracht geeft. Heel normaal!')
        self.droomrobot.say('Jij blijft lekker zwemmen. Een bochtje hier, een bochtje daar.')
        self.droomrobot.say(
            'Misschien voel je een klein golfje langs je neus, net als een dolfijn, die door een stroomversnelling zwemt!')
        self.droomrobot.say('Maar jij weet: als je rustig blijft bewegen, zwem je er moeiteloos doorheen!')
        self.droomrobot.say('De verpleegkundige vertelt je wanneer je bij de schat bent.')
        self.droomrobot.say('Je zwemt soepel verder.')
        self.droomrobot.say('Kijk maar of je al iets van de schat kunt zien!')

        ## outro
        self.droomrobot.say('Kijk eens! Je bent bij het einde van de grot en ja hoor, daar is de schat!')
        self.droomrobot.say('De kist ligt op de bodem, verstopt tussen de mooie onderwaterplantjes.')
        self.droomrobot.say('Wow, er zitten allemaal gouden munten en glisterende juwelen in!')
        self.droomrobot.say('Wat heb jij dit supergoed gedaan! Jij bent net een echte slimme en sterke dolfijn!')
        self.droomrobot.say('Zwem maar rustig omhoog en als je klaar bent, mag je je ogen weer open doen.')

    def on_dialog(self, message):
        if message.response:
            if message.response.recognition_result.is_final:
                print("Transcript:", message.response.recognition_result.transcript)
                self.transcript = message.response.recognition_result.transcript


if __name__ == '__main__':
    sonde4 = Sonde4(mini_ip="192.168.178.111", mini_id="00167", mini_password="alphago",
                    redis_ip="192.168.178.84",
                    google_keyfile_path=abspath(join("..", "conf", "dialogflow", "google_keyfile.json")),
                    openai_key_path=abspath(join("..", "conf", "openai", ".openai_env")),
                    default_speaking_rate=0.8, computer_test_mode=False)
    sonde4.run('Tessa', 8)
