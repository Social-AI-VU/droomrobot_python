from sic_framework.services.openai_gpt.gpt import GPTRequest

from droomrobot.core import AnimationType, InteractionConf
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext, InteractionSession, InterventionPhase, \
    InteractionChoice, InteractionChoiceCondition


class Bloedafname4(DroomrobotScript):

    def __init__(self, *args, **kwargs):
        super(Bloedafname4, self).__init__(*args, **kwargs, interaction_context=InteractionContext.BLOEDAFNAME)

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
        self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True)
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        self.add_move(self.droomrobot.say, 'Hallo, ik ben de droomrobot!')
        self.add_move(self.droomrobot.say, 'Wat fijn dat ik je mag helpen vandaag.')
        self.add_move(self.droomrobot.ask_fake, 'Hoe heet jij?', 3)
        self.add_move(self.droomrobot.say, lambda: f'{self.user_model['child_name']}, wat leuk je te ontmoeten.')
        self.add_move(self.droomrobot.ask_fake, 'En hoe oud ben je?', 3)
        self.add_move(self.droomrobot.say, lambda: f'{str(self.user_model['child_age'])} jaar. '
                                           f'Oh wat goed, dan ben je al oud genoeg om mijn speciale trucje te leren.')
        self.add_move(self.droomrobot.say, 'Het is een truukje dat kinderen helpt om zich fijn en'
                                           'sterk te voelen in het ziekenhuis.')
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed het bij jou gaat werken.',animated=True)
        self.add_move(self.droomrobot.say, 'Het werkt zo',animated=True)
        self.add_move(self.droomrobot.say, 'Ik kan jou meenemen op een droomreis!')
        self.add_move(self.droomrobot.say, 'Een droomreis is een trucje waarbij je aan iets heel leuks denkt.',animated=True)
        self.add_move(self.droomrobot.say, 'Dat helpt je om rustig en sterk te blijven.',animated=True)
        self.add_move(self.droomrobot.say, 'Nu mag jij kiezen waar je heen wil in jouw droomreis.'
                                           'Je kunt kiezen uit het strand, het bos, de speeltuin of de ruimte.')

        self.add_move(self.droomrobot.ask_entity,
                      'Wat is de plek waar jij je fijn voelt?',
                      {'droomplek': 1},
                      'droomplek',
                      'droomplek',
                      user_model_key='droomplek')
        self.add_move(self.droomrobot.get_article, lambda: self.user_model['droomplek'],
                      user_model_key='droomplek_lidwoord')
        self.add_choice(self._build_interaction_choice_droomplek())

        # # SAMEN OEFENEN
        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False)
        self.add_move(self.droomrobot.set_interaction_conf, interaction_conf)
        
        self.add_move(self.droomrobot.say, 'Oke, laten we samen gaan oefenen.')
        self.add_move(self.droomrobot.say, 'Ga even lekker zitten zoals jij dat fijn vindt.', sleep_time=1)

        self.add_move(self.droomrobot.ask_yesno, "Zit je zo goed?", user_model_key='zit_goed')
        zit_goed_choice = InteractionChoice('zit_goed', InteractionChoiceCondition.MATCHVALUE)
        zit_goed_choice.add_move('yes', self.droomrobot.say, 'En nu je lekker bent gaan zitten.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Het zit vaak het lekkerste als je stevig gaat zitten.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'met beide benen op de grond.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Ga maar eens kijken hoe goed dat zit.', sleep_time=1)
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Als je goed zit.')
        self.add_choice(zit_goed_choice)
        self.add_move(self.droomrobot.say, 'mag je je ogen dicht doen.')
        self.add_move(self.droomrobot.say, 'dan werkt het truukje het beste.', sleep_time=1)

        self.add_move(self.droomrobot.say, lambda: f'Stel je voor dat je bij {self.user_model['droomplek_lidwoord']} '
                                                   f'{self.user_model['droomplek']} bent.')
        self.add_move(self.droomrobot.say, 'Kijk maar eens om je heen, wat je allemaal op die mooie plek ziet.')
        self.add_move(self.droomrobot.say, 'Misschien ben je er alleen, of is er iemand bij je.')
        self.add_move(self.droomrobot.say, 'Kijk maar welke mooie kleuren je allemaal om je heen ziet.')
        self.add_move(self.droomrobot.say, 'Misschien wel groen, of paars, of regenboog kleuren.')
        self.add_move(self.droomrobot.say, 'En merk maar hoe fijn jij je op deze plek voelt.')
        self.add_move(self.droomrobot.say,lambda: f'Nu je zo fijn bij {self.user_model['droomplek_lidwoord']} {self.user_model['droomplek']} bent, kunnen we je ook wat superkrachten gaan geven.')
        self.add_move(self.droomrobot.say, 'We gaan samen oefenen hoe je die kracht gebruikt.')
        # self.add_move(self.droomrobot.say, 'Jij mag kiezen welke kracht je hebt.', )
        #
        # #niet in originele script, in 4-6 word kracht niet uit gekozen maar alleen gepraat over een kracht. hier nu laten kiezen is betere (personalisatie)
        # self.add_move(self.droomrobot.ask_entity_llm, 'Welke kracht kies je?', user_model_key='superkracht')
        #
        # superkracht_choice = InteractionChoice('superkracht', InteractionChoiceCondition.HASVALUE)
        # superkracht_choice.add_move('success', self.droomrobot.generate_question,
        #                             lambda: self.user_model['child_age'],
        #                             "Welke superkracht zou je willen?",
        #                             lambda: self.user_model['superkracht'],
        #                             user_model_key='superkracht_follow_up_question')
        # superkracht_choice.add_move('success', self.droomrobot.ask_open,
        #                             lambda: f"{self.user_model['superkracht_follow_up_question']}",
        #                             user_model_key='superkracht_follow_up_response')
        # superkracht_choice.add_move('success', lambda: self.droomrobot.say(
        #     self.droomrobot.personalize(self.user_model['superkracht_follow_up_question'], self.user_model['child_age'],
        #                                 self.user_model['superkracht_follow_up_response'])))
        #
        # superkracht_choice.add_move('success', self.droomrobot.say,
        #                             lambda: f'Laten we samen oefenen hoe je '
        #                                     f'jouw superkracht {self.user_model['superkracht']} gebruikt.',
        #                             )
        # superkracht_choice.add_move('fail', self.droomrobot.say, 'Laten we samen oefenen hoe je die kracht gebruikt.',
        #                             
        #                            )
        # self.add_choice(superkracht_choice)

        self.add_move(self.droomrobot.say, 'Adem diep in door je neus.', )
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        self.add_move(self.droomrobot.say, 'en blaas langzaam uit door je mond.')
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        self.add_move(self.droomrobot.say, lambda: f'Goed zo {self.user_model['child_name']}, dat doe je al heel knap.')
        self.add_move(self.droomrobot.say, 'En nu zal je merken dat er een klein, warm, lichtje op je arm verschijnt.')
        self.add_move(self.droomrobot.say, 'Dat lichtje is magisch, en laadt jouw kracht op.')
        self.add_move(self.droomrobot.say, 'Stel je eens voor, hoe dat lichtje eruit ziet.')
        self.add_move(self.droomrobot.say, 'Is het geel, oranje, of misschien jouw lievelingskleur?')

        self.add_move(self.droomrobot.ask_entity_llm, 'Welke kleur heeft jouw lichtje?', strict=True,
                      user_model_key='kleur')

        kleur_choice = InteractionChoice('kleur', InteractionChoiceCondition.HASVALUE)
        kleur_choice.add_move('success', self.droomrobot.say, lambda: f'{self.user_model['kleur']}, wat goed, die heb je goed gekozen, {self.user_model['child_name']}.')
        kleur_choice.add_move('fail', self.droomrobot.say, 'Sorry, dat verstond ik even niet goed. Weet je wat? Ik vind groen een mooie kleur. Laten we het lichtje groen maken.')
        kleur_choice.add_move('fail', lambda: self.set_user_model_variable('kleur', 'groen'))
        self.add_choice(kleur_choice)
        self.add_move(self.droomrobot.get_adjective, lambda: self.user_model['kleur'], user_model_key='kleur_adjective')
        self.add_move(self.droomrobot.say, lambda: f'Merk maar eens hoe het {self.user_model['kleur_adjective']} '
                                                   f'lichtje je heel sterk maakt, en je beschermt.')
        self.add_move(self.droomrobot.say, 'En hoe jij nu een superheld bent, met jouw superkracht, en alles aankan.')
        self.add_move(self.droomrobot.say, 'Als je het nodig hebt, kun je diep in en uitademen'
                                           ' om het lichtje aan te zetten, en je kracht te laten groeien.')
        self.add_move(self.droomrobot.say, 'Hartstikke goed, ik ben benieuwd hoe goed het'
                                           ' lichtje je zometeen gaat helpen.', )
        self.add_move(self.droomrobot.say, 'Als je genoeg geoefend hebt, mag je je ogen weer '
                                           'lekker open doen, en zeggen, het lichtje gaat mij helpen.')

        # self.add_move(self.droomrobot.ask_yesno, 'Ging het oefenen goed?', user_model_key='oefenen_goed')
        # oefenen_choice = InteractionChoice('oefenen_goed', InteractionChoiceCondition.MATCHVALUE)
        # oefenen_choice.add_move('yes', self.droomrobot.ask_open, 'Wat fijn. Wat vond je goed gaan?',
        #                         user_model_key='oefenen_goed_uitleg')
        # oefenen_goed_choice = InteractionChoice('oefenen_goed_uitleg', InteractionChoiceCondition.HASVALUE)
        # oefenen_goed_choice.add_move('success', lambda: self.droomrobot.say(
        #     self.droomrobot.personalize('Wat fijn. Wat vond je goed gaan?',
        #                                 self.user_model['child_age'],
        #                                 self.user_model['oefenen_goed_uitleg'])))
        # oefenen_goed_choice.add_move('fail', self.droomrobot.say, "Wat knap van jou.")
        # oefenen_choice.add_choice('yes', oefenen_goed_choice)
        # oefenen_choice.add_move('yes', self.droomrobot.say,
        #                         lambda: f'Ik vind {self.user_model['kleur']} een hele mooie kleur, die heb je goed gekozen.')
        # 
        # oefenen_choice.add_move('other', self.droomrobot.ask_open, 'Wat ging er nog niet zo goed?',
        #                         user_model_key='oefenen_slecht_uitleg')
        # 
        # oefenen_slecht_choice = InteractionChoice('oefenen_slecht_uitleg', InteractionChoiceCondition.HASVALUE)
        # oefenen_slecht_choice.add_move('success', lambda: self.droomrobot.say(
        #     self.droomrobot.personalize('Wat ging er nog niet zo goed?',
        #                                 self.user_model['child_age'],
        #                                 self.user_model['oefenen_slecht_uitleg'])))
        # oefenen_slecht_choice.add_move('fail', self.droomrobot.say, "Wat jammer zeg. Probeer ik het de volgende keer beter te doen.")
        # oefenen_choice.add_choice('other', oefenen_slecht_choice)
        # oefenen_choice.add_move('fail', self.droomrobot.say, "Oke.")
        # self.add_choice(oefenen_choice)

        self.add_move(self.droomrobot.reset_interaction_conf)
        
        self.add_move(self.droomrobot.say, 'Gelukkig wordt het steeds makkelijker als je het vaker oefent.')
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed het zometeen gaat.')
        self.add_move(self.droomrobot.say, 'Je zult zien dat dit je gaat helpen.')
        self.add_move(self.droomrobot.say, 'Als je zometeen aan de beurt bent, ga ik je helpen om het lichtje '
                                           'weer samen aan te zetten, zodat je weer die superheld bent.')
        self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        self.add_move(self.droomrobot.say, 'Tot straks, doei!')

    def _intervention(self):
        self.phases = [
            InterventionPhase.PREPARATION.name,
            InterventionPhase.PROCEDURE.name,
            InterventionPhase.WRAPUP.name
        ]
        self.phase_moves_build = InteractionChoice('Bloedafname4', InteractionChoiceCondition.PHASE)
        self.phase_moves_build = self._intervention_preparation(self.phase_moves_build)
        self.phase_moves_build = self._intervention_procedure(self.phase_moves_build)
        self.phase_moves = self._intervention_wrapup(self.phase_moves_build)

    def _intervention_preparation(self, phase_moves: InteractionChoice) -> InteractionChoice:
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, lambda: f'Wat fijn dat ik je weer mag helpen, we gaan weer samen een droomreis naar {self.user_model['droomplek_lidwoord']} {self.user_model['droomplek']} maken.', animated=False)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Omdat je net al zo goed hebt geoefend, zul je zien dat het nu nog beter en makkelijker gaat.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,'Je mag weer goed gaan zitten, en je ogen dicht doen, zodat deze droomreis nog beter voor jou werkt.', sleep_time=1)

        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.set_interaction_conf, interaction_conf)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Luister maar weer goed naar mijn stem, en merk maar dat andere geluiden in het ziekenhuis veel stiller worden.', )
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say,'Ga maar rustig ademen, zoals je dat gewend bent.', )
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Adem rustig in.', )
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'en rustig uit.', )
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, lambda:f'Stel je maar voor dat je bij {self.user_model['droomplek_lidwoord']} {self.user_model['droomplek']} bent.', )
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Kijk maar weer naar alle mooie kleuren die om je heen zijn, en voel hoe fijn het is om daar te zijn.', )
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Luister maar naar alle fijne geluiden op die plek.', )
        sentences = [
            'Kijk maar naar de leuke dingen die je daar kunt doen',
            'Misschien ben je er alleen of juist met je vrienden',
            'Wat een leuke plek, die wil ik ook wel eens bezoeken',
        ]
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.repeat_sentences, sentences)

        return phase_moves

    def _intervention_procedure(self, phase_moves: InteractionChoice) -> InteractionChoice:
        interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.set_interaction_conf, interaction_conf)

        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'Nu gaan we je superkracht weer aanzetten, net zoals je hebt geleerd.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'Adem in door je neus.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'en blaas rustig uit via je mond.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, lambda: f'Je {self.user_model['kleur_adjective']} lichtje verschijnt weer op je arm.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'Zie het lichtje steeds sterker worden.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'Zo word jij weer een superheld, en kun je jezelf helpen.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, lambda: f'En als je het nodig hebt, stel je voor dat je {self.user_model['kleur_adjective']} lichtje nog helderder gaat schijnen.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'Dat betekent dat jouw kracht helemaal opgeladen is.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'je kunt het lichtje nog sterker maken door met je tenen te wiebelen.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'Het geeft een zachte, veilige gloed om je te helpen.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'Als je iets voelt op je arm, dan werkt de superkracht helemaal.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'Adem diep in.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, 'en blaas uit.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.play_audio,'resources/audio/breath_out.wav')
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say,'Merk maar hoe goed jij jezelf kunt helpen, je bent echt een superheld.', )
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.droomrobot.say, lambda: f'En nu je {self.user_model['kleur_adjective']} lichtje goed aan staat, kan jij weer verder spelen bij {self.user_model['droomplek_lidwoord']} {self.user_model['droomplek']}.', )
        sentences = [
            "Je doet het fantastisch! Wat een geweldige kleur heeft jouw lichtje nu.",
            "Adem rustig door, je bent helemaal in controle. Goed bezig!",
            "Wist je dat jouw kracht nog sterker wordt als je je lichtje groter maakt in je gedachten?",
            "Kijk ook nog eens rond op welke mooie plek je bent, wat kan je daar allemaal doen?",
        ]
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.repeat_sentences, sentences)

        return phase_moves

    def _intervention_wrapup(self, phase_moves: InteractionChoice) -> InteractionChoice:
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.reset_interaction_conf)
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.say, 'Dat was het weer.')
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.say, 'Je hebt het heel goed gedaan.')
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.say, 'We gaan zo nog even doei zeggen.')
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.say, 'Maar eerst ronden we dit even af. Tot zo')

        return phase_moves

    def _goodbye(self):
        self.add_move(self.droomrobot.say, lambda: f'Zo {self.user_model['child_name']}, het is weer tijd om doei te zeggen.')
        self.add_move(self.droomrobot.say,'Wat fijn dat ik jou vandaag mocht helpen.')
        self.add_move(self.droomrobot.ask_opinion_llm, "Was het goed gegaan?", user_model_key='interventie_ervaring')
        ervaring_choice = InteractionChoice('interventie_ervaring', InteractionChoiceCondition.MATCHVALUE)
        ervaring_choice.add_move('positive', self.droomrobot.say, lambda: f'Wat fijn! je hebt jezelf echt goed geholpen, {self.user_model['child_name']}')
        ervaring_choice.add_move('other', self.droomrobot.say, 'Dat geeft niet.')
        ervaring_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Je hebt goed je best gedaan.')
        ervaring_choice.add_move(['other', 'fail'], self.droomrobot.say, 'En kijk welke stapjes je allemaal al goed gelukt zijn.')
        self.add_choice(ervaring_choice)
        self.add_move(self.droomrobot.say, lambda: f'je kon al goed een {self.user_model['kleur']} lichtje uitzoeken.')
        self.add_move(self.droomrobot.say, 'En weet je wat nu zo fijn is, hoe vaker je dit truukje oefent, hoe makkelijker het wordt.')
        self.add_move(self.droomrobot.say, 'Je kunt dit ook zonder mij oefenen.')
        self.add_move(self.droomrobot.say, lambda: f'Je hoeft alleen maar je ogen dicht te doen en aan je {self.user_model['kleur_adjective']} lichtje te denken.')
        self.add_move(self.droomrobot.say, 'Dan word jij weer een superheld met extra kracht.')
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed je het de volgende keer gaat doen.')
        self.add_move(self.droomrobot.say, 'Je doet het op jouw eigen manier, en dat is precies goed.')
        self.add_move(self.droomrobot.say, 'Ik ga nu een ander kindje helpen, net zoals ik jou nu heb geholpen.')
        self.add_move(self.droomrobot.say, 'Misschien zien we elkaar de volgende keer!')
        self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        self.add_move(self.droomrobot.say, 'Doei')

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
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
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
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
        interaction_choice.add_choice('bos', motivation_choice)

        # Speeltuin
        interaction_choice.add_move('speeltuin', self.droomrobot.say,
                                    'De speeltuin, wat een vrolijke plek! Ik hou van de glijbaan en de schommel.')
        interaction_choice.add_move('speeltuin', self.droomrobot.say,
                                    'Weet je wat ik daar graag doe? Heel hoog schommelen, bijna tot aan de sterren.')
        interaction_choice.add_move('speeltuin', self.droomrobot.ask_open,
                                    f'Wat vind jij het leukste om te doen in de speeltuin {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie')

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat vind jij het leukste om te doen in de speeltuin?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
        interaction_choice.add_choice('speeltuin', motivation_choice)

        # Ruimte
        interaction_choice.add_move('ruimte', self.droomrobot.say,
                                    'De ruimte, wat een avontuurlijke plek! Ik stel me voor dat ik in een raket zit en langs de sterren vlieg.')
        interaction_choice.add_move('ruimte', self.droomrobot.say,
                                    'Weet je wat ik daar graag zou doen? Zwaaien naar de planeten en zoeken naar aliens die willen spelen.')
        interaction_choice.add_move('ruimte', self.droomrobot.ask_open,
                                    f'Wat zou jij in de ruimte willen doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie')

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat zou jij in de ruimte willen doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])))
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.")
        interaction_choice.add_choice('ruimte', motivation_choice)

        # Other
        interaction_choice.add_move('other', lambda: self.droomrobot.say(self.droomrobot.gpt.request(
            GPTRequest(
                f'Je bent een sociale robot die praat met een kind van {str(self.user_model['child_age'])} jaar oud.'
                f'Het kind ligt in het ziekenhuis.'
                f'Jij bent daar om het kind op te vrolijken en af te leiden met een leuk, vriendelijk gesprek.'
                f'Gebruik warme, positieve taal die past bij een kind van {str(self.user_model['child_age'])} jaar.'
                f'Zorg dat je praat zoals een lieve, grappige robotvriend, niet als een volwassene. '
                f'Het gesprek gaat over een fijne plek waar het kind zich blij en veilig voelt. '
                f'De fijne plek voor het kind is: "{self.user_model['droomplek']}". '
                f'Jouw taak is om twee korte zinnen te maken over deze plek. '
                f'De eerste zin is een observatie over wat deze plek zo fijn maakt. '
                f'De tweede zin gaat over wat jij, als droomrobot, daar graag samen met het kind zou doen. '
                f'Bijvoorbeeld als de fijne plek de speeltuin is zouden dit de twee zinnen kunnen zijn.'
                f'"De speeltuin, wat een vrolijke plek! Ik hou van de glijbaan en de schommel."'
                f'Weet je wat ik daar graag doe? Heel hoog schommelen, bijna tot aan de sterren."'
                f'Gebruik kindvriendelijke verbeelding wat te maken heeft met de plek. ')).response))
        interaction_choice.add_move('other', self.droomrobot.ask_open,
                                    lambda: f'Wat zou jij willen doen bij jouw droomplek {self.user_model['droomplek']} {self.user_model['child_name']}?',
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
