from droomrobot.core import AnimationType, InteractionConf
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext, InteractionSession, InteractionChoice, \
    InteractionChoiceCondition, InterventionPhase
from droomrobot.introduction_factory import IntroductionFactory


class Kapinductie4(DroomrobotScript):
    def __init__(self, *args, **kwargs):
        super(Kapinductie4, self).__init__(*args, **kwargs, interaction_context=InteractionContext.KAPINDUCTIE)

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
        intro_moves = IntroductionFactory.age4(droomrobot=self.droomrobot, interaction_context=self.interaction_context, user_model=self.user_model)
        self.add_moves(intro_moves)

        self.add_move(self.droomrobot.say, 'Je kunt kiezen uit het strand, het bos, of de ruimte.')
        self.add_move(self.droomrobot.ask_entity,
                      'Wat is de plek waar jij je fijn voelt?',
                      {'droomplek': 1},
                      'droomplek',
                      'droomplek',
                      user_model_key='droomplek')
        self.add_move(self.droomrobot.get_article, lambda: self.user_model['droomplek'],
                      user_model_key='droomplek_lidwoord')
        self.add_choice(self._build_interaction_choice_droomplek())
        
        # SAMEN OEFENEN
        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False, amplified=self.audio_amplified, always_regenerate=self.always_regenerate)
        self.add_move(self.droomrobot.set_interaction_conf, interaction_conf)

        self.add_move(self.droomrobot.say, 'Oke, laten we samen gaan oefenen met het maken van de droomreis.')

        self.add_choice(self._build_interaction_choice_comfortable_position())
        self.add_move(self.droomrobot.say, 'mag je je ogen dicht doen.')
        self.add_move(self.droomrobot.say, 'dan werkt het truukje het beste.')
        self.add_move(self.droomrobot.say, 'leg nu je handen op je buik.', sleep_time=1)

        self.add_move(self.droomrobot.say, 'Adem rustig in.', )
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        self.add_move(self.droomrobot.say, 'en rustig uit.')
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        self.add_move(self.droomrobot.say, 'En voel maar dat je buik rustig op en neer beweegt.')

        self.add_choice(self._build_interaction_choice_oefenen())
        self.add_move(self.droomrobot.reset_interaction_conf)

        self.add_move(self.droomrobot.say, 'als je klaar bent, mag je je ogen weer open doen.')
        self.add_move(self.droomrobot.say, 'Weet je wat zo fijn is? Je kunt altijd teruggaan naar deze mooie plekken in je hoofd.')
        self.add_move(self.droomrobot.say, 'Je hoeft alleen maar rustig in en uit te ademen.')
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed dit je zometeen gaat helpen.')
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        self.add_move(self.droomrobot.say, lambda: f'Straks ga ik je helpen om weer terug te gaan naar {self.user_model['droomplek_lidwoord']} {self.user_model['droomplek']} te gaan in gedachten. Je hebt super goed geoefend, dus je kan verrast zijn hoe goed het zometeen gaat!')
        # self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True)
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        self.add_move(self.droomrobot.say, lambda: f'Ik rij zo gewoon met je mee {self.user_model['child_name']}.')

    def _intervention(self):
        self.phases = [
            InterventionPhase.PREPARATION.name,
            # InterventionPhase.PROCEDURE.name
        ]
        self.phase_moves_build = InteractionChoice('Kapinductie4', InteractionChoiceCondition.PHASE)
        self.phase_moves_build = self._intervention_preparation(self.phase_moves_build)
        self.phase_moves = self._intervention_procedure(self.phase_moves_build)

    def _goodbye(self):
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

    def _build_interaction_choice_droomplek(self) -> InteractionChoice:
        interaction_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Strand
        interaction_choice.add_move('strand', self.droomrobot.say,
                                    'Wat is het fijn op het strand, Ik voel het warme zand en hoor de golven zachtjes ruisen.')
        interaction_choice.add_move('strand', self.droomrobot.say,
                                    'Weet je wat ik daar graag doe? Grote zandkastelen bouwen en schelpjes zoeken.')
        interaction_choice.add_move('strand', self.droomrobot.ask_open,
                                    f'Wat zou jij op het stand willen doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie')

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat zou jij op het strand willen doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Er is zoveel leuks te doen op het strand.")
        interaction_choice.add_choice('strand', motivation_choice)

        # Bos
        interaction_choice.add_move('bos', self.droomrobot.say,
                                    'Het bos, wat een rustige plek! De bomen zijn hoog en soms hoor ik de vogeltjes fluiten.')
        interaction_choice.add_move('bos', self.droomrobot.say,
                                    'Weet je wat ik daar graag doe? Takjes verzamelen en speuren naar eekhoorntjes.')
        interaction_choice.add_move('bos', self.droomrobot.ask_open,
                                    f'Wat zou je in het bos willen doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie')

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat zou jij in het bos willen doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Je kan van alles doen in het bos, zo fijn.")
        interaction_choice.add_choice('bos', motivation_choice)

        # Ruimte
        interaction_choice.add_move('ruimte', self.droomrobot.say,
                                    'De ruimte is heel bijzonder, ik stel me voor dat ik in een raket zit en langs de sterren vlieg.')
        interaction_choice.add_move('ruimte', self.droomrobot.say,
                                    'Weet je wat ik daar graag doe? Naar de planeten zwaaien en kijken of ik grappige mannetjes zie.')
        interaction_choice.add_move('ruimte', self.droomrobot.ask_open,
                                    f'Wat zou jij in de ruimte willen doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie')

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat zou jij in de ruimte willen doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Je kan van alles doen in de ruimte, zo fijn.")
        interaction_choice.add_choice('ruimte', motivation_choice)

        # # Other
        # interaction_choice.add_move('other', lambda: self.droomrobot.say(self.droomrobot.gpt.request(
        #     GPTRequest(
        #         f'Je bent een sociale robot die praat met een kind van {str(self.user_model['child_age'])} jaar oud.'
        #         f'Het kind ligt in het ziekenhuis.'
        #         f'Jij bent daar om het kind op te vrolijken en af te leiden met een leuk, vriendelijk gesprek.'
        #         f'Gebruik warme, positieve taal die past bij een kind van {str(self.user_model['child_age'])} jaar.'
        #         f'Zorg dat je praat zoals een lieve, grappige robotvriend, niet als een volwassene. '
        #         f'Het gesprek gaat over een fijne plek waar het kind zich blij en veilig voelt. '
        #         f'De fijne plek voor het kind is: "{self.user_model['droomplek']}". '
        #         f'Jouw taak is om twee korte zinnen te maken over deze plek. '
        #         f'De eerste zin is een observatie over wat deze plek zo fijn maakt. '
        #         f'De tweede zin gaat over wat jij, als droomrobot, daar graag samen met het kind zou doen. '
        #         f'Bijvoorbeeld als de fijne plek de speeltuin is zouden dit de twee zinnen kunnen zijn.'
        #         f'"De speeltuin, wat een vrolijke plek! Ik hou van de glijbaan en de schommel."'
        #         f'Weet je wat ik daar graag doe? Heel hoog schommelen, bijna tot aan de sterren."'
        #         f'Gebruik kindvriendelijke verbeelding wat te maken heeft met de plek. ')).response))
        # interaction_choice.add_move('other', self.droomrobot.ask_open,
        #                             lambda: f'Wat zou jij willen doen bij jouw droomplek {self.user_model['droomplek']} {self.user_model['child_name']}?',
        #                             user_model_key='droomplek_motivatie')
        #
        # motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        # motivation_choice.add_move('success', lambda: self.droomrobot.say(
        #     self.droomrobot.personalize(f'Wat zou jij willen doen bij jouw droomplek {self.user_model['droomplek']}?',
        #                                 self.user_model['child_age'],
        #                                 self.user_model['droomplek_motivatie'])))
        # motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
        # interaction_choice.add_choice('other', motivation_choice)

        # Fail
        interaction_choice.add_move('fail', self.droomrobot.say, 'Oh sorry ik begreep je even niet.')
        interaction_choice.add_move('fail', self.droomrobot.say, 'Weetje wat. Ik vind het stand echt super leuk.')
        interaction_choice.add_move('fail', self.droomrobot.say, 'Laten we naar het strand gaan als droomplek.')
        interaction_choice.add_move('fail', self.droomrobot.say,
                                    'Ah, het strand! Ik kan de golven bijna horen en het zand onder mijn voeten voelen.')
        interaction_choice.add_move('fail', self.droomrobot.say,
                                    'Weet je wat ik daar graag doe? Een zandkasteel bouwen met een vlag er op.')
        interaction_choice.add_move('fail', self.droomrobot.ask_open,
                                    f'Wat zou jij op het stand willen doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie')

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat zou jij op het strand willen doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
        interaction_choice.add_choice('fail', motivation_choice)
        interaction_choice.add_move('fail', self.set_user_model_variable, 'droomplek', 'strand')
        interaction_choice.add_move('fail', self.droomrobot.get_article, lambda: self.user_model['droomplek'],
                                    user_model_key='droomplek_lidwoord')

        return interaction_choice

    def _build_interaction_choice_oefenen(self) -> InteractionChoice:
        interaction_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Strand
        interaction_choice.add_move('strand', self.droomrobot.say, 'En terwijl je zo rustig aan het ademhalen bent mag je gaan voorstellen dat je op het strand bent.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Kijk maar in je hoofd om je heen. Wat zie je allemaal?')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Misschien zie je het zand, de zee of een mooie schelp.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Ben je daar alleen, of is er iemand bij je?')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Zie je die mooie kleuren?')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Misschien wel groen of paars of andere kleuren.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'En merk maar hoe fijn jij je op deze plek voelt.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Luister maar lekker naar de golven van de zee.')
        interaction_choice.add_move('strand', self.droomrobot.play_audio, 'resources/audio/ocean_waves.wav')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Misschien voel je de warme zon op je gezicht, of is het een beetje koel.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Hier kun je alles doen wat je leuk vindt.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Misschien bouw je een groot zandkasteel, of spring je over de golven.')
        interaction_choice.add_move('strand', self.droomrobot.ask_open,
                                    lambda: f'Wat ga jij op het strand doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_practice_activity')
        motivation_choice = InteractionChoice('droomplek_practice_activity', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('WWat ga jij op het strand doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_practice_activity'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Wat je ook doet, merk maar hoe fijn het is om dat daar te doen!")
        interaction_choice.add_choice('strand', motivation_choice)

        # Bos
        interaction_choice.add_move('bos', self.droomrobot.say, 'En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in een prachtig bos bent.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Kijk maar eens in je hoofd om je heen wat je allemaal op die mooie plek ziet.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Misschien zie je hoe bomen, groene blaadjes of een klein diertje.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'En merk maar hoe fijn jij je op deze plek voelt.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Luister maar naar de vogels die zingen.')
        interaction_choice.add_move('bos', self.droomrobot.play_audio, 'resources/audio/forest-sounds.wav')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Misschien voel je de frisse lucht, of schijnt de zon door de bomen op je gezicht.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Hier kun je alles doen wat je leuk vindt.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Misschien klim je in een boom, of zoek je naar dieren.')
        interaction_choice.add_move('bos', self.droomrobot.ask_open,
                                    lambda: f'Wat ga jij doen in het bos {self.user_model['child_name']}?',
                                    user_model_key='droomplek_practice_activity')
        motivation_choice = InteractionChoice('droomplek_practice_activity', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat ga jij doen in het bos?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_practice_activity'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Merk maar hoe fijn het is om dat te doen!")
        interaction_choice.add_choice('bos', motivation_choice)

        # Ruimte
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in de ruimte bent, heel hoog in de lucht.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Misschien ben je er alleen, of is er iemand bij je.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Kijk maar eens in je hoofd om je heen, wat zie je daar allemaal?')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Misschien zie je de aarde heel klein worden.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Misschien zie je sterren die heel fel schijnen, in verschillende kleuren.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Je voelt je heel rustig en veilig in de ruimte, want er is zoveel te ontdekken.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'De ruimte is zo groot, vol met leuke plekken.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Misschien zie je wel regenbogen of ontdek je een speciale ster met grappige dieren er op.')
        interaction_choice.add_move('ruimte', self.droomrobot.ask_open,
                                    f'Wat ga jij doen in de ruimte {self.user_model['child_name']}?',
                                    user_model_key='droomplek_practice_activity')
        motivation_choice = InteractionChoice('droomplek_practice_activity', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat ga jij doen in de ruimte?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_practice_activity'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Oooooh, merk maar hoe fijn het is om dat daar te doen!")
        interaction_choice.add_choice('ruimte', motivation_choice)

        return interaction_choice

    def _intervention_preparation(self, phase_moves: InteractionChoice) -> InteractionChoice:
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        interaction_conf = InteractionConf(speaking_rate=0.75, animated=True, amplified=self.audio_amplified, always_regenerate=self.always_regenerate)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.set_interaction_conf, interaction_conf)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Wat fijn dat ik je mag helpen! We gaan samen weer op een mooie droomreis.', animated=False)
        # phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Omdat je net al zo goed hebt geoefend, zal het nu nog makkelijker gaan.')
        # phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Ga maar lekker zitten zoals jij dat fijn vindt.', sleep_time=1)
        # phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,  'Sluit je ogen maar, dan werkt de droomreis het allerbeste.')
        # phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,  'En je mag ze altijd even op doen en als je wilt weer dicht.')
        # phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Luister goed naar mijn stem, en merk maar dat alle andere geluiden in het ziekenhuis steeds zachter worden.')
        # phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,  'Leg je handen op je buik')
        # phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,  'en adem rustig in.')
        # phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        # phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'en weer heel goed uit.')
        # phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        intervention_prep_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Strand
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Stel je maar voor dat je weer op het strand bent, op die fijne plek.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Wat zie je daar allemaal? Misschien een grote zee en zacht zand.')
        # intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Luister maar naar alle fijne geluiden op het strand.')
        # intervention_prep_choice.add_move('strand', self.droomrobot.play_audio, 'resources/sounds/ocean_waves.wav')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Voel het zand maar onder je voeten. Het is lekker zacht en warm.')
        # intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Als je je tenen beweegt, voel je hoe lekker het zand voelt.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'En terwijl je nu zo lekker op het strand bent, zie je een mooie schommel staan.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Die heeft precies jouw lievelingskleur.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Je mag op de schommel gaan zitten.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Voel maar hoe je zachtjes heen en weer gaat.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say,
                                          'Voel maar hoe makkelijk de schommel doet wat jij wil, heen en weer, heen en weer.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say,
                                          'De schommel gaat precies zo hoog als jij fijn vindt.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Jij bent de baas.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say,
                                          'Het kan ook een lekker kriebelend gevoel in je buik geven.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say,
                                          'En terwijl je zo lekker aan het schommelen bent, voel je de zachte warme wind op je gezicht.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say,
                                          'Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt op het strand.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say,
                                          'Je hoort de golven van de zee, terwijl je lekker blijft schommelen.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say,
                                          'De zon is net als een warme zachte deken die over je heen gaat.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say,
                                          'Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say,
                                          'Steeds lichter, steeds rustiger, helemaal ontspannen.')

        # Bos
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Stel je maar voor dat je weer in het bos bent, op die fijne plek.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Kijk maar weer naar alle mooie kleuren die om je heen zijn en hoe fijn je je voelt op deze plek.')
        # intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Luister maar naar alle rustige geluiden in het bos.')
        # intervention_prep_choice.add_move('bos', self.droomrobot.play_audio, 'resources/audio/forest-sounds.wav')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'De grond onder je voeten is lekker zacht.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Voel maar hoe fijn het is om hier te zijn.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Kijk, daar hangt een schommel tussen de bomen.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Het is precies jouw lievelingskleur.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say,
                                          'Je mag op de schommel gaan zitten. Voel maar hoe je zachtjes heen en weer gaat.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say,
                                          'Voel maar hoe makkelijk de schommel doet wat jij wil, heen en weer, heen en weer.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say,
                                          'De schommel gaat precies zo hoog als dat jij fijn vindt.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Jij bent de baas.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say,
                                          'Het kan ook een lekker kriebelend gevoel in je buik geven.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say,
                                          'En terwijl je zo lekker aan het schommelen bent, voel je de frisse lucht op je gezicht.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say,
                                          'Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt in het bos.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Je hoort de vogels zachtjes fluiten.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say,
                                          'De zon is net als een warme zachte deken die over je heen gaat.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say,
                                          'Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say,
                                          'Steeds lichter, steeds rustiger, helemaal ontspannen.')

        # Ruimte
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say, 'Stel je maar voor dat je weer in de ruimte bent, heel hoog in de lucht.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say, 'Wat zie je daar allemaal? Misschien sterren die twinkelen en planeten in mooie kleuren.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say, 'Voel maar hoe rustig het is om hier te zweven.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say, 'Kijk daar is een ruimteschip! Je mag erin gaan zitten.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say, 'Het voelt zacht en veilig. Jij bent de baas.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say, 'Het ruimteschip zweeft langzaam met je mee.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say,
                                          'In het ruimteschip krijg je een ruimtekapje op.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say,
                                          'Het voelt heerlijk zacht tegen je gezicht en het zal je beschermen.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say,
                                          'Het houdt je helemaal veilig, zodat je nergens anders aan hoeft te denken dan aan je avontuur in de ruimte.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say,
                                          'En terwijl je in het ruimteschip zit, voel je hoe het ruimteschip langzaam met je mee zweeft.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say,
                                          'Jij kunt kiezen waar je naartoe wilt zweven, naar de sterren of verder weg.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say,
                                          'Voel de rust om je heen, terwijl je door de ruimte zweeft')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say,
                                          'Kijk, daar is een mooie planeet! Misschien is hij blauw, paars of heeft hij ringen.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say,
                                          'Je voelt je veilig en stoer als een echte astronaut.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say,
                                          'Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker in de ruimte zweeft.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say,
                                          'Steeds lichter, steeds rustiger, helemaal ontspannen.')
        phase_moves.add_choice(InterventionPhase.PREPARATION.name, intervention_prep_choice)

        sentences = [
            'Adem maar goed door, je bent echt heel goed bezig!',
            'Merk maar hoe fijn jij je voelt op je fijne veilige plek.',
            'Je wordt steeds lichter en zachter. Merk maar hoe fijn dat is.',
            'Je bent veilig en je hebt alles onder controle.'
        ]
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.repeat_sentences, sentences)

        return phase_moves

    def _intervention_procedure(self, phase_moves: InteractionChoice) -> InteractionChoice:
        return phase_moves

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
