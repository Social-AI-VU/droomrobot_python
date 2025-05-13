from os.path import abspath, join
from time import sleep

from sic_framework.services.openai_gpt.gpt import GPTRequest

from droomrobot import Droomrobot, AnimationType


class Bloedafname9:

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
        self.droomrobot.animate(AnimationType.ACTION, "009")
        self.droomrobot.say(f'Hallo, ik ben {robot_name} de droomrobot!')
        self.droomrobot.say('Wat fijn dat ik je mag helpen vandaag.')
        self.droomrobot.say('Wat is jouw naam?')
        sleep(3)
        self.droomrobot.say(f'{child_name}, wat een leuke naam.')
        self.droomrobot.say('En hoe oud ben je?')
        sleep(3)
        self.droomrobot.say(
            f'{str(child_age)} jaar. Oh wat goed, dan kan ik je een truc leren om alles in het ziekenhuis voor jou makkelijker te maken.')
        self.droomrobot.say(
            'Die truc werkt bij veel kinderen heel goed.')
        self.droomrobot.say('En ik ben dan ook benieuwd hoe goed het bij jou gaat werken.')
        self.droomrobot.say('Jij kunt jezelf helpen door je lichaam en je hoofd te ontspannen.')
        self.droomrobot.say('We gaan het samen doen, op jouw eigen manier.')
        self.droomrobot.say('Ik ga je wat vertellen over deze truc.')
        self.droomrobot.say('Let maar goed op, dan ga jij het ook leren.')
        self.droomrobot.say('We gaan samen een reis maken in je fantasie, wat ervoor zorgt dat jij je fijn, rustig en sterk voelt.')
        self.droomrobot.say('Met je fantasie kun je aan iets fijns denken terwijl je hier bent, als een soort droom.')
        self.droomrobot.say('En het grappige is dat als je denkt aan iets fijns, dat jij je dan ook fijner gaat voelen.')
        self.droomrobot.say('Ik zal het even voordoen.')
        self.droomrobot.say('Ik ga het liefst in gedachten naar de wolken, lekker relaxed zweven.')
        # self.droomrobot.say('Kijk maar eens in mijn ogen, dan zie je wat ik bedoel.')
        # self.droomrobot.say('cool he.')
        self.droomrobot.say('Maar het hoeft niet de wolken te zijn. Iedereen heeft een eigen fijne plek.')
        self.droomrobot.say('Laten we nu samen bedenken wat jouw fijne plek is.')
        self.droomrobot.say('Je kan bijvoorbeeld in gedachten naar het strand, het bos, of op vakantie.')

        # droomplek = self.droomrobot.ask_entity('Wat is een plek waar jij je fijn voelt? Het strand, het bos, de speeltuin of de ruimte?',
        #                             {'droom_plek': 1},
        #                             'droom_plek',
        #                             'droom_plek')

        droomplek = self.droomrobot.ask_entity_llm('Naar welke veilige plek zou jij in gedachten willen gaan?')

        if droomplek:
            if 'strand' in droomplek:
                self.strand(child_name, child_age)
            elif 'bos' in droomplek:
                self.bos(child_name, child_age)
            elif 'vakantie' in droomplek:
                self.vakantie(child_name, child_age)
            else:
                self.nieuwe_droomplek(droomplek, child_name, child_age)
        else:
            droomplek = 'strand'  # default
            self.droomplek_not_recognized(child_name, child_age)
        droomplek_lidwoord = self.droomrobot.get_article(droomplek)

        # SAMEN OEFENEN
        self.droomrobot.say(f'Laten we alvast oefenen om samen een reis in je fantasie te maken, zodat het je zometeen gaat helpen bij het bloedprikken.')
        self.droomrobot.say('Ga even lekker zitten zoals jij dat fijn vindt.')
        sleep(1)
        zit_goed = self.droomrobot.ask_yesno("Zit je goed zo?")
        if zit_goed and 'yes' in zit_goed:
            self.droomrobot.say('En nu je lekker bent gaan zitten.')
        else:
            self.droomrobot.say('Het zit vaak het lekkerste als je stevig gaat zitten.')
            self.droomrobot.say('met beide benen op de grond.')
            self.droomrobot.say('Ga maar eens kijken hoe goed dat zit.')
            sleep(1)
            self.droomrobot.say('Als je goed zit.')
        self.droomrobot.say('mag je je ogen dicht doen.')
        self.droomrobot.say('dan werkt het trucje het beste.')

        sleep(1)
        self.droomrobot.say('Stel je voor, dat je op een hele fijne mooie plek bent in je eigen gedachten.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say(f'Misschien is dit weer {droomplek_lidwoord} {droomplek}, of een nieuwe fantasieplek', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Kijk maar eens om je heen, wat je allemaal op die mooie plek ziet.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Misschien ben je er alleen of is er iemand bij je.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Kijk maar welke mooie kleuren je allemaal om je heen ziet.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Misschien wel groen, of paars, of regenboog kleuren.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('En merk maar hoe fijn jij je op deze plek voelt.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Luister naar de geluiden die je op die plek kan horen.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('En hoe de temperatuur daar voelt, misschien is het heerlijk warm of lekker koel.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('En stel je dan nu voor, dat er een luchtballon is op jouw fijne plek.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Die speciaal op jou staat te wachten.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Kijk maar eens welke kleur jouw luchtballon heeft.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Jij mag een ballonvaart gaan maken in die superveilige luchtballon.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Je mag je voorstellen dat je in de mand van de luchtballon stapt.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Als je goed in het mandje bent gestapt gaat de luchtballon in een prettig en rustig tempo omhoog.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Precies zo hoog als dat jij fijn vindt.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('En kijk maar weer om je heen wat je allemaal ziet.', speaking_rate=0.9)
        self.droomrobot.play_audio('resources/audio/birds.wav')
        self.droomrobot.say('Merk maar hoe fijn je je voelt op deze plek.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Dan gaan we nu oefenen hoe je je nog krachtiger en veiliger kan voelen.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Dit doe je door diep in en uit te ademen.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Adem diep in door je neus.', speaking_rate=0.9)
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en blaas langzaam uit door je mond.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')
        sleep(0.5)
        self.droomrobot.say('Goed zo, dat gaat al heel goed.', speaking_rate=0.9)
        self.droomrobot.say(
            'En terwijl je zo goed aan het ademen bent, stel je voor dat er een klein, warm lichtje op je arm verschijnt.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Dat lichtje laadt jouw kracht op.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Stel je eens voor hoe dat lichtje eruit ziet.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Is het geel, blauw of misschien jouw lievelingskleur?', speaking_rate=0.9)
        sleep(0.5)
        kleur = self.droomrobot.ask_entity_llm('Welke kleur heeft jouw lichtje?')
        sleep(0.5)
        self.droomrobot.say(f'{kleur}, wat goed.', speaking_rate=0.9)
        sleep(0.5)
        kleur_adjective = self.droomrobot.get_adjective(kleur)
        ##
        self.droomrobot.say(f'Merk maar eens hoe dat {kleur_adjective} lichtje je een heel fijn, krachtig gevoel geeft.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('En hoe jij nu een superheld bent met jouw superkracht en alles aankan.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say(
            'En iedere keer als je het nodig hebt, kun je zoals je nu geleerd hebt, een paar keer diep in en uit ademen, om het lichtje te activeren en jouw kracht te laten groeien.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Hartstikke goed, ik ben benieuwd hoe goed het lichtje je zometeen gaat helpen.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say(
            'Als je genoeg geoefend hebt, mag je de luchtballon weer rustig laten landen.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Als dat gelukt is, mag je je ogen weer lekker open doen, en met je gedachten terugkomen in deze kamer.', speaking_rate=0.9)
        sleep(1)

        oefenen_goed = self.droomrobot.ask_yesno('Ging het oefenen goed?')
        if 'yes' in oefenen_goed:
            experience = self.droomrobot.ask_open('Wat fijn. Wat vond je goed gaan?')
            if experience:
                personalized_response = self.droomrobot.personalize('Wat fijn. Wat vond je goed gaan?', child_age,
                                                                    experience)
                self.droomrobot.say(personalized_response)
            else:
                self.droomrobot.say("Wat knap van jou.")
            self.droomrobot.say(f'Ik vind {kleur} een hele mooie kleur, die heb je goed gekozen.')
        else:
            experience = self.droomrobot.ask_open('Wat ging er nog niet zo goed?')
            if experience:
                personalized_response = self.droomrobot.personalize('Wat ging er nog niet zo goed?', child_age,
                                                                    experience)
                self.droomrobot.say(personalized_response)
            else:
                pass
            self.droomrobot.say(f'Gelukkig wordt het steeds makkelijker als je het vaker oefent.')
        self.droomrobot.say('Ik ben benieuwd hoe goed het zometeen gaat.')
        self.droomrobot.say('Je zult zien dat dit je gaat helpen.')
        self.droomrobot.say(
            'Als je zometeen aan de beurt bent, ga ik je helpen om weer een reis met je fantasie te maken.')

        ### INTERVENTIE
        sleep(5)
        self.droomrobot.say('Wat fijn dat ik je weer mag helpen, we gaan weer samen een reis door je fantasie maken.')
        self.droomrobot.say(
            'Omdat je net al zo goed hebt geoefend, zul je zien dat het nu nog beter en makkelijker gaat.')
        self.droomrobot.say(
            'Je mag weer goed gaan zitten en je ogen dicht doen zodat het trucje nog beter werkt.')
        sleep(1)
        self.droomrobot.say(
            'Luister maar weer goed naar mijn stem en merk maar dat andere geluiden in het ziekenhuis veel stiller worden.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Ga maar rustig ademen zoals je dat gewend bent.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Adem rustig in.', speaking_rate=0.9)
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')
        sleep(0.5)
        self.droomrobot.say(f'Stel je maar voor dat je weer bij {droomplek_lidwoord} {droomplek} bent.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say(
            'Kijk maar weer naar alle mooie kleuren die om je heen zijn en merk hoe fijn je je voelt op deze plek.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Luister maar naar alle fijne geluiden op die plek.', speaking_rate=0.9)
        sleep(0.5)
        # Sound should be here but this is not possible with the LLM generated content
        self.droomrobot.say('Als je wil mag je weer een ritje maken in jouw speciale luchtballon, of je kan iets anders leuks doen op je fijne plek.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Merk maar hoe fijn jij je voelt op jouw fijne veilige plek.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Nu gaan we je kracht weer activeren zoals je dat geleerd hebt.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Adem in via je neus.', speaking_rate=0.9)
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en blaas rustig uit via je mond.', speaking_rate=0.9)
        self.droomrobot.play_audio('resources/audio/breath_out.wav')
        sleep(0.5)
        self.droomrobot.say(
            'En kijk maar hoe je krachtige lichtje weer op je arm verschijnt in precies de goede kleur die je nodig hebt.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Zie het lichtje steeds sterker en krachtiger worden.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Zodat jij jezelf kan helpen.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('En als je het nodig hebt, stel je voor dat je lichtje nog helderder gaat schijnen.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Dat betekent dat jouw kracht helemaal wordt opgeladen.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Als het nodig is, kan je de kracht nog groter maken door met je tenen te wiebelen.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Het geeft een veilige en zachte gloed om je te helpen.', speaking_rate=0.9)
        sleep(0.5)
        self.droomrobot.say('Adem diep in.', speaking_rate=0.9)
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en blaas uit.', speaking_rate=0.9)
        self.droomrobot.play_audio('resources/audio/breath_out.wav')
        sleep(0.5)
        self.droomrobot.say('Merk maar hoe goed jij jezelf kan helpen, op je eigen veilige plek.', speaking_rate=0.9)

        ### AFSCHEID
        sleep(1)
        self.droomrobot.say('Wat heb je jezelf goed geholpen om alles makkelijker te maken.')
        ging_goed = self.droomrobot.ask_opinion_llm("Hoe goed is het gegaan?")
        if 'positive' in ging_goed:
            self.droomrobot.say('Wat fijn! je hebt jezelf echt goed geholpen.')
        else:
            self.droomrobot.say('Dat geeft niets.')
            self.droomrobot.say('Je hebt goed je best gedaan.')
            self.droomrobot.say('En kijk welke stapjes je allemaal al goed gelukt zijn.')
        self.droomrobot.say(f'je kon al goed een {kleur} lichtje uitzoeken.')  # weet niet of het zo goed gaat met '
        self.droomrobot.say('En weet je wat nu zo fijn is, hoe vaker je dit truukje oefent, hoe makkelijker het wordt.')
        self.droomrobot.say('Je kunt dit ook zonder mij oefenen.')
        self.droomrobot.say('Je hoeft alleen maar je ogen dicht te doen en op reis te gaan in je fantasie.')
        self.droomrobot.say('Dan word je lichaam vanzelf wel rustig en voel jij je fijn.')
        self.droomrobot.say('Ik ben benieuwd hoe goed je het de volgende keer gaat doen.')
        self.droomrobot.say('Je doet het op jouw eigen manier, en dat is precies goed.')
        self.droomrobot.say('Ik ga nu een ander kindje helpen, net zoals ik jou nu heb geholpen.')
        self.droomrobot.say('Misschien zien we elkaar de volgende keer!')

    def strand(self, child_name: str, child_age: int):
        self.droomrobot.say('Ah, het strand! Ik kan de golven bijna horen en het zand onder mijn voeten voelen.')
        self.droomrobot.say('Weet je wat ik daar graag doe? Een zandkasteel bouwen met een vlag er op.')
        motivation = self.droomrobot.ask_open(f'Wat zou jij daar willen doen {child_name}?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat zou jij op het strand willen doen?', child_age,
                                                                motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Dat klinkt heerlijk! Ik kan me dat helemaal voorstellen.")

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
            self.droomrobot.say("Wat een leuk idee! Het bos is echt een magische plek.")

    def vakantie(self, child_name: str, child_age: int):
        self.droomrobot.say('Oh ik hou van vakantie. Mijn laatste vakantie was in Frankrijk op een camping met veel waterglijbanen.')
        self.droomrobot.say('Het was er heerlijk warm in de zon.')
        motivation = self.droomrobot.ask_open(f'Wat gingen jullie op vakantie doen {child_name}?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat gingen jullie op vakantie doen?',
                                                                child_age, motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Dat klinkt heel leuk. Wat fijn dat je daaraan kan terug denken.")


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


if __name__ == '__main__':
    bloedafname6 = Bloedafname6(mini_ip="192.168.178.111", mini_id="00167", mini_password="alphago",
                                redis_ip="192.168.178.84",
                                google_keyfile_path=abspath(join("..", "conf", "dialogflow", "google_keyfile.json")),
                                openai_key_path=abspath(join("..", "conf", "openai", ".openai_env")),
                                default_speaking_rate=0.8, computer_test_mode=False)
    bloedafname6.run('Tessa', 8)