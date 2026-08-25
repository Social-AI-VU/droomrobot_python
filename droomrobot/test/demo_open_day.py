from json import load
from os.path import abspath, join

from sic_framework.core.sic_application import SICApplication
from sic_framework.devices.common_mini.mini_speaker import MiniSpeakersConf

from droomrobot.core import Droomrobot, SDKAnimationType, InteractionConf
from droomrobot.droomrobot_control import DroomrobotControl
from droomrobot.droomrobot_script import DroomrobotScript, InteractionContext
from droomrobot.droomrobot_tts import ElevenLabsTTSConf
from droomrobot.sonde4 import Sonde4
from sic_framework.devices.alphamini import Alphamini, SDKAnimationType



def guided_visualization():
    droomrobot_control.droomrobot.say('Hi there, I am the dream robot.')
    droomrobot_control.droomrobot.say('In a moment, you can choose a wonderful place.')
    droomrobot_control.droomrobot.say('And then we will imagine together that we are going there.')
    droomrobot_control.droomrobot.say('In our minds.')
    droomrobot_control.droomrobot.say('Thinking about something nice helps you stay calm and strong.')
    droomrobot_control.droomrobot.say('You can choose from the beach, the forest, the playground, or outer space.')

    dream_place = droomrobot_control.droomrobot.ask_entity('What is the place where you feel happy?',
                                         {'droomplek': 1},
                                         'droomplek',
                                         'droomplek')

    if dream_place == 'strand':
        dream_place_article = 'the'
        dream_place = 'beach'
        droomrobot_control.droomrobot.say('Ah, the beach! I can almost hear the waves and feel the sand under my feet.')
        droomrobot_control.droomrobot.say('Do you know what I love to do there? Build a sandcastle with a flag on top.')
    elif dream_place == 'bos':
        dream_place_article = 'the'
        dream_place = 'forest'
        droomrobot_control.droomrobot.say('The forest, what a peaceful place! I love the tall trees and the soft moss on the ground.')
        droomrobot_control.droomrobot.say(
            'Do you know what I love to do there? I look for animals that are hiding, like birds or squirrels.')
    elif dream_place == 'speeltuin':
        dream_place_article = 'the'
        dream_place = 'playground'
        droomrobot_control.droomrobot.say('The playground, what a cheerful place! I love the slide and the swing.')
        droomrobot_control.droomrobot.say('Do you know what I love to do there? Swing really high, almost up to the stars.')
    elif dream_place == 'ruimte':
        dream_place_article = ''
        dream_place = 'space'
        droomrobot_control.droomrobot.say(
            'Outer space, what an adventurous place! I imagine being in a rocket and flying past the stars.')
        droomrobot_control.droomrobot.say(
            'Do you know what I would love to do there? Wave to the planets and look for aliens who want to play.')
    else:
        dream_place = 'beach'
        dream_place_article = 'the'
        droomrobot_control.droomrobot.say("Oh sorry, I didn't quite understand you.")
        droomrobot_control.droomrobot.say('You know what? I think the beach is really wonderful.')
        droomrobot_control.droomrobot.say("Let's go to the beach as our dream spot.")

    droomrobot_control.droomrobot.say(f'Imagine that you are at {dream_place_article} {dream_place}.')
    droomrobot_control.droomrobot.say('Just look around in your head and see everything at that beautiful place.')
    droomrobot_control.droomrobot.say('Look at all the beautiful colors you see around you.')
    droomrobot_control.droomrobot.say('Maybe green, or purple, or even rainbow colors.')
    droomrobot_control.droomrobot.say('And notice how happy you feel in this place.', sleep_time=1)
    droomrobot_control.droomrobot.say('Breathe in deeply through your nose.')
    droomrobot_control.droomrobot.play_audio('../resources/audio/breath_in_amplified.wav')
    droomrobot_control.droomrobot.say('And blow out slowly through your mouth.')
    droomrobot_control.droomrobot.play_audio('../resources/audio/breath_out_amplified.wav')
    droomrobot_control.droomrobot.say('Well done, you are doing a great job.', sleep_time=1)
    droomrobot_control.droomrobot.say('And now you will notice a small, warm light appearing on your finger.')
    droomrobot_control.droomrobot.say('That light is magical, and it charges up your strength.')
    droomrobot_control.droomrobot.say('Imagine what that light looks like.')
    droomrobot_control.droomrobot.say('Is it yellow, orange, or maybe your favorite color?')

    color = droomrobot_control.droomrobot.ask_entity_llm('What color is your light?', strict=True)

    droomrobot_control.droomrobot.say(f'Your {color} light appears on your finger.')
    droomrobot_control.droomrobot.say('See the light getting stronger and stronger.')
    droomrobot_control.droomrobot.say('This way you become a superhero, and you can help yourself.')
    droomrobot_control.droomrobot.say(f'And whenever you need it, imagine your {color} light shining even brighter.')
    droomrobot_control.droomrobot.say('That means your strength is fully charged.')
    droomrobot_control.droomrobot.say('You can make the light even stronger by wiggling your toes.')
    droomrobot_control.droomrobot.say('It gives off a soft, safe glow to help you.')
    droomrobot_control.droomrobot.say('If you feel something on your finger, then the light is working perfectly.')
    droomrobot_control.droomrobot.say(
        f'And now that your {color} light is shining bright, you can continue playing at {dream_place_article} {dream_place}.')
    droomrobot_control.droomrobot.say('That is all for now.')
    droomrobot_control.droomrobot.say('Thank you for letting me help you today.')
    droomrobot_control.droomrobot.say('You helped yourself very well!')

def geleide_fantasie():
    interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=True,
                                       amplified=False, always_regenerate=False)
    droomrobot_control.droomrobot.set_interaction_conf(interaction_conf)

    droomrobot_control.droomrobot.say('Hoi hoi, ik ben de droomrobot.')
    droomrobot_control.droomrobot.say('Je mag zo een fijne plek kiezen.')
    droomrobot_control.droomrobot.say('En dan gaan we samen fantaseren dat we daar heen gaan.')
    droomrobot_control.droomrobot.say('In onze gedachten.')
    droomrobot_control.droomrobot.say('Aan iets fijns denken helpt je om rustig en sterk te blijven.')
    droomrobot_control.droomrobot.say('Je kunt kiezen uit het strand, het bos, de speeltuin of de ruimte.')

    droomplek = droomrobot_control.droomrobot.ask_entity('Wat is de plek waar jij je fijn voelt?',
                  {'droomplek': 1},
                  'droomplek',
                  'droomplek')

    if droomplek == 'strand':
        droomplek_lidwoord = 'het'
        droomrobot_control.droomrobot.say('Ah, het strand! Ik kan de golven bijna horen en het zand onder mijn voeten voelen.')
        droomrobot_control.droomrobot.say('Weet je wat ik daar graag doe? Een zandkasteel bouwen met een vlag er op.')
    elif droomplek == 'bos':
        droomplek_lidwoord = 'het'
        droomrobot_control.droomrobot.say('Het bos, wat een rustige plek! Ik hou van de hoge bomen en het zachte mos op de grond.')
        droomrobot_control.droomrobot.say('Weet je wat ik daar graag doe? Ik zoek naar dieren die zich verstoppen, zoals vogels of eekhoorns.')
    elif droomplek == 'speeltuin':
        droomplek_lidwoord = 'de'
        droomrobot_control.droomrobot.say('De speeltuin, wat een vrolijke plek! Ik hou van de glijbaan en de schommel.')
        droomrobot_control.droomrobot.say('Weet je wat ik daar graag doe? Heel hoog schommelen, bijna tot aan de sterren.')
    elif droomplek == 'ruimte':
        droomplek_lidwoord = 'de'
        droomrobot_control.droomrobot.say('De ruimte, wat een avontuurlijke plek! Ik stel me voor dat ik in een raket zit en langs de sterren vlieg.')
        droomrobot_control.droomrobot.say('Weet je wat ik daar graag zou doen? Zwaaien naar de planeten en zoeken naar aliens die willen spelen.')
    else:
        droomplek = 'strand'
        droomplek_lidwoord = 'het'
        droomrobot_control.droomrobot.say('Oh sorry ik begreep je even niet.')
        droomrobot_control.droomrobot.say('Weet je wat. Ik vind het strand echt super leuk.')
        droomrobot_control.droomrobot.say('Laten we naar het strand gaan als droomplek.')

    # interaction_conf = InteractionConf(speaking_rate=0.75, sleep_time=0.5, animated=False,
    #                                    amplified=False,
    #                                    always_regenerate=False)
    # droomrobot_control.droomrobot.set_interaction_conf(interaction_conf)

    droomrobot_control.droomrobot.say(f'Stel je voor dat je bij {droomplek_lidwoord} {droomplek} bent.')
    droomrobot_control.droomrobot.say('Kijk maar eens in je hoofd om je heen, wat je allemaal op die mooie plek ziet.')
    droomrobot_control.droomrobot.say('Kijk maar welke mooie kleuren je allemaal om je heen ziet.')
    droomrobot_control.droomrobot.say('Misschien wel groen, of paars, of regenboog kleuren.')
    droomrobot_control.droomrobot.say('En merk maar hoe fijn jij je op deze plek voelt.')
    droomrobot_control.droomrobot.say('Adem diep in door je neus.', )
    droomrobot_control.droomrobot.play_audio('../resources/audio/breath_in_amplified.wav')
    droomrobot_control.droomrobot.say('en blaas langzaam uit door je mond.')
    droomrobot_control.droomrobot.play_audio('../resources/audio/breath_out_amplified.wav')
    droomrobot_control.droomrobot.say(f'Goed zo, dat doe je al heel knap.')
    droomrobot_control.droomrobot.say('En nu zal je merken dat er een klein, warm, lichtje op je vinger verschijnt.')
    droomrobot_control.droomrobot.say('Dat lichtje is magisch, en laadt jouw kracht op.')
    droomrobot_control.droomrobot.say('Stel je eens voor, hoe dat lichtje eruit ziet.')
    droomrobot_control.droomrobot.say('Is het geel, oranje, of misschien jouw lievelingskleur?')
    kleur = droomrobot_control.droomrobot.ask_entity_llm('Welke kleur heeft jouw lichtje?', strict=True)
    kleur_adjective = droomrobot_control.droomrobot.get_adjective(kleur)
    droomrobot_control.droomrobot.say(f'Je {kleur_adjective} lichtje verschijnt op je vinger.')
    droomrobot_control.droomrobot.say('Zie het lichtje steeds sterker worden.')
    droomrobot_control.droomrobot.say('Zo word jij een superheld, en kun je jezelf helpen.')
    droomrobot_control.droomrobot.say(f'En als je het nodig hebt, stel je voor dat je {kleur_adjective} lichtje nog helderder gaat schijnen.')
    droomrobot_control.droomrobot.say('Dat betekent dat jouw kracht helemaal opgeladen is.')
    droomrobot_control.droomrobot.say('je kunt het lichtje nog sterker maken door met je tenen te wiebelen.')
    droomrobot_control.droomrobot.say('Het geeft een zachte, veilige gloed om je te helpen.')
    droomrobot_control.droomrobot.say(f'Als je iets voelt op je vinger, dan werkt het lichtje helemaal.')
    droomrobot_control.droomrobot.say(f'En nu je {kleur_adjective} lichtje goed aan staat,. kan jij weer verder spelen bij {droomplek_lidwoord} {droomplek}.')
    droomrobot_control.droomrobot.say('Dat was het weer.')
    droomrobot_control.droomrobot.say('Bedankt dat ik je mocht helpen vandaag.')
    droomrobot_control.droomrobot.say('Je hebt jezelf heel goed geholpen!.')

def dance():
    droomrobot_control.droomrobot.say("Laten we dansen.")
    droomrobot_control.droomrobot.animate(SDKAnimationType.ACTION, "dance_0007en", run_async=True)
    droomrobot_control.droomrobot.play_audio('../resources/audio/happy_dance.wav')

app = SICApplication()

# droomrobot = Droomrobot(sic_app=app, mini_ip="10.0.0.228", mini_id="00268", mini_password="alphago",
#                             redis_ip="10.0.0.109",
#                             google_keyfile_path=abspath(join("../../conf", "google", "google_keyfile.json")),
#                             env_path=abspath(join("../../conf", ".env")),
#                             sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
#                             dialogflow_timeout=10.0,
#                             tts_conf=ElevenLabsTTSConf(),
#                             computer_test_mode=False)
# interaction_context = InteractionContext.SONDE
# droomrobot_script = DroomrobotScript(droomrobot=droomrobot, interaction_context=interaction_context)
droomrobot_control = DroomrobotControl()
droomrobot_control.connect(sic_app=app, mini_ip="10.0.0.155", mini_id="00268", mini_password="alphago",
                            redis_ip="10.0.0.109",
                            google_keyfile_path=abspath(join("../../conf", "google", "google_keyfile.json")),
                            env_path=abspath(join("../../conf", ".env")),
                            sample_rate_dialogflow_hertz=44100, dialogflow_language="nl",
                            dialogflow_timeout=10.0,
                            tts_conf=ElevenLabsTTSConf(),
                            computer_test_mode=True)

# droomrobot_control.droomrobot = Alphamini(ip="10.0.0.228",
#                                             mini_id="00297",
#                                             mini_password="alphago",
#                                             redis_ip="10.0.0.109",
#                                             speaker_conf=MiniSpeakersConf(sample_rate=44100),
#                                             bypass_install=True)

# file_path = "../user_models/user_model_999.json"
# with open(file_path, "r", encoding="utf-8") as file:
#     user_model = load(file)
# print(user_model)


while True:
    choice = input("\n[EN] english | [NL] dutch | [D] dance | [Q] quit: ").lower()

    if choice == 'en':
        guided_visualization()
    elif choice == 'nl':
        geleide_fantasie()
    elif choice == 'd':
        dance()
    elif choice == 'q':
        exit()  # Stop everything

# dances = ['dance_0004en', 'dance_0005en', 'dance_0006en', 'dance_0007en', 'dance_0008en', 'dance_0009en', 'dance_0011en', 'dance_0013']
#
# for dance in dances:
#     droomrobot_control.droomrobot.say(dance)
#     droomrobot_control.droomrobot.animate(AnimationType.ACTION, dance)
