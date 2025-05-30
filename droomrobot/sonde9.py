from enum import Enum
from os.path import abspath, join
from time import sleep

from sic_framework.services.openai_gpt.gpt import GPTRequest

from core import Droomrobot, AnimationType, InteractionPart


class Sonde9:

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
            droomplek='raceauto', kleur='blauw'):

        self.user_model = {
            'child_name': child_name,
            'child_age': child_age
        }

        self.droomrobot.start_logging(participant_id, {
            'participant_id': participant_id,
            'interaction_part': interaction_part,
            'child_age': child_age
        })
        if interaction_part == InteractionPart.INTRODUCTION:
            self.introductie(child_name, child_age)
        elif interaction_part == InteractionPart.INTERVENTION:
            self.interventie(child_name, droomplek, kleur)
        else:
            print("Interaction part not recognized")
        self.droomrobot.stop_logging()

    def introductie(self, child_name: str, child_age: int):
        # INTRODUCTIE
        self.droomrobot.animate(AnimationType.ACTION, "009")
        self.droomrobot.animate(AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        self.droomrobot.animate(AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        self.droomrobot.say(f'Hallo, ik ben de droomrobot!')
        self.droomrobot.say('Wat fijn dat ik je mag helpen vandaag.')
        self.droomrobot.ask_fake('Wat is jouw naam?', 3)
        self.droomrobot.say(f'{child_name}, wat een leuke naam.')
        self.droomrobot.ask_fake('En hoe oud ben je?', 3)
        self.droomrobot.say(
            f'{str(child_age)} jaar. Oh wat goed, dan kan ik je een truukje leren om alles in het ziekenhuis makkelijker te maken.')
        self.droomrobot.say('Dat truukje werkt bij veel kinderen heel goed.')
        self.droomrobot.say('Ik ben benieuwd hoe goed het bij jou gaat werken.')
        self.droomrobot.say(
            'Jij kunt namelijk heel makkelijk jezelf helpen in het ziekenhuis door je lichaam en hoofd te ontspannen.')
        self.droomrobot.say('Ik ga je wat meer vertellen over het truukje wat ik kan.')
        self.droomrobot.say('Let maar goed op, dan kan jij het ook leren.')
        self.droomrobot.say(
            'We gaan samen een reis maken in je fantasie wat ervoor zorgt dat jij je fijn, rustig en sterk voelt.')
        self.droomrobot.say('Met je fantasie kun je aan iets fijns denken terwijl je hier bent, als een soort droom.')
        self.droomrobot.say('Ik zal het trucje even voor doen.')
        self.droomrobot.say('Ik ga in mijn droomreis het liefst in gedachten naar de wolken.')
        # self.droomrobot.say('Kijk maar eens in mijn ogen, daar zie je wat ik bedoel.') ## not really possible with current expressions
        # self.droomrobot.say('Cool hé') 
        self.droomrobot.say(
            'En wat nu zo handig is aan dit truukje is dat het je ook kan helpen met het inbrengen van de sonde.')

        self.droomrobot.say(
            'Door ergens anders aan te denken, zoals iets dat jij leuk vind, richt je je aandacht daarop in plaats van de sonde.')
        self.droomrobot.say('Dat maakt het vaker minder ongemakkelijk, en kan het fijner laten voelen.')
        self.droomrobot.say(
           'Wat goed helpt is om je voor te stellen dat je in een raceauto door een tunnel scheurt, of van een waterglijbaan gaat, of als dolfijn door het water beweegt.')
        self.droomrobot.say('Welke lijkt jij het leukste?')

        droomplek = self.droomrobot.ask_entity('De waterglijbaan, de race-auto of dolfijn?',
                                               {'droomplek': 1},
                                               'droomplek',
                                               'droomplek')
        # droomplek = self.droomrobot.ask_entity_llm('De waterglijbaan, de race-auto of dolfijn?') ## wellicht "kies uit raceauto racen, naar een waterpretpark of als dolfijn in de zee zwemmen"

        if droomplek:
            if 'raceauto' in droomplek:
                self.raceauto(child_name, child_age)
            elif 'waterglijbaan' in droomplek:
                self.waterglijbaan(child_name, child_age)
            elif 'dolfijn' in droomplek:
                self.dolfijn(child_name, child_age)
            # else:
            #     self.nieuwe_droomplek(droomplek, child_name, child_age)
        else:
            droomplek = 'raceauto'  # default
            self.droomplek_not_recognized(child_name, child_age)
        # droomplek_lidwoord = self.droomrobot.get_article(droomplek)

        # SAMEN OEFENEN
        self.droomrobot.say(
            'Laten we alvast gaan oefenen om samen een ontspannen reis te maken, zodat het je zometeen gaat helpen bij het inbrengen van de sonde.')
        self.droomrobot.say(
            'De sonde is een dun zacht buiksje dat heel makkelijk door je neus naar binnen kan om jou te helpen je beter te voelen.')
        self.droomrobot.say('Ga even lekker zitten zoals jij dat prettig vindt.')
        sleep(1)
        zit_goed = self.droomrobot.ask_yesno("Zit je zo goed?")
        if 'yes' in zit_goed:
            self.droomrobot.say('En nu je lekker bent gaan zitten.')
        else:
            self.droomrobot.say('Het helpt vaak als je je benen een beetje ontspant.')
            self.droomrobot.say('probeer maar een fijne houding te vinden.')
            sleep(1)
            self.droomrobot.say('Als je goed zit.')
        self.droomrobot.say('mag je je ogen dicht doen.')
        self.droomrobot.say('dat maakt het makkelijker om je rustig te voelen.')
        self.droomrobot.say(
            'En terwijl je nu zo zit, leg je rustig je handen op je buik doen en adem je kalm in en uit.')

        self.droomrobot.say('Adem rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')
        self.droomrobot.say('Voel hoe je buik zachtjes op en neer beweegt bij iedere ademhaling.')

        if droomplek:
            if 'raceauto' in droomplek:
                kleur = self.raceauto_oefenen(child_name, child_age)
            elif 'waterglijbaan' in droomplek:
                kleur = self.waterglijbaan_oefenen(child_name, child_age)
            elif 'dolfijn' in droomplek:
                kleur = self.dolfijn_oefenen(child_name, child_age)

        self.droomrobot.say(
            'En wat zo fijn is, is dat iedere keer als je het nodig hebt je weer terug kan gaan naar deze fijne plek.')
        self.droomrobot.say('Je hoeft alleen maar een paar keer diep in en uit te ademen.')
        self.droomrobot.say('Ik ben benieuwd hoe goed dit je zometeen gaat helpen.')
        self.droomrobot.say('Als je genoeg geoefend hebt, mag je je ogen weer lekker open doen.')
        self.droomrobot.say(f'Ik vind {kleur} een hele mooie kleur, die heb je goed gekozen.')

        if droomplek:
            if 'raceauto' in droomplek:
                self.droomrobot.say(
                    'Als je zometeen aan de beurt bent, ga ik je helpen om weer naar de racebaan te gaan in gedachten.')
            elif 'waterglijbaan' in droomplek:
                self.droomrobot.say(
                    'Als je zometeen aan de beurt bent, ga ik je helpen om weer naar het waterpretpark te gaan in gedachten.')
            elif 'dolfijn' in droomplek:
                self.droomrobot.say(
                    'Als je zometeen aan de beurt bent, ga ik je helpen om weer naar de zee te gaan in gedachten.')
        self.droomrobot.say(f'Tot straks, {child_name}.')

    def interventie(self, child_name: str, droomplek: str, kleur: str):
        self.droomrobot.animate(AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        self.droomrobot.animate(AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        self.droomrobot.say('Wat fijn dat ik je weer mag helpen, we gaan weer samen een reis door je fantasie maken.')
        self.droomrobot.say(
            'Omdat je net al zo goed hebt geoefend zul je zien dat het nu nog beter en makkelijker gaat.')
        self.droomrobot.say('Je mag weer goed gaan zitten en je ogen dicht doen zodat deze droomreis nog beter werkt.')
        self.droomrobot.say(
            'Luister maar weer goed naar mijn stem en merk maar dat andere geluiden in het ziekenhuis veel stiller worden.')
        self.droomrobot.say('Ga maar rustig ademen zoals je dat gewend bent, met je handen op je buik.')

        self.droomrobot.say('Adem rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')

        if droomplek:
            if 'raceauto' in droomplek:
                self.raceauto_interventie(child_name, kleur)
            elif 'waterglijbaan' in droomplek:
                self.waterglijbaan_interventie(child_name, kleur)
            elif 'dolfijn' in droomplek:
                self.dolfijn_interventie(child_name, kleur)

    def afscheid(self):
        self.droomrobot.say('Wat heb je jezelf goed geholpen om alles makkelijker te maken.')
        ging_goed = self.droomrobot.ask_opinion_llm("Hoe goed is het gegaan?")
        if 'positive' in ging_goed:
            self.droomrobot.say('Wat fijn! Je hebt jezelf echt goed geholpen.')
        else:
            self.droomrobot.say('Ik vind dat je echt goed je best hebt gedaan.')
            self.droomrobot.say('En kijk welke stapjes je allemaal al goed gelukt zijn.')
            self.droomrobot.say('Je hebt goed geluisterd naar mijn stem.')

        self.droomrobot.say(
            'En weet je wat nu zo fijn is, hoe vaker je deze droomreis oefent, hoe makkelijker het wordt.')
        self.droomrobot.say('Je kunt dit ook zonder mij oefenen.')
        self.droomrobot.say('Je hoeft alleen maar je ogen dicht te doen en terug te denken aan jouw plek in gedachten.')
        self.droomrobot.say(
            'Ik ben benieuwd hoe goed je het de volgende keer gaat doen. Je doet het op jouw eigen manier, en dat is precies goed.')

    def raceauto(self, child_name: str, child_age: int):
        self.droomrobot.say('De raceauto, die vind ik ook het leukste!')
        self.droomrobot.say('Ik vind het fijn dat je zelf kan kiezen hoe snel of rustig je gaat rijden.')
        motivation = self.droomrobot.ask_open(f'Hou jij van snel rijden of rustig?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Hou jij van snel rijden of rustig?', child_age,
                                                                motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")
        ## maar wat als het kind rustig zegt.
        self.droomrobot.say(
            'Wat mij altijd goed helpt is om in gedachten te denken dat de sonde een race auto is die lekker snel en makkelijk door een tunnel rijdt.')

    def waterglijbaan(self, child_name: str, child_age: int):
        self.droomrobot.say('Wat leuk, een waterglijbaan!')
        self.droomrobot.say('Gelukkig kan ik tegen water zodat ik met je mee kan gaan.')
        motivation = self.droomrobot.ask_open(f'Ga jij het liefste snel of rustig van de waterglijbaan?')
        if motivation:
            personalized_response = self.droomrobot.personalize(
                'Ga jij het liefste snel of rustig van de waterglijbaan?', child_age, motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")
        self.droomrobot.say(
            'Wat mij altijd goed helpt is om in gedachten te denken dat de sonde door een waterglijbaan gaat, lekker snel en makkelijk.')

    def dolfijn(self, child_name: str, child_age: int):
        self.droomrobot.say('Dat vind ik dol fijn.')
        self.droomrobot.say(
            'Ik vind het altijd heerlijk om door het water te zwemmen op zoek naar schatten onder water.')
        motivation = self.droomrobot.ask_open(f'Hou jij van snel of rustig zwemmen?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Hou jij van snel of rustig zwemmen?', child_age,
                                                                motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")
        self.droomrobot.say(
            'Wat mij altijd goed helpt is om in gedachten te denken dat de sonde een dolfijn is die heel makkelijk en snel door het water beweegt, op zoek naar een schat.')

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
        self.droomrobot.say('Dus laten we met de raceauto racen.')
        self.raceauto(child_name, child_age)

    def raceauto_oefenen(self, child_name: str, child_age: int):
        self.droomrobot.say(
            'En terwijl je zo rustig aan het ademhalen bent mag je je gaan voorstellen dat je op een plek met een racebaan bent.')
        self.droomrobot.say('En op die plek staat een mooie raceauto, speciaal voor jou!')
        self.droomrobot.say('Kijk maar eens hoe jouw speciale raceauto eruit ziet.')
        sleep(1)
        kleur = self.droomrobot.ask_entity_llm('Welke kleur heeft jouw raceauto?')
        self.droomrobot.say(f"Wat goed, die mooie {kleur} raceauto gaat jou vandaag helpen.")
        self.droomrobot.say('Ga maar in de raceauto zitten, en voel maar hoe fijn je je daar voelt.')
        sleep(1)
        self.droomrobot.say('De motor ronkt.')
        self.droomrobot.play_audio('resources/audio/vroomvroom.wav')
        self.droomrobot.say(
            'Je voelt het stuur in je handen. Je zit vast met een stevige gordel. helemaal klaar voor de start.')
        self.droomrobot.say('Ga maar lekker een rondje rijden in je speciale auto en voel maar hoe makkelijk dat gaat.')
        self.droomrobot.say('Jij hebt alles onder controle.')
        return kleur

    def dolfijn_oefenen(self, child_name: str, child_age: int):
        self.droomrobot.say(
            'En terwijl je zo rustig aan het ademhalen bent, mag je je gaan voorstellen dat je een dolfijn bent die aan het zwemmen is.')
        self.droomrobot.say('Je bent in een mooie, blauwe zee.')
        self.droomrobot.say('Kijk maar eens om je heen wat je allemaal kan zien.')
        self.droomrobot.say('Welke kleuren er allemaal zijn en hoe het er voelt.')
        sleep(2)
        self.droomrobot.say('Misschien is het water warm en zacht, of fris en koel.')
        self.droomrobot.say('Je voelt hoe je licht wordt, alsof je zweeft.')
        kleur = self.droomrobot.ask_entity_llm('Wat voor kleur dolfijn ben je?')
        self.droomrobot.say(f'Aah, een {kleur} dolfijn! Die zijn extra krachtig.')
        self.droomrobot.say(
            'Je zult wellicht zien dat als je om je heen kijkt dat je dan de zonnenstralen door het water ziet schijnen.')
        sleep(1)
        self.droomrobot.say('Er zwemmen vrolijke vissen om je heen.')
        self.droomrobot.say('Ga maar lekker op avontuur in die onderwaterwereld en kijk wat je allemaal kan vinden.')
        sleep(2)
        return kleur

    def waterglijbaan_oefenen(self, child_name: str, child_age: int):
        self.droomrobot.say(
            'En terwijl je zo rustig aan het ademhalen bent mag je je gaan voorstellen dat je in een waterpretpark bent.')
        self.droomrobot.say('Het is een lekker warme dag en je voelt de zon op je gezicht.')
        self.droomrobot.say('Om je heen hoor je het spetterende water en vrolijke stemmen.')
        self.droomrobot.say('En voor je zie je de grootste, gaafste waterglijbanen die je ooit hebt gezien!')
        self.droomrobot.say(
            'Kijk maar eens om je heen welke glijbanen je allemaal ziet en welke kleuren de glijbanen hebben.')
        kleur = self.droomrobot.ask_entity_llm('Welke kleur heeft de glijbaan waar je vanaf wilt gaan?')
        self.droomrobot.say(f'Wat goed! Die mooie {kleur} glijbaan gaat jou vandaag helpen.')
        self.droomrobot.say('Je loopt langzaam de trap op naar de top van de glijbaan')
        self.droomrobot.say('Merk maar dat je je bij iedere stap fijner en rustiger voelt.')
        self.droomrobot.say('Misschien voel je een beetje kriebels in je buik dat is helemaal oké!')
        self.droomrobot.say('Dat betekent dat je er klaar voor bent.')
        self.droomrobot.say('Bovenaan ga je zitten.')
        self.droomrobot.say('Je voelt het koele water om je heen.')
        self.droomrobot.say('Je plaatst je handen naast je.')
        self.droomrobot.say('Adem diep in')
        sleep(2)
        self.droomrobot.say('en klaar voor de start!')
        self.droomrobot.say('Ga maar rustig naar beneden met de glijbaan en merk maar hoe rustig en soepel dat gaat.')
        return kleur

    def raceauto_interventie(self, child_name: str, kleur: str):
        self.droomrobot.say(f'Stel je maar weer voor dat je op de racebaan staat met jouw {kleur} raceauto!')
        sleep(3)
        self.droomrobot.say('Je auto rijdt op een rechte weg.')
        self.droomrobot.say(
            'Je rijdt precies zo snel als jij fijn vindt en je hebt alles onder controle, waardoor je je sterk voelt.')
        self.droomrobot.say('De auto heeft speciale zachte banden die over de speciale weg heen rijden.')
        self.droomrobot.say('Kijk maar wat voor mooie kleur de speciale weg heeft.')
        self.droomrobot.say('Je kunt je zelfs voorstellen dat de weg glitters heeft om je extra kracht te geven.')
        self.droomrobot.say(
            'Voor je zie je een tunnel. Het is een speciale tunnel, precies groot genoeg voor jouw auto.')
        self.droomrobot.say('Je weet dat als je rustig blijft rijden, je er soepel doorheen komt.')
        self.droomrobot.say(
            'De tunnel heeft precies de juiste vorm, je hoeft alleen maar ontspannen door te blijven rijden.')
        self.droomrobot.say('En in de tunnel zitten prachtige lichtjes en hele mooie kleuren.')
        self.droomrobot.say('Kijk maar eens wat voor mooie kleuren jij allemaal in de tunnel ziet.')
        self.droomrobot.say(
            'En jij blijft rustig doorrijden. Precies zo snel als jij fijn vindt, je hebt alles onder controle.')
        self.droomrobot.say(
            'Misschien voelt het soms even gek of kriebelt het een beetje in de tunnel, net als wanneer je met je auto over een hobbel in de weg rijdt.')
        self.droomrobot.say(
            'Maar jij weet: als je rustig blijft ademen en je blik op de weg houdt, kom je er zo doorheen.')
        self.droomrobot.say('Je auto glijdt soepel verder en verder.')
        self.droomrobot.say('En steeds dieper de tunnel in. En jij blijft heerlijk in je auto zitten.')
        self.droomrobot.say(
            'En je stuurt de auto met de juiste snelheid, precies wat goed is voor jou. En voel maar dat jij dit heel goed kan.')
        self.droomrobot.say('En de verpleegkundige zal je vertellen wanneer je bij het einde van de tunnel bent.')

        ## outro
        self.droomrobot.say('Wow! Jij bent door de tunnel gereden als een echte coureur!')
        self.droomrobot.say('De finishvlag wappert voor je en het publiek juicht.')
        self.droomrobot.say('Wat een geweldige race!')
        self.droomrobot.say('Je hebt dit zo goed gedaan.')
        self.droomrobot.say('Je auto staat nu stil op de eindstreep en je mag lekker even ontspannen.')
        self.droomrobot.say('Misschien voel je nog een klein beetje de weg onder je trillen, maar dat is oké.')
        self.droomrobot.say('Je hebt alles onder controle en je bent een echte racekampioen!')
        self.droomrobot.say('Nu mag je je ogen weer open doen.')

    def waterglijbaan_interventie(self, child_name: str, kleur: str):
        self.droomrobot.say('Stel je je maar weer voor dat je in het waterpretpark bent.')
        self.droomrobot.say(f'Je gaat weer de trap op van jouw {kleur} glijbaan, die je net al zo goed geoefend hebt.')
        self.droomrobot.say('Bij iedere stap voel je weer dat je lichaam zich goed voelt en je er kracht van krijgt.')
        self.droomrobot.say('Hoor het geluid van het water maar.')
        self.droomrobot.play_audio('resources/audio/splashing_water.wav')

        self.droomrobot.say('Boven aan ga je weer zitten en adem je weer rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('En uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')

        self.droomrobot.say('Je plaatst je handen naast je ademt diep in. en klaar voor de start!')
        self.droomrobot.say('Daar ga je! Je duwt jezelf zachtjes af en voelt hoe je begint te glijden.')
        self.droomrobot.say('Eerst heel langzaam.')
        self.droomrobot.say('En dan iets sneller.')
        self.droomrobot.say('Precies zoals jij dat fijn vindt!')
        self.droomrobot.say('Je voelt het water langs je glijden, net als een zachte golf die je meevoert.')
        self.droomrobot.say(
            'Misschien voel je dat je soms tegen de zijkant aan komt, dat is gewoon een bocht in de glijbaan! Heel normaal!')
        self.droomrobot.say(
            'Misschien heeft het water in je glijbaan wel een speciale kleur en glitters, zodat het je extra kan helpen.')
        self.droomrobot.say(
            'Je blijft lekker glijden, met het water dat je moeiteloos omlaag laat gaan. Soms gaat het even iets sneller, dan weer iets rustiger.')
        self.droomrobot.say(
            'Misschien voel je een klein raar kriebeltje, alsof een waterstraaltje even tegen je neus spat.')
        self.droomrobot.say('Maar dat is oké, want jij weet dat je bijna beneden bent.')
        self.droomrobot.say('Je ademt rustig in en uit, net als de zachte golfjes om je heen.')
        self.droomrobot.say('Je komt lager en lager.')
        self.droomrobot.say('En nog een bocht.')
        self.droomrobot.say('De verpleegkundige vertelt je wanneer je bij de laatste bocht bent.')
        self.droomrobot.say('Je voelt jezelf soepel door de tunnel van de glijbaan glijden.')

        ## outro
        self.droomrobot.play_audio('resources/audio/splash.wav')
        self.droomrobot.say('Daar plons je in het zwembad, precies zoals je wilde!')
        self.droomrobot.say('Je voelt je licht en ontspannen. Wat een gave rit!')
        self.droomrobot.say('Het lekkere water heeft je geholpen en het is je gelukt.')
        self.droomrobot.say('En weet je wat? Jij bent echt een supergoede glijbaan-avonturier!')
        self.droomrobot.say(
            'Je hebt laten zien dat je rustig kunt blijven, en dat je overal soepel doorheen kunt glijden.')
        self.droomrobot.say(
            'Je mag jezelf een high vijf geven want jij bent een echte waterkampioen! En doe je ogen maar weer open.')

    def dolfijn_interventie(self, child_name: str, kleur: str):
        self.droomrobot.say(f'Stel je je maar weer voor dat je een {kleur} dolfijn in de zee bent.')
        self.droomrobot.say('Kijk maar weer om je heen wat je allemaal ziet.')
        self.droomrobot.say('De visjes om je heen en de mooie kleuren.')
        self.droomrobot.say(
            'Merk maar hoe soepel je je door het water heen beweegt, en hoe fijn je je voelt op die plek.')
        self.droomrobot.say('Als je goed kijkt zie je in de verte een oude schatkist op de oceaanbodem.')
        self.droomrobot.say('Dat is jouw missie van vandaag: je gaat ernaartoe zwemmen als een echte dolfijn.')
        self.droomrobot.say('Je beweegt je lichaam soepel, net als een dolfijn.')
        self.droomrobot.say('Eerst rustig.')
        self.droomrobot.say('En dan iets sneller.')
        self.droomrobot.say('Je voelt hoe het water je zachtjes verder en lager brengt.')
        self.droomrobot.say('Elke keer dat je inademt, voel je de frisse zeelucht vullen met energie.')
        self.droomrobot.say('Als je uitademt, laat je alle spanning los.')
        self.droomrobot.say('Heel ontspannen, net als een dolfijn die rustig door het water glijdt.')
        self.droomrobot.say('En terwijl je zwemt zie je een onderwatergrot.')
        self.droomrobot.say('Het is een geheime doorgang en de ingang is precies groot genoeg voor jou.')
        self.droomrobot.say('Je weet dat als je soepel en rustig zwemt, je er moeiteloos doorheen glijdt.')
        self.droomrobot.say('Je voelt misschien een zacht gevoel bij je neus of keel.')
        self.droomrobot.say(
            'Dat is gewoon een klein zeewierplantje dat je even aanraakt en dat jou extra kracht geeft. Heel normaal!')
        self.droomrobot.say('Jij blijft rustig zwemmen door de grot, met een bochtje en weer verder.')
        self.droomrobot.say(
            'Soms voel je een klein golfje langs je neus, net als een dolfijn die door een stroomversnelling zwemt!')
        self.droomrobot.say('En je weet dat als je rustig blijft bewegen dat je er gemakkelijk doorheen gaat.')
        self.droomrobot.say('De verpleegkundige vertelt je wanneer je bij de schat bent.')
        self.droomrobot.say('Je zwemt soepel verder.')
        self.droomrobot.say('Kijk maar of je al iets van de schat kunt zien!')

        ## outro
        self.droomrobot.say('Je bent bij de uitgang van de grot en ja hoor, je ziet de schat!')
        self.droomrobot.say('De kist ligt op de bodem, glinsterend tussen het koraal.')
        self.droomrobot.say('Je strekt je vinnen uit en je hebt hem. Het zit vol met gouden munten en juwelen.')
        self.droomrobot.say(
            'Je hebt het geweldig gedaan! Je hebt laten zien hoe rustig en sterk je bent, als een echte dolfijn.')
        self.droomrobot.say('Zwem maar weer rustig omhoog en open je ogen zodat je weer hier in de ruimte bent.')
