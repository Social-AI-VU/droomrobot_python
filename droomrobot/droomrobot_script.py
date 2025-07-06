import abc
from enum import Enum
from threading import Event

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
        if self.condition == InteractionChoiceCondition.HASVALUE:
            if self.target in data:
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

    def add_move(self, option: str, func, *args, **kwargs):
        if option not in self.moves:
            self.moves[option] = []
        self.moves[option].append(InteractionMove(func, *args, **kwargs))

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
        self.is_running = True
        self.pause_event = Event()
        self.pause_event.set()
        self.phases = []
        self.current_phase = 0
        self.phase_moves = None


    @abc.abstractmethod
    def prepare(self, participant_id: str, session: InteractionSession, user_model_addendum: dict):
        self.participant_id = participant_id
        self.user_model = self.droomrobot.load_user_model(participant_id=participant_id)
        self.user_model.update(user_model_addendum)

        if 'droomplek' in self.user_model:
            self.user_model['droomplek_lidwoord'] = self.droomrobot.get_article(self.user_model['droomplek'])

    def add_move(self, func, *args, **kwargs):
        self.interaction_moves.append(InteractionMove(func, *args, **kwargs))

    def add_interaction_choice(self, interaction_choice: InteractionChoice):
        self.interaction_moves.append(interaction_choice)

    def run(self):
        self.droomrobot.start_logging(self.participant_id, {
            'participant_id': self.participant_id,
            'context': self.interaction_context.name,
            'session': self.session,
            'child_age': self.user_model['child_age']
        })

        if self.phases and self.phase_moves:
            self.interaction_moves = self.phase_moves.execute(self.phases[self.current_phase])

        i = 0
        while i < len(self.interaction_moves) and self.is_running:
            self.pause_event.wait()
            move = self.interaction_moves[i]

            if isinstance(move, InteractionMove):
                result = move.execute()
                if move.user_model_key:
                    self.user_model[move.user_model_key] = result
                    self.droomrobot.save_user_model(self.participant_id, self.user_model)
                i += 1

            elif isinstance(move, InteractionChoice):
                moves = move.execute(self.user_model)
                self.interaction_moves[i:i + 1] = moves  # insert the moves beloning to the choice in the list

        self.droomrobot.stop_logging()

    def stop(self):
        self.is_running = False

    def pause(self):
        self.pause_event.clear()

    def resume(self):
        self.pause_event.set()
    
    def to_phase(self, phase: str):
        if self.phases and self.phase_moves:
            if phase not in self.phases:
                raise InteractionChoiceNotAvailable(f"{phase} is not available.")
            self.pause()
            self.interaction_moves = self.phase_moves.execute(phase)
            self.current_phase = self.phases.index(phase)
            self.resume()
        else:
            raise InteractionChoiceNotAvailable(f"No phases available.")


