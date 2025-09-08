from time import sleep

from sic_framework.services.openai_gpt.gpt import GPTRequest

from droomrobot.core import AnimationType, InteractionConf
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext, InteractionSession, InteractionChoice, \
    InteractionChoiceCondition, InterventionPhase
from droomrobot.introduction_factory import IntroductionFactory


class Kapinductie9(DroomrobotScript):

    def __init__(self, *args, **kwargs):
        super(Kapinductie9, self).__init__(*args, **kwargs, interaction_context=InteractionContext.KAPINDUCTIE)

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
        intro_moves = IntroductionFactory.age6_9(droomrobot=self.droomrobot,
                                                 interaction_context=self.interaction_context,
                                                 user_model=self.user_model)
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
        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False)
        self.add_move(self.droomrobot.set_interaction_conf, interaction_conf)

        self.add_move(self.droomrobot.say,
                      'Laten we alvast gaan oefenen om samen een mooie droomreis te maken, zodat het je zometeen gaat helpen bij de slaapdokter.')
        self.add_move(self.droomrobot.say, 'Ga even lekker zitten zoals jij dat fijn vindt.', sleep_time=1)

        self.add_move(self.droomrobot.ask_yesno, "Zit je zo goed?", user_model_key='zit_goed')
        zit_goed_choice = InteractionChoice('zit_goed', InteractionChoiceCondition.MATCHVALUE)
        zit_goed_choice.add_move('yes', self.droomrobot.say, 'En nu je lekker bent gaan zitten.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say,
                                 'Het zit vaak het lekkerste als je stevig gaat zitten.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Ga maar eens kijken hoe goed dat zit.',
                                 sleep_time=1)
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Als je goed zit.')
        self.add_choice(zit_goed_choice)
        self.add_move(self.droomrobot.say, 'mag je je ogen dicht doen.')
        self.add_move(self.droomrobot.say, 'dan werkt het truukje het beste.')
        self.add_move(self.droomrobot.say,
                      'En terwijl je nu zo lekker zit mag je je handen op je buik doen en rustig gaan ademhalen',
                      sleep_time=1)

        self.add_move(self.droomrobot.say, 'Adem rustig in.', )
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        self.add_move(self.droomrobot.say, 'en rustig uit.')
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        self.add_move(self.droomrobot.say, 'En voel maar dat je buik en je handen iedere keer rustig omhoog en omlaag gaan terwijl je zo lekker aan het ademhalen bent.')

        self.add_choice(self._build_interaction_choice_oefenen())
        self.add_move(self.droomrobot.reset_interaction_conf)

        self.add_move(self.droomrobot.say, 'Nu je genoeg geoefend hebt mag je je ogen weer lekker opendoen.')
        self.add_move(self.droomrobot.say, 'En wat zo fijn is, is dat je iedere keer als je deze droomreis nodig hebt, je weer terug kan gaan in gedachten naar deze fijne plek.')
        self.add_move(self.droomrobot.say, 'Je hoeft alleen maar een paar keer diep in en uit te ademen. Ik ben benieuwd hoe goed dit je zometeen gaat helpen.')
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        self.add_move(self.droomrobot.say, lambda: f'Wanneer je zometeen aan de beurt bent ga ik je helpen om weer naar {self.user_model['droomplek_lidwoord']} {self.user_model['droomplek']} te gaan in gedachten. Je hebt super goed geoefend, dus je kan verrast zijn hoe goed het zometeen gaat!')
        # self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True)
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        self.add_move(self.droomrobot.say, lambda: f'Ik rij gewoon met je mee zo, {self.user_model['child_name']}.')

    def _intervention(self):
        self.phases = [
            InterventionPhase.PREPARATION.name,
            InterventionPhase.PROCEDURE.name
        ]
        self.phase_moves_build = InteractionChoice('Sonde4', InteractionChoiceCondition.PHASE)
        self.phase_moves_build = self._intervention_preparation(self.phase_moves_build)
        self.phase_moves = self._intervention_procedure(self.phase_moves_build)

    def _goodbye(self):
        pass

    def _build_interaction_choice_droomplek(self) -> InteractionChoice:
        interaction_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Strand
        interaction_choice.add_move('strand', self.droomrobot.say,
                                    'Ah, het strand! Ik kan de golven bijna horen en het zand onder mijn voeten voelen.')
        interaction_choice.add_move('strand', self.droomrobot.say,
                                    'Weet je wat ik daar graag doe? Een zandkasteel bouwen met een vlag er op.')
        interaction_choice.add_move('strand', self.droomrobot.ask_open,
                                    f'Wat zou jij op het stand willen doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie')

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat zou jij op het strand willen doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Dat klinkt heerlijk! Ik kan me dat helemaal voorstellen.")
        interaction_choice.add_choice('strand', motivation_choice)

        # Bos
        interaction_choice.add_move('bos', self.droomrobot.say,
                                    'Het bos, wat een rustige plek!'
                                    'Ik hou van de hoge bomen en het zachte mos op de grond.')
        interaction_choice.add_move('bos', self.droomrobot.say,
                                    'Weet je wat ik daar graag doe? Ik zoek naar dieren die zich verstoppen,'
                                    ' zoals vogels of eekhoorns.')
        interaction_choice.add_move('bos', self.droomrobot.ask_open,
                                    f'Wat zou je in het bos willen doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie')

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat zou jij in het bos willen doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Wat een leuk idee! Het bos is echt een magische plek.")
        interaction_choice.add_choice('bos', motivation_choice)

        # Vakantie
        interaction_choice.add_move('vakantie', self.droomrobot.say,
                                    'Oh ik hou van vakantie. Mijn laatste vakantie was in Frankrijk op een camping met veel waterglijbanen.')
        interaction_choice.add_move('vakantie', self.droomrobot.say,
                                    'WHet was er heerlijk warm in de zon.')
        interaction_choice.add_move('vakantie', self.droomrobot.ask_open,
                                    lambda: f'Wat gingen jullie op vakantie doen {self.user_model['child_name']}??',
                                    user_model_key='droomplek_motivatie')

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat gingen jullie op vakantie doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say,
                                   "Dat klinkt heel leuk. Wat fijn dat je daaraan kan terug denken.")
        interaction_choice.add_choice('vakantie', motivation_choice)

        # Other
        interaction_choice.add_move('other', lambda: self.droomrobot.say(self.droomrobot.gpt.request(
            GPTRequest(f'Je bent een sociale robot die praat met een kind van {str(self.user_model['child_age'])} jaar oud.'
                       f'Het kind ligt in het ziekenhuis.'
                       f'Jij bent daar om het kind af te leiden met een leuk gesprek. '
                       f'Gebruik alleen positief taalgebruik dat past bij de leeftijd van het kind.'
                       f'Praat tegen het kind als een robot vriend.'
                       f'Het gesprek gaat over een fijne plek voor het kind en wat je daar kunt doen.'
                       f'Jouw taak is het genereren van twee zinnen over die plek.'
                       f'De eerste zin is een observatie die de plek typeert'
                       f'De tweede zin gaat over wat de robot leuk zou vinden om te doen op die plek.'
                       f'Bijvoorbeeld als de fijne plek de speeltuin is zouden dit de twee zinnen kunnen zijn.'
                       f'"De speeltuin, wat een vrolijke plek! Ik hou van de glijbaan en de schommel."'
                       f'Weet je wat ik daar graag doe? Heel hoog schommelen, bijna tot aan de sterren."'
                       f'De fijne plek voor het kind is "{self.user_model['droomplek']}"'
                       f'Genereer nu de twee zinnen (observatie en wat de robot zou doen op die plek). ')).response))
        interaction_choice.add_move('other', self.droomrobot.ask_open,
                                    lambda: f'Wat zou jij willen doen in {self.user_model['droomplek_lidwoord']} {self.user_model['droomplek']} {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie')

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize(f'Wat zou jij willen doen bij jouw droomplek {self.user_model['droomplek']}?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
        interaction_choice.add_choice('other', motivation_choice)

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

        interaction_choice.add_move('strand', self.droomrobot.say, 'En terwijl je zo rustig aan het ademhalen bent mag je gaan voorstellen dat je op het strand bent.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Kijk maar eens in gedachten om je heen wat je allemaal op die mooie plek ziet.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Misschien ben je er alleen, of is er iemand bij je.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Kijk maar welke mooie kleuren je allemaal om je heen ziet.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Misschien wel groen of paars of regenboog kleuren.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'En merk maar hoe fijn jij je op deze plek voelt.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Luister maar lekker naar de golven van de zee.')
        interaction_choice.add_move('strand', self.droomrobot.play_audio, 'resources/audio/ocean_waves.wav')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Misschien is het er heerlijk warm of lekker koel. Voel de zonnestralen maar op je gezicht.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'En op deze plek kan je alles doen waar je zin in hebt.')
        interaction_choice.add_move('strand', self.droomrobot.say, 'Misschien ga je een zandkaasteel bouwen, of spring je over de golven heen.')
        interaction_choice.add_move('strand', self.droomrobot.ask_open,
                                    lambda: f'Wat ga jij op het strand doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_practice_activity')
        motivation_choice = InteractionChoice('droomplek_practice_activity', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('WWat ga jij op het strand doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_practice_activity'])))
        motivation_choice.add_move('fail', self.droomrobot.say,
                                   "Wat je ook doet, merk maar hoe fijn het is om dat daar te doen!")
        interaction_choice.add_choice('strand', motivation_choice)


        # Bos
        interaction_choice.add_move('bos', self.droomrobot.say, 'En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in een prachtig bos bent.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Kijk maar eens om je heen wat je allemaal op die mooie plek ziet.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Misschien zie je grote bomen, of kleine bloemen die zachtjes in de wind bewegen.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'En merk maar hoe fijn jij je op deze plek voelt.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Luister maar naar het geluid van de vogeltjes die fluiten.')
        interaction_choice.add_move('strand', self.droomrobot.play_audio, 'resources/audio/forest-sounds.wav')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Misschien is het er lekker fris, of voel je de zonnestralen door de bomen schijnen. Voel maar de zachte warmte op je gezicht.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'En op deze plek kun je alles doen waar je zin in hebt.')
        interaction_choice.add_move('bos', self.droomrobot.say, 'Misschien ga je een boom beklimmen, of op zoek naar dieren.')
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
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in de ruimte bent, hoog boven de aarde.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Misschien ben je er alleen, of is er iemand bij je.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Kijk maar eens om je heen, wat zie je daar allemaal?')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Misschien zie je de aarde heel klein worden, helemaal onder je, alsof je heel hoog in de lucht vliegt.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Misschien zie je sterren die heel fel schijnen, in verschillende kleuren.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Je voelt je heel rustig en veilig in de ruimte, want er is zoveel te ontdekken.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'De ruimte is eindeloos, vol met geheimen en wonderen.')
        interaction_choice.add_move('ruimte', self.droomrobot.say, 'Misschien zie je wel regenbogen of ontdek je een speciale wereld.')
        interaction_choice.add_move('ruimte', self.droomrobot.ask_open,
                                    f'Wat ga jij doen in de ruimte {self.user_model['child_name']}?',
                                    user_model_key='droomplek_practice_activity')
        motivation_choice = InteractionChoice('droomplek_practice_activity', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat ga jij doen in de ruimte?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_practice_activity'])))
        motivation_choice.add_move('fail', self.droomrobot.say,
                                   "Oooooh, merk maar hoe fijn het is om dat daar te doen!")
        interaction_choice.add_choice('ruimte', motivation_choice)

        return interaction_choice

    def _intervention_preparation(self, phase_moves: InteractionChoice) -> InteractionChoice:
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.ACTION,
                             "random_short4", run_async=True)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.EXPRESSION,
                             "emo_007", run_async=True)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,
                             'Wat fijn dat ik je mag helpen! We gaan samen weer op een mooie droomreis.',
                             animated=False)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,
                             'Omdat je net al zo goed hebt geoefend, zal het nu nog makkelijker gaan.')
        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.set_interaction_conf, interaction_conf)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,
                             'Je mag weer goed gaan zitten en je ogen dicht doen zodat deze droomreis nog beter voor jou werkt.', sleep_time=1)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,
                             'Luister maar weer goed naar mijn stem en merk maar dat andere geluiden in het ziekenhuis veel stiller worden.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Ga maar rustig ademen zoals je dat gewend bent.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Adem rustig in.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio,
                             'resources/audio/breath_in.wav')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'en rustig uit.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio,
                             'resources/audio/breath_out.wav')
        intervention_prep_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Strand
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Stel je maar voor dat je weer op het strand bent, op die fijne plek.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Kijk maar weer naar alle mooie kleuren die om je heen zijn en merk hoe fijn je je voelt op deze plek.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Luister maar naar alle fijne geluiden op het strand.')
        intervention_prep_choice.add_move('strand', self.droomrobot.play_audio, 'resources/sounds/ocean_waves.wav')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Het zand onder je voeten is heerlijk zacht.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Als je je tenen beweegt, voel je hoe lekker het zand voelt.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'En terwijl je nu zo lekker op het strand bent, zie je een mooie schommel staan.')
        intervention_prep_choice.add_move('strand', self.droomrobot.say, 'Precies in de kleur die jij mooi vindt.')

        # Bos
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Stel je maar voor dat je weer in het bos bent, op die fijne plek.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Kijk maar weer naar alle mooie kleuren die om je heen zijn en merk hoe fijn je je voelt op deze plek.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Luister maar naar alle fijne geluiden in het bos.')
        intervention_prep_choice.add_move('bos', self.droomrobot.play_audio, 'resources/audio/forest-sounds.wav')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'De grond onder je voeten is zacht en bedekt met een klein laagje mos.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Voel maar hoe lekker het is om op deze plek te staan.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'En terwijl je nu zo lekker in het bos bent, zie je een mooie schommel tussen twee grote bomen hangen.')
        intervention_prep_choice.add_move('bos', self.droomrobot.say, 'Precies in de kleur die jij mooi vindt.')

        # Ruimte
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say, 'Stel je maar voor dat je weer in de ruimte bent, boven de aarde, omgeven door de sterren.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say, 'Kijk maar naar de sterren die glinsteren, voel maar hoe rustig het is in deze uitgestrekte ruimte.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say, 'Luister naar het zachte geluid van je ademhaling en de stilte om je heen.')
        intervention_prep_choice.add_move('ruimte', self.droomrobot.say, 'Je mag naar het ruimteschip toe zweven en er lekker in gaan zitten.')

        phase_moves.add_choice(InterventionPhase.PREPARATION.name, intervention_prep_choice)

        return phase_moves

    def _intervention_procedure(self, phase_moves: InteractionChoice) -> InteractionChoice:
        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.set_interaction_conf, interaction_conf)

        intervention_proc_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Strand
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'Je mag naar de schommel toe gaan en lekker gaan schommelen.')
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'Voel maar hoe makkelijk de schommel met je mee beweegt, heen en weer, heen en weer.')
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'De schommel gaat precies zo hoog als dat jij het fijn vindt.')
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'Jij hebt namelijk alle controle.')
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'Het kan ook een lekker kriebellend gevoel in je buik geven.')
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'En terwijl je zo lekker aan het schommelen bent, voel je de zachte warme wind op je gezicht.')
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt op het strand.')
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'Je hoort de golven van de zee, terwijl je lekker blijft schommelen.')
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'De zon is net als een warme zachte deken die over je heen gaat.')
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        intervention_proc_choice.add_move('strand', self.droomrobot.say, 'Steeds lichter, steeds rustiger, helemaal ontspannen.')

        # Bos
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'Je mag naar de schommel toe gaan en lekker gaan schommelen.')
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'Voel maar hoe makkelijk de schommel met je mee beweegt, heen en weer, heen en weer.')
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'De schommel gaat precies zo hoog als dat jij het fijn vindt.')
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'Jij hebt namelijk alle controle.')
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'Het kan ook een lekker kriebelend gevoel in je buik geven.')
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'En terwijl je zo lekker aan het schommelen bent, voel je de frisse lucht op je gezicht.')
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt in het bos.')
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'Je hoort de vogels zachtjes fluiten.')
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'De zon is net als een warme zachte deken die over je heen gaat.')
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        intervention_proc_choice.add_move('bos', self.droomrobot.say, 'Steeds lichter, steeds rustiger, helemaal ontspannen.')

        # Ruimte
        intervention_proc_choice.add_move('ruimte', self.droomrobot.say, 'In het ruimteschip krijg je een ruimtekapje op.')
        intervention_proc_choice.add_move('ruimte', self.droomrobot.say, 'Het voelt heerlijk zacht tegen je gezicht en het zal je beschermen.')
        intervention_proc_choice.add_move('ruimte', self.droomrobot.say, 'Het houdt je helemaal veilig, zodat je nergens anders aan hoeft te denken dan aan je avontuur in de ruimte.')
        intervention_proc_choice.add_move('ruimte', self.droomrobot.say, 'En terwijl je in het ruimteschip zit, voel je hoe het ruimteschip met je meebeweegt, zacht en langzaam.')
        intervention_proc_choice.add_move('ruimte', self.droomrobot.say, 'Je hebt alle controle over waar je naartoe wilt, je kunt naar de sterren vliegen of verder weg gaan, het maakt niet uit.')
        intervention_proc_choice.add_move('ruimte', self.droomrobot.say, 'Voel de rust om je heen, terwijl je door de ruimte zweeft.')
        intervention_proc_choice.add_move('ruimte', self.droomrobot.say, 'Nu zweef je rustig langs een prachtige planeet die helemaal van kleur is, misschien wel in een fel blauw, of paars, of misschien zie je wel ringen om de planeet heen.')
        intervention_proc_choice.add_move('ruimte', self.droomrobot.say, 'Jij voelt je veilig en rustig, als een astronaut in je eigen avontuur.')
        intervention_proc_choice.add_move('ruimte', self.droomrobot.say, 'Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker in de ruimte zweeft.')
        intervention_proc_choice.add_move('ruimte', self.droomrobot.say, 'Steeds lichter, steeds rustiger, helemaal ontspannen.')

        phase_moves.add_choice(InterventionPhase.PROCEDURE.name, intervention_proc_choice)

        sentences = [
            'Adem rustig door, je bent helemaal in controle. Goed bezig!',
            'Merk maar hoe fijn jij je voelt op je fijne veilige plek.',
            'Je wordt steeds lichter en zachter. Merk maar hoe fijn dat is.',
            'Je bent veilig en je hebt alles onder controle.'
        ]
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.repeat_sentences, sentences)

        return phase_moves