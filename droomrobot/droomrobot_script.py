import abc
from enum import Enum
from threading import Event, Thread, Lock
from time import sleep

from droomrobot.core import Droomrobot
from pathlib import Path

prompt_file = Path(__file__).parent / "resources" / "prompts" / "droomplek_keuze.txt" 
with open(prompt_file, 'r', encoding='utf-8') as f:
    droomplek_choice_prompt = f.read()

imagery_prompt_file = Path(__file__).parent / "resources" / "prompts" / "droomplek_imagery.txt"
with open(imagery_prompt_file, 'r', encoding='utf-8') as f:
    droomplek_imagery_prompt = f.read()
    

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
        self.audio_amplified = False
        self.always_regenerate = False

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
        
        # Background generation storage
        self._pending_futures = {} 

    @abc.abstractmethod
    def prepare(self, participant_id: str, session: InteractionSession, user_model_addendum: dict,
                audio_amplified: bool = False, always_regenerate: bool = False):
        self.participant_id = participant_id
        self.session = session
        self.user_model = self.droomrobot.load_user_model(participant_id=self.participant_id)
        self.user_model.update(user_model_addendum)
        self.audio_amplified = audio_amplified
        self.always_regenerate = always_regenerate

        if 'droomplek' in self.user_model:
            self.user_model['droomplek_lidwoord'] = self.droomrobot.get_article(self.user_model['droomplek'])

        #if 'kleur' in self.user_model:
        #    self.user_model['kleur_adjective'] = self.droomrobot.get_adjective(self.user_model['kleur'])
            
        # Colour context
        if 'kleur' in self.user_model and self.user_model['kleur']:
            kleur_context = f"De lievelingskleur van het kind is: {self.user_model['kleur']}."
            kleur_adjective = self.droomrobot.get_adjective(self.user_model['kleur'])
            kleur_context += f" Het bijvoeglijk naamwoord is: {kleur_adjective}."
        else:
            kleur_context = "De lievelingskleur van het kind is niet bekend."

        # Companion context
        if 'metgezel' in self.user_model and self.user_model['metgezel']:
            metgezel_context = f"Het kind wil graag {self.user_model['metgezel']} meenemen op avontuur."
        else:
            metgezel_context = "Het kind heeft geen specifieke metgezel genoemd."


    # ----------------------------------
    # Background prompt functions:
    # ----------------------------------
    def _fire_background_prompt(self, key, generate_func, *args, **kwargs):
        """Fire an LLM generation in a background thread."""
        def _worker():
            try:
                result = generate_func(*args, **kwargs)
                self._pending_futures[key] = ('success', result)
            except Exception as e:
                self._pending_futures[key] = ('error', str(e))
                print(f"[Background] Prompt {key} failed: {e}")

        self._pending_futures[key] = ('pending', None)
        thread = Thread(target=_worker, daemon=True)
        thread.start()
        
    def _await_background_prompt(self, key, timeout=60):
        """Block until a background prompt result is ready."""
        import time
        start = time.time()
        while time.time() - start < timeout:
            if key in self._pending_futures:
                status, result = self._pending_futures[key]
                if status == 'success':
                    del self._pending_futures[key]
                    return result
                elif status == 'error':
                    del self._pending_futures[key]
                    return None
            time.sleep(0.2)
        print(f"[Background] Prompt {key} timed out after {timeout}s")
        return None
    
    
    # ----------------------------------
    # Script functions:
    # ----------------------------------
    def add_move(self, func, *args, **kwargs):
        self.interaction_moves.append(InteractionMove(func, *args, **kwargs))

    def add_choice(self, interaction_choice: InteractionChoice):
        self.interaction_moves.append(interaction_choice)

    def add_moves(self, moves: list):
        self.interaction_moves.extend(moves)

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
                    thread = Thread(
                        target = self.prepare_user_model_audio,
                        args = (move.user_model_key,),
                        daemon = True)
                    thread.start()
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
                    
                    
    # ----------------------------------
    # User model functions:
    # ----------------------------------

    def set_user_model_variable(self, key: str, value):
        self.user_model[key] = value
        self.droomrobot.save_user_model(self.participant_id, self.user_model)

    def set_user_model_variables(self, updates: dict):
        self.user_model.update(updates)
        self.droomrobot.save_user_model(self.participant_id, self.user_model)
    
    def ensure_default_droomplek_motivatie(self, default_value: str = "spelen"):
        motivation = self.user_model.get('droomplek_motivatie')
        if motivation is None:
            self.set_user_model_variable('droomplek_motivatie', default_value)
            return

        normalized = str(motivation).strip().lower()
        if normalized in {"", "none", "niet bekend"}:
            self.set_user_model_variable('droomplek_motivatie', default_value)


    # ----------------------------------
    # Interaction functions & LLM calls personalisation:
    # ----------------------------------
    """def build_interaction_choice_droomplek(self) -> InteractionChoice:
        interaction_choice = InteractionChoice('droomplek_raw_answer', InteractionChoiceCondition.HASVALUE)

        def _store_first_payload():
            payload = self.droomrobot.generate_droomplek_payload(
                child_name=self.user_model['child_name'],
                child_age=self.user_model['child_age'],
                child_answer=self.user_model['droomplek_raw_answer']
            )
            self.set_user_model_variables({
                'droomplek_speech_text': payload['speech_text'],
                'droomplek_candidate': payload['dream_place_final'],
                'droomplek_candidate_lidwoord': payload['dream_place_article'],
                'place_decided': payload['place_decided'],
            })

        interaction_choice.add_move('success', _store_first_payload)

        first_decision_choice = InteractionChoice('place_decided', InteractionChoiceCondition.MATCHVALUE)

        # CASE 1: first answer is a valid place -> promote and ask for motivation
        def _promote_first_payload():
            self.set_user_model_variables({
                'droomplek': self.user_model['droomplek_candidate'],
                'droomplek_lidwoord': self.user_model['droomplek_candidate_lidwoord'],
            })

        first_decision_choice.add_move([True], _promote_first_payload)
        first_decision_choice.add_move(
            [True],
            self.droomrobot.ask_open,
            lambda: self.user_model['droomplek_speech_text'],
            user_model_key='droomplek_motivatie'
        )

        # CASE 2: first answer vague/inappropriate -> ask once more
        first_decision_choice.add_move(
            [False],
            self.droomrobot.ask_open,
            lambda: self.user_model['droomplek_speech_text'],
            user_model_key='droomplek_second_answer'
        )

        second_answer_choice = InteractionChoice('droomplek_second_answer', InteractionChoiceCondition.HASVALUE)

        def _store_second_payload():
            payload = self.droomrobot.generate_droomplek_payload(
                child_name=self.user_model['child_name'],
                child_age=self.user_model['child_age'],
                child_answer=self.user_model['droomplek_second_answer']
            )
            self.set_user_model_variables({
                'droomplek_speech_text_second': payload['speech_text'],
                'droomplek_candidate_second': payload['dream_place_final'],
                'droomplek_candidate_lidwoord_second': payload['dream_place_article'],
                'place_decided_second': payload['place_decided'],
            })

        second_answer_choice.add_move('success', _store_second_payload)

        second_decision_choice = InteractionChoice('place_decided_second', InteractionChoiceCondition.MATCHVALUE)

        # CASE 2A: second answer is valid -> promote and ask for motivation
        def _promote_second_payload():
            self.set_user_model_variables({
                'droomplek': self.user_model['droomplek_candidate_second'],
                'droomplek_lidwoord': self.user_model['droomplek_candidate_lidwoord_second'],
            })

        second_decision_choice.add_move([True], _promote_second_payload)
        second_decision_choice.add_move(
            [True],
            self.droomrobot.ask_open,
            lambda: self.user_model['droomplek_speech_text_second'],
            user_model_key='droomplek_motivatie'
        )

        # CASE 2B: second answer still not valid -> fallback to strand
        def _store_strand_fallback():
            self.set_user_model_variables({
                'droomplek': 'strand',
                'droomplek_lidwoord': 'het',
                'droomplek_speech_text_final': (
                    'Zullen we anders naar het strand? Ik vind dat altijd zo een fijne plek. '
                    'Ik kan de golven bijna horen en het zand onder mijn voeten voelen. '
                    'Weet je wat ik daar graag doe? Een zandkasteel bouwen met een vlag er op. '
                    f"Wat zou jij op het strand willen doen {self.user_model['child_name']}?"
                ),
                'place_decided': True,
                'place_decided_second': True,
            })

        second_decision_choice.add_move([False], _store_strand_fallback)
        second_decision_choice.add_move(
            [False],
            self.droomrobot.ask_open,
            lambda: self.user_model['droomplek_speech_text_final'],
            user_model_key='droomplek_motivatie'
        )

        second_answer_choice.add_choice('success', second_decision_choice)

        # Second answer missing entirely -> fallback to strand
        second_answer_choice.add_move('fail', _store_strand_fallback)
        second_answer_choice.add_move(
            'fail',
            self.droomrobot.ask_open,
            lambda: self.user_model['droomplek_speech_text_final'],
            user_model_key='droomplek_motivatie'
        )

        true_case_terminal = InteractionChoice('child_name', InteractionChoiceCondition.HASVALUE)
        true_case_terminal.add_move('success', lambda: None)
        first_decision_choice.add_choice(True, true_case_terminal)

        first_decision_choice.add_choice(False, second_answer_choice)
        interaction_choice.add_choice('success', first_decision_choice)

        # First answer missing entirely -> fallback to strand
        interaction_choice.add_move('fail', _store_strand_fallback)
        interaction_choice.add_move(
            'fail',
            self.droomrobot.ask_open,
            lambda: self.user_model['droomplek_speech_text_final'],
            user_model_key='droomplek_motivatie'
        )

        return interaction_choice"""
        
    def build_interaction_choice_droomplek(self) -> InteractionChoice:
        """
        Builds the full droomplek selection flow as a nested InteractionChoice tree.
        
        Flow:
        1. Child answers "Waar wil je naartoe?" → raw answer stored in droomplek_raw_answer
        2. Prompt A validates the answer (is it a concrete, safe, visualisable place?)
        3a. If valid → promote to droomplek, speak reaction, ask motivation → store droomplek_motivatie
        3b. If vague/invalid → speak clarification, ask again → repeat validation once
        3c. If still invalid after 2 attempts → fallback to strand, ask motivation
        
        After this choice completes, the following user_model keys are guaranteed to be set:
        - droomplek (str): the validated location name
        - droomplek_lidwoord (str): "de" or "het"  
        - droomplek_motivatie (str|None): what the child wants to do there
        """

        # --- Helper functions ---
        
        def _run_prompt_a(answer_key: str, prefix: str = ''):
            """Run Prompt A on the child's answer, store results with optional prefix."""
            def _execute():
                payload = self.droomrobot.generate_droomplek_payload(
                    child_name=self.user_model['child_name'],
                    child_age=self.user_model['child_age'],
                    child_answer=self.user_model[answer_key]
                )
                self.set_user_model_variables({
                    f'{prefix}prompt_a_payload': payload,
                    f'{prefix}droomplek_speech_text': payload['speech_text'],
                    f'{prefix}droomplek_candidate': payload['dream_place_final'],
                    f'{prefix}droomplek_candidate_lidwoord': payload['dream_place_article'],
                    f'{prefix}place_decided': payload['place_decided'],
                })
            return _execute
        
        def _promote_candidate(prefix: str = ''):
            """Promote a candidate droomplek to the final droomplek."""
            def _execute():
                self.set_user_model_variables({
                    'droomplek': self.user_model[f'{prefix}droomplek_candidate'],
                    'droomplek_lidwoord': self.user_model[f'{prefix}droomplek_candidate_lidwoord'],
                })
            return _execute
        
        def _set_strand_fallback():
            """Fallback to strand when no valid location could be determined."""
            self.set_user_model_variables({
                'droomplek': 'strand',
                'droomplek_lidwoord': 'het',
                'fallback_speech_text': (
                    'Zullen we anders naar het strand gaan? '
                    'Ik vind dat altijd zo een fijne plek. '
                    'Ik kan de golven bijna horen en het zand voelen. '
                    f'Wat zou jij op het strand willen doen {self.user_model["child_name"]}?'
                ),
            })

        # =====================================================
        # LEVEL 1: Did we get a raw answer at all?
        # =====================================================
        root = InteractionChoice('droomplek_raw_answer', InteractionChoiceCondition.HASVALUE)

        # --- LEVEL 1 SUCCESS: got an answer, run Prompt A ---
        root.add_move('success', _run_prompt_a('droomplek_raw_answer'))

        # =====================================================
        # LEVEL 2: Did Prompt A decide it's a valid place?
        # =====================================================
        first_decision = InteractionChoice('place_decided', InteractionChoiceCondition.MATCHVALUE)

        # --- CASE A: Valid location on first try ---
        # Promote candidate, speak reaction (ends with motivation question), capture answer
        first_decision.add_move([True], _promote_candidate())
        first_decision.add_move(
            [True],
            self.droomrobot.ask_open,
            lambda: self.user_model['droomplek_speech_text'],
            user_model_key='droomplek_motivatie'
        )
        first_decision.add_move([True], self.ensure_default_droomplek_motivatie)

        # --- CASE B: Vague/inappropriate first answer → ask once more ---
        # Prompt A's speech_text here contains a clarification + 2 suggested alternatives
        first_decision.add_move(
            [False],
            self.droomrobot.ask_open,
            lambda: self.user_model['droomplek_speech_text'],
            user_model_key='droomplek_second_answer'
        )

        # =====================================================
        # LEVEL 3: Did we get a second answer?
        # =====================================================
        second_answer = InteractionChoice('droomplek_second_answer', InteractionChoiceCondition.HASVALUE)

        # --- Got a second answer → run Prompt A again ---
        second_answer.add_move('success', _run_prompt_a('droomplek_second_answer', prefix='second_'))

        # =====================================================
        # LEVEL 4: Did Prompt A accept the second answer?
        # =====================================================
        second_decision = InteractionChoice('second_place_decided', InteractionChoiceCondition.MATCHVALUE)

        # --- CASE B1: Valid on second try ---
        second_decision.add_move([True], _promote_candidate(prefix='second_'))
        second_decision.add_move(
            [True],
            self.droomrobot.ask_open,
            lambda: self.user_model['second_droomplek_speech_text'],
            user_model_key='droomplek_motivatie'
        )
        second_decision.add_move([True], self.ensure_default_droomplek_motivatie)

        # --- CASE B2: Still invalid → fallback to strand ---
        second_decision.add_move([False], _set_strand_fallback)
        second_decision.add_move(
            [False],
            self.droomrobot.ask_open,
            lambda: self.user_model['fallback_speech_text'],
            user_model_key='droomplek_motivatie'
        )
        second_decision.add_move([False], self.ensure_default_droomplek_motivatie)

        second_answer.add_choice('success', second_decision)

        # --- No second answer at all → fallback to strand ---
        second_answer.add_move('fail', _set_strand_fallback)
        second_answer.add_move(
            'fail',
            self.droomrobot.ask_open,
            lambda: self.user_model['fallback_speech_text'],
            user_model_key='droomplek_motivatie'
        )
        second_answer.add_move('fail', self.ensure_default_droomplek_motivatie)

        # =====================================================
        # Wire the tree together
        # =====================================================
        first_decision.add_choice(False, second_answer)
        root.add_choice('success', first_decision)

        # --- LEVEL 1 FAIL: no answer at all → fallback to strand ---
        root.add_move('fail', _set_strand_fallback)
        root.add_move(
            'fail',
            self.droomrobot.ask_open,
            lambda: self.user_model['fallback_speech_text'],
            user_model_key='droomplek_motivatie'
        )
        root.add_move('fail', self.ensure_default_droomplek_motivatie)

        return root

    """ def build_imagery_store_move(self): # Old blooddraw function
        #Returns an InteractionMove that generates and stores the full imagery payload after droomplek_motivatie is known.
        def _store_imagery_payload():
            payload = self.droomrobot.generate_droomplek_imagery_payload(
                child_name=self.user_model['child_name'],
                child_age=self.user_model['child_age'],
                droomplek=self.user_model['droomplek'],
                droomplek_article=self.user_model['droomplek_lidwoord'],
                motivatie=self.user_model.get('droomplek_motivatie', ''),
            )
            self.set_user_model_variables({
                'transition_sentence': payload['transition_sentence'],
                'guided_imagery_seed': payload['guided_imagery_seed'],
                'guided_imagery_seed_2': payload['guided_imagery_seed_2'],
                'intervention_preparation_sentences': payload['intervention_preparation_sentences'],
                'intervention_procedure_sentences': payload['intervention_procedure_sentences'],
            })
        return InteractionMove(_store_imagery_payload)"""
    
    def _generate_and_speak_motivation_reaction(self):
        """Prompt B: generate quick reaction + transition, speak immediately."""
        payload = self.droomrobot.generate_motivation_reaction(
            child_name=self.user_model['child_name'],
            child_age=self.user_model['child_age'],
            droomplek=self.user_model['droomplek'],
            droomplek_article=self.user_model['droomplek_lidwoord'],
            motivatie=self.user_model.get('droomplek_motivatie', '')
        )
        self.set_user_model_variable('prompt_b_payload', payload)
        self.droomrobot.say(payload['motivatie_reactie'])
        self.droomrobot.say(payload['transitie_zin'])

        thread = Thread(
            target=self.prepare_user_model_audio,
            args=("droomplek",),
            daemon=True)
        thread.start()

    def _fire_practice_imagery_background(self):
        """Fire Prompt C in background — result needed after breathing exercise."""
        self._fire_background_prompt(
            'practice_imagery',
            self.droomrobot.generate_practice_imagery,
            child_name=self.user_model['child_name'],
            child_age=self.user_model['child_age'],
            droomplek=self.user_model['droomplek'],
            droomplek_article=self.user_model['droomplek_lidwoord'],
            motivatie=self.user_model.get('droomplek_motivatie', ''),
            kleur=self.user_model.get('kleur'),
            metgezel=self.user_model.get('metgezel'),
            dier=self.user_model.get('dier')
        )
        
    def _play_practice_imagery_and_fire_intervention(self):
        """Block for Prompt C, play it back, fire Prompt D during playback."""
        # Wait for practice imagery
        payload = self._await_background_prompt('practice_imagery', timeout=45)

        if payload and 'practice_imagery' in payload:
            self.set_user_model_variable('prompt_c_payload', payload)
            sentences = payload['practice_imagery']
        else:
            # Fallback: use generic practice sentences
            sentences = self._get_fallback_practice_imagery()
            payload = {'practice_imagery': sentences}
            self.set_user_model_variable('prompt_c_payload', payload)

        # can be here to pregenerate sentences
        # but does not seem to save time
        # if sentences:
        #     thread = Thread(
        #         target=self.pregenerate_prompt_output,
        #         args=(sentences,),
        #         daemon=True)
        #     thread.start()

        # Start playing practice imagery
        # Fire Prompt D in background BEFORE first sentence
        self._fire_background_prompt(
            'intervention_imagery',
            self.droomrobot.generate_intervention_imagery,
            child_name=self.user_model['child_name'],
            child_age=self.user_model['child_age'],
            droomplek=self.user_model['droomplek'],
            droomplek_article=self.user_model['droomplek_lidwoord'],
            motivatie=self.user_model.get('droomplek_motivatie', ''),
            kleur=self.user_model.get('kleur'),
            metgezel=self.user_model.get('metgezel'),
            dier=self.user_model.get('dier')
        )

        # Play practice sentences one by one
        for sentence in sentences:
            if not self.is_running:
                break
            self.droomrobot.say(sentence)
            
    
    def _store_intervention_result(self):
        """Block for Prompt D result, store in user_model for intervention session."""
        payload = self._await_background_prompt('intervention_imagery', timeout=90)

        if payload:
            self.set_user_model_variable('prompt_d_payload', payload)
            self.set_user_model_variables({
                'intervention_preparation_sentences': payload.get('intervention_preparation', []),
                'filler_sentences': payload.get('filler_sentences', []),
            })
        else:
            # Fallback stored
            intervention_sentences = self._get_fallback_intervention_imagery()
            filler_sentences = self._get_default_fillers()
            payload = {
                'intervention_preparation': intervention_sentences,
                'filler_sentences': filler_sentences,
            }
            self.set_user_model_variable('prompt_d_payload', payload)
            self.set_user_model_variables({
                'intervention_preparation_sentences': intervention_sentences,
                'filler_sentences': filler_sentences,
            })

        sentences = []
        if 'intervention_preparation_sentences' in self.user_model:
            for sentence in self.user_model['intervention_preparation_sentences']:
                sentences.append(sentence)
        if 'filler_sentences' in self.user_model:
            for sentence in self.user_model['filler_sentences']:
                sentences.append(sentence)

        thread = Thread(
            target=self.pregenerate_prompt_output,
            args=(sentences,),
            daemon=True)
        thread.start()

            
    # --------------------------------
    # Fallback content generators:
    # --------------------------------
    def _get_fallback_practice_imagery(self):
        dp = self.user_model.get('droomplek', 'strand')
        art = self.user_model.get('droomplek_lidwoord', 'het')
        return [
            f'En terwijl je zo rustig aan het ademhalen bent, mag je gaan voorstellen dat je bij {art} {dp} bent.',
            'Kijk maar eens in je gedachten om je heen.',
            'Misschien ben je er alleen, of is er iemand bij je.',
            'Kijk maar welke mooie kleuren je allemaal om je heen ziet.',
            'En merk maar hoe fijn jij je op deze plek voelt.',
            'Luister maar naar alle fijne geluiden om je heen.',
            'Misschien is het er heerlijk warm. Voel de warmte maar op je gezicht.',
            'En op deze plek kan je alles doen waar je zin in hebt.',
            'Misschien doe je iets heel leuks, waar je blij van wordt.',
            'Merk maar hoe fijn en rustig je je voelt op deze mooie plek.',
        ]

    def _get_fallback_intervention_imagery(self):
        dp = self.user_model.get('droomplek', 'strand')
        art = self.user_model.get('droomplek_lidwoord', 'het')
        return [
            f'Stel je maar voor dat je weer bij {art} {dp} bent, op die fijne plek.',
            'Kijk maar weer naar alle mooie kleuren en merk hoe fijn je je voelt.',
            'Voel maar hoe fijn het is om hier te zijn.',
            'En terwijl je hier zo lekker bent, zie je een mooie schommel staan.',
            'Precies in de kleur die jij mooi vindt.',
            'Je mag op de schommel gaan zitten. Het voelt lekker zacht.',
            'De schommel houdt je helemaal veilig en voelt heel fijn.',
            'Voel maar hoe je zachtjes heen en weer gaat, heen en weer.',
            'Jij bent de baas. Het gaat precies zo hoog als jij fijn vindt.',
            'Het kan ook een lekker kriebelend gevoel in je buik geven.',
            'En terwijl je schommelt, voel je een zachte warme wind op je gezicht.',
            f'Merk maar hoe lekker rustig je lichaam wordt en hoe veilig jij je voelt bij {art} {dp}.',
            'Je hoort alle fijne geluiden om je heen terwijl je lekker schommelt.',
            'De warmte is net als een zachte deken die over je heen gaat.',
            'Voel maar hoe je lichaam steeds lichter wordt nu je zo lekker schommelt.',
            'Steeds lichter, steeds rustiger, helemaal ontspannen.',
        ]

    def _get_default_fillers(self):
        dp = self.user_model.get('droomplek', 'strand')
        art = self.user_model.get('droomplek_lidwoord', 'het')
        return [
            'Adem rustig door, je bent helemaal in controle.',
            f'Merk maar hoe fijn jij je voelt bij {art} {dp}.',
            'Je wordt steeds lichter en zachter. Merk maar hoe fijn dat is.',
            'Je bent veilig en je hebt alles onder controle.',
        ]

    def prepare_user_model_audio(self, variable=None):
        if self.phases:
            moves = []

            for phase in self.phases:
                things = self.phase_moves.execute(phase)
                for move in things:
                    moves.append(move)
        else:
            moves = self.interaction_moves

        for move in moves:
            if hasattr(move, 'func') and move.func == self.droomrobot.say:
                if callable(move.args[0]):
                    constants = move.args[0].__code__.co_consts

                    if variable and variable in constants or variable is None:
                        try:
                            text = move.args[0]()
                            self.droomrobot.generate_audio(text, self.droomrobot.interaction_conf.amplified)
                        except KeyError:
                            continue

    def pregenerate_prompt_output(self, sentences):
        for sentence in sentences:
            print('[background TTS generation]', sentence)
            self.droomrobot.generate_audio(sentence)
        print("DONE PREGENERATING PROMPT OUTPUT")