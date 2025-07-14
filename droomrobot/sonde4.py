
from core import AnimationType, InteractionConf
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext, InteractionSession, InteractionChoice, \
    InteractionChoiceCondition, InterventionPhase


class Sonde4(DroomrobotScript):
    def __init__(self, *args, **kwargs):
        super(Sonde4, self).__init__(*args, **kwargs, interaction_context=InteractionContext.BLOEDAFNAME)

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
        self.add_move(self.droomrobot.animate, AnimationType.ACTION, "009")
        self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand up
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        # INTRODUCTIE
        self.add_move(self.droomrobot.say, f'Hallo, ik ben de droomrobot!', animate=False)
        self.add_move(self.droomrobot.say, 'Wat fijn dat ik je mag helpen vandaag.')
        self.add_move(self.droomrobot.ask_fake, 'Hoe heet jij?', 3)
        self.add_move(self.droomrobot.say, lambda: f'{self.user_model['child_name']}, wat leuk je te ontmoeten.')
        self.add_move(self.droomrobot.ask_fake, 'En hoe oud ben je?', 3)
        self.add_move(self.droomrobot.say, lambda: f'{str(self.user_model['child_age'])} jaar. Oh wat goed, dan ben je al oud genoeg om mijn speciale trucje te leren.')
        self.add_move(self.droomrobot.say, 'Het is een truukje dat kinderen helpt om zich fijn en sterk te voelen in het ziekenhuis.')
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed het bij jou gaat werken.')
        self.add_move(self.droomrobot.say, 'We gaan samen iets leuks bedenken dat jou gaat helpen.')
        self.add_move(self.droomrobot.say, 'Nu ga ik je wat meer vertellen over het trucje wat ik kan.')
        self.add_move(self.droomrobot.say, 'Let maar goed op, ik ga je iets bijzonders leren.')
        self.add_move(self.droomrobot.say, 'Ik kan jou meenemen op een droomreis!')
        self.add_move(self.droomrobot.say, 'Een droomreis is een trucje waarbij je aan iets heel leuks denkt.')
        self.add_move(self.droomrobot.say, 'Dat helpt je om rustig en sterk te blijven.')
        self.add_move(self.droomrobot.say, 'Ik ga je laten zien hoe het werkt.')
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
        self.add_move(self.droomrobot.say, 'Ga even lekker zitten zoals jij dat fijn vindt.', sleep_time=1)
        self.add_move(self.droomrobot.ask_yesno, "Zit je zo goed?", user_model_key='zit_goed')
        zit_goed_choice = InteractionChoice('zit_goed', InteractionChoiceCondition.MATCHVALUE)
        zit_goed_choice.add_move('yes', self.droomrobot.say, 'En nu je lekker bent gaan zitten.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say,
                                 'Het zit vaak het lekkerste als je stevig gaat zitten.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'met beide benen op de grond.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Ga maar eens kijken hoe goed dat zit.',
                                 sleep_time=1)
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Als je goed zit.')
        self.add_choice(zit_goed_choice)

        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False)
        self.add_move(self.droomrobot.set_interaction_conf, interaction_conf)

        self.add_move(self.droomrobot.say, 'Leg je nu je handen op je buik en adem rustig in.')
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        self.add_move(self.droomrobot.say, 'En adem rustig uit.')
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        self.add_move(self.droomrobot.say, 'Voel maar hoe je buik rustig op en neer beweegt.')

        self.add_choice(self._build_interaction_choice_oefenen())

        self.add_move(self.droomrobot.reset_interaction_conf)

        self.add_move(self.droomrobot.say, 'En weet je wat fijn is? Als je dit rustige gevoel later weer nodig hebt, kun je er altijd naar terug.')
        self.add_move(self.droomrobot.say, 'Je hoeft alleen maar rustig diep in en uit te ademen, en daar ben je weer.')
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed het je zometeen gaat helpen.')
        self.add_move(self.droomrobot.say, 'Als je klaar bent met oefenen, mag je je ogen weer open doen.')
        self.add_move(self.droomrobot.say, lambda: f'Ik vind {self.user_model['kleur']} een hele mooie kleur, die heb je goed gekozen.')

        self.add_move(self.droomrobot.say, lambda: f'Als je straks aan de beurt bent ga ik je vragen om in gedachten terug te gaan naar {self.user_model['droomplek_locatie']}.')

    def _intervention(self):
        self.phases = [
            InterventionPhase.PREPARATION.name,
            InterventionPhase.PROCEDURE.name,
            InterventionPhase.WRAPUP.name
        ]
        self.phase_moves_build = InteractionChoice('Sonde4', InteractionChoiceCondition.PHASE)
        self.phase_moves_build = self._intervention_preparation(self.phase_moves_build)
        self.phase_moves_build = self._intervention_procedure(self.phase_moves_build)
        self.phase_moves = self._intervention_wrapup(self.phase_moves_build)

    def _intervention_preparation(self, phase_moves: InteractionChoice) -> InteractionChoice:
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Wat fijn dat ik je mag helpen! We gaan samen weer op een mooie droomreis.', animated=False)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Omdat je net al zo goed hebt geoefend, zal het nu nog makkelijker gaan.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Ga maar lekker zitten zoals jij dat fijn vindt.', sleep_time=1)
        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.set_interaction_conf, interaction_conf)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,  'Sluit je ogen maar, dan werkt de droomreis het allerbeste.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Luister goed naar mijn stem. Alle andere geluiden in het ziekenhuis worden steeds zachter..')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,  'Leg je handen op je buik en adem rustig in.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'en weer rustig uit.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        intervention_prep_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Raceauto
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, lambda: f'Stel je voor, je staat op de racebaan met jouw mooie {self.user_model['kleur_adjective']} raceauto!', sleep_time=3)
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'Je auto rijdt op een rechte weg.')
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'Je mag zelf kiezen hoe snel of rustig je rijdt, precies zoals jij dat fijn vindt.')
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'Jij weet precies hoe jij wilt rijden, waardoor je je sterk voelt.')
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'De wielen van de auto zijn lekker zacht, en rollen makkelijk over de weg.')
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'Kijk eens, welke kleur heeft jouw speciale racebaan?')
        intervention_prep_choice.add_move('raceauto', self.droomrobot.say, 'Misschien zitten er glitters op de weg, die jou extra sterk maken.')

        # Waterglijbaan
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'Stel je voor, je bent weer in het waterpretpark.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, lambda: f'Je loopt langzaam de trap op van jouw {self.user_model['kleur_adjective']} glijbaan, net als daarnet.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je hebt dit al goed geoefend, waardoor het makkelijker gaat.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'Bij elke stap voel je hoe sterk en fijn je je voelt.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'Luister maar naar het spetterende water om je heen!')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.play_audio, 'resources/audio/splashing_water.wav')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'Boven aan ga je lekker zitten. Je ademt rustig in.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.say, 'En rustig uit.')
        intervention_prep_choice.add_move('waterglijbaan', self.droomrobot.play_audio, 'resources/audio/breath_out.wav')

        # Dolfijn
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, lambda: f'Stel je je maar weer voor dat je een {self.user_model['kleur_adjective']} dolfijn in de zee bent.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Kijk maar eens goed om je heen.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Je ziet vrolijke visjes om je heen zwemmen, en overal zijn prachtige kleuren!')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Voel maar hoe je soepel door het water glijdt, net als een echte dolfijn!')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Het voelt heel fijn en rustig hier in de zee.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Kijk daar, in de verte! Op de bodem van de oceaan ligt een oude schatkist!')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Dat is jouw missie vandaag: je mag ernaartoe zwemmen!')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Je beweegt je lichaam net als een echte dolfijn.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Eerst heel rustig.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'En dan iets sneller.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Het zachte water helpt je naar beneden.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Adem maar rustig in, en voel hoe de frisse zeelucht je energie geeft.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'En als je uitademt, laat je alle spanningen los.')
        intervention_prep_choice.add_move('dolfijn', self.droomrobot.say, 'Heel ontspannen, net als een dolfijn, die rustig zwemt.')
        phase_moves.add_choice(InterventionPhase.PREPARATION.name, intervention_prep_choice)

        return phase_moves

    def _intervention_procedure(self, phase_moves: InteractionChoice) -> InteractionChoice:
        intervention_proc_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)
        # Raceauto
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'En daar, voor je, een tunnel! Een hele speciale tunnel, precies groot genoeg voor jouw auto.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Je rijdt er rustig naartoe, en als je rustig blijft rijden, dan ga je er soepel doorheen.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'De tunnel is precies groot genoeg.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'De tunnel is mooi en kleurrijk, met lichtjes, die zachtjes schijnen.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Kijk maar eens welke mooie kleuren jij allemaal in de tunnel ziet.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Je blijft lekker doorrijden, zo snel als jij fijn vindt.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Misschien voelt het even gek of een beetje kriebelig, net als over een hobbeltje rijden.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Maar jij weet: als je rustig blijft ademen, rijd je er heel makkelijk doorheen.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Je auto glijdt soepel verder en verder.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'Merk maar hoe veilig jij je in je eigen auto voelt.')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'En jij blijft heerlijk zitten in je auto, je hebt alles onder controle!')
        intervention_proc_choice.add_move('raceauto', self.droomrobot.say, 'De verpleegkundige vertelt je wanneer je bij het einde van de tunnel bent.')

        # Waterglijbaan
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je zet je handen weer naast je neer. Dan zet je je zachtjes af, en daar ga je!')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Voel hoe je rustig begint te glijden.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Eerst heel langzaam.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Dan een beetje sneller.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Precies zoals jij dat fijn vindt!')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Het zachte water glijdt langs je heen, net als een zachte golf die je meeneemt.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Soms voel je dat je even tegen de zijkant aankomt, dat is gewoon een bocht in de glijbaan! Heel normaal!')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Misschien heeft het water wel glitters, of een speciale kleur, om jou extra kan helpen.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je blijft lekker glijden, soms wat sneller, soms wat rustiger. Het gaat helemaal vanzelf.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Misschien voel je even een klein kriebeltje, alsof een waterstraaltje tegen je neus spat.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je ademt rustig in en uit, net als de zachte golfjes om je heen.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je komt lager en lager.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Nog een bocht, en nog één.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'De verpleegkundige vertelt je wanneer je bij de laatste bocht bent.')
        intervention_proc_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je glijdt soepel verder, en je kan dit heel goed!')

        # Dolfijn
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Ooh, kijk! Daar is een onderwatergrot, een geheime doorgang!')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'De ingang is precies groot genoeg voor jou.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Je zwemt heel soepel naar binnen.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Misschien voel je een zacht kriebeltje bij je neus of keel.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Dat is gewoon een klein zeewierplantje dat je extra kracht geeft. Heel normaal!')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Jij blijft lekker zwemmen. Een bochtje hier, een bochtje daar.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Misschien voel je een klein golfje langs je neus, net als een dolfijn, die door een stroomversnelling zwemt!')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Maar jij weet: als je rustig blijft bewegen, zwem je er moeiteloos doorheen!')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'De verpleegkundige vertelt je wanneer je bij de schat bent.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Je zwemt soepel verder.')
        intervention_proc_choice.add_move('dolfijn', self.droomrobot.say, 'Kijk maar of je al iets van de schat kunt zien!')

        sentences = [
            "Wat doe jij dit goed! Voel maar hoe sterk en rustig je bent.",
            "Je bent precies op de juiste weg, blijf maar lekker doorgaan.",
            "Elke keer als je rustig in- en uitademt, voel je je nog fijner en sterker.",
            "Kijk eens hoeveel moois er om je heen is, misschien zie je nog iets bijzonders!",
            "Jij hebt alles onder controle, je lichaam weet precies wat het moet doen.",
            "Misschien voel je iets geks of kriebelt het een beetje, dat is helemaal normaal!",
            "Je mag zelf kiezen hoe snel of langzaam je gaat, precies zoals jij fijn vindt.",
            "Wist je dat je gedachten je kunnen helpen? Stel je maar voor dat je nog lichter en sterker wordt."
        ]
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.repeat_sentences, sentences)
        phase_moves.add_choice(InterventionPhase.PROCEDURE.name, intervention_proc_choice)
        return phase_moves

    def _intervention_wrapup(self, phase_moves: InteractionChoice) -> InteractionChoice:
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.reset_interaction_conf)
        intervention_wrapup_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)
        # Raceauto
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Wow! Jij bent als een supersnelle coureur door de tunnel gereden!')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Kijk eens, daar is de finishvlag, hij wappert speciaal voor jou!')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Hoor je het publiek juichen?')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Ze klappen voor jou, omdat je het zo goed hebt gedaan!')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Je auto is nu veilig gestopt op de finishlijn.')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Pfoe, wat een gave race.')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Misschien voel je nog een klein beetje het trillen van de weg, maar dat is helemaal oké.')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Jij bent een echte racekampioen!')
        intervention_wrapup_choice.add_move('raceauto', self.droomrobot.say, 'Nu mag je je ogen weer open doen.')

        # Waterglijbaan
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.play_audio, 'resources/audio/splash.wav')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Daar plons je in het zwembad, precies zoals je wilde!')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Wat een supercoole rit was dat!')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Jij bent helemaal beneden gekomen, goed gedaan!')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Het zachte water heeft je geholpen, en jij hebt het helemaal zelf gedaan.')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'En weet je wat? Jij bent echt een supergoede glijbaan-avonturier!')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je hebt laten zien hoe knap jij bent, en hoe goed je overal doorheen kunt glijden.')
        intervention_wrapup_choice.add_move('waterglijbaan', self.droomrobot.say, 'Geef jezelf maar een high five, en doe je ogen maar weer open.')

        # Dolfijn
        intervention_wrapup_choice.add_move('dolfijn', self.droomrobot.say, 'Kijk eens! Je bent bij het einde van de grot en ja hoor, daar is de schat!')
        intervention_wrapup_choice.add_move('dolfijn', self.droomrobot.say, 'De kist ligt op de bodem, verstopt tussen de mooie onderwaterplantjes.')
        intervention_wrapup_choice.add_move('dolfijn', self.droomrobot.say, 'Wow, er zitten allemaal gouden munten en glisterende juwelen in!')
        intervention_wrapup_choice.add_move('dolfijn', self.droomrobot.say, 'Wat heb jij dit supergoed gedaan! Jij bent net een echte slimme en sterke dolfijn!')
        intervention_wrapup_choice.add_move('dolfijn', self.droomrobot.say, 'Zwem maar rustig omhoog en als je klaar bent, mag je je ogen weer open doen.')

        phase_moves.add_choice(InterventionPhase.WRAPUP.name, intervention_wrapup_choice)
        return phase_moves

    def _goodbye(self):
        self.add_move(self.droomrobot.say, 'Wat heb je jezelf goed geholpen om alles makkelijker te maken.')
        self.add_move(self.droomrobot.say, 'En weet je wat nu zo fijn is, hoe vaker je deze droomreis oefent, hoe makkelijker het wordt.')
        self.add_move(self.droomrobot.say, 'Je kunt dit ook zonder mij oefenen.')
        self.add_move(self.droomrobot.say, 'Je hoeft alleen maar je ogen dicht te doen en terug te denken aan jouw plek in gedachten.')
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed je het de volgende keer gaat doen. Je doet het op jouw eigen manier, en dat is precies goed.')

    def _build_interaction_choice_droomplek(self) -> InteractionChoice:
        interaction_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Raceauto
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Een raceauto, die is stoer!')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Ik vind het fijn dat je zelf kan kiezen hoe snel of rustig je gaat rijden.')

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
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Weet je wat mij helpt? Ik stem me voor dat de sonde een raceauto is die snel en soepel door een tunnel rijdt!')
        interaction_choice.add_move('raceauto', self.set_user_model_variable, 'droomplek_locatie', 'de racebaan')


        # Waterglijbaan
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
        interaction_choice.add_move('waterglijbaan', self.set_user_model_variable, 'droomplek_locatie', 'het waterpretpark')

        # Dolfijn
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Een dolfijn, die vind ik zo leuk!')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Ze zwemmen snel en zoeken naar schatten onder water.')

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
        interaction_choice.add_move('dolfijn', self.droomrobot.say,
                                    'Ik stel me voor dat de sonde een dolfijn is die makkelijk door het water zwemt, op zoek naar een schat!')
        interaction_choice.add_move('dolfijn', self.set_user_model_variable, 'droomplek_locatie', 'de zee')

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
        interaction_choice.add_move('raceauto', self.droomrobot.say,'Terwijl je zo rustig ademt, stel je je voor dat je op een racebaan bent.')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'En op die plek staat een mooie raceauto, speciaal voor jou!')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Daar staat een supermooie raceauto, helemaal voor jou!', sleep_time=1)
        interaction_choice.add_move('raceauto', self.droomrobot.ask_entity_llm, 'Kijk maar goed, welke kleur heeft jouw raceauto?', strict=True, user_model_key='kleur')
        interaction_choice.add_move('raceauto', self.droomrobot.get_adjective, lambda: self.user_model['kleur'], user_model_key='kleur_adjective')
        interaction_choice.add_move('raceauto', self.droomrobot.say, lambda: f"Wat goed, die mooie {self.user_model['kleur_adjective']} raceauto gaat jou vandaag helpen.")
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Stap maar in, en voel hoe fijn het is.', sleep_time=1)
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Luister maar naar de motor, die maakt een stoer geluid.')
        interaction_choice.add_move('raceauto', self.droomrobot.play_audio, 'resources/audio/vroomvroom.wav')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Voel het stuur in je handen. De gordel zit stevig om je heen.')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'En nu mag je gaan rijden in je speciale auto, en voel maar hoe makkelijk dat gaat.')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Je raceauto gaat makkelijk en snel over de baan.')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Jij stuurt precies zoals jij wilt.')
        interaction_choice.add_move('raceauto', self.droomrobot.say, 'Jij hebt alles onder controle.')

        # Waterglijbaan
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Terwijl je rustig ademt, stel je voor dat je in een waterpretpark bent.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Het is een lekkere warme dag en je voelt de zon op je gezicht.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Om je heen hoor je het water spetteren en kinderen lachen.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'En kijk eens voor je, daar staan de allergaafste waterglijbanen die je ooit hebt gezien!')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Er zijn allemaal verschillende, en ze hebben mooie kleuren.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.ask_entity_llm, 'Welke kleur heeft de glijbaan waar jij vanaf wilt gaan?', strict=True, user_model_key='kleur')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.get_adjective, lambda: self.user_model['kleur'], user_model_key='kleur_adjective')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, lambda: f'Wat goed! Die mooie {self.user_model['kleur_adjective']} glijbaan gaat jou vandaag helpen.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Je loopt de trap op, stap voor stap, steeds hoger.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Voel maar hoe fijn en rustig je je bij elke stap voelt.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Misschien voel je een beetje kriebels in je buik, dat is helemaal oké!')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Dat betekent dat je er klaar voor bent.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Bovenaan ga je zitten.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Voel het koele water om je heen.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Zet je handen naast je neer.')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Adem diep in', sleep_time=2)
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'en klaar voor de start!')
        interaction_choice.add_move('waterglijbaan', self.droomrobot.say, 'Glij maar rustig naar beneden, en voel hoe makkelijk en fijn dat gaat.')

        # Dolfijn
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Terwijl je rustig ademt, stel je voor dat je een dolfijn bent die lekker aan het zwemmen is.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Je zwemt in een mooie, blauwe zee.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Kijk maar eens om je heen wat je allemaal ziet.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Welke kleuren zie je in het water?', sleep_time=2)
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Voelt het water warm en zacht, of juist een beetje fris en koel.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Je voelt je licht, alsof je zweeft in het water.')
        interaction_choice.add_move('dolfijn', self.droomrobot.ask_entity_llm,
                                    'Welke kleur dolfijn ben jij?', strict=True, user_model_key='kleur')
        interaction_choice.add_move('dolfijn', self.droomrobot.get_adjective,
                                    lambda: self.user_model['kleur'], user_model_key='kleur_adjective')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, lambda: f'Wauw, een {self.user_model['kleur_adjective']} dolfijn! Die zijn extra krachtig.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Kijk maar eens goed, je ziet misschien zonnestralen door het water schijnen.', sleep_time=1)
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Om je heen zwemmen vrolijke visjes.')
        interaction_choice.add_move('dolfijn', self.droomrobot.say, 'Ga maar lekker op avontuur en ontdek wat er allemaal te zien is in de zee.', sleep_time=2)

        return interaction_choice
