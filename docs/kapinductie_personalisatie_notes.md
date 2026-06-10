# Droomrobot — `kapinductie-personalisatie` branch

## Project notes & deliverable documentation

*Working notes covering the changes made, options considered, design choices,
lessons learned, and the final workflow of the personalised kapinductie
(mask-induction) interaction. Intended as raw material for the end-of-project
report.*

---

## 1. Goal & background

The kapinductie interaction guides a child through a "droomreis" (dream journey
/ guided imagery) that is later used as distraction while the child goes under
anaesthesia via a face mask ("kapinductie"). The original script was a **fixed,
hand-written script** with three pre-baked dream locations (strand / bos /
ruimte) and a branch per location.

The personalisation branch reworks this into a **fully open, child-driven dream
journey**: the child may name *any* place, and the robot generates a tailored
guided-imagery script around that place, the child's name, age, favourite
colour, favourite animal, chosen companion, and stated motivation — while
keeping the strict therapeutic structure that makes guided imagery work for
induction.

Two interaction sessions matter here:

- **INTRODUCTION** — the practice session, done in the holding/waiting area.
  Robot introduces itself, gathers personalisation, lets the child choose a
  dream place, and practices the dream journey once.
- **INTERVENTION** — the real induction in the OR. Robot replays a personalised
  journey to the same dream place, now including the mask reframed as a natural
  object of the scene.

---

## 2. How we analysed the existing written script to write the prompts

The written therapeutic script (provided by the medical/psychology side) was
treated as the **ground truth for structure and tone**, and we reverse-engineered
its rules into explicit prompt constraints rather than letting the LLM
improvise freely. Concretely, the analysis surfaced these recurring rules, which
became hard constraints in the prompts:

- **Permissive language** — always "mag", "maar", invitational. Never commands
  ("doe je ogen dicht"). Encoded as an explicit ✅/❌ block in prompts C and D.
- **Suggestive perception** — the child is invited to *notice* ("merk maar",
  "misschien voel je"), never *told* that something is true ("je voelt je
  fijn"). This is a core hypnotic-language rule; it is spelled out with positive
  and negative examples.
- **No questions** — the child has their eyes closed and cannot answer, so the
  imagery must never contain a question mark. Enforced as an internal-check item.
- **Forbidden vocabulary** — pijn, bang, eng, ziekenhuis, dokter, naald, masker,
  kapje, prikken, operatie, slapen, bloed, infuus, verdoving, narcose, medicijn.
  This is the single most safety-critical extraction from the original script:
  the imagery must reframe the medical reality without ever naming it.
- **The fixed therapeutic arc** — the original strand/bos/ruimte scripts all
  followed the same beat sequence, written through research and confirmed 
  to work by experts (return to place → sensory anchoring → introduce a 
  rhythmic/face object → rhythmic deepening → safe cocoon → getting
  lighter → closing). We formalised this into the **7-phase, 17-sentence arc**
  that prompt D must follow exactly, sentence by sentence.
- **Sentence-by-sentence templating** — because each sentence is spoken in
  isolation at slow pace, we discovered the script works best when each sentence
  has a fixed *role* (e.g. "zin 5 must contain 'merk maar hoe fijn'", "zin 17
  is verbatim 'Steeds lichter, steeds rustiger, helemaal ontspannen.'"). The
  prompts therefore prescribe per-sentence openers and required phrases rather
  than a free paragraph.
- **The mask reframe** — the original ruimte script reframed the mask as a
  "ruimtekapje". Generalising this was the key creative insight: prompt D asks
  the model to choose a *child-known face object or rhythmic object* that
  emerges naturally from the chosen dream place (duikbril at the sea, ruimtehelm
  in space, schommel/wiegend bootje/vliegend tapijt otherwise), with "if in
  doubt, use a schommel" as the safe default.

### Prompt design principles that came out of this

- **Structure over freedom.** Every prompt ends with an *INTERNE CONTROLE*
  (internal self-check) checklist mirroring the hard rules, plus a strict JSON
  output contract. This drastically reduced malformed/oversized output.
- **Character limits per sentence** (≤75 chars for imagery, ≤100 for the
  transport/longer lines, ≤60 for filler). This is a **TTS optimisation**: long
  sentences chunk awkwardly and break the slow, calm cadence. The limit is
  stated in the prompt *and* enforced downstream by the chunker.
- **Age tiering.** Every prompt has a 4-6 / 6-9 / 9-12 age band with concrete
  language guidance, so the same structure scales from very simple to more
  autonomous phrasing.
- **Concrete over vague.** A specific lesson: "misschien wel groen of paars of
  regenboog kleuren" was explicitly flagged as *too vague* and replaced by a
  rule demanding concrete objects + their real colours per location
  ("blauwe water, goudgele zand, witte schuimkoppen"). Recognisability beats
  originality for this age group.

---

## 3. The four prompts (final design)

The personalisation pipeline is built around four LLM calls, labelled A–D.
Prompt files live in `droomrobot/resources/prompts/`.

| Prompt | File | Role | Output |
|--------|------|------|--------|
| **A** | `prompt_a_droomplek_keuze.txt` | Validate the child's chosen place; decide if it is concrete/safe/visualisable; produce a spoken reaction that ends in a motivation question (valid) or a re-ask with 2 alternatives (vague). | `{speech_text, dream_place_final, dream_place_article, place_decided}` |
| **B** | `prompt_b_motivatie_reactie.txt` | React warmly to the child's motivation; clean it into a short canonical activity ("effective_motivatie") or fall back to "spelen" if unclear; produce a transition sentence into practice. | `{motivatie_reactie, transitie_zin, effective_motivatie}` |
| **C** | `prompt_c_practice_imagery.txt` | Generate the 11-sentence **practice** dream journey for the holding area, weaving in colour / companion / animal / motivation. | `{practice_imagery: [11]}` |
| **D** | `prompt_d_intervention_imagery.txt` | Generate the full **intervention** journey (the 7-phase, 17-sentence arc) plus 4 looping filler sentences, with the mask reframed as a natural scene object. Split into `setting_context` (zin 1-3) and `start_analogy` (zin 4-17). | `{setting_context: [3], start_analogy: [14], filler_sentences: [4]}` |

### Key design choices inside the prompts

- **Prompt A doubles as a safety/validation gate.** It rejects vague answers
  ("ergens", "ik weet het niet"), dangerous/scary places (slagveld, griezelig
  huis), and *hospital-adjacent* negatives (the hospital itself, operatiekamer,
  begraafplaats). On rejection it places `place_decided=false` and uses "strand"
  as a placeholder while re-asking — so the flow always has a usable place. If
  after re-asking the location is still vague, we continue with "strand". If the
  location is clear and appropriate, the robot acknowledges the location, gives
  a fun example of what it likes about that choice and then asks for the childs
  motivation.
- **Prompt B normalises motivation.** A free-text child answer
  ("eh… zwemmen met dolfijnen denk ik") becomes a clean 1–3 word infinitive
  ("zwemmen") in `effective_motivatie`, which is then promoted into the user
  model and fed to C and D. If the answer is unclear it deterministically
  becomes "spelen" — never fake-enthusiastic about an answer the child didn't
  give.
- **Prompt D's split (setting_context vs start_analogy).** This split exists so
  the operator can **fast-forward**: `setting_context` (returning to the place +
  sensory anchoring) plays during PREPARATION and auto-advances; pressing the
  PROCEDURE button jumps straight into `start_analogy` (the object/analogy and
  the lighter-cocoon block) — important because in the OR the timing of the
  actual mask is controlled by the anaesthetist, not the script.
- **filler_sentences** are a short looped "holding pattern" (breathing
  compliment, place+safety, lightness, control) that repeats with pauses to
  cover whatever real time the induction takes.

---

## 4. Script changes & personalisation decisions

### 4.1 Two extra introduction questions (colour + companion)

**Decision:** beyond the original favourite-animal question, the introduction
now also asks **favourite colour** and **who you'd take with you (companion)**.

**Motivation:** children spend a relatively long time in the holding area before
induction. That dead time is an opportunity, not a problem — extra questions
(a) keep the child engaged and distracted for longer, and (b) give the
generator richer, more personal material so the dream journey references things
the child actually cares about. More references back to the child's own world
= stronger, more absorbing imagery.

- Implemented in `introduction_factory.py` (`age4` and `age6_9`) behind an
  `only_animal` flag.
- The three answers (`dier`, `kleur`, `metgezel`) flow into prompts C and D as
  `dier_context`, `kleur_context`, `metgezel_context`.
- **Operator override:** a GUI toggle ("Alleen dier vragen", kapinductie-only)
  sets `only_animal_intro`, which skips colour + companion when time is short.
  Default is to ask all three.

### 4.2 References back to the dream place / motivation / name, wherever natural

A deliberate design throughline: **re-reference the personal anchors as often as
feels natural** to deepen immersion and ownership.

- **Name calling** — the child's name is used at warm beats (greeting, motivation
  question, wrap-up: "Ik rij gewoon met je mee zo, {naam}.") but *deliberately
  banned* inside the calm imagery sentences of B (motivatie_reactie /
  transitie_zin) so the meditative cadence isn't broken.
- **Dream place** — re-named throughout: in prompt A's reaction, B's transition,
  C's transport sentence, D's phase-1 return and the phase-5 "safe cocoon"
  sentence (which must contain the place by name), and in the fixed wrap-up
  ("je weer terug kan gaan in gedachten naar deze fijne plek …").
- **Motivation** — promoted from B's `effective_motivatie` and referenced subtly
  in C (zin 10, activity) and woven into D's opening where natural.
- **Colour / animal / companion** — colour appears as a concrete object's colour
  (not "your favourite colour"); the animal gets a playful cameo (C zin 8) and a
  calm, protective reappearance (D zin 13); the companion is named beside the
  child ("en {metgezel} is er ook, vlak naast je"). These actively fill in the 
  earlier vaguer parts of the script (e.g. "misschien ben je alleen of is er iemand bij je")
  with personalised references.

### 4.3 Open-ended place choice replaces the 3-way branch

The old `_build_interaction_choice_droomplek` / `_build_interaction_choice_oefenen`
(fixed strand/bos/ruimte branches) is retained but commented out for reference.
The new flow is `build_interaction_choice_droomplek()` in `droomrobot_script.py`:

1. Ask open: "Waar zou jij naartoe willen op droomreis?"
2. Prompt A validates → if valid, promote + ask motivation; if vague, re-ask
   once with 2 concrete alternatives.
3. Second attempt validated again → if still invalid (or no answer at all),
   **fall back to "strand"** with a warm scripted bridge.
4. `ensure_default_droomplek_motivatie()` guarantees a non-empty motivation
   ("spelen") so downstream prompts never receive a null.

The late commit `extra check locatie her-vraag als 1e x onduidelijk was`
hardened prompt A's internal check so that when `place_decided=false` it ends
with a *location* re-question, and only ends with a *motivation* question when
`place_decided=true`.

### 4.4 Fallbacks everywhere ("go to the beach")

Every generated step has a canned strand fallback so a GPT timeout, a JSON parse
failure, or an empty answer never breaks the interaction, this matches the 
professionally written script from before:

- Prompt A → strand placeholder + scripted bridge.
- Prompt B → "Soms is het lastig kiezen, laten we gewoon lekker gaan spelen!"
- Prompt C → `_get_fallback_practice_imagery()` (10-sentence beach journey).
- Prompt D → `_get_fallback_intervention_imagery(age)` — **age-specific**
  (4 / 6 / 9) beach+schommel scripts, matching the original written script, plus
  `_get_default_fillers()`. The fallback returns the *same split structure* as
  D (setting_context / start_analogy) so the skip button still works on the
  fallback path.

---

## 5. Making the interaction smoother (timing, ordering, caching)

This is where most of the engineering effort went. The core problem: LLM
generation (prompts C and D especially) and TTS synthesis are both slow, and a
guided-imagery session cannot tolerate dead air or awkward pauses. The solution
is **aggressive pre-generation and careful ordering**, so that by the time the
robot needs to *speak* something, both the text and its audio are already ready.

### 5.1 Background prompt firing + filler masking

Implemented in `droomrobot_script.py` via `_fire_background_prompt` /
`_await_background_prompt` (a tiny futures registry over daemon threads).

The introduction order (see `kapinductie9.py::_introduction`) is deliberately:

1. **Fire prompt B in the background** the instant the motivation answer is in.
2. **Speak a cached filler** — "Wat een leuk idee {naam}!" — to mask B's latency (*point of improvement in case child does not answer).
3. **Await B**, store payload, promote `effective_motivatie`.
4. **Fire C, then D** in the background (order matters — see below).
5. **Speak B's output** (reaction + transition). C and D keep generating.
6. Fixed scaffold (comfortable position + breathing, ~30–45s) runs — this is
   cached/wav audio, so the TTS service is *idle* and free to pre-generate C's
   audio in the background.
7. **Await + play C.**
8. Fixed wrap-up plays while **D** finishes and its audio is pre-generated.
9. **Await D** and store it for the intervention session.

The net effect: the child never waits on a spinner. GPT latency is always hidden
behind speech that was going to happen anyway.

### 5.2 Prompt ordering: C must be queued before D

The SIC GPT service **serialises requests**. So `_fire_practice_imagery_background`
(C) must be called *before* `_fire_intervention_imagery_background` (D), otherwise
D would block C and delay the part the child hears first. This ordering
constraint is documented inline at both call sites.

### 5.3 TTS pre-generation chained C → D

This is the subtlest piece (commits `Volgorde veranderd caching audio`,
`casche verbertering`):

- When **C** resolves, its `on_success` callback (`_pregen_c_tts`) immediately
  synthesises TTS for all of C's sentences during the breathing scaffold, when
  the TTS service is otherwise idle — so live playback of C is **all cache hits**.
- C then sets an `Event` (`_prompt_c_tts_pregen_done`).
- When **D** resolves, its callback (`_pregen_d_tts_chained`) **blocks on that
  event** before pre-generating D's audio. This guarantees D's TTS work runs
  *strictly after* C's, in the idle window during C playback + wrap-up — they
  never compete for the single TTS pipe. By the time the intervention needs D,
  its audio is largely cached.

**Ordering of save vs play.** In `core.py::say`, generated audio is now saved to
the cache via a `ThreadPoolExecutor.submit(...)` *before/parallel to* playback,
rather than blocking playback on the disk write. This means live-generated
speech is never lost if a speaker request times out, but the child also doesn't
wait on disk I/O.

### 5.4 Per-answer audio pre-generation

When any move stores a `user_model_key`, the script kicks off
`prepare_user_model_audio(key)` in a daemon thread (see
`DroomrobotScript.run`). This introspects upcoming `say(lambda: ... key ...)`
moves and pre-synthesises their audio as soon as the relevant variable
(e.g. `droomplek`, `child_name`) is known — so personalised fixed lines are
already cached before they're reached.

### 5.5 Auto-advancing phases + operator skip

The intervention is modelled as phases (PREPARATION → PROCEDURE).
`_play_setting_context` plays D's `setting_context` and then **auto-advances**
to PROCEDURE via `next_phase`. The operator can also press the PROCEDURE button
at any time to jump straight to the analogy (`_requested_phase` breaks the
loop). The GUI polls `current_phase` every 500ms (`_poll_phase_change`) to keep
the button highlight in sync when the script advances itself.

---

## 6. Technical / infrastructure changes

### 6.1 `core.py`

- **GPT timeouts** (`_gpt_request_with_timeout`): every GPT call runs in a
  daemon thread joined with a timeout (default 15s, 8s for short calls like
  article/entity), returning `None` on timeout → triggers the fallback. Stops a
  hung GPT call from freezing the whole interaction. `max_tokens` tuned per
  prompt (300 for B, 900 for C, larger for D).
- **Robust JSON extraction** (`_extract_json_object`): strips markdown fences,
  tries a direct parse, then progressively repairs truncated JSON (balancing
  braces, closing strings, trimming to the last complete value). LLMs
  occasionally wrap or truncate JSON; this keeps a usable payload instead of
  crashing.
- **Text chunking** (`_split_text`, `max_len=120` for `say`): splits on sentence
  boundaries first, then commas, then spaces, avoiding tiny tail fragments
  (`min_tail`). Commit `chunken verbeterd - ging fout met kommas` fixed comma
  handling and `up max_len in chunking` widened the window to avoid awkward
  splits mid-clause. Chunking matters because each chunk is a separate TTS unit
  and cache key.
- **`get_article` / `get_adjective`**: small GPT helpers to get the correct
  Dutch lidwoord ("de"/"het") and adjective form for an arbitrary place/colour,
  with "de" as a safe fallback. "Lidwoord protection" (commit `d6c8326`) keeps
  grammatical correctness when the place is fully open-ended.
- **`ask_entity_llm`**: the introduction questions switched from Dialogflow
  entity matching (`ask_entity`) to an LLM-based extractor, because open answers
  (colour, animal, companion) don't fit fixed Dialogflow entity lists well.

### 6.2 `droomrobot_tts.py`

- **ElevenLabs chunk accumulation**: the websocket receive loop now accumulates
  *all* audio chunks until `isFinal` (or a graceful close / timeout) instead of
  returning on the first chunk. Previously only the first audio frame was
  returned → truncated speech. On any closure path it returns whatever audio was
  collected rather than `None`.
- **Thread-safe, atomic cache** (`TTSCacher`): because live `say()` can now race
  with background pre-generation for the same `.wav`/cache map, the cacher got:
  - a `threading.Lock` (`_write_lock`) serialising all writes;
  - a short-circuit so a second writer for the same key doesn't redo the work;
  - **atomic publish** of both the `.wav` and the JSON map via temp file +
    `os.replace`, so a reader never sees a half-written wav or a truncated map
    (which would orphan every cached file);
  - relative cache paths (portable cache dir) + stale-entry cleanup under lock.

  This robustness was prompted directly by the concurrency the new
  pre-generation strategy introduced.

### 6.3 `droomrobot_gui.py`

- **Debug-prints toggle**: the console is extremely chatty ([TTS], [GPT],
  [JSON], [BG], [SCRIPT]…), and painting every line into the Tk Text widget was
  a measurable slowdown. `TextRedirector` now filters known debug tags at line
  boundaries when "Debug Prints" is off, while always showing
  `[Error]`/`[Interrupted]`/tracebacks/untagged output. Persisted via
  `debug_console` in settings. (Commit `Gui button for debug prints`.)
- **"Alleen dier vragen" toggle** (kapinductie-only) → `only_animal_intro`
  (commit `Gui button to decide on introduction length`).
- **Phase-highlight polling** to reflect script-driven phase auto-advance.
- **Asyncio loop per connect thread** + `set_log_file_path` fixed to a relative
  path.

### 6.4 Other

- `requirements.txt` / `sync_data.py` / `.gitignore` minor updates; local files
  (e.g. `dump.rdb`, system logs) ignored.

---

## 7. Final workflow (architecture summary)

```
INTRODUCTION (holding area)
  intro: greeting + animal [+ colour + companion]      ← personalisation gathered
  ask "Waar wil je naartoe?"  → droomplek_raw_answer
  ─ Prompt A (validate place) ──► valid?  yes → promote + ask motivation
                                          no  → re-ask w/ 2 options → (2nd A) → else strand
  ensure motivation (default "spelen")
  ┌ fire Prompt B (bg) ─┐
  │  say cached filler  │   ← masks B latency
  └ await B ────────────┘   → promote effective_motivatie
  fire Prompt C (bg) ─► on resolve: pregen C audio, signal event
  fire Prompt D (bg) ─► on resolve: wait for C event, then pregen D audio
  speak B (reaction + transition)
  fixed scaffold: comfortable position + breathing      ← cached audio, TTS idle
  await + play Prompt C (practice journey, 11 sentences) ← cache hits
  fixed wrap-up                                          ← D finishing in bg
  await + store Prompt D                                 → carried to intervention

INTERVENTION (OR)
  PREPARATION: greeting + setting_context (zin 1-3) ──auto──► PROCEDURE
               (operator may press PROCEDURE to skip)
  PROCEDURE:   start_analogy (zin 4-17: object/analogy + cocoon + lighter)
               filler loop (repeats until stopped)
```

**Key components**

- `DroomrobotScript` — generic move/choice engine (`InteractionMove`,
  `InteractionChoice`, phases, background-prompt registry, user-model + audio
  pre-gen). Context-agnostic.
- `Kapinductie9` (and 4/6 variants) — the concrete kapinductie scripts wiring
  moves, choices, prompts, fallbacks and phases.
- `IntroductionFactory` — age-banded introduction builders (`only_animal` flag).
- `Droomrobot` (`core.py`) — robot/IO layer: TTS (`say`, chunking, timeouts,
  cache), GPT (timeouts, JSON extraction), Dialogflow/LLM listening, the four
  `generate_*` prompt functions, audio pre-gen executor.
- `ElevenLabsTTS` / `TTSCacher` (`droomrobot_tts.py`) — synthesis + thread-safe
  atomic cache.
- `DroomrobotGUI` / `DroomrobotControl` — operator front-end.

---

## 8. Lessons learned

1. **Structure beats freedom for therapeutic LLM output.** Free-form prompts
   produced output that drifted in tone, length and safety. Per-sentence
   templates + an explicit internal-check checklist + a strict JSON contract
   gave reliable, on-spec output. The model is best used as a *filler of a
   fixed mould*, not an author.
2. **Hide latency, don't fight it.** We could not make GPT/TTS fast enough for
   synchronous use. The winning pattern was firing generation early in the
   background and masking the wait behind speech that had to happen anyway
   (fillers, fixed scaffold, wrap-up). Ordering of fires (C before D) and
   chaining TTS pre-gen (D waits for C) matter as much as the calls themselves.
3. **Pre-generate audio into a cache; make the cache concurrency-safe.** Once
   multiple threads write audio, the cache becomes a correctness hazard. Atomic
   temp-file + `os.replace` and a write lock were necessary, not optional.
4. **Always have a scripted fallback.** Every generated step has an age-matched
   "go to the beach" fallback, structurally identical to the generated output
   (including the skip-point split), so timeouts/parse-errors degrade gracefully
   instead of breaking the session.
5. **Validate the child's input as a safety gate.** Prompt A rejecting
   scary/medical/hospital places is a clinical-safety requirement, not just a UX
   nicety.
6. **Personalisation depth is bounded by time, so make it operator-tunable.**
   The "alleen dier" toggle exists because the right amount of personalisation
   depends on how long the child is actually in the holding area.
7. **Console I/O can be a real bottleneck.** Painting every debug line into the
   Tk widget was slowing the interaction; gating it behind a toggle was a cheap,
   real win.
8. **Keep the old scripts as reference.** The commented-out fixed strand/bos/
   ruimte branches and the age-specific fallbacks are effectively the
   "specification" the generated output must match — worth preserving.

---

## 9. Ideas for future improvements

### 9.1 Streaming
- **Streaming TTS playback.** Today a sentence is fully synthesised, then
  played. ElevenLabs already streams audio chunks (we accumulate them) — we
  could begin playback as the first chunks arrive, cutting per-sentence latency
  and reducing reliance on pre-generation.
- **Streaming LLM generation.** Prompts C and D return a JSON list of sentences;
  we could stream and start synthesising/queuing sentence 1's audio while the
  model is still producing later sentences, instead of awaiting the whole JSON.
  Needs a tolerant streaming JSON/array parser (we already have a tolerant
  whole-object parser to build on).
- **Pipeline the two stages.** Combine the above: GPT streams → TTS streams →
  speaker, as a continuous pipeline rather than discrete await-then-play steps.

### 9.2 Listening / timeout tuning
- **Re-examine the listening (Dialogflow/VAD) timeout.** Observed problem: the
  robot sometimes keeps listening to ambient hospital noise *after* the child
  has already finished answering, causing long awkward waits. Options:
  - shorter end-of-speech / silence timeout, especially for the short
    introduction answers;
  - tunable per-question timeouts (a yes/no needs far less listening window than
    an open motivation answer);
  - barge-in / manual "child is done" operator button to cut the listen short;
  - better endpointing / VAD tuned for a noisy room, or a push-to-talk style
    cue.
- **Adaptive timeouts** based on expected answer type and measured ambient noise.

### 9.3 Generation quality & robustness
- **Validate generated output against the internal-check rules in code** (e.g.
  assert no question marks, sentence length ≤ limit, required phrases present)
  and regenerate/repair automatically instead of trusting the model's
  self-check.
- **Schema-constrained decoding** (function-calling / JSON-mode / grammar) to
  eliminate the JSON-repair path entirely.

### 9.4 Personalisation
- Use **companion / animal / colour** even more consistently across both
  sessions (currently strongest in C/D; the introduction reactions could
  reference them more?).
- Carry **practice-session observations** (what worked, child's reactions) into
  the intervention generation.
- Optional **extra holding-area content** (a short story, a game) generated to
  fill variable wait times, gated by the same operator time-budget idea.
- Q&A opportunity between kid and robot (when streaming works, children often
  wanted to ask questions to the robot)
- Increase level of **droomplek** details into D's script
- Make sure the script focusses on relevant parts of the story (dont care
  about the color of a sword, more about the sea around the ship)

### 9.5 Tooling / ops
- Surface generation/latency metrics in the GUI (time-to-first-word, cache
  hit-rate) to spot regressions.


---

## 10. File map (where to look)

| Concern | File |
|---------|------|
| Move/choice engine, background prompts, audio pre-gen, droomplek flow | `droomrobot/droomrobot_script.py` |
| Kapinductie script (intro + intervention, phases, fallbacks) | `droomrobot/kapinductie9.py` (and `kapinductie4.py`, `kapinductie6.py`) |
| Robot IO: TTS `say`/chunking/timeouts, GPT timeouts, JSON extraction, `generate_*` | `droomrobot/core.py` |
| ElevenLabs synthesis + thread-safe atomic cache | `droomrobot/droomrobot_tts.py` |
| Age-banded introduction (`only_animal`) | `droomrobot/introduction_factory.py` |
| Operator GUI (debug toggle, only-animal toggle, phase polling) | `droomrobot/droomrobot_gui.py` |
| Prompts A–D | `droomrobot/resources/prompts/prompt_{a,b,c,d}_*.txt` |
```
