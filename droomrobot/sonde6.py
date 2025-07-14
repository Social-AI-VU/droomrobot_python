from time import sleep

from sic_framework.services.openai_gpt.gpt import GPTRequest

from core import AnimationType
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext, InteractionSession, InterventionPhase, \
    InteractionChoice, InteractionChoiceCondition


class Sonde6(DroomrobotScript):

    def __init__(self, *args, **kwargs):
        super(Sonde6, self).__init__(*args, **kwargs, interaction_context=InteractionContext.BLOEDAFNAME)

    def prepare(self, participant_id: str, session: InteractionSession, user_model_addendum: dict):
        super().prepare(participant_id, session, user_model_addendum)

        if session == InteractionSession.INTRODUCTION:
            self._introduction()
        elif session == InteractionSession.INTERVENTION:
            self._intervention()
        elif session == InteractionSession.GOODBYE:
            self._goodbye()
        else:
            print("Interaction part not recognized")

    def _introduction(self):
        self.droomrobot.animate(AnimationType.ACTION, "009")
        self.droomrobot.animate(AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand up
        self.droomrobot.animate(AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile        
        # INTRODUCTIE
        self.droomrobot.say(f'Hallo, ik ben de droomrobot!')
        self.droomrobot.say('Wat fijn dat ik je mag helpen vandaag.')
        self.droomrobot.ask_fake('Wat is jouw naam?', 3)
        self.droomrobot.say(f'{self.user_model['child_name']}, wat een leuke naam.')
        self.droomrobot.ask_fake('En hoe oud ben je?', 3)
        self.droomrobot.say(f'{str(self.user_model['child_age'])} jaar. Oh wat goed, dan ben je al oud genoeg om mijn speciale trucje te leren.')
        self.droomrobot.say('Ik heb namelijk een truukje dat bij heel veel kinderen goed werkt om alles in het ziekenhuis makkelijker te maken.')
        self.droomrobot.say('Ik ben benieuwd hoe goed het bij jou gaat werken.')
        self.droomrobot.say('Mijn trucje is dat je gaat luisteren naar een bijzonder verhaal.')
        self.droomrobot.say('Het is een soort droom reis die jou helpt om je nu en straks fijn, rustig en sterk te voelen.')
        self.droomrobot.say('We gaan het verhaal van jouw droomreis samen maken zodat het precies bij jou past, want dan werkt het het allerbeste.')
        self.droomrobot.say('Nu ga ik je wat meer vertellen over het trucje wat ik kan.')
        self.droomrobot.say('Let maar goed op, ik ga je iets bijzonders leren. Het heet een droomreis.')
        self.droomrobot.say('Met een droomreis kun je aan iets fijns denken terwijl je hier in het ziekenhuis bent.')
        self.droomrobot.say('Ik zal het trucje even voor doen.')
        self.droomrobot.say('Ik ga in mijn droomreis het liefst in gedachten naar de wolken.')
        self.droomrobot.say('Je kan van alles bedenken.')
        self.droomrobot.say('Wat goed helpt is om je voor te stellen dat je in een raceauto door een tunnel scheurt, of van een waterglijbaan gaat, of als dolfijn door het water beweegt.')
        self.droomrobot.say('Welke lijkt jij het leukste?')

        self.user_model['droomplek'] = self.droomrobot.ask_entity('De waterglijbaan, de race-auto of dolfijn?',
                                               {'droomplek': 1},
                                               'droomplek',
                                               'droomplek')

        if self.user_model['droomplek']:
            if 'raceauto' in self.user_model['droomplek']:
                self.raceauto()
            elif 'waterglijbaan' in self.user_model['droomplek']:
                self.waterglijbaan()
            elif 'dolfijn' in self.user_model['droomplek']:
                self.dolfijn()
            # else:
            #     self.nieuwe_droomplek(droomplek, child_name, self.user_model['child_age'])
        else:
            self.user_model['droomplek'] = 'raceauto'  # default
            self.droomplek_not_recognized()
        self.user_model['droomplek_lidwoord'] = self.droomrobot.get_article(self.user_model['droomplek'])
        self.droomrobot.save_user_model(self.participant_id, self.user_model)

        # SAMEN OEFENEN
        self.droomrobot.say('Laten we alvast gaan oefenen om samen een mooie droomreis te maken, zodat het je zometeen gaat helpen bij het sonde inbrengen.')
        self.droomrobot.say('De sonde is een soort zacht rietje die je gaat helpen om je goed te voelen.')
        self.droomrobot.say('Ga even lekker zitten zoals jij dat fijn vindt.', sleep_time=1)
        zit_goed = self.droomrobot.ask_yesno("Zit je zo goed?")
        if 'yes' in zit_goed:
            self.droomrobot.say('En nu je lekker bent gaan zitten.')
        else:
            self.droomrobot.say('Het zit vaak het lekkerste als je stevig gaat zitten.')
            self.droomrobot.say('met beide benen op de grond.', sleep_time=1)
            self.droomrobot.say('Als je goed zit.')
        self.droomrobot.say('mag je je ogen dicht doen.')
        self.droomrobot.say('dan werkt het truukje het beste.', sleep_time=1)
        self.droomrobot.say('En terwijl je nu zo lekker zit, mag je je handen op je buik doen en rustig gaan ademhalen.')
        self.droomrobot.say('Adem rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')
        self.droomrobot.say('En voel maar dat je buik iedere keer rustig omhoog en omlaag gaat als je zo lekker aan het ademhalen bent.')

        if self.user_model['droomplek']:
            if 'raceauto' in self.user_model['droomplek']:
                self.raceauto_oefenen()
            elif 'waterglijbaan' in self.user_model['droomplek']:
                self.waterglijbaan_oefenen()
            elif 'dolfijn' in self.user_model['droomplek']:
                self.dolfijn_oefenen()

        self.droomrobot.say('En wat zo fijn is, is dat iedere keer als je het nodig hebt je weer terug kan gaan naar deze fijne plek.')
        self.droomrobot.say('Je hoeft alleen maar een paar keer diep in en uit te ademen.')
        self.droomrobot.say('Ik ben benieuwd hoe goed dit je zometeen gaat helpen.')
        self.droomrobot.say('Als je genoeg geoefend hebt, mag je je ogen weer lekker open doen.', sleep_time=1)
        self.droomrobot.say(f'Ik vind {self.user_model['kleur']} een hele mooie kleur, die heb je goed gekozen.')

        if self.user_model['droomplek']:
            if 'raceauto' in self.user_model['droomplek']:
                self.droomrobot.say('Als je zometeen aan de beurt bent, ga ik je helpen om weer naar de racebaan te gaan in gedachten.')
            elif 'waterglijbaan' in self.user_model['droomplek']:
                self.droomrobot.say('Als je zometeen aan de beurt bent, ga ik je helpen om weer naar het waterpretpark te gaan in gedachten.')
            elif 'dolfijn' in self.user_model['droomplek']:
                self.droomrobot.say('Als je zometeen aan de beurt bent, ga ik je helpen om weer naar de zee te gaan in gedachten.')

    def _intervention(self):
        self.phases = [
            InterventionPhase.PREPARATION.name,
            InterventionPhase.PROCEDURE.name,
            InterventionPhase.WRAPUP.name
        ]
        self.phase_moves_build = InteractionChoice('Sonde6', InteractionChoiceCondition.PHASE)
        self.phase_moves_build = self._intervention_preparation(self.phase_moves_build)
        self.phase_moves_build = self._intervention_procedure(self.phase_moves_build)
        self.phase_moves = self._intervention_wrapup(self.phase_moves_build)

    def _intervention_preparation(self, phase_moves: InteractionChoice) -> InteractionChoice:
        self.droomrobot.animate(AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        self.droomrobot.animate(AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        self.droomrobot.say('Wat fijn dat ik je weer mag helpen, we gaan weer samen een droomreis maken.', animated=False)
        self.droomrobot.say('Omdat je net al zo goed hebt geoefend zul je zien dat het nu nog beter en makkelijker gaat.')
        self.droomrobot.say('Je mag weer goed gaan zitten en je ogen dicht doen zodat deze droomreis nog beter voor jou werkt.', sleep_time=1)
        self.droomrobot.say('Luister maar weer goed naar mijn stem en merk maar dat andere geluiden in het ziekenhuis veel stiller worden.')
        self.droomrobot.say('Ga maar rustig ademen zoals je dat gewend bent.')

        self.droomrobot.say('Adem rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')

        intervention_prep_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Raceauto
        self.droomrobot.say(f'Stel je maar weer voor dat je op de racebaan staat met jouw {self.user_model['kleur']} raceauto!', sleep_time=3)
        self.droomrobot.say('Je auto rijdt op een rechte weg.')
        self.droomrobot.say('Je rijdt precies zo snel als jij fijn vindt en je hebt alles onder controle, waardoor je je sterk voelt.')
        self.droomrobot.say('De auto heeft speciale zachte banden die over de speciale weg heen rijden.')
        self.droomrobot.say('Kijk maar wat voor mooie kleur de speciale weg heeft.')
        self.droomrobot.say('Je kunt je zelfs voorstellen dat de weg glitters heeft om je extra kracht te geven.')

        # Waterglijbaan
        self.droomrobot.say('Stel je je maar weer voor dat je in het waterpretpark bent.')
        self.droomrobot.say(f'Je gaat weer de trap op van jouw {self.user_model['kleur']} glijbaan, die je net al zo goed geoefend hebt.')
        self.droomrobot.say('Bij iedere stap voel je weer dat je lichaam zich goed voelt en je er kracht van krijgt.')
        self.droomrobot.say('Hoor het geluid van het water maar.')
        self.droomrobot.play_audio('resources/audio/splashing_water.wav')

        self.droomrobot.say('Boven aan ga je weer zitten en adem je weer rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('En uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')

        # Dolfijn
        self.droomrobot.say(f'Stel je je maar weer voor dat je een {self.user_model['kleur']} dolfijn in de zee bent.')
        self.droomrobot.say('Kijk maar weer om je heen wat je allemaal ziet.')
        self.droomrobot.say('De visjes om je heen en de mooie kleuren.')
        self.droomrobot.say('Merk maar hoe soepel je je door het water heen beweegt, en hoe fijn je je voelt op die plek.')
        self.droomrobot.say('Als je goed kijkt zie je in de verte een oude schatkist op de oceaanbodem.')
        self.droomrobot.say('Dat is jouw missie van vandaag: je gaat ernaartoe zwemmen als een echte dolfijn.')
        self.droomrobot.say('Je beweegt je lichaam soepel, net als een dolfijn.')
        self.droomrobot.say('Eerst rustig.')
        self.droomrobot.say('En dan iets sneller.')
        self.droomrobot.say('Je voelt hoe het water je zachtjes verder en lager brengt.')
        self.droomrobot.say('Elke keer dat je inademt, voel je de frisse zeelucht vullen met energie.')
        self.droomrobot.say('Als je uitademt, laat je alle spanning los.')
        self.droomrobot.say('Heel ontspannen, net als een dolfijn die rustig door het water glijdt.')

        phase_moves.add_choice(InterventionPhase.PREPARATION.name, intervention_prep_choice)
        return phase_moves

    def _intervention_procedure(self, phase_moves: InteractionChoice) -> InteractionChoice:
        intervention_proc_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Raceauto
        self.droomrobot.say('Voor je zie je een tunnel. Het is een speciale tunnel, precies groot genoeg voor jouw auto.')
        self.droomrobot.say('Je weet dat als je rustig blijft rijden, je er soepel doorheen komt.')
        self.droomrobot.say('De tunnel heeft precies de juiste vorm, je hoeft alleen maar ontspannen door te blijven rijden.')
        self.droomrobot.say('En in de tunnel zitten prachtige lichtjes en hele mooie kleuren.')
        self.droomrobot.say('Kijk maar eens wat voor mooie kleuren jij allemaal in de tunnel ziet.')
        self.droomrobot.say('En jij blijft rustig doorrijden. Precies zo snel als jij fijn vindt, je hebt alles onder controle.')
        self.droomrobot.say('Misschien voelt het soms even gek of kriebelt het een beetje in de tunnel, net als wanneer je met je auto over een hobbel in de weg rijdt.')
        self.droomrobot.say('Maar jij weet: als je rustig blijft ademen en je blik op de weg houdt, kom je er zo doorheen.')
        self.droomrobot.say('Je auto glijdt soepel verder en verder.')
        self.droomrobot.say('En steeds dieper de tunnel in. En jij blijft heerlijk in je auto zitten.')
        self.droomrobot.say('En je stuurt de auto met de juiste snelheid, precies wat goed is voor jou. En voel maar dat jij dit heel goed kan.')
        self.droomrobot.say('En de verpleegkundige zal je vertellen wanneer je bij het einde van de tunnel bent.')

        # Waterglijbaan
        self.droomrobot.say('Je plaatst je handen naast, je ademt diep in, en klaar voor de start!')
        self.droomrobot.say('Daar ga je! Je duwt jezelf zachtjes af, en voelt hoe je begint te glijden.')
        self.droomrobot.say('Eerst heel langzaam.')
        self.droomrobot.say('En dan iets sneller.')
        self.droomrobot.say('Precies zoals jij dat fijn vindt!')
        self.droomrobot.say('Je voelt het water langs je glijden, net als een zachte golf, die je meevoert.')
        self.droomrobot.say('Misschien voel je dat je soms tegen de zijkant aan komt, dat is gewoon een bocht in de glijbaan! Heel normaal!')
        self.droomrobot.say('Misschien heeft het water in je glijbaan wel een speciale kleur, en glitters, zodat het je extra kan helpen.')
        self.droomrobot.say('Je blijft lekker glijden, met het water dat je moeiteloos omlaag laat gaan. Soms gaat het even iets sneller, dan weer iets rustiger.')
        self.droomrobot.say('Misschien voel je een klein raar kriebeltje, alsof een waterstraaltje even tegen je neus spat.')
        self.droomrobot.say('Maar dat is oké, want jij weet dat je bijna beneden bent.')
        self.droomrobot.say('Je ademt rustig in en uit, net als de zachte golfjes om je heen.')
        self.droomrobot.say('Je komt lager en lager.')
        self.droomrobot.say('En nog een bocht.')
        self.droomrobot.say('De verpleegkundige vertelt je wanneer je bij de laatste bocht bent.')
        self.droomrobot.say('Je voelt jezelf soepel door de tunnel van de glijbaan glijden.')

        # Dolfijn
        self.droomrobot.say('En terwijl je zwemt zie je een onderwatergrot.')
        self.droomrobot.say('Het is een geheime doorgang en de ingang is precies groot genoeg voor jou.')
        self.droomrobot.say('Je weet dat als je soepel en rustig zwemt, je er moeiteloos doorheen glijdt.')
        self.droomrobot.say('Je voelt misschien een zacht gevoel bij je neus of keel.')
        self.droomrobot.say('Dat is gewoon een klein zeewierplantje dat je even aanraakt en dat jou extra kracht geeft. Heel normaal!')
        self.droomrobot.say('Jij blijft rustig zwemmen door de grot, met een bochtje en weer verder.')
        self.droomrobot.say('Soms voel je een klein golfje langs je neus, net als een dolfijn die door een stroomversnelling zwemt!')
        self.droomrobot.say('En je weet dat als je rustig blijft bewegen dat je er gemakkelijk doorheen gaat.')
        self.droomrobot.say('De verpleegkundige vertelt je wanneer je bij de schat bent.')
        self.droomrobot.say('Je zwemt soepel verder.')
        self.droomrobot.say('Kijk maar of je al iets van de schat kunt zien!')

        phase_moves.add_choice(InterventionPhase.PROCEDURE.name, intervention_proc_choice)
        return phase_moves

    def _intervention_wrapup(self, phase_moves: InteractionChoice) -> InteractionChoice:
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.reset_interaction_conf)
        intervention_wrapup_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Raceauto
        self.droomrobot.say('Wow! Jij bent door de tunnel gereden als een echte coureur!')
        self.droomrobot.say('De finishvlag wappert voor je en het publiek juicht.')
        self.droomrobot.say('Wat een geweldige race!')
        self.droomrobot.say('Je hebt dit zo goed gedaan.')
        self.droomrobot.say('Je auto staat nu stil op de eindstreep en je mag lekker even ontspannen.')
        self.droomrobot.say('Misschien voel je nog een klein beetje de weg onder je trillen, maar dat is oké.')
        self.droomrobot.say('Je hebt alles onder controle en je bent een echte racekampioen!')
        self.droomrobot.say('Nu mag je je ogen weer open doen.')

        # Waterglijbaan
        self.droomrobot.play_audio('resources/sounds/splash.wav')
        self.droomrobot.say('Daar plons je in het zwembad, precies zoals je wilde!')
        self.droomrobot.say('Je voelt je licht en ontspannen. Wat een gave rit!')
        self.droomrobot.say('Het lekkere water heeft je geholpen, en het is je gelukt.')
        self.droomrobot.say('En weet je wat? Jij bent echt een supergoede glijbaan-avonturier!')
        self.droomrobot.say('Je hebt laten zien dat je rustig kunt blijven, en dat je overal soepel doorheen kunt glijden.')
        self.droomrobot.say('Je mag jezelf een high vijf geven want jij bent een echte waterkampioen! En doe je ogen maar weer open.')

        # Dolfijn
        self.droomrobot.say('Je bent bij de uitgang van de grot en ja hoor, je ziet de schat!')
        self.droomrobot.say('De kist ligt op de bodem, glinsterend tussen het koraal.')
        self.droomrobot.say('Je strekt je vinnen uit en je hebt hem. Het zit vol met gouden munten en juwelen.')
        self.droomrobot.say('Je hebt het geweldig gedaan! Je hebt laten zien hoe rustig en sterk je bent, als een echte dolfijn.')
        self.droomrobot.say('Zwem maar weer rustig omhoog en open je ogen zodat je weer hier in de ruimte bent.')

        phase_moves.add_choice(InterventionPhase.WRAPUP.name, intervention_wrapup_choice)
        return phase_moves

    def _goodbye(self):
        self.droomrobot.say('Wat heb je jezelf goed geholpen om alles makkelijker te maken.')
        ging_goed = self.droomrobot.ask_opinion_llm("Hoe goed is het gegaan?")
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

    def _build_interaction_choice_droomplek(self) -> InteractionChoice:
        interaction_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)
        
        # Raceauto
        self.droomrobot.say('De raceauto, die vind ik ook het leukste!')
        self.droomrobot.say('Ik vind het fijn dat je zelf kan kiezen hoe snel of rustig je gaat rijden.')
        motivation = self.droomrobot.ask_open(f'Hou jij van snel rijden of rustig?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Hou jij van snel rijden of rustig?', self.user_model['child_age'], motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")
        self.droomrobot.say('Wat mij altijd goed helpt is om in gedachten te denken dat de sonde een race auto is die lekker snel en makkelijk door een tunnel rijdt.')
        
        # Waterglijbaan
        self.droomrobot.say('Wat leuk, het waterpretpark!')
        self.droomrobot.say('Gelukkig kan ik tegen water zodat ik met je mee kan gaan.')
        motivation = self.droomrobot.ask_open(f'Ga jij het liefste snel of rustig van de waterglijbaan?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Ga jij het liefste snel of rustig van de waterglijbaan?', self.user_model['child_age'], motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")
        self.droomrobot.say('Wat mij altijd goed helpt is om in gedachten te denken dat de sonde door een waterglijbaan gaat, lekker snel en makkelijk.')

        # Dolfijn
        self.droomrobot.say('Dat vind ik dol fijn.')
        self.droomrobot.say('Ik vind het altijd heerlijk om door het water te zwemmen op zoek naar schatten onder water.')
        motivation = self.droomrobot.ask_open(f'Hou jij van snel of rustig zwemmen?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Hou jij van snel of rustig zwemmen?', self.user_model['child_age'], motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")
        self.droomrobot.say('Wat mij altijd goed helpt is om in gedachten te denken dat de sonde een dolfijn is die heel makkelijk en snel door het water beweegt, op zoek naar een schat.')
        
        # Fail
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Wauw, een waterglijbaan!')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Ik hou van spetteren in het water.')

        interaction_choice.add_move('waterglijbaan', self.droomrobot.ask_open,
                                    'Glij jij liever snel of langzaam naar beneden?',
                                    user_model_key='droomplek_motivatie')
        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Glij jij liever snel of langzaam naar beneden?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
        interaction_choice.add_choice('waterglijbaan', motivation_choice)
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say,
                                    'Wat mij helpt, is denken dat de sonde net als een waterglijbaan is: hij glijdt zo naar beneden, makkelijk en snel!')
        interaction_choice.add_move('fail', self.set_user_model_variable, 'droomplek_locatie', 'het waterpretpark')
        interaction_choice.add_move('fail', self.set_user_model_variable, 'droomplek', 'waterglijbaan')
        interaction_choice.add_move('fail', self.droomrobot.get_article, lambda: self.user_model['droomplek'],
                                    user_model_key='droomplek_lidwoord')
        
        return interaction_choice

    def _build_interaction_choice_oefenen(self) -> InteractionChoice:
        interaction_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)
        
        # Raceauto
        self.droomrobot.say('En terwijl je zo rustig aan het ademhalen bent mag je je gaan voorstellen dat je op een plek met een racebaan bent.')
        self.droomrobot.say('En op die plek staat een mooie raceauto, speciaal voor jou!')
        self.droomrobot.say('Kijk maar eens hoe jouw speciale raceauto eruit ziet.', sleep_time=1)
        kleur = self.droomrobot.ask_entity_llm('Welke kleur heeft jouw raceauto?')
        self.droomrobot.say(f"Wat goed, die mooie {self.user_model['kleur']} raceauto gaat jou vandaag helpen.")
        self.droomrobot.say('Ga maar in de raceauto zitten, en voel maar hoe fijn je je daar voelt.', sleep_time=1)
        self.droomrobot.say('De motor ronkt.')
        self.droomrobot.play_audio('resources/audio/vroomvroom.wav')
        self.droomrobot.say('Je voelt het stuur in je handen. Je zit vast met een stevige gordel, helemaal klaar voor de start.')
        self.droomrobot.say('Ga maar lekker een rondje rijden in je speciale auto en voel maar hoe makkelijk dat gaat.')
        self.droomrobot.say('Jij hebt alles onder controle.')

        # Waterglijbaan
        self.droomrobot.say('En terwijl je zo rustig aan het ademhalen bent, mag je je gaan voorstellen dat je een dolfijn bent die aan het zwemmen is.')
        self.droomrobot.say('Je bent in een mooie, blauwe zee.')
        self.droomrobot.say('Kijk maar eens om je heen wat je allemaal kan zien.')
        self.droomrobot.say('Welke kleuren er allemaal zijn en hoe het er voelt.', sleep_time=2)
        self.droomrobot.say('Misschien is het water warm en zacht, of fris en koel.')
        self.droomrobot.say('Je voelt hoe je licht wordt, alsof je zweeft.')
        kleur = self.droomrobot.ask_entity_llm('Wat voor kleur dolfijn ben je?')
        self.droomrobot.say(f'Aah, een {self.user_model['kleur']} dolfijn! Die zijn extra krachtig.')
        self.droomrobot.say('Je zult wellicht zien, dat als je om je heen kijkt, dat je dan de zonnestralen door het water ziet schijnen.', sleep_time=1)
        self.droomrobot.say('Er zwemmen vrolijke vissen om je heen.')
        self.droomrobot.say('Ga maar lekker op avontuur in die onderwaterwereld en kijk wat je allemaal kan vinden.', sleep_time=2)

        # Dolfijn
        self.droomrobot.say('En terwijl je zo rustig aan het ademhalen bent mag je je gaan voorstellen dat je in een waterpretpark bent.')
        self.droomrobot.say('Het is een lekker warme dag en je voelt de zon op je gezicht.')
        self.droomrobot.say('Om je heen hoor je het spetterende water en vrolijke stemmen.')
        self.droomrobot.say('En voor je zie je de grootste, gaafste waterglijbanen die je ooit hebt gezien!')
        self.droomrobot.say('Kijk maar eens om je heen, welke glijbanen je allemaal ziet, en welke kleuren de glijbanen hebben.')
        kleur = self.droomrobot.ask_entity_llm('Welke kleur heeft de glijbaan waar je vanaf wilt gaan?')
        self.droomrobot.say(f'Wat goed! Die mooie {self.user_model['kleur']} glijbaan gaat jou vandaag helpen.')
        self.droomrobot.say('Je loopt langzaam de trap op naar de top van de glijbaan')
        self.droomrobot.say('Merk maar dat je je bij iedere stap fijner en rustiger voelt.')
        self.droomrobot.say('Misschien voel je een beetje kriebels in je buik dat is helemaal oké!')
        self.droomrobot.say('Dat betekent dat je er klaar voor bent.')
        self.droomrobot.say('Bovenaan ga je zitten.')
        self.droomrobot.say('Je voelt het koele water om je heen.')
        self.droomrobot.say('Je plaatst je handen naast je.')
        self.droomrobot.say('Adem diep in', sleep_time=2)
        self.droomrobot.say('en klaar voor de start!')
        self.droomrobot.say('Ga maar rustig naar beneden met de glijbaan en merk maar hoe rustig en soepel dat gaat.')

        return interaction_choice
