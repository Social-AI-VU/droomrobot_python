from droomrobot.core import AnimationType, InteractionConf
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext, InteractionSession, InterventionPhase, \
    InteractionChoice, InteractionChoiceCondition
from droomrobot.introduction_factory import IntroductionFactory


class Sonde6(DroomrobotScript):

    def __init__(self, *args, **kwargs):
        super(Sonde6, self).__init__(*args, **kwargs, interaction_context=InteractionContext.BLOEDAFNAME)

    def prepare(self, participant_id: str, session: InteractionSession, user_model_addendum: dict,
                audio_amplified: bool = False, always_regenerate: bool = False):
        super().prepare(participant_id, session, user_model_addendum, audio_amplified, always_regenerate)

        if session == InteractionSession.INTRODUCTION:
            self._introduction()
        elif session == InteractionSession.INTERVENTION:
            self._intervention()
        elif session == InteractionSession.GOODBYE:
            self._goodbye()
        else:
            print("Interaction part not recognized")

    def _introduction(self):
        interaction_conf = InteractionConf(amplified=self.audio_amplified, always_regenerate=self.always_regenerate)
        self.add_move(self.droomrobot.set_interaction_conf, interaction_conf)
        intro_moves = IntroductionFactory.age6_9(droomrobot=self.droomrobot,
                                                 interaction_context=self.interaction_context,
                                                 user_model=self.user_model)
        self.add_moves(intro_moves)
        self.add_move(self.droomrobot.say, 'Wat goed helpt is om je voor te stellen dat je in een raceauto door een tunnel scheurt, of van een waterglijbaan gaat, of als dolfijn door het water beweegt.')
        self.add_move(self.droomrobot.say, 'Welke lijkt jij het leukste?')

        self.add_move(self.droomrobot.ask_entity, 'De waterglijbaan, de race-auto of dolfijn?',
                      {'droomplek': 1},
                      'droomplek',
                      'droomplek',
                      user_model_key='droomplek')
        self.add_move(self.droomrobot.get_article, lambda: self.user_model['droomplek'],
                      user_model_key='droomplek_lidwoord')

        self.add_choice(self._build_interaction_choice_droomplek())

        # SAMEN OEFENEN
        self.add_move(self.droomrobot.say, 'Oke, laten we samen gaan oefenen.')
        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False)
        self.add_move(self.droomrobot.set_interaction_conf, interaction_conf)

        self.add_choice(self._build_interaction_choice_comfortable_position())
        self.add_move(self.droomrobot.say,  'mag je je ogen dicht doen.')
        self.add_move(self.droomrobot.say,  'dat maakt het makkelijker om je rustig te voelen.')

        self.add_move(self.droomrobot.say, 'En terwijl je nu zo lekker zit, mag je je handen op je buik doen en rustig gaan ademhalen.')
        self.add_move(self.droomrobot.say, 'Adem rustig in.')
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        self.add_move(self.droomrobot.say, 'en rustig uit.')
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        self.add_move(self.droomrobot.say, 'En voel maar dat je buik iedere keer rustig omhoog en omlaag gaat als je zo lekker aan het ademhalen bent.')

        self.add_choice(self._build_interaction_choice_oefenen())
        self.add_move(self.droomrobot.reset_interaction_conf)

        self.add_move(self.droomrobot.say, 'En wat zo fijn is, is dat iedere keer als je het nodig hebt je weer terug kan gaan naar deze fijne plek.')
        self.add_move(self.droomrobot.say, 'Je hoeft alleen maar een paar keer diep in en uit te ademen.')
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed dit je zometeen gaat helpen.')
        self.add_move(self.droomrobot.say, 'Als je genoeg geoefend hebt, mag je je ogen weer lekker open doen.', sleep_time=1)
        self.add_move(self.droomrobot.say,  lambda: f'Ik vind {self.user_model['kleur']} een hele mooie kleur, die heb je goed gekozen.')

        self.add_move(self.droomrobot.say, lambda: f'Als je straks aan de beurt bent ga ik je vragen om in gedachten terug te gaan naar {self.user_model['droomplek_locatie']}.')
        self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)  ## Smile
        self.add_move(self.droomrobot.say, f'Tot straks, {self.user_model['child_name']}.')

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
        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False, amplified=self.audio_amplified, always_regenerate=self.always_regenerate)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.set_interaction_conf, interaction_conf)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Wat fijn dat ik je weer mag helpen, we gaan weer samen een droomreis maken.', animated=False)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Omdat je net al zo goed hebt geoefend zul je zien dat het nu nog beter en makkelijker gaat.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Je mag weer goed gaan zitten en je ogen dicht doen zodat deze droomreis nog beter voor jou werkt.', sleep_time=1)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Luister maar weer goed naar mijn stem en merk maar dat andere geluiden in het ziekenhuis veel stiller worden.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Ga maar rustig ademen zoals je dat gewend bent.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Adem rustig in.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'en rustig uit.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio, 'resources/audio/breath_out.wav')

        intervention_prep_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Raceauto
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, lambda: f'Stel je maar weer voor dat je op de racebaan staat met jouw {self.user_model['kleur']} raceauto!', sleep_time=3)
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'Je auto rijdt op een rechte weg.')
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'Je rijdt precies zo snel als jij fijn vindt en je hebt alles onder controle, waardoor je je sterk voelt.')
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'De auto heeft speciale zachte banden die over de speciale weg heen rijden.')
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'Kijk maar wat voor mooie kleur de speciale weg heeft.')
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'Je kunt je zelfs voorstellen dat de weg glitters heeft om je extra kracht te geven.')

        # Waterglijbaan
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'Stel je je maar weer voor dat je in het waterpretpark bent.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, lambda: f'Je gaat weer de trap op van jouw {self.user_model['kleur']} glijbaan, die je net al zo goed geoefend hebt.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'Bij iedere stap voel je weer dat je lichaam zich goed voelt en je er kracht van krijgt.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'Hoor het geluid van het water maar.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.play_audio, 'resources/audio/splashing_water.wav')

        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'Boven aan ga je weer zitten en adem je weer rustig in.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'En uit.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.play_audio, 'resources/audio/breath_out.wav')

        # Dolfijn
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, lambda: f'Stel je je maar weer voor dat je een {self.user_model['kleur']} dolfijn in de zee bent.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Kijk maar weer in gedachten om je heen wat je allemaal ziet.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'De visjes om je heen en de mooie kleuren.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Merk maar hoe soepel je je door het water heen beweegt, en hoe fijn je je voelt op die plek.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Als je goed kijkt zie je in de verte een oude schatkist op de oceaanbodem.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Dat is jouw missie van vandaag: je gaat ernaartoe zwemmen als een echte dolfijn.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Je beweegt je lichaam soepel, net als een dolfijn.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Eerst rustig.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'En dan iets sneller.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Je voelt hoe het water je zachtjes verder en lager brengt.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Elke keer dat je inademt, voel je de frisse zeelucht vullen met energie.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Als je uitademt, laat je alle spanning los.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Heel ontspannen, net als een dolfijn die rustig door het water glijdt.')

        phase_moves.add_choice(InterventionPhase.PREPARATION.name, intervention_prep_choice)
        return phase_moves

    def _intervention_procedure(self, phase_moves: InteractionChoice) -> InteractionChoice:
        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False, amplified=self.audio_amplified, always_regenerate=self.always_regenerate)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.set_interaction_conf, interaction_conf)

        intervention_proc_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Raceauto
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Voor je zie je een tunnel. Het is een speciale tunnel, precies groot genoeg voor jouw auto.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Je weet dat als je rustig blijft rijden, je er soepel doorheen komt.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'De tunnel heeft precies de juiste vorm, je hoeft alleen maar ontspannen door te blijven rijden.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'En in de tunnel zitten prachtige lichtjes en hele mooie kleuren.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Kijk maar eens wat voor mooie kleuren jij allemaal in de tunnel ziet.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'En jij blijft rustig doorrijden. Precies zo snel als jij fijn vindt, je hebt alles onder controle.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Misschien voelt het soms even gek of kriebelt het een beetje in de tunnel, net als wanneer je met je auto over een hobbel in de weg rijdt.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Maar jij weet: als je rustig blijft ademen en je blik op de weg houdt, kom je er zo doorheen.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Je auto glijdt soepel verder en verder.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'En steeds dieper de tunnel in. En jij blijft heerlijk in je auto zitten.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'En je stuurt de auto met de juiste snelheid, precies wat goed is voor jou. En voel maar dat jij dit heel goed kan.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'En de verpleegkundige zal je vertellen wanneer je bij het einde van de tunnel bent.')

        # Waterglijbaan
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je plaatst je handen naast, je ademt diep in, en klaar voor de start!')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Daar ga je! Je duwt jezelf zachtjes af, en voelt hoe je begint te glijden.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Eerst heel langzaam.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'En dan iets sneller.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Precies zoals jij dat fijn vindt!')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je voelt het water langs je glijden, net als een zachte golf, die je meevoert.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Misschien voel je dat je soms tegen de zijkant aan komt, dat is gewoon een bocht in de glijbaan! Heel normaal!')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Misschien heeft het water in je glijbaan wel een speciale kleur, en glitters, zodat het je extra kan helpen.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je blijft lekker glijden, met het water dat je moeiteloos omlaag laat gaan. Soms gaat het even iets sneller, dan weer iets rustiger.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Misschien voel je een klein raar kriebeltje, alsof een waterstraaltje even tegen je neus spat.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Maar dat is oké, want jij weet dat je bijna beneden bent.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je ademt rustig in en uit, net als de zachte golfjes om je heen.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je komt lager en lager.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'En nog een bocht.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'De verpleegkundige vertelt je wanneer je bij de laatste bocht bent.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je voelt jezelf soepel door de tunnel van de glijbaan glijden.')

        # Dolfijn
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'En terwijl je zwemt zie je een onderwatergrot.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Het is een geheime doorgang en de ingang is precies groot genoeg voor jou.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Je weet dat als je soepel en rustig zwemt, je er moeiteloos doorheen glijdt.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Je voelt misschien een zacht gevoel bij je neus of keel.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Dat is gewoon een klein zeewierplantje dat je even aanraakt en dat jou extra kracht geeft. Heel normaal!')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Jij blijft rustig zwemmen door de grot, met een bochtje en weer verder.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Soms voel je een klein golfje langs je neus, net als een dolfijn die door een stroomversnelling zwemt!')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'En je weet dat als je rustig blijft bewegen dat je er gemakkelijk doorheen gaat.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'De verpleegkundige vertelt je wanneer je bij de schat bent.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Je zwemt soepel verder.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Kijk maar of je al iets van de schat kunt zien!')
        phase_moves.add_choice(InterventionPhase.PROCEDURE.name, intervention_proc_choice)

        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, "Wat doe jij dit goed! Voel maar hoe sterk en rustig je bent.")

        sentences = [
            "Je bent precies op de juiste weg, blijf maar lekker doorgaan.",
            "Elke keer als je rustig in- en uitademt, voel je je nog fijner en sterker.",
            "Kijk eens hoeveel moois er is, misschien zie je nog iets bijzonders!",
            "Jij hebt alles onder controle, je lichaam weet precies wat het moet doen.",
            "Misschien voel je iets geks of kriebelt het een beetje, dat is helemaal normaal!",
            "Je mag zelf kiezen hoe snel of langzaam je gaat, precies zoals jij fijn vindt.",
            "Wist je dat je gedachten je kunnen helpen? Stel je maar voor dat je nog lichter en sterker wordt."
        ]
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.repeat_sentences, sentences)

        return phase_moves

    def _intervention_wrapup(self, phase_moves: InteractionChoice) -> InteractionChoice:
        interaction_conf = InteractionConf(amplified=self.audio_amplified, always_regenerate=self.always_regenerate)
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.set_interaction_conf, interaction_conf)
        intervention_wrapup_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Raceauto
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Wow! Jij bent door de tunnel gereden als een echte coureur!')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'De finishvlag wappert voor je en het publiek juicht.')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Wat een geweldige race!')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Je hebt dit zo goed gedaan.')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Je auto staat nu stil op de eindstreep en je mag lekker even ontspannen.')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Misschien voel je nog een klein beetje de weg onder je trillen, maar dat is oké.')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Je hebt alles onder controle en je bent een echte racekampioen!')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Nu mag je je ogen weer open doen.')

        # Waterglijbaan
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.play_audio, 'resources/audio/splash.wav')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Daar plons je in het zwembad, precies zoals je wilde!')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je voelt je licht en ontspannen. Wat een gave rit!')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Het lekkere water heeft je geholpen, en het is je gelukt.')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'En weet je wat? Jij bent echt een supergoede glijbaan-avonturier!')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je hebt laten zien dat je rustig kunt blijven, en dat je overal soepel doorheen kunt glijden.')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je mag jezelf een high vijf geven want jij bent een echte waterkampioen! En doe je ogen maar weer open.')

        # Dolfijn
        intervention_wrapup_choice.add_move('dolfijn', self.droomrobot.say, 'Je bent bij de uitgang van de grot en ja hoor, je ziet de schat!')
        intervention_wrapup_choice.add_move('dolfijn', self.droomrobot.say, 'De kist ligt op de bodem, glinsterend tussen het koraal.')
        intervention_wrapup_choice.add_move('dolfijn', self.droomrobot.say, 'Je strekt je vinnen uit en je hebt hem. Het zit vol met gouden munten en juwelen.')
        intervention_wrapup_choice.add_move('dolfijn', self.droomrobot.say, 'Je hebt het geweldig gedaan! Je hebt laten zien hoe rustig en sterk je bent, als een echte dolfijn.')
        intervention_wrapup_choice.add_move('dolfijn', self.droomrobot.say, 'Zwem maar weer rustig omhoog en open je ogen zodat je weer hier in de ruimte bent.')

        phase_moves.add_choice(InterventionPhase.WRAPUP.name, intervention_wrapup_choice)
        return phase_moves

    def _goodbye(self):
        interaction_conf = InteractionConf(amplified=self.audio_amplified, always_regenerate=self.always_regenerate)
        self.add_move(self.droomrobot.set_interaction_conf, interaction_conf)
        self.add_move(self.droomrobot.say, 'En weet je wat nu zo fijn is, hoe vaker je deze droomreis oefent, hoe makkelijker het wordt.')
        self.add_move(self.droomrobot.say, 'Je kunt dit ook zonder mij oefenen.')
        self.add_move(self.droomrobot.say, 'Je hoeft alleen maar je ogen dicht te doen en terug te denken aan jouw plek in gedachten.')
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed je het de volgende keer gaat doen. Je doet het op jouw eigen manier, en dat is precies goed.')
        self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        self.add_move(self.droomrobot.say, f'Doei, {self.user_model['child_name']}.', animated=False)

    def _build_interaction_choice_droomplek(self) -> InteractionChoice:
        interaction_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Raceauto
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'De raceauto, die vind ik ook het leukste!')
        interaction_choice.add_move('raceauto', self.droomrobot.say,
                                    'Ik vind het fijn dat je zelf kan kiezen hoe snel of rustig je gaat rijden.')
        interaction_choice.add_move('raceauto', self.droomrobot.ask_open,
                                    'Rijd jij graag snel of liever langzaam?',
                                    user_model_key='droomplek_motivatie')
        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Rijd jij graag snel of liever langzaam?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
        interaction_choice.add_choice('raceauto', motivation_choice)
        interaction_choice.add_move('raceauto', self.set_user_model_variable, 'droomplek_locatie', 'de racebaan')

        interaction_choice.add_move('raceauto', self.droomrobot.say,
                                    'Wat mij altijd goed helpt is om in gedachten te denken dat de sonde door een waterglijbaan gaat, lekker snel en makkelijk.')

        # Waterglijbaan
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Wat leuk, de waterglijbaan!')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say,
                                    'Gelukkig kan ik tegen water zodat ik met je mee kan gaan.')
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
        interaction_choice.add_move('waterglijbaan', self.set_user_model_variable, 'droomplek_locatie',
                                    'het waterpretpark')

        interaction_choice.add_move('waterglijbaan', self.droomrobot.say,
                                    'Wat mij altijd goed helpt is om in gedachten te denken dat de sonde door een waterglijbaan gaat, lekker snel en makkelijk.')

        # Dolfijn
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Dat vind ik dol fijn.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say,
                                    'Ik vind het altijd heerlijk om door het water te zwemmen op zoek naar schatten onder water.')

        interaction_choice.add_move('dolfijn', self.droomrobot.ask_open,
                                    'Zwem jij graag snel of rustig?',
                                    user_model_key='droomplek_motivatie')
        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Zwem jij graag snel of rustig?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
        interaction_choice.add_choice('dolfijn', motivation_choice)
        interaction_choice.add_move('dolfijn', self.set_user_model_variable, 'droomplek_locatie', 'de zee')

        interaction_choice.add_move('dolfi', self.droomrobot.say,
                                    'Wat mij altijd goed helpt is om in gedachten te denken dat de sonde een dolfijn is die heel makkelijk en snel door het water beweegt, op zoek naar een schat.')

        # Fail
        interaction_choice.add_move('fail', self.droomrobot.say, 'Sorry dat verstond ik even niet.')
        interaction_choice.add_move('fail', self.droomrobot.say, 'Weet je wat leuk is. De waterglijbaan.')
        interaction_choice.add_move('fail', self.droomrobot.say, 'Lekker spetteren in het water.')

        interaction_choice.add_move('fail', self.droomrobot.ask_open,
                                    'Glij jij liever snel of langzaam naar beneden?',
                                    user_model_key='droomplek_motivatie')
        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Glij jij liever snel of langzaam naar beneden?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
        interaction_choice.add_choice('fail', motivation_choice)
        interaction_choice.add_move('fail', self.droomrobot.say,
                                    'Wat mij helpt, is denken dat de sonde net als een waterglijbaan is: hij glijdt zo naar beneden, makkelijk en snel!')
        interaction_choice.add_move('fail', self.set_user_model_variable, 'droomplek_locatie', 'het waterpretpark')
        interaction_choice.add_move('fail', self.set_user_model_variable, 'droomplek', 'waterglijbaan')
        interaction_choice.add_move('fail', self.droomrobot.get_article, lambda: self.user_model['droomplek'],
                                    user_model_key='droomplek_lidwoord')

        return interaction_choice

    def _build_interaction_choice_oefenen(self) -> InteractionChoice:
        interaction_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)
        
        # Raceauto
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'En terwijl je zo rustig aan het ademhalen bent mag je je gaan voorstellen dat je op een plek met een racebaan bent.')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'En op die plek staat een mooie raceauto, speciaal voor jou!')
        interaction_choice.add_move('raceauto', self.droomrobot.ask_entity_llm, 'Kijk maar goed, welke kleur heeft jouw raceauto?', strict=True, user_model_key='kleur')
        interaction_choice.add_move('raceauto', self.droomrobot.get_adjective, lambda: self.user_model['kleur'], user_model_key='kleur_adjective')
        interaction_choice.add_move('raceauto', self.droomrobot.say, lambda: f"Wat goed, die mooie {self.user_model['kleur_adjective']} raceauto gaat jou vandaag helpen.")
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Ga maar in de raceauto zitten, en voel maar hoe fijn je je daar voelt.', sleep_time=1)
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'De motor ronkt.')
        interaction_choice.add_move('raceauto', self.droomrobot.play_audio, 'resources/audio/vroomvroom.wav')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Je voelt het stuur in je handen. Je zit vast met een stevige gordel, helemaal klaar voor de start.')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Ga maar lekker een rondje rijden in je speciale auto en voel maar hoe makkelijk dat gaat.')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Jij hebt alles onder controle.')

        # Waterglijbaan
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'En terwijl je zo rustig aan het ademhalen bent mag je je gaan voorstellen dat je in een waterpretpark bent.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Het is een lekker warme dag en je voelt de zon op je gezicht.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Om je heen hoor je het spetterende water en vrolijke stemmen.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'En voor je zie je de grootste, gaafste waterglijbanen die je ooit hebt gezien!')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Kijk maar eens in gedachten om je heen, welke glijbanen je allemaal ziet, en welke kleuren de glijbanen hebben.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.ask_entity_llm, 'Welke kleur heeft de glijbaan waar jij vanaf wilt gaan?', strict=True, user_model_key='kleur')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.get_adjective, lambda: self.user_model['kleur'], user_model_key='kleur_adjective')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, lambda: f'Wat goed! Die mooie {self.user_model['kleur_adjective']} glijbaan gaat jou vandaag helpen.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je loopt langzaam de trap op naar de top van de glijbaan')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Merk maar dat je je bij iedere stap fijner en rustiger voelt.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Misschien voel je een beetje kriebels in je buik dat is helemaal oké!')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Dat betekent dat je er klaar voor bent.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Bovenaan ga je zitten.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je voelt het koele water om je heen.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je plaatst je handen naast je.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Adem diep in', sleep_time=2)
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'en klaar voor de start!')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Ga maar rustig naar beneden met de glijbaan en merk maar hoe rustig en soepel dat gaat.')

        # Dolfijn
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'En terwijl je zo rustig aan het ademhalen bent, mag je je gaan voorstellen dat je een dolfijn bent die aan het zwemmen is.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Je bent in een mooie, blauwe zee.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Kijk maar eens in gedachten om je heen wat je allemaal kan zien.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Welke kleuren er allemaal zijn en hoe het er voelt.', sleep_time=2)
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Misschien is het water warm en zacht, of fris en koel.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Je voelt hoe je licht wordt, alsof je zweeft.')
        interaction_choice.add_move('dolfijn', self.droomrobot.ask_entity_llm, 'Welke kleur dolfijn ben jij?', strict=True, user_model_key='kleur')
        interaction_choice.add_move('dolfijn', self.droomrobot.get_adjective, lambda: self.user_model['kleur'], user_model_key='kleur_adjective')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, lambda: f'Wauw, een {self.user_model['kleur_adjective']} dolfijn! Die zijn extra krachtig.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Je zult wellicht zien, dat als je om je heen kijkt, dat je dan de zonnestralen door het water ziet schijnen.', sleep_time=1)
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Er zwemmen vrolijke vissen om je heen.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Ga maar lekker op avontuur in die onderwaterwereld en kijk wat je allemaal kan vinden.', sleep_time=2)

        return interaction_choice

    def _build_interaction_choice_comfortable_position(self) -> InteractionChoice:
        position_choice = InteractionChoice('positie', InteractionChoiceCondition.MATCHVALUE)

        # Zittend
        position_choice.add_move('zittend', self.droomrobot.say, 'Ga even lekker zitten zoals jij dat fijn vindt.', sleep_time=1)
        position_choice.add_move('zittend', self.droomrobot.ask_yesno, "Zit je zo goed?", user_model_key='zit_goed')

        zit_goed_choice = InteractionChoice('zit_goed', InteractionChoiceCondition.MATCHVALUE)
        zit_goed_choice.add_move('yes', self.droomrobot.say, 'En nu je lekker bent gaan zitten.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say,
                                 'Het zit vaak het lekkerste als je stevig gaat zitten.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Ga maar eens kijken hoe goed dat zit.',
                                 sleep_time=1)
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Als je goed zit.')
        position_choice.add_choice('zittend', zit_goed_choice)

        # Liggend
        position_choice.add_move('liggend', self.droomrobot.say, 'Ga even lekker liggen zoals jij dat fijn vindt.', sleep_time=1)
        position_choice.add_move('liggend', self.droomrobot.ask_yesno, "Lig je zo goed?", user_model_key='zit_goed')

        zit_goed_choice = InteractionChoice('zit_goed', InteractionChoiceCondition.MATCHVALUE)
        zit_goed_choice.add_move('yes', self.droomrobot.say, 'En nu je lekker bent gaan liggen.')
        # should still be another sentence for fail/other
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Als je goed ligt.')
        position_choice.add_choice('liggend', zit_goed_choice)

        # NVT
        position_choice.add_move('other', self.droomrobot.say, 'Als je er klaar voor bent')

        return position_choice
