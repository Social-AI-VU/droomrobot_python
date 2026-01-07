from droomrobot.core import Droomrobot, AnimationType
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext, InteractionChoice, \
    InteractionChoiceCondition


class IntroductionFactory:

    @staticmethod
    def age4(droomrobot: Droomrobot, interaction_context: InteractionContext, user_model):
        script = DroomrobotScript(droomrobot, interaction_context)

        script.add_move(droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True)
        script.add_move(droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        script.add_move(droomrobot.say, 'Hoi hoi, ik ben de droomrobot.')
        script.add_move(droomrobot.say, 'Ik ben hier om te leren hoe ik kinderen kan helpen.')
        script.add_move(droomrobot.say, 'Wat fijn dat jij mij daar bij wilt helpen.')
        script.add_move(droomrobot.say, 'Zo helpen we elkaar een beetje!')

        script.add_move(droomrobot.ask_fake, 'Hoe heet jij?', 3)
        script.add_move(droomrobot.say, lambda: f'Wat leuk om je te ontmoeten {user_model['child_name']}')
        script.add_move(droomrobot.say, 'We gaan kletsen en samen op droomreis.')
        script.add_move(droomrobot.say, 'Hoe dat werkt zal ik zo vertellen.')
        script.add_move(droomrobot.say, 'Ik zal je eerst uitleggen hoe je met mij kunt praten.')
        script.add_move(droomrobot.say, 'Mijn mondje wordt groen als ik luister.')
        script.add_move(droomrobot.say, 'Dan kun je lekker luid en duidelijk je antwoord geven.')
        script.add_move(droomrobot.say, 'Soms moet ik even nadenken, en dan duurt het even voordat ik weer wat zeg.')
        script.add_move(droomrobot.say, 'En omdat ik nog maar aan het leren ben, gaat het soms ook mis.')
        script.add_move(droomrobot.say, 'Maar dat hoort er bij. Ik stel de vraag dan gewoon nog een keer.')
        script.add_move(droomrobot.say, 'Degene die met je mee is mag ook helpen.')

        script.add_move(droomrobot.say, 'Laten we even oefenen!')

        script.add_move(droomrobot.ask_entity,
                        'Welk dier vind jij heel cool?',
                        {'animals': 1},
                        'animals',
                        'animals',
                        user_model_key='dier')
        animal_choice = InteractionChoice('dier', InteractionChoiceCondition.HASVALUE)
        animal_choice.add_move('success', droomrobot.say, lambda: f'Een {user_model['dier']}')
        animal_choice.add_move('success', lambda: droomrobot.say(
            droomrobot.generate_funny_response(user_model['child_age'],
                                               'Je hebt een kennismakingsgesprek en je hebt net gevraagd '
                                               'naar een dier dat het kind heel cool vind.',
                                               user_model['dier'])))
        animal_choice.add_move('fail', droomrobot.say, 'Cool zeg.')
        script.add_choice(animal_choice)
        script.add_move(droomrobot.say, 'Ik zelf vind een schaap een prachtig dier.')
        script.add_move(droomrobot.say, 'Ik zou wel een ritje willen maken op een schaap.')
        script.add_move(droomrobot.say, 'Al val ik dan misschien wel in slaap in het zachte wol.')

        script.add_move(droomrobot.say, 'Laat ik nu wat vertellen over de droomreis.')
        script.add_move(droomrobot.say, 'Je mag zo een fijne plek kiezen.')
        script.add_move(droomrobot.say, 'En dan gaan we samen dromen dat we daar heen gaan.')
        script.add_move(droomrobot.say, 'In onze gedachten.')
        script.add_move(droomrobot.say, 'Aan iets fijns denken helpt je om rustig en sterk te blijven.')

        return script.interaction_moves

    @staticmethod
    def age6_9(droomrobot: Droomrobot, interaction_context: InteractionContext, user_model):
        script = DroomrobotScript(droomrobot, interaction_context)

        script.add_move(droomrobot.animate, AnimationType.ACTION, "random_short4", run_async=True)
        script.add_move(droomrobot.animate, AnimationType.EXPRESSION, "emo_007", run_async=True)
        script.add_move(droomrobot.say, 'Hoi hoi, ik ben de droomrobot.')
        script.add_move(droomrobot.say, 'Ik ben hier om te leren hoe ik kinderen kan helpen.')
        script.add_move(droomrobot.say, 'Wat fijn dat jij mij daar bij wilt helpen.')
        script.add_move(droomrobot.say, 'Zo helpen we elkaar een beetje!')

        script.add_move(droomrobot.ask_fake, 'Hoe heet jij?', 3)
        script.add_move(droomrobot.say, lambda: f'Wat leuk om je te ontmoeten {user_model['child_name']}')
        script.add_move(droomrobot.say, 'We gaan kletsen en samen op droomreis.')
        script.add_move(droomrobot.say, 'Hoe dat werkt zal ik zo vertellen.')
        script.add_move(droomrobot.say, 'Ik zal je eerst uitleggen hoe je met mij kunt praten.')
        script.add_move(droomrobot.say, 'Mijn mond wordt groen als ik luister.')
        script.add_move(droomrobot.say, 'Dan kun je lekker luid en duidelijk je antwoord geven.')
        script.add_move(droomrobot.say, 'Soms moet ik even nadenken, en dan duurt het even voordat ik weer wat zeg.')
        script.add_move(droomrobot.say, 'En omdat ik nog maar aan het leren ben, gaat het soms ook mis.')
        script.add_move(droomrobot.say, 'Maar dat hoort er bij. Ik stel de vraag dan gewoon nog een keer.')
        script.add_move(droomrobot.say, 'Degene die met je mee is mag ook helpen.')

        script.add_move(droomrobot.say, 'Laten we even oefenen!')

        script.add_move(droomrobot.ask_entity,
                        'Welk dier vind jij heel cool?',
                        {'animals': 1},
                        'animals',
                        'animals',
                        user_model_key='dier')
        animal_choice = InteractionChoice('dier', InteractionChoiceCondition.HASVALUE)
        animal_choice.add_move('success', droomrobot.say, lambda: f'Een {user_model['dier']}')
        animal_choice.add_move('success', lambda: droomrobot.say(
            droomrobot.generate_funny_response(user_model['child_age'],
                                               'Je hebt een kennismakingsgesprek en je hebt net gevraagd '
                                               'naar een dier dat het kind heel cool vind.',
                                               user_model['dier'])))
        animal_choice.add_move('fail', droomrobot.say, 'Cool zeg.')
        script.add_choice(animal_choice)
        script.add_move(droomrobot.say, 'Ik zelf vind een schaap een prachtig dier.')
        script.add_move(droomrobot.say, 'Ik zou wel een ritje willen maken op een schaap.')
        script.add_move(droomrobot.say, 'Al val ik dan misschien wel in slaap in het zachte wol.')

        script.add_move(droomrobot.say, 'Laat ik nu wat vertellen over de droomreis.')
        script.add_move(droomrobot.say, 'Je mag zo een fijne plek kiezen.')
        script.add_move(droomrobot.say, 'En dan gaan we samen fantaseren dat we daar heen gaan.')
        script.add_move(droomrobot.say, 'In onze gedachten.')
        script.add_move(droomrobot.say, 'Aan iets fijns denken helpt je om rustig en sterk te blijven.')

        return script.interaction_moves