from sic_framework.services.openai_gpt.gpt import GPTRequest

from core import AnimationType
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext, InteractionSession, InteractionChoice, \
    InteractionChoiceCondition, InterventionPhase


class Bloedafname9(DroomrobotScript):

    def __init__(self, *args, **kwargs):
        super(Bloedafname9, self).__init__(*args, **kwargs, interaction_context=InteractionContext.BLOEDAFNAME)

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
        self.add_move(self.droomrobot.say, 'Wat fijn dat ik je mag helpen vandaag.', animated=True)
        self.add_move(self.droomrobot.ask_fake, 'Wat is jouw naam?', 3, animated=True)
        self.add_move(self.droomrobot.say, lambda: f'{self.user_model['child_name']}, wat een leuke naam.', animated=True)
        self.add_move(self.droomrobot.ask_fake, 'En hoe oud ben je?', 3, animated=True)
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        self.add_move(self.droomrobot.say, lambda: f'{str(self.user_model['child_age'])} jaar. Oh wat goed, dan kan ik je een truc leren om alles in het ziekenhuis voor jou makkelijker te maken.', animated=True)
        self.add_move(self.droomrobot.say, 'Die truc werkt bij veel kinderen heel goed.', animated=True)
        self.add_move(self.droomrobot.say, 'En ik ben dan ook benieuwd hoe goed het bij jou gaat werken.', animated=True)
        self.add_move(self.droomrobot.say, 'Jij kunt jezelf helpen door je lichaam en je hoofd te ontspannen.', animated=True)
        self.add_move(self.droomrobot.say, 'We gaan het samen doen, op jouw eigen manier.', animated=True)
        self.add_move(self.droomrobot.say, 'Ik ga je wat vertellen over deze truc.', animated=True)
        self.add_move(self.droomrobot.say, 'Let maar goed op, dan ga jij het ook leren.', animated=True)
        self.add_move(self.droomrobot.say, 'We gaan samen een reis maken in je fantasie, wat ervoor zorgt dat jij je fijn, rustig en sterk voelt.', animated=True)
        self.add_move(self.droomrobot.say, 'Met je fantasie kun je aan iets fijns denken terwijl je hier bent, als een soort droom.', animated=True)
        self.add_move(self.droomrobot.say, 'En het grappige is dat als je denkt aan iets fijns, dat jij je dan ook fijner gaat voelen.', animated=True)
        self.add_move(self.droomrobot.say, 'Ik zal het even voordoen.', animated=True)
        self.add_move(self.droomrobot.say, 'Ik ga het liefst in gedachten naar de wolken, lekker relaxed zweven.', animated=True)
        self.add_move(self.droomrobot.say, 'Maar het hoeft niet de wolken te zijn. Iedereen heeft een eigen fijne plek.', animated=True)
        self.add_move(self.droomrobot.say, 'Laten we nu samen bedenken wat jouw fijne plek is.', animated=True)
        self.add_move(self.droomrobot.say, 'Je kan bijvoorbeeld in gedachten naar het strand, het bos, op vakantie of wat anders.', animated=True)

        self.add_move(self.droomrobot.ask_entity_llm, 'Naar welke veilige plek zou jij in gedachten willen gaan?',
                      user_model_key='droomplek', animated=True)
        self.add_move(self.droomrobot.get_article, lambda: self.user_model['droomplek'],
                      user_model_key='droomplek_lidwoord')
        self.add_choice(self._build_interaction_choice_droomplek())

        # SAMEN OEFENEN
        self.add_move(self.droomrobot.ask_yesno, "Zit je zo goed?", user_model_key='zit_goed', animated=True)
        zit_goed_choice = InteractionChoice('zit_goed', InteractionChoiceCondition.MATCHVALUE)
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Het zit vaak het lekkerste als je stevig gaat zitten.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'met beide benen op de grond.')
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Ga maar eens kijken hoe goed dat zit.', sleep_time=1)
        zit_goed_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Als je goed zit.')
        self.add_choice(zit_goed_choice)
        self.add_move(self.droomrobot.say, 'mag je je ogen dicht doen.')
        self.add_move(self.droomrobot.say, 'dan werkt het trucje het beste.')

        self.add_move(self.droomrobot.say, 'Stel je voor, dat je op een hele fijne mooie plek bent in je eigen gedachten.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, lambda: f'Misschien is dit weer {self.user_model['droomplek_lidwoord']} {self.user_model['droomplek']}, of een nieuwe fantasieplek', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Kijk maar eens om je heen, wat je allemaal op die mooie plek ziet.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Misschien ben je er alleen of is er iemand bij je.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Kijk maar welke mooie kleuren je allemaal om je heen ziet.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Misschien wel groen, of paars, of regenboog kleuren.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'En merk maar hoe fijn jij je op deze plek voelt.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Luister naar de geluiden die je op die plek kan horen.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'En hoe de temperatuur daar voelt, misschien is het heerlijk warm of lekker koel.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'En stel je dan nu voor, dat er een luchtballon is op jouw fijne plek.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, lambda: f'Die speciaal op jou staat te wachten, {self.user_model['child_name']}.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Kijk maar eens welke kleur jouw luchtballon heeft.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Jij mag een ballonvaart gaan maken in die superveilige luchtballon.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Je mag je voorstellen dat je in de mand van de luchtballon stapt.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Als je goed in het mandje bent gestapt, gaat de luchtballon in een prettig en rustig tempo omhoog.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Precies zo hoog als dat jij fijn vindt.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'En kijk maar weer om je heen, wat je allemaal ziet.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.play_audio, 'resources/audio/birds.wav')
        self.add_move(self.droomrobot.say, 'Merk maar hoe fijn je je voelt op deze plek.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Dan gaan we nu oefenen hoe je je nog krachtiger en veiliger kan voelen.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Dit doe je door diep in en uit te ademen.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Adem diep in door je neus.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        self.add_move(self.droomrobot.say, 'en blaas langzaam uit door je mond.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        self.add_move(self.droomrobot.say, lambda: f'Goed zo {self.user_model['child_name']}, dat gaat al heel goed.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'En terwijl je zo goed aan het ademen bent, stel je voor dat er een klein, warm lichtje op je arm verschijnt.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Dat lichtje laadt jouw kracht op.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Stel je eens voor hoe dat lichtje eruit ziet.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Is het geel, blauw of misschien jouw lievelingskleur?', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.ask_entity_llm, 'Welke kleur heeft jouw lichtje?', strict=True, user_model_key='kleur')
        kleur_choice = InteractionChoice('kleur', InteractionChoiceCondition.HASVALUE)
        kleur_choice.add_move('success', self.droomrobot.say,
                              lambda: f'{self.user_model['kleur']}, wat goed, die heb je goed gekozen, {self.user_model['child_name']}.',
                              speaking_rate=0.75,
                              sleep_time=0.7)
        kleur_choice.add_move('fail', self.droomrobot.say,
                              'Sorry, dat verstond ik even niet goed. Weet je wat? Ik vind groen een mooie kleur. Laten we het lichtje groen maken.')
        kleur_choice.add_move('fail', lambda: self.set_user_model_variable('kleur', 'groen'))
        self.add_choice(kleur_choice)
        self.add_move(self.droomrobot.get_adjective, lambda: self.user_model['kleur'], user_model_key='kleur_adjective')
        self.add_move(self.droomrobot.say, lambda: f'Merk maar eens, hoe dat {self.user_model['kleur_adjective']} lichtje, je een heel fijn, krachtig gevoel geeft.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'En hoe jij nu een superheld bent, met jouw superkracht, en alles aankan.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'En iedere keer als je het nodig hebt, kun je zoals je nu geleerd hebt, een paar keer diep in en uit ademen, om het lichtje te activeren, en jouw kracht te laten groeien.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Hartstikke goed, ik ben benieuwd hoe goed het lichtje je zometeen gaat helpen.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Als je genoeg geoefend hebt, mag je de luchtballon weer rustig laten landen.', speaking_rate=0.75, sleep_time=0.7)
        self.add_move(self.droomrobot.say, 'Als dat gelukt is, mag je je ogen weer lekker open doen, en met je gedachten terugkomen in deze kamer.', speaking_rate=0.75, sleep_time=1)

        self.add_move(self.droomrobot.ask_yesno, 'Ging het oefenen goed?', user_model_key='oefenen_goed', animated=True)
        oefenen_choice = InteractionChoice('oefenen_goed', InteractionChoiceCondition.MATCHVALUE)
        oefenen_choice.add_move('yes', self.droomrobot.ask_open, 'Wat fijn. Wat vond je goed gaan?',
                                user_model_key='oefenen_goed_uitleg', animated=True)
        oefenen_goed_choice = InteractionChoice('oefenen_goed_uitleg', InteractionChoiceCondition.HASVALUE)
        oefenen_goed_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat fijn. Wat vond je goed gaan?',
                                        self.user_model['child_age'],
                                        self.user_model['oefenen_goed_uitleg'])), animated=True)
        oefenen_goed_choice.add_move('fail', self.droomrobot.say, "Wat knap van jou.", animated=True)
        oefenen_choice.add_choice('yes', oefenen_goed_choice)
        oefenen_choice.add_move('yes', self.droomrobot.say,
                                lambda: f'Ik vind {self.user_model['kleur']} een hele mooie kleur, die heb je goed gekozen.', animated=True)

        oefenen_choice.add_move('other', self.droomrobot.ask_open, 'Wat ging er nog niet zo goed?',
                                user_model_key='oefenen_slecht_uitleg', animated=True)

        oefenen_slecht_choice = InteractionChoice('oefenen_slecht_uitleg', InteractionChoiceCondition.HASVALUE)
        oefenen_slecht_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat ging er nog niet zo goed?',
                                        self.user_model['child_age'],
                                        self.user_model['oefenen_slecht_uitleg'])), animated=True)
        oefenen_slecht_choice.add_move('fail', self.droomrobot.say,
                                       "Wat jammer zeg. Probeer ik het de volgende keer beter te doen.", animated=True)
        oefenen_choice.add_choice('other', oefenen_slecht_choice)
        oefenen_choice.add_move('fail', self.droomrobot.say, "Oke.", animated=True)
        self.add_choice(oefenen_choice)
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)  # smile
        self.add_move(self.droomrobot.say, 'Gelukkig wordt het steeds makkelijker als je het vaker oefent.', animated=True)
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed het zometeen gaat.', animated=True)
        self.add_move(self.droomrobot.say, 'Je zult zien dat dit je gaat helpen.', animated=True)
        self.add_move(self.droomrobot.say,'Als je zometeen aan de beurt bent, ga ik je helpen om weer een reis met je fantasie te maken.', animated=True)
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
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, lambda: f'Wat fijn dat ik je weer mag helpen {self.user_model['child_name']}, we gaan weer samen een reis door je fantasie maken.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Omdat je net al zo goed hebt geoefend, zul je zien dat het nu nog beter en makkelijker gaat.')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Je mag weer goed gaan zitten en je ogen dicht doen zodat het trucje nog beter werkt.', sleep_time=1.0)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Luister maar weer goed naar mijn stem, en merk maar dat andere geluiden in het ziekenhuis veel stiller worden.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Ga maar rustig ademen zoals je dat gewend bent.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Adem rustig in.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'en rustig uit.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, lambda: f'Stel je maar voor dat je weer bij {self.user_model['droomplek_lidwoord']} {self.user_model['droomplek']} bent.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Kijk maar weer naar alle mooie kleuren die om je heen zijn en merk hoe fijn je je voelt op deze plek.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.droomrobot.say, 'Luister maar naar alle fijne geluiden op die plek.', speaking_rate=0.75, sleep_time=0.7)
        sentences = [
            'Kijk maar naar de leuke dingen die je daar kunt doen',
            'Misschien ben je er alleen of juist met je vrienden',
            'Wat een leuke plek, die wil ik ook wel eens bezoeken',
        ]
        phase_moves.add_move(InterventionPhase.PREPARATION.name, self.repeat_sentences, sentences)
        return phase_moves

    def _intervention_procedure(self, phase_moves: InteractionChoice) -> InteractionChoice:
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Als je wil, mag je weer een ritje maken in jouw speciale luchtballon, of je kan iets anders leuks doen op je fijne plek.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Merk maar hoe fijn jij je voelt, op jouw fijne veilige plek.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Nu gaan we je kracht weer activeren, zoals je dat geleerd hebt.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Adem in via je neus.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'en blaas rustig uit via je mond.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, lambda: f'En kijk maar hoe je krachtige {self.user_model['kleur_adjective']} lichtje weer op je arm verschijnt.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Zie het lichtje steeds sterker en krachtiger worden.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Zodat jij jezelf kan helpen.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, lambda: f'En als je het nodig hebt, stel je voor dat je {self.user_model['kleur_adjective']} lichtje nog helderder gaat schijnen.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Dat betekent dat jouw kracht helemaal wordt opgeladen.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Als het nodig is, kan je de kracht nog groter maken door met je tenen te wiebelen.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Het geeft een veilige en zachte gloed om je te helpen.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Adem diep in.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.play_audio, 'resources/audio/breath_in.wav')
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'en blaas uit.', speaking_rate=0.75, sleep_time=0.7)
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.play_audio, 'resources/audio/breath_out.wav')
        phase_moves.add_move(InterventionPhase.PROCEDURE.name,self.droomrobot.say, 'Merk maar hoe goed jij jezelf kan helpen, op je eigen veilige plek.', speaking_rate=0.75, sleep_time=0.7)
        sentences = [
            "Je doet het fantastisch! Wat een geweldige kleur heeft jouw lichtje nu.",
            "Adem rustig door, je bent helemaal in controle. Goed bezig!",
            "Wist je dat jouw kracht nog sterker wordt als je je lichtje groter maakt in je gedachten?",
            "Kijk ook nog eens rond op welke mooie plek je bent, wat kan je daar allemaal doen?",
        ]
        phase_moves.add_move(InterventionPhase.PROCEDURE.name, self.repeat_sentences, sentences)
        return phase_moves

    def _intervention_wrapup(self, phase_moves: InteractionChoice) -> InteractionChoice:
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.say, 'Dat was het weer.')
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.say, 'Je hebt het heel goed gedaan.', animated=True)
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.say, 'We gaan zo nog even doei zeggen.', animated=True)
        phase_moves.add_move(InterventionPhase.WRAPUP.name, self.droomrobot.say,
                             'Maar eerst ronden we dit even af. Tot zo', animated=True)
        return phase_moves

    def _goodbye(self):
        self.add_move(self.droomrobot.ask_opinion_llm, "Was het goed gegaan?", user_model_key='interventie_ervaring', animated=True)
        ervaring_choice = InteractionChoice('interventie_ervaring', InteractionChoiceCondition.MATCHVALUE)
        ervaring_choice.add_move('positive', self.droomrobot.say,
                                 lambda: f'Wat fijn! je hebt jezelf echt goed geholpen, {self.user_model['child_name']}', animated=True)
        ervaring_choice.add_move('other', self.droomrobot.say, 'Dat geeft niet.', animated=True)
        ervaring_choice.add_move(['other', 'fail'], self.droomrobot.say, 'Je hebt goed je best gedaan.', animated=True)
        ervaring_choice.add_move(['other', 'fail'], self.droomrobot.say, 'En kijk welke stapjes je allemaal al goed gelukt zijn.', animated=True)
        self.add_choice(ervaring_choice)
        self.add_move(self.droomrobot.say,
                      lambda: f'je kon al goed een {self.user_model['kleur']} lichtje uitzoeken.', animated=True)
        self.add_move(self.droomrobot.say,
                      'En weet je wat nu zo fijn is, hoe vaker je dit truukje oefent, hoe makkelijker het wordt.', animated=True)
        self.add_move(self.droomrobot.say, 'Je kunt dit ook zonder mij oefenen.', animated=True)
        self.add_move(self.droomrobot.say,
                      'Je hoeft alleen maar je ogen dicht te doen en op reis te gaan in je fantasie.', animated=True)
        self.add_move(self.droomrobot.say, 'Dan word je lichaam vanzelf wel rustig en voel jij je fijn.', animated=True)
        self.add_move(self.droomrobot.say, 'Ik ben benieuwd hoe goed je het de volgende keer gaat doen.', animated=True)
        self.add_move(self.droomrobot.say, 'Je doet het op jouw eigen manier, en dat is precies goed.', animated=True)
        self.add_move(self.droomrobot.say, 'Ik ga nu een ander kindje helpen, net zoals ik jou nu heb geholpen.', animated=True)
        self.add_move(self.droomrobot.say, 'Misschien zien we elkaar de volgende keer!', animated=True)
        self.add_move(self.droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True) ## Wave right hand
        self.add_move(self.droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True) ## Smile
        self.add_move(self.droomrobot.say, 'Doei')

    def _build_interaction_choice_droomplek(self) -> InteractionChoice:
        interaction_choice = InteractionChoice('droomplek', InteractionChoiceCondition.MATCHVALUE)

        # Strand
        interaction_choice.add_move('strand', self.droomrobot.say,
                                    'Ah, het strand! Ik kan de golven bijna horen en het zand onder mijn voeten voelen.', animated=True)
        interaction_choice.add_move('strand', self.droomrobot.say,
                                    'Weet je wat ik daar graag doe? Een zandkasteel bouwen met een vlag er op.', animated=True)
        interaction_choice.add_move('strand', self.droomrobot.ask_open,
                                    f'Wat zou jij op het stand willen doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie', animated=True)

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat zou jij op het strand willen doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])), animated=True)
        motivation_choice.add_move('fail', self.droomrobot.say, "Dat klinkt heerlijk! Ik kan me dat helemaal voorstellen.", animated=True)
        interaction_choice.add_choice('strand', motivation_choice)

        # Bos
        interaction_choice.add_move('bos', self.droomrobot.say,
                                    'Het bos, wat een rustige plek!'
                                    'Ik hou van de hoge bomen en het zachte mos op de grond.', animated=True)
        interaction_choice.add_move('bos', self.droomrobot.say,
                                    'Weet je wat ik daar graag doe? Ik zoek naar dieren die zich verstoppen,'
                                    ' zoals vogels of eekhoorns.', animated=True)
        interaction_choice.add_move('bos', self.droomrobot.ask_open,
                                    f'Wat zou je in het bos willen doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie', animated=True)

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat zou jij in het bos willen doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])), animated=True)
        motivation_choice.add_move('fail', self.droomrobot.say, "Wat een leuk idee! Het bos is echt een magische plek.", animated=True)
        interaction_choice.add_choice('bos', motivation_choice)

        # Vakantie
        interaction_choice.add_move('vakantie', self.droomrobot.say,
                                    'Oh ik hou van vakantie. Mijn laatste vakantie was in Frankrijk op een camping met veel waterglijbanen.', animated=True)
        interaction_choice.add_move('vakantie', self.droomrobot.say,
                                    'WHet was er heerlijk warm in de zon.', animated=True)
        interaction_choice.add_move('vakantie', self.droomrobot.ask_open,
                                    lambda: f'Wat gingen jullie op vakantie doen {self.user_model['child_name']}??',
                                    user_model_key='droomplek_motivatie', animated=True)

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat gingen jullie op vakantie doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])), animated=True)
        motivation_choice.add_move('fail', self.droomrobot.say,
                                   "Dat klinkt heel leuk. Wat fijn dat je daaraan kan terug denken.", animated=True)
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
                                    user_model_key='droomplek_motivatie', animated=True)

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize(f'Wat zou jij willen doen bij jouw droomplek {self.user_model['droomplek']}?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])), animated=True)
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.", animated=True)
        interaction_choice.add_choice('other', motivation_choice)

        # Fail
        interaction_choice.add_move('fail', self.droomrobot.say, 'Oh sorry ik begreep je even niet.', animated=True)
        interaction_choice.add_move('fail', self.droomrobot.say, 'Weetje wat. Ik vind het stand echt super leuk.', animated=True)
        interaction_choice.add_move('fail', self.droomrobot.say, 'Laten we naar het strand gaan als droomplek.', animated=True)
        interaction_choice.add_move('fail', self.droomrobot.say,
                                    'Ah, het strand! Ik kan de golven bijna horen en het zand onder mijn voeten voelen.', animated=True)
        interaction_choice.add_move('fail', self.droomrobot.say,
                                    'Weet je wat ik daar graag doe? Een zandkasteel bouwen met een vlag er op.', animated=True)
        interaction_choice.add_move('fail', self.droomrobot.ask_open,
                                    f'Wat zou jij op het stand willen doen {self.user_model['child_name']}?',
                                    user_model_key='droomplek_motivatie', animated=True)

        motivation_choice = InteractionChoice('droomplek_motivatie', InteractionChoiceCondition.HASVALUE)
        motivation_choice.add_move('success', lambda: self.droomrobot.say(
            self.droomrobot.personalize('Wat zou jij op het strand willen doen?',
                                        self.user_model['child_age'],
                                        self.user_model['droomplek_motivatie'])), animated=True)
        motivation_choice.add_move('fail', self.droomrobot.say, "Oke, super.", animated=True)
        interaction_choice.add_choice('fail', motivation_choice)

        return interaction_choice
