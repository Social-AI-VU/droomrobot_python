import abc
from enum import Enum
from threading import Event
from time import sleep

from droomrobot.core import Droomrobot


class InteractionChoiceNotAvailable(Exception):
    """Raised when the list of move branches does not have a certain choice option available"""
    pass


class InteractionContext(Enum):
    SONDE = 1
    KAPINDUCTIE = 2
    BLOEDAFNAME = 3


class InteractionSession(Enum):
    INTRODUCTION = 1
    INTERVENTION = 2
    GOODBYE = 3


class InterventionPhase(Enum):
    PREPARATION = 1
    PROCEDURE = 2
    WRAPUP = 3


class InteractionChoiceCondition(Enum):
    HASVALUE = 1
    MATCHVALUE = 2
    PHASE = 3


class InteractionMove:
    def __init__(self, func, *args, user_model_key=None, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.user_model_key = user_model_key

    def resolve(self, value):
        return value() if callable(value) else value

    def execute(self):
        if callable(self.func) and not self.args and not self.kwargs:
            # lambda or fully-wrapped func
            return self.func()
        else:
            resolved_args = [self.resolve(arg) for arg in self.args]
            resolved_kwargs = {k: self.resolve(v) for k, v in self.kwargs.items()}
            return self.func(*resolved_args, **resolved_kwargs)


class InteractionChoice:

    def __init__(self, target: str, condition: InteractionChoiceCondition):
        self.target = target
        self.condition = condition
        self.moves = {}

    def execute(self, data: dict | str):
        try:
            if self.condition == InteractionChoiceCondition.HASVALUE:
                if self.target in data:
                    if isinstance(data, dict) and data[self.target] is None:
                        return self.moves['fail']
                    return self.moves['success']
                else:
                    return self.moves['fail']
            elif self.condition == InteractionChoiceCondition.MATCHVALUE:
                if self.target in data:
                    if data[self.target] is not None:
                        if data[self.target] in self.moves:
                            return self.moves[data[self.target]]
                        else:
                            return self.moves['other']
                return self.moves['fail']
            elif self.condition == InteractionChoiceCondition.PHASE:
                if data in self.moves:
                    return self.moves[data]
                else:
                    raise InteractionChoiceNotAvailable(f"{data} is not available.")
            else:
                raise InteractionChoiceNotAvailable(f"{self.condition} is not available as a condition")
        except KeyError as e:
            raise InteractionChoiceNotAvailable(f"{e} is not available.")

    def add_move(self, option: str | list, func, *args, **kwargs):
        options = [option] if isinstance(option, str) else option
        for item in options:
            self.moves.setdefault(item, []).append(InteractionMove(func, *args, **kwargs))

    def add_choice(self, option: str, choice: "InteractionChoice"):
        if option not in self.moves:
            self.moves[option] = []
        self.moves[option].append(choice)


class DroomrobotScript:

    def __init__(self, droomrobot: Droomrobot, interaction_context: InteractionContext):

        # Droomrobot
        self.droomrobot = droomrobot

        # Interaction information
        self.participant_id = None
        self.session = None
        self.interaction_context = interaction_context
        self.user_model = {}

        # Script management
        self.interaction_moves = []
        self.script_idx = 0

        self.is_running = True
        self.pause_event = Event()
        self.pause_event.set()

        self.phases = []
        self.current_phase = 0
        self.phase_moves = None
        self._requested_phase = None

    @abc.abstractmethod
    def prepare(self, participant_id: str, session: InteractionSession, user_model_addendum: dict):
        self.participant_id = participant_id
        self.session = session
        self.user_model = self.droomrobot.load_user_model(participant_id=self.participant_id)
        self.user_model.update(user_model_addendum)

        if 'droomplek' in self.user_model:
            self.user_model['droomplek_lidwoord'] = self.droomrobot.get_article(self.user_model['droomplek'])

        if 'kleur' in self.user_model:
            self.user_model['kleur_adjective'] = self.droomrobot.get_adjective(self.user_model['kleur'])

    def add_move(self, func, *args, **kwargs):
        self.interaction_moves.append(InteractionMove(func, *args, **kwargs))

    def add_choice(self, interaction_choice: InteractionChoice):
        self.interaction_moves.append(interaction_choice)

    def run(self):
        if self.phases and self.phase_moves:
            self.interaction_moves = self.phase_moves.execute(self.phases[self.current_phase])

        self.script_idx = 0
        while self.script_idx < len(self.interaction_moves) and self.is_running:
            self.pause_event.wait()

            # Handle phase switch request BEFORE executing next move
            if self._requested_phase:
                self._switch_to_requested_phase()

            move = self.interaction_moves[self.script_idx]

            if isinstance(move, InteractionMove):
                result = move.execute()
                if move.user_model_key:
                    self.user_model[move.user_model_key] = result
                    self.droomrobot.save_user_model(self.participant_id, self.user_model)
                self.script_idx += 1

            elif isinstance(move, InteractionChoice):
                moves = move.execute(self.user_model)
                self.interaction_moves[self.script_idx:self.script_idx + 1] = moves  # insert the moves beloning to the choice in the list

        self.is_running = False
        if self._requested_phase:
            self._switch_to_requested_phase()

    def stop(self):
        self.is_running = False

    def pause(self):
        self.pause_event.clear()

    def resume(self):
        self.pause_event.set()

    def next_phase(self, phase: str):
        if not self.phases or not self.phase_moves:
            raise InteractionChoiceNotAvailable("No phases available.")

        if phase not in self.phases:
            raise InteractionChoiceNotAvailable(f"{phase} is not available.")

        if self.is_running:
            # Request the phase switch
            self._requested_phase = phase
        else:  # restart if not is running anymore
            self.current_phase = self.phases.index(phase)
            self.is_running = True
            self.run()

    def _switch_to_requested_phase(self):
        phase = self._requested_phase
        self._requested_phase = None

        self.interaction_moves = self.phase_moves.execute(phase)
        self.current_phase = self.phases.index(phase)
        self.script_idx = 0

        if not self.is_running:
            self.is_running = True
            self.run()

    def repeat_sentences(self, sentences: list):
        sentence_idx = 0
        while not self._requested_phase and self.is_running:
            total_wait = 5
            interval = 0.1
            waited = 0
            while waited < total_wait:
                if self._requested_phase or not self.is_running:
                    return
                sleep(interval)
                waited += interval
            if not self._requested_phase:
                self.droomrobot.say(sentences[sentence_idx])
                if sentence_idx < len(sentences) - 1:
                    sentence_idx += 1
                else:
                    sentence_idx = 0

    def set_user_model_variable(self, key: str, value):
        self.user_model[key] = value



