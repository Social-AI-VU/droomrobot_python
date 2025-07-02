from time import sleep

from sic_framework.services.openai_gpt.gpt import GPTRequest

from droomrobot.droomrobot_script import DroomrobotScript, ScriptId, InteractionPart


class Kapinductie4(DroomrobotScript):
    def __init__(self, *args, **kwargs):
        super(Kapinductie4, self).__init__(*args, **kwargs)
        self.script_id = ScriptId.KAPINDUCTIE

    def run(self, participant_id: str, interaction_part: InteractionPart, user_model: dict):
        self.user_model = user_model

        if 'droomplek' in self.user_model:
            self.user_model['droomplek_lidwoord'] = self.droomrobot.get_article(self.user_model['droomplek'])

        self.droomrobot.start_logging(participant_id, {
            'participant_id': participant_id,
            'script_id': self.script_id,
            'interaction_part': interaction_part,
            'child_age': self.user_model['child_age']
        })
        if interaction_part == InteractionPart.INTRODUCTION:
            self.introductie()
        elif interaction_part == InteractionPart.INTERVENTION:
            self.interventie()
        else:
            print("Interaction part not recognized")
        self.droomrobot.stop_logging()

    def introductie(self):

        # INTRODUCTIE
        self.droomrobot.say(f'Hallo, ik ben de droomrobot!')
        self.droomrobot.say('Wat fijn dat ik je mag helpen vandaag.')
        self.droomrobot.say('Wat is jouw naam?')
        sleep(3)
        self.droomrobot.say(f'{self.user_model['child_name']}, wat een leuke naam.')
        self.droomrobot.say('En hoe oud ben je?')
        sleep(3)
        self.droomrobot.say(f'{str(self.user_model['child_age'])} jaar. Oh wat goed, dan ben je al oud genoeg om mijn speciale trucje te leren.')
        self.droomrobot.say('het is een truukje dat kinderen helpt om zich fijn en sterk te voelen in het ziekenhuis.')
        self.droomrobot.say('Ik ben benieuwd hoe goed het bij jou gaat werken.')
        self.droomrobot.say('We gaan samen iets leuks bedenken dat jou gaat helpen.')
        self.droomrobot.say('Nu ga ik je wat meer vertellen over het truukje wat ik kan.')
        self.droomrobot.say('Let maar goed op, ik ga je iets bijzonders leren.')
        self.droomrobot.say('Ik kan jou meenemen op een droomreis!')
        self.droomrobot.say('Een droomreis is een truukje waarbij je aan iets heel leuks denkt.')
        self.droomrobot.say('Dat helpt je om rustig en sterk te blijven.')
        self.droomrobot.say('Laten we nu samen bedenken wat jouw fijne plek is.')
        self.droomrobot.say('Je kan bijvoorbeeld in gedachten naar het strand, het bos of de ruimte.')

        # droomplek = self.droomrobot.ask_entity_llm('Naar welke plek zou jij graag willen?')
        self.user_model['droomplek'] = self.droomrobot.ask_entity('Naar welke plek zou jij graag willen?',
                                               {'droomplek': 1},
                                               'droomplek',
                                               'droomplek')
        if self.user_model['droomplek']:
            if 'strand' in self.user_model['droomplek']:
                self.strand()
            elif 'bos' in self.user_model['droomplek']:
                self.bos()
            elif 'ruimte' in self.user_model['droomplek']:
                self.ruimte()
            # else:
            #     self.nieuwe_droomplek(droomplek, child_name, self.user_model['self.user_model['child_age']'])
        else:
            self.user_model['droomplek'] = 'strand'  # default
            self.droomplek_not_recognized()
        self.user_model['droomplek_lidwoord'] = self.droomrobot.get_article(self.user_model['droomplek'])
        
        # SAMEN OEFENEN
        self.droomrobot.say('Laten we samen gaan oefenen.')
        self.droomrobot.say('Ga even lekker zitten zoals jij dat fijn vindt.')
        sleep(1)
        zit_goed = self.droomrobot.ask_yesno("Zit je zo goed?")
        if 'yes' in zit_goed:
            self.droomrobot.say('En nu je lekker bent gaan zitten.')
        else:
            self.droomrobot.say('Het zit vaak het lekkerste als je je benen lekker slap maakt, net als spaghetti.')
            self.droomrobot.say('ga maar eens kijke hoe goed dat zit.')
            sleep(1)
            self.droomrobot.say('als je goed zit.')
        self.droomrobot.say('mag je je ogen dicht doen.')
        self.droomrobot.say('dan werkt het truukje het beste.')
        self.droomrobot.say('leg nu je handen op je buik.')

        self.droomrobot.say('Adem rustig in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en rustig uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')
        self.droomrobot.say('En voel maar dat je buik rustig op en neer beweegt.')

        if self.user_model['droomplek']:
            if 'strand' in self.user_model['droomplek']:
                self.strand_oefenen()
            elif 'bos' in self.user_model['droomplek']:
                self.bos_oefenen()
            elif 'ruimte' in self.user_model['droomplek']:
                self.ruimte_oefenen()

        self.droomrobot.say('Weet je wat zo fijn is? Je kunt altijd teruggaan naar deze mooie plekken in je hoofd.')
        self.droomrobot.say('Je hoeft alleen maar rustig in en uit te ademen.')
        self.droomrobot.say('Ik ben benieuwd hoe goed dit je zometeen gaat helpen.')
        self.droomrobot.say('als je klaar bent, mag je je ogen weer open doen.')
        self.droomrobot.say(f'Straks ga ik je helpen om weer terug te gaan naar {self.user_model['droomplek_lidwoord']} {self.user_model['droomplek']} te gaan in gedachten. Je hebt super goed geoefend, dus je kan verrast zijn hoe goed het zometeen gaat!')

        ### INTERVENTIE
    def interventie(self):
        self.droomrobot.say('Wat fijn dat ik je  mag helpen, we gaan weer samen op een mooie droomreis.')
        self.droomrobot.say('Omdat je net al zo goed hebt geoefend, zal het nu nog makkelijker gaan.')
        self.droomrobot.say('Ga maar lekker zitten zoals jij dat fijn vindt.')
        sleep(1)
        self.droomrobot.say('Sluit je ogen maar, dan werkt de droomreis het allerbeste en kan je in gedachten op reis gaan.')
        self.droomrobot.say('En je mag ze altijd even op doen en als je wilt weer dicht.')
        self.droomrobot.say('Luister goed naar mijn stem, en merk maar dat alle andere geluiden in het ziekenhuis steeds zachter worden.')
        self.droomrobot.say('Leg je handen op je buik.')
        self.droomrobot.say('en adem heel goed in.')
        self.droomrobot.play_audio('resources/audio/breath_in.wav')
        self.droomrobot.say('en weer heel goed uit.')
        self.droomrobot.play_audio('resources/audio/breath_out.wav')

        if self.user_model['droomplek']:
            if 'strand' in self.user_model['droomplek']:
                self.strand_interventie()
            elif 'bos' in self.user_model['droomplek']:
                self.bos_interventie()
            elif 'ruimte' in self.user_model['droomplek']:
                self.ruimte_interventie()

        ### AFSCHEID
        ## geen afscheid want het kind slaapt?
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

    def strand(self):
        self.droomrobot.say('Wat is het fijn op het strand, Ik voel het warme zand en hoor de golven zachtjes ruisen.')
        self.droomrobot.say('Weet je wat ik daar graag doe? Grote zandkastelen bouwen en schelpjes zoeken.')
        motivation = self.droomrobot.ask_open(f'Wat zou jij daar willen doen {self.user_model['child_name']}?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat zou jij op het strand willen doen?', self.user_model['child_age'], motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Er is zoveel leuks te doen op het strand.")

    def bos(self):
        self.droomrobot.say('Het bos, wat een rustige plek! De bomen zijn hoog en soms hoor ik de vogeltjes fluiten.')
        self.droomrobot.say('Weet je wat ik daar graag doe? Takjes verzamelen en speuren naar eekhoorntjes.')
        motivation = self.droomrobot.ask_open(f'Wat zou jij daar willen doen {self.user_model['child_name']}?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat zou jij in het bos willen doen?', self.user_model['child_age'], motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Je kan van alles doen in het bos, zo fijn.")

    def ruimte(self):
        self.droomrobot.say('De ruimte is heel bijzonder, ik stel me voor dat ik in een raket zit en langs de sterren vlieg.')
        self.droomrobot.say('Weet je wat ik daar graag doe? Naar de planeten zwaaien en kijken of ik grappige mannetjes zie.')
        motivation = self.droomrobot.ask_open('Wat zou jij willen doen in de ruimte?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat zou jij in de ruimte willen doen?', self.user_model['child_age'],
                                                     motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Je kan van alles doen in de ruimte, zo fijn.")

    def nieuwe_droomplek(self):
        gpt_response = self.droomrobot.gpt.request(
            GPTRequest(f'Je bent een sociale robot die praat met een kind van {str(self.user_model['child_age'])} jaar oud.'
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
                       f'De fijne plek voor het kind is "{self.user_model['droomplek']}"'
                       f'Genereer nu de twee zinnen (observatie en wat de robot zou doen op die plek). '))
        self.droomrobot.say(gpt_response.response)
        motivation = self.droomrobot.ask_open(f'Wat zou jij daar willen doen {self.user_model['child_name']}?')
        if motivation:
            personalized_response = self.droomrobot.personalize(f'Wat zou jij op jouw droomplek {self.user_model['droomplek']} willen doen?', self.user_model['child_age'], motivation)
            self.droomrobot.say(personalized_response)
        else:
            self.droomrobot.say("Oke, super.")

    def droomplek_not_recognized(self):
        self.droomrobot.say('Oh sorry ik begreep je even niet.')
        self.droomrobot.say('Weetje wat. Ik vind het stand echt super leuk.')
        self.droomrobot.say('Laten we naar het strand gaan als droomplek.')
        self.strand()

    def strand_oefenen(self):
        self.droomrobot.say('En terwijl je zo rustig aan het ademhalen bent mag je gaan voorstellen dat je op het strand bent.')
        self.droomrobot.say('Kijk maar in je hoofd om je heen. Wat zie je allemaal?')
        self.droomrobot.say('Misschien zie je het zand, de zee of een mooie schelp.')
        self.droomrobot.say('Ben je daar alleen, of is er iemand bij je?')
        self.droomrobot.say('Kijk maar welke mooie kleuren je allemaal om je heen ziet.')
        self.droomrobot.say('Misschien wel groen of paars of andere kleuren.')
        self.droomrobot.say('En merk maar hoe fijn jij je op deze plek voelt.')
        self.droomrobot.say('Luister maar lekker naar de golven van de zee.')
        self.droomrobot.play_audio('resources/audio/ocean_waves.wav')
        self.droomrobot.say('Misschien voel je de warme zon op je gezicht, of is het een beetje koel.')
        self.droomrobot.say('Hier kun je alles doen wat je leuk vindt.')
        self.droomrobot.say('Misschien bouw je een groot zandkasteel, of spring je over de golven.')
        motivation = self.droomrobot.ask_open(f'Wat ga jij op het strand doen?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat ga jij op het strand doen?', self.user_model['child_age'],
                                                     motivation)
            self.droomrobot.say(personalized_response)
        self.droomrobot.say("Wat je ook doet, merk maar hoe fijn het is om dat daar te doen!")
    
    def bos_oefenen(self):
        self.droomrobot.say('En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in een prachtig bos bent.')
        self.droomrobot.say('Kijk maar eens om je heen wat je allemaal op die mooie plek ziet.')
        self.droomrobot.say('Misschien zie je hoe bomen, groene blaadjes of een klein diertje.')
        self.droomrobot.say('En merk maar hoe fijn jij je op deze plek voelt.')
        self.droomrobot.say('Luister maar naar de vogels die zingen.')
        self.droomrobot.play_audio('resources/audio/forest-sounds.wav')
        self.droomrobot.say('Misschien voel je de frisse lucht, of schijnt de zon door de bomen op je gezicht.')
        self.droomrobot.say('Hier kun je alles doen wat je leuk vindt.')
        self.droomrobot.say('Misschien klim je in een boom, of zoek je naar dieren.')
        motivation = self.droomrobot.ask_open(f'Wat ga jij doen in het bos?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat ga jij in het bos doen?', self.user_model['child_age'],
                                                     motivation)
            self.droomrobot.say(personalized_response)
        self.droomrobot.say("Merk maar hoe fijn het is om dat te doen!")
    
    def ruimte_oefenen(self):
        self.droomrobot.say('En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je in de ruimte bent, heel hoog in de lucht.')
        self.droomrobot.say('Misschien ben je er alleen, of is er iemand bij je.')
        self.droomrobot.say('Kijk maar eens om je heen, wat zie je daar allemaal?')
        self.droomrobot.say('Misschien zie je de aarde heel klein worden.')
        self.droomrobot.say('Misschien zie je sterren die heel fel schijnen, in verschillende kleuren.')
        self.droomrobot.say('Je voelt je heel rustig en veilig in de ruimte, want er is zoveel te ontdekken.')
        self.droomrobot.say('De ruimte is zo groot, vol met leuke plekken.')
        self.droomrobot.say('Misschien zie je wel regenbogen of ontdek je een speciale ster met grappige dieren er op.')
        motivation = self.droomrobot.ask_open(f'Wat ga jij doen in de ruimte?')
        if motivation:
            personalized_response = self.droomrobot.personalize('Wat ga jij doen in de ruimte?', self.user_model['child_age'],
                                                     motivation)
            self.droomrobot.say(personalized_response)
        #self.droomrobot.say("Misschien zie je sterren die heel fel schijnen, in verschillende kleuren.")
        self.droomrobot.say('Oooooh, merk maar hoe fijn het is om dat daar te doen!')

    def strand_interventie(self):
        self.droomrobot.say('Stel je maar voor dat je weer op het strand bent, op die fijne plek.')
        self.droomrobot.say('Wat zie je daar allemaal? Misschien een grote zee en zacht zand.')
        self.droomrobot.say('Luister maar naar alle fijne geluiden op het strand.')
        self.droomrobot.play_audio('resources/sounds/ocean_waves.wav')
        self.droomrobot.say('Voel het zand maar onder je voeten. Het is lekker zacht en warm.')
        self.droomrobot.say('Als je je tenen beweegt, voel je hoe lekker het zand voelt.')
        self.droomrobot.say('En terwijl je nu zo lekker op het strand bent, zie je een mooie schommel staan.')
        self.droomrobot.say('Die heeft precies jouw lievelingskleur.')
        self.droomrobot.say('Je mag op de schommel gaan zitten.')
        self.droomrobot.say('Voel maar hoe je zachtjes heen en weer gaat.')
        self.droomrobot.say('Voel maar hoe makkelijk de schommel doet wat jij wil, heen en weer, heen en weer.')
        self.droomrobot.say('De schommel gaat precies zo hoog als jij fijn vindt.')
        self.droomrobot.say('Jij bent de baas.')
        self.droomrobot.say('Het kan ook een lekker kriebelend gevoel in je buik geven.')
        self.droomrobot.say('En terwijl je zo lekker aan het schommelen bent, voel je de zachte warme wind op je gezicht.')
        self.droomrobot.say('Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt op het strand.')
        self.droomrobot.say('Je hoort de golven van de zee, terwijl je lekker blijft schommelen.')
        self.droomrobot.say('De zon is net als een warme zachte deken die over je heen gaat.')
        self.droomrobot.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        self.droomrobot.say('Steeds lichter, steeds rustiger, helemaal ontspannen.')
    
    def bos_interventie(self):
        self.droomrobot.say('Stel je maar voor dat je weer in het bos bent, op die fijne plek.')
        self.droomrobot.say('Kijk maar weer naar alle mooie kleuren die om je heen zijn en hoe fijn je je voelt op deze plek.')
        self.droomrobot.say('Luister maar naar alle rustige geluiden in het bos.')
        self.droomrobot.play_audio('resources/audio/forest-sounds.wav')
        self.droomrobot.say('De grond onder je voeten is lekker zacht.')
        self.droomrobot.say('Voel maar hoe fijn het is om hier te zijn.')
        self.droomrobot.say('Kijk, daar hangt een schommel tussen de bomen.')
        self.droomrobot.say('Het is precies jouw lievelingskleur.')
        self.droomrobot.say('Je mag op de schommel gaan zitten. Voel maar hoe je zachtjes heen en weer gaat.')
        self.droomrobot.say('Voel maar hoe makkelijk de schommel doet wat jij wil, heen en weer, heen en weer.')
        self.droomrobot.say('De schommel gaat precies zo hoog als dat jij fijn vindt.')
        self.droomrobot.say('Jij bent de baas.')
        self.droomrobot.say('Het kan ook een lekker kriebelend gevoel in je buik geven.')
        self.droomrobot.say('En terwijl je zo lekker aan het schommelen bent, voel je de frisse lucht op je gezicht.')
        self.droomrobot.say('Merk maar hoe lekker rustig je lichaam wordt en hoe veilig en fijn jij je voelt in het bos.')
        self.droomrobot.say('Je hoort de vogels zachtjes fluiten.')
        self.droomrobot.say('De zon is net als een warme zachte deken die over je heen gaat.')
        self.droomrobot.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker aan het schommelen bent.')
        self.droomrobot.say('Steeds lichter, steeds rustiger, helemaal ontspannen.')
        
    def ruimte_interventie(self):
        self.droomrobot.say('Stel je maar voor dat je weer in de ruimte bent, heel hoog in de lucht.')
        self.droomrobot.say('Wat zie je daar allemaal? Misschien sterren die twinkelen en planeten in mooie kleuren.')
        self.droomrobot.say('Voel maar hoe rustig het is om hier te zweven.')
        self.droomrobot.say('Kijk daar is een ruimteschip! Je mag erin gaan zitten.')
        self.droomrobot.say('Het voelt zacht en veilig. Jij bent de baas.')
        self.droomrobot.say('Het ruimteschip zweeft langzaam met je mee.')
        self.droomrobot.say('In het ruimteschip krijg je een ruimtekapje op.')
        self.droomrobot.say('Het voelt heerlijk zacht tegen je gezicht en het zal je beschermen.')
        self.droomrobot.say('Het houdt je helemaal veilig, zodat je nergens anders aan hoeft te denken dan aan je avontuur in de ruimte.')
        self.droomrobot.say('En terwijl je in het ruimteschip zit, voel je hoe het ruimteschip langzaam met je mee zweeft.')
        self.droomrobot.say('Jij kunt kiezen waar je naartoe wilt zweven, naar de sterren of verder weg.')
        self.droomrobot.say('Voel de rust om je heen, terwijl je door de ruimte zweeft')
        self.droomrobot.say('Kijk, daar is een mooie planeet! Misschien is hij blauw, paars of heeft hij ringen.')
        self.droomrobot.say('Je voelt je veilig en stoer als een echte astronaut.')
        self.droomrobot.say('Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker in de ruimte zweeft.')
        self.droomrobot.say('Steeds lichter, steeds rustiger, helemaal ontspannen.')

