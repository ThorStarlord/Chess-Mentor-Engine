# Chess Mentor Engine — Repository Build Plan

**Status:** Working product-development roadmap  
**Purpose:** Preserve the current repository-building ideas, implementation order, epistemic boundaries, and deferred decisions so future work does not accidentally promote research hypotheses into settled architecture.  
**Scope:** Product/repository construction after the initial research pilots.  
**Authority:** This document is a planning artifact. It does **not** supersede frozen research protocols, pilot results, or later ratified ADRs.

---

## 1. Product direction to preserve

Chess Mentor Engine should not become merely another engine-analysis UI.

The product hypothesis is a **persistent chess tutor that learns how a particular player makes decisions, grounds its conclusions in objective chess evidence, and uses that evidence to choose what the player should practice next**.

The repository should therefore evolve around this evidence chain:

```text
Chess Evidence
    ↓
Player Decision Evidence
    ↓
Position-Level Reasoning Discrepancy
    ↓
Recurring Pattern / Learner Hypothesis
    ↓
Training Intervention
    ↓
Transfer / Longitudinal Evidence
```

Three questions remain central:

1. What is objectively happening on the board?
2. What did the player actually notice, consider, and expect?
3. What recurring explanation is currently supported strongly enough to affect training?

The repository must keep those questions separate.

---

## 2. Evidence and authority principles

### 2.1 Chess truth is not player psychology

Engine analysis can establish move quality, candidate strength, and chess consequences. It cannot establish what the player saw or why the player chose a move.

### 2.2 Player self-report is evidence, not objective truth

Player responses are direct evidence of what the player reports thinking. They may be incomplete, reconstructed, mistaken, or influenced by the measurement process.

### 2.3 Analyst interpretation must remain derived

Normalized categories such as `candidate generation failure`, `opponent resource missed`, or `plan formation incomplete` are analyst/model interpretations and must remain traceable to raw evidence.

### 2.4 Local discrepancies are not stable weaknesses

Use an evidence ladder:

```text
Position observation
→ Reasoning Discrepancy
→ Candidate recurrence
→ Supported participant-specific hypothesis
→ Training-eligible hypothesis
→ Tested intervention
→ Transfer / competency evidence
```

Never skip levels.

### 2.5 Contradictory evidence is first-class

The system should search for correct handling of the same apparent problem, not only failures.

### 2.6 Provenance is part of product correctness

Every important claim should eventually be explainable through source game, position, engine provenance, player evidence, model/analyst interpretation, and hypothesis revision history.

---

## 3. Four-plane target architecture

Use this as a conceptual map, not yet a frozen implementation architecture.

### Plane 1 — Chess Truth

Owns:

- games;
- positions;
- rules and legality;
- deterministic board state;
- engine evaluations;
- candidate moves;
- principal variations;
- deterministic tactical/structural facts;
- source provenance.

### Plane 2 — Player Evidence

Owns:

- raw player responses;
- reported candidate moves;
- chosen move;
- expected opponent reply;
- expected continuation;
- stated plan/objective;
- confidence/uncertainty where collected;
- original-game recollection versus current reasoning;
- evidence timing and exposure state.

### Plane 3 — Learning Inference

Owns:

- position-level Reasoning Discrepancies;
- controls and contradictory evidence;
- recurrence analysis;
- competing explanations;
- learner hypotheses;
- hypothesis lifecycle and strength;
- evidence-for/evidence-against relations.

### Plane 4 — Pedagogy

Owns:

- training interventions;
- lesson selection;
- drills/exercises;
- intervention outcomes;
- near/far transfer;
- real-game recurrence;
- competency evidence.

A tutoring/orchestration layer may coordinate these planes later.

---

# 4. Phased implementation roadmap

## Phase 0 — Repository and authority reconciliation

### Goal

Make the repository state itself trustworthy before implementing product capabilities.

### Tasks

- Reconcile local Git history with the GitHub remote.
- Push or otherwise establish the local history as the authoritative remote history without rewriting validated research provenance.
- Confirm the current `main` HEAD and clean working tree.
- Preserve all frozen research protocol hashes and pilot results.
- Add this roadmap under a repository path such as:

```text
docs/product/repository-build-plan.md
```

- Add a short link from `CONTEXT.md` or `docs/product/product-definition.md` if appropriate.

### Exit criteria

- Remote and local repository histories agree.
- Research history is preserved.
- Roadmap is committed as a planning document, not an ADR or canonical architecture specification.

---

## Phase 1 — Canonical game and position substrate

### Goal

Create the smallest deterministic chess-domain foundation on which every later system can rely.

### Candidate concepts

```text
GameSource
CanonicalGame
CanonicalPosition
PositionRef
GameContext
```

### Capabilities

- Parse PGN.
- Normalize required headers.
- Identify player color.
- Normalize time control.
- Classify rated/casual where source data supports it.
- Classify human/bot where source data supports it.
- Distinguish Standard/From Position.
- Detect duplicates.
- Generate stable internal IDs.
- Produce exact FEN for positions.
- Preserve source and source checksum.

### Do not build yet

- learner model;
- tutoring dialogue;
- recommendation engine;
- database-backed profile;
- GUI.

### Tests

- PGN parsing fixtures;
- duplicate detection;
- source-provenance round trip;
- FEN correctness;
- color/time-control normalization;
- malformed-input behavior.

### Exit criteria

Given a frozen PGN fixture, the repository deterministically produces the same canonical games and positions with stable provenance.

---

## Phase 2 — Position Context Packet

### Goal

Make a chess position fully legible to humans and models without requiring unreliable reconstruction from FEN or SAN alone.

### Candidate research-to-product concept

`PositionContextPacket`

### Initial deterministic fields

```yaml
position_id:
game_id:
move_number:
side_to_move:
fen:
board_ascii:
piece_map:
material_summary:
source_provenance:
```

### Engine-derived fields, added only when engine analysis is present

```yaml
played_move:
evaluation_before:
evaluation_after:
top_candidates:
principal_variations:
engine_provenance:
```

### Key rule

Canonical state, deterministic derived state, engine-derived state, and model interpretation must not be mixed into one unlabeled blob.

### Tests

- FEN ↔ ASCII board consistency;
- piece-map consistency;
- material calculation;
- side-to-move correctness;
- stable serialization;
- missing-engine-data behavior.

### Exit criteria

Any selected position can be rendered into a deterministic, inspectable context packet whose board representation matches the canonical FEN exactly.

---

## Phase 3 — Deterministic chess-feature extraction

### Goal

Reduce spatial/bookkeeping burden on the reasoning model without pretending high-level chess judgment is deterministic.

### Good early candidates

- legal moves;
- legal checks;
- legal captures;
- attackers by square;
- defenders by square;
- pinned pieces where deterministically definable;
- hanging/undefended pieces where a precise rule is defined;
- material balance;
- open/semi-open files where a precise definition is used;
- passed pawns where a precise definition is used.

### Keep interpretive concepts out initially

Examples:

- dangerous initiative;
- weak king;
- superior activity;
- good attacking chances;
- strategically urgent break.

Those may later be model-derived explanations grounded in deterministic facts and engine evidence.

### Exit criteria

The system can expose important low-level board relationships without asking the LLM to reconstruct them manually and without claiming subjective strategic interpretation as deterministic fact.

---

## Phase 4 — Engine analysis abstraction

### Goal

Make engine evidence a replaceable provider rather than embedding Stockfish semantics throughout the domain.

### Candidate interface

```text
ChessAnalysisProvider
```

Possible adapters:

```text
StockfishAnalysisProvider
LichessAnnotationProvider
PrecomputedAnalysisProvider
```

### Normalized output

```yaml
position_id:
evaluation:
best_move:
top_candidates:
principal_variations:
depth:
nodes:
engine_name:
engine_version:
configuration:
source:
```

### Principles

- Record engine provenance.
- Allow incomplete provenance and label it honestly.
- Never treat engine output as player reasoning.
- Avoid making one engine implementation the domain model.

### Exit criteria

The rest of the code can consume normalized chess-analysis evidence without knowing which provider produced it.

---

## Phase 5 — Diagnostic position selection

### Goal

Choose positions for learning value, not merely centipawn loss.

### Candidate selection dimensions

- major tactical error;
- tactical opportunity;
- defensive resource;
- strategic plan choice;
- quiet improvement;
- prophylactic decision;
- ambiguous candidate choice;
- successful/control decision;
- recurrence test;
- contradiction test;
- transfer test.

### Important rule

The selector should be capable of choosing **correct decisions** as controls.

### Initial implementation approach

Start deterministic/rule-based where possible. Keep model-assisted selection explicitly derived and inspectable if later introduced.

### Exit criteria

Given a game set, the selector can produce a bounded, provenance-rich candidate set containing both potentially instructive errors and relevant successful controls.

---

## Phase 6 — Player Decision Evidence capture

### Goal

Store what the player reports thinking before engine feedback.

### Candidate concepts

```text
PlayerDecisionEvidence
RawPlayerResponse
ReasoningPrompt
ExposureState
```

### Preserve multiple evidence stages

```text
minimal response
standardized probe response
post-engine reflection
original-game recollection
```

Never silently merge them.

### Candidate structured fields

```yaml
raw_response:
chosen_move:
reported_candidates:
expected_reply:
expected_continuation:
stated_objective:
uncertainty:
confidence:
```

### Critical rule

Raw response is authoritative. Structured extraction is `ANALYST CODING` unless the player directly filled the structured fields.

### Exit criteria

The repository can freeze, checksum, retrieve, and compare player reasoning evidence without rewriting the raw participant response.

---

## Phase 7 — Reasoning Discrepancy representation

### Goal

Create the first evidence-backed bridge between objective chess state and reported player reasoning.

### Candidate definition

> A traceable mismatch between the player's reported pre-engine reasoning and an objectively relevant demand or consequence of the position.

### Candidate categories

- critical feature not reported;
- strong candidate not generated;
- opponent resource not anticipated;
- continuation calculated incorrectly;
- resulting position evaluated incorrectly;
- strategic target recognized but no executable move generated;
- correct move with incomplete rationale;
- correct reasoning / no discrepancy;
- unclear;
- emergent/other.

### Rules

- Multiple categories may apply.
- `unclear` is valid.
- A discrepancy belongs first to a **position**, not to the player globally.
- Every discrepancy must cite the player evidence and chess evidence used to derive it.

### Exit criteria

A reviewer can inspect any discrepancy and reconstruct exactly which board/engine facts and player statements support it.

---

## Phase 8 — Hypothesis and contradiction ledger

### Goal

Replace static weakness labels with evidence-backed, revisable participant-specific hypotheses.

### Candidate concept

```text
LearnerHypothesis
```

### Candidate structure

```yaml
hypothesis_id:
statement:
status:
supporting_evidence:
contradictory_evidence:
contexts:
competing_explanations:
evidence_strength:
first_observed:
last_tested:
revision_history:
```

### Candidate lifecycle

```text
Observed
→ Candidate
→ Supported
→ Training Eligible
→ Improving / Not Improving
→ Competency Candidate
```

Alternative paths:

```text
Candidate → Contradicted → Retired
Candidate → Insufficient
Supported → Weakened
```

### Required behaviors

- actively attach contradictory evidence;
- allow hypotheses to weaken;
- allow retirement;
- preserve history;
- never overwrite old evidence because a later interpretation changes.

### Exit criteria

The system can answer:

> Why does Chess Mentor currently believe this about the player?

with inspectable support, contradiction, context, and uncertainty.

---

## Phase 9 — Evidence-aware tutoring session workflow

### Goal

Create a controlled interaction sequence rather than a free-form chatbot.

### Candidate session state machine

```text
SELECT POSITION
→ PRESENT POSITION
→ CAPTURE MINIMAL RESPONSE
→ OPTIONAL STANDARDIZED PROBE
→ FREEZE PLAYER EVIDENCE
→ REVEAL CHESS EVIDENCE
→ COMPARE
→ EXPLAIN
→ UPDATE EVIDENCE
```

Later extensions may add:

```text
PRACTICE
→ TEST
→ UPDATE LEARNER HYPOTHESIS
```

### Key constraints

- Engine answer cannot leak before player evidence is frozen where the session intends pre-engine reasoning capture.
- Tutoring explanation cannot silently mutate earlier evidence.
- Information sequencing is part of correctness.

### Exit criteria

A complete local session can be replayed from stored evidence and state transitions.

---

## Phase 10 — Training intervention registry

### Goal

Make pedagogy inspectable and testable instead of letting the LLM invent every exercise ad hoc.

### Candidate concept

```text
TrainingIntervention
```

Possible early families:

- candidate-generation drill;
- opponent-resource verification;
- calculation-tree exercise;
- final-position evaluation;
- quiet-move comparison;
- plan-generation exercise;
- prophylaxis exercise;
- defensive-resource search.

### Candidate structure

```yaml
intervention_id:
targets:
eligibility_requirements:
exercise_definition:
progression:
success_observation:
transfer_test:
```

### Critical boundary

```text
supported diagnosis ≠ effective intervention
```

Intervention effectiveness requires separate evidence.

### Exit criteria

A training recommendation can be traced to an eligible hypothesis and a defined intervention rather than generated as unsupported advice.

---

## Phase 11 — Transfer and mastery evidence

### Goal

Measure whether learning persists beyond the exercise itself.

### Evidence ladder

```text
Exercise success
→ Near transfer
→ Far transfer
→ Real-game transfer
→ Competency candidate
```

### Principles

- Solving drills is not mastery.
- Rating improvement is useful but too noisy to be the only signal.
- Fresh positions matter.
- Real-game recurrence matters.

### Exit criteria

The system can distinguish training performance from transfer and can revise the learner hypothesis accordingly.

---

## Phase 12 — Longitudinal learner state

### Goal

Make Chess Mentor persistent across weeks/months of play.

### Candidate event stream

```text
GameImported
PositionSelected
PlayerReasoningCaptured
ReasoningDiscrepancyObserved
HypothesisCreated
ContradictionObserved
InterventionAssigned
ExerciseCompleted
TransferTestCompleted
HypothesisRevised
CompetencyObserved
```

### Recommended architectural bias

Prefer an append-oriented/evidence-ledger model over mutable numeric weakness scores.

Derive current learner state from history where practical.

### Exit criteria

The system can reconstruct how a learner hypothesis changed over time and why its current state exists.

---

# 5. Product surfaces

## 5.1 CLI first

Build the domain and workflow through a CLI before a polished UI.

Possible eventual commands:

```bash
cme import games.pgn
cme games inspect
cme position packet <position-id>
cme analyze <position-id>
cme positions select
cme session start
cme hypotheses list
cme hypothesis show <id>
cme evidence show <id>
```

The exact CLI should emerge from implemented capabilities rather than be frozen now.

## 5.2 Local web UI later

Candidate views:

```text
Dashboard
├── Recent games
├── Current learning focus
├── Candidate hypotheses
├── Evidence
├── Training
└── Progress
```

Position/session view:

```text
Board
↓
Player response
↓
Diagnostic probing when appropriate
↓
Reveal
↓
Explanation
↓
Practice / next step
```

Do not build this until the session and evidence contracts are stable.

---

# 6. LLM integration strategy

## Do not start with the LLM tutor

The LLM should receive well-structured evidence rather than be asked to invent the substrate.

Preferred context sections:

```text
OBJECTIVE_CHESS_EVIDENCE
PLAYER_REPORTED_EVIDENCE
ANALYST_DERIVED_EVIDENCE
SUPPORTED_LEARNER_HYPOTHESES
CONTRADICTORY_EVIDENCE
UNRESOLVED_COMPETING_EXPLANATIONS
CLAIM_CEILING
```

Potential LLM responsibilities later:

- human-readable chess explanation;
- Socratic dialogue;
- candidate learner hypotheses;
- comparison of competing explanations;
- lesson adaptation;
- explanation of evidence and uncertainty.

Responsibilities that should remain deterministic/provider-owned where possible:

- legality;
- FEN parsing;
- board rendering;
- material;
- engine evaluation;
- source identity;
- provenance;
- immutable raw responses.

---

# 7. Evaluation infrastructure

Eventually build evaluation harnesses for:

## Chess correctness

- Is the explanation consistent with objective position/engine evidence?

## Evidence sufficiency

- Does the conclusion follow from the cited evidence?

## Personalization

- Could substantially the same diagnosis be given generically to many players at this rating?

## Overclaiming

- Has a local discrepancy been promoted into a stable learner trait without recurrence?

## Contradiction handling

- Were successful/control cases searched and incorporated?

## Pedagogical linkage

- Does the recommended intervention target the supported discrepancy?

## Transfer

- Does later fresh evidence show improvement beyond the training exercise?

---

# 8. Candidate future repository structure

This is a direction map, **not an instruction to create all directories immediately**.

```text
src/chess_mentor_engine/
├── chess/
│   ├── games/
│   ├── positions/
│   ├── notation/
│   └── context/
├── analysis/
│   ├── engines/
│   ├── features/
│   └── position_selection/
├── evidence/
│   ├── chess/
│   ├── player/
│   └── provenance/
├── learning/
│   ├── discrepancies/
│   ├── hypotheses/
│   ├── recurrence/
│   └── learner_state/
├── pedagogy/
│   ├── interventions/
│   ├── exercises/
│   ├── transfer/
│   └── mastery/
├── tutoring/
│   ├── sessions/
│   ├── dialogue/
│   └── explanations/
└── evaluation/
    ├── chess/
    ├── diagnosis/
    └── pedagogy/
```

Create modules only when the corresponding phase earns them.

---

# 9. Recommended implementation sequence

The preferred sequence is:

```text
0. Repository/authority reconciliation
1. Canonical Game + Position substrate
2. Position Context Packet
3. Deterministic chess-feature extraction
4. Engine-analysis abstraction
5. Diagnostic position selection
6. Player Decision Evidence capture
7. Reasoning Discrepancy representation
8. Hypothesis + contradiction ledger
9. Tutor session state machine
10. Training intervention registry
11. Transfer/mastery evidence
12. Longitudinal learner state
13. CLI hardening
14. Local web UX
15. Broader provider/LLM integration
```

Do not parallelize later conceptual layers before the upstream evidence contracts are stable unless a bounded spike is explicitly labeled experimental.

---

# 10. Phase-gate discipline

For every phase, require:

1. **Problem statement** — What failure or product need does this solve?
2. **Evidence basis** — Which research finding or product requirement justifies it?
3. **Contract** — Inputs, outputs, provenance, and authority boundaries.
4. **Minimal implementation** — Smallest code proving the contract.
5. **Tests** — Deterministic tests and relevant fixtures.
6. **Counterexample handling** — What inputs or evidence should *not* produce the expected result?
7. **Documentation** — What is implemented versus still candidate.
8. **Exit criterion** — What must be true before the next phase is authorized?

Avoid using "implemented" to mean "concept described in docs."

---

# 11. Decisions to defer deliberately

Do **not** freeze these prematurely:

- final persistent database technology;
- production LLM provider;
- production engine provider;
- final learner taxonomy;
- numeric learner scores;
- final mastery thresholds;
- final intervention library;
- web framework;
- cloud deployment architecture;
- multiplayer/coaching features;
- cross-player analytics;
- rating prediction;
- social/gamification features.

The repository should first prove the evidence and tutoring contracts.

---

# 12. Error-prevention checklist

Use this section when starting new implementation work.

## Do not confuse

```text
engine evaluation
with
player reasoning
```

```text
player self-report
with
objective chess truth
```

```text
analyst coding
with
raw participant evidence
```

```text
one position-level discrepancy
with
a recurring learner weakness
```

```text
recurrence
with
causal cognitive explanation
```

```text
supported diagnosis
with
effective training intervention
```

```text
exercise success
with
transfer/mastery
```

```text
research concept
with
production domain object
```

```text
candidate architecture
with
ratified architecture
```

```text
model eloquence
with
evidence quality
```

---

# 13. Repository documentation discipline

Each important concept should eventually have one authoritative home.

Suggested hierarchy:

```text
docs/product/
    product definition, principles, roadmap

docs/domain/
    ratified domain concepts and invariants

docs/architecture/
    implemented architecture and boundaries

docs/research/
    experiments, hypotheses, findings, claim ceilings

docs/decisions/
    ratified ADRs
```

Research should be allowed to propose concepts before domain/architecture documents ratify them.

A useful progression is:

```text
Research finding
→ Candidate product implication
→ Implementation experiment
→ Ratified domain/architecture decision
→ Production implementation
```

Do not skip from research idea directly to canonical architecture because the idea sounds good.

---

# 14. Near-term build milestone

## Milestone M1 — Trustworthy Chess Evidence Substrate

Recommended initial production milestone:

> Given one or more PGN games, Chess Mentor Engine can deterministically ingest them, reconstruct canonical positions, generate accurate Position Context Packets, attach normalized engine evidence with provenance, and expose all of it through tests and a minimal developer-facing interface.

M1 deliberately excludes:

- player psychology;
- learner diagnosis;
- tutoring recommendations;
- interventions;
- persistent learner model;
- polished GUI.

### M1 acceptance criteria

- canonical PGN ingestion works on representative fixtures;
- duplicate/malformed inputs are handled explicitly;
- positions have stable identity;
- FEN/board/piece-map/material representations agree;
- engine provider is abstracted;
- engine provenance is recorded;
- Position Context Packets serialize deterministically;
- research fixtures from earlier pilots can be represented without manual repair;
- tests and lint pass;
- documentation distinguishes deterministic, engine-derived, and interpretive data.

This is the best first implementation target because every later personalized-tutoring capability depends on trustworthy chess evidence.

---

# 15. M2 candidate milestone — Player Evidence and Discrepancy

Only after M1 is qualified:

> Capture pre-engine player reasoning as immutable evidence and support traceable position-level comparison against objective chess evidence.

Candidate M2 scope:

- player response capture;
- evidence timing/exposure metadata;
- raw versus analyst-coded separation;
- position-level Reasoning Discrepancy;
- correct/no-discrepancy controls;
- replayable provenance.

Do not include recurring learner hypotheses until M2 position-level evidence is trustworthy.

---

# 16. M3 candidate milestone — Evidence-Backed Learner Hypotheses

Only after M2 is qualified:

> Accumulate position-level discrepancies and controls into revisable participant-specific hypotheses with support, contradiction, contexts, competing explanations, and explicit evidence strength.

This is where Chess Mentor Engine begins to become genuinely persistent and personalized.

---

# 17. M4 candidate milestone — Tutor Loop

Only after M3 is qualified:

> Use supported learner hypotheses to select diagnostic interactions and bounded training interventions, then gather new evidence that can strengthen, weaken, or retire the hypothesis.

This is the first milestone where a user-facing tutor experience should become a major implementation focus.

---

# 18. Current recommendation

Begin implementation with **M1: Trustworthy Chess Evidence Substrate**.

The first coding work should be deliberately boring and deterministic:

```text
PGN
→ CanonicalGame
→ CanonicalPosition
→ PositionContextPacket
→ EngineEvidence
```

Once that path is reliable, the repository can safely move toward the distinctive part of the product:

```text
PlayerDecisionEvidence
→ ReasoningDiscrepancy
→ LearnerHypothesis
→ Intervention
→ Transfer
```

The repository should earn personalization through evidence rather than beginning with a personalized-sounding LLM.

---

## Durable principles

> It is not enough to know which move was wrong; the repository must preserve the position and evidence that made it wrong.

> It is not engine evidence and is not player self-report alone; useful diagnosis depends on preserving both without confusing their authority.

> A weakness label is not the starting point; it is the possible downstream result of repeated, contradictory-tested evidence.

> The LLM should explain and reason over evidence, not manufacture the evidence substrate.

> Build the evidence system first. Let the tutor emerge from it.
