# M25 — Coach Review Read Model & Presentation Contract

## Purpose

M25 adds a thin deterministic application-facing projection over already-qualified
repository records. It exists so a later web or desktop UI does not need to infer
which layer owns chess truth, diagnostic selection, participant authorization,
workflow state, deterministic feedback, model prose, or model-output evaluation.

M25 is a **read model only**. It creates no new chess facts, learner hypotheses,
training decisions, consent, tutor transitions, model output, or evaluation verdicts.

The section order is frozen as:

```text
objective_evidence        M15
diagnostic_selection      M18
participant_authority     M21
tutor_state               M8
deterministic_grounding   M16
model_coaching             M19
model_evaluation           M20
```

Every downstream section is optional and remains `null` when its source record does
not exist. M25 never fills a missing layer by guessing.

## Public API

```python
from chess_mentor_engine.review import build_coach_review_read_model
```

The output schema is:

```text
m25.coach-review-read-model.v1
```

The output is content-addressed by `read_model_id` and `fingerprint`. Each source
layer also has an explicit source fingerprint in `source_fingerprints`.

## Objective evidence is never reinterpreted

The M15 `evaluation_presentation` is copied verbatim into `objective_evidence` after
mechanical validation. M25 requires the qualified M15 score-semantics contract:

```text
canonical_engine_perspective = white
display_perspective = decision_mover
centipawn_unit = centipawns
mate_representation = winner_and_plies_to_mate
bound_semantics = ordering_bound_in_display_perspective
```

This preserves distinctions that a UI must not collapse:

- canonical White score vs decision-mover display score;
- exact centipawn values vs ordering bounds;
- symbolic mate vs centipawn evaluation;
- exact vs bounded vs partial vs incompatible vs unavailable evidence;
- successful child analysis vs unavailable or failed child evidence.

Non-exact comparisons may not expose an exact mover-relative centipawn delta. Mate
records remain symbolic.

## Diagnostic and participant layers

When supplied, M18 candidate and batch records are mechanically checked for:

- content-addressed signal identity;
- content-addressed candidate identity;
- candidate membership in the exact batch;
- content-addressed batch identity;
- matching game, position, and M4 comparison identity with the M15 presentation.

M21 participant authorization remains distinct from diagnostic selection. M25
requires a supplied authorization to be explicitly participant-authored, selected,
and capture-consented. Its candidate and batch fingerprints must match the exact
M18 records.

A supplied M21 launch must retain its original content-addressed identity and exact
authorization/candidate/batch references. Its launch snapshot must still be the M8
`selected` state. A later supplied M8 `tutor_state` may advance through the qualified
M8 workflow, but it must retain the same tutor-session identity.

M25 does not infer consent or start a tutor session.

## Deterministic grounding

A supplied M16 grounded-feedback record is checked for:

- exact M16 schema and claim scope;
- content-addressed feedback identity;
- valid fingerprinted M16 policy;
- exact M15 presentation fingerprint and M4 comparison reference;
- required objective, reasoning, and reflection sections;
- matching tutor-session identity when an M8 state is also supplied.

The entire exact M16 record is then copied into `deterministic_grounding`. M25 does
not rewrite its prose or merge it with model-authored language.

## Model language remains separate

A supplied M19 record is copied into `model_coaching` only after checking:

- exact M19 schema and content-addressed identity;
- `session_local_model_rendering` claim scope;
- `request_bound_not_semantically_verified` grounding status;
- exact M16 grounded-feedback reference;
- tutor-session continuity.

The M19 prose is never copied into `objective_evidence` or
`deterministic_grounding`. A model can therefore make an overclaim while the
objective and deterministic sections remain unchanged and inspectable.

## Bounded evaluator judgment remains non-truth

A supplied M20 record is copied into `model_evaluation` only after checking:

- exact M20 schema and content-addressed identity;
- exact M19 coaching and M16 feedback references;
- complete, unique seven-dimension judgment coverage;
- only `pass`, `fail`, or `unclear` verdicts;
- qualification status derived from those verdicts;
- `verified_against_exact_m16_m19_sources` source-integrity status;
- `bounded_model_output_quality_assessment` claim scope;
- `truth_status = not_established_by_m20_evaluation`.

Accepted, rejected, and inconclusive evaluator outcomes therefore remain quality
assessment records, never objective chess truth.

## Progressive dependency rules

M25 rejects impossible partial bundles:

```text
M18 candidate <-> M18 batch are paired
M21 authorization requires M18 selection
M21 launch requires M21 authorization
M8 tutor state requires M21 launch
M19 coaching requires M16 grounding
M20 evaluation requires M19 coaching
```

An objective-only M15 view is valid. An M15 + M16 view with no model output is also
valid. Missing downstream layers stay visibly absent.

## Local JSON inspection CLI

M25 provides a repository-only JSON command:

```bash
cme-coach-review path/to/m25-bundle.json
```

The input object must contain exactly these keys; optional values are explicit
`null`:

```json
{
  "evaluation_presentation": {},
  "diagnostic_candidate": null,
  "diagnostic_batch": null,
  "authorization": null,
  "launch": null,
  "tutor_state": null,
  "grounded_feedback": null,
  "model_coaching": null,
  "model_evaluation": null
}
```

The command reads local files only. It performs no provider calls, engine calls,
network requests, credentials, persistence mutations, or deployments.

## Hermetic qualification

Focused M25 suite:

```bash
python -m pytest tests/test_m25_coach_review_read_model.py
```

The golden objective matrix covers:

- exact White perspective;
- bounded Black perspective with reversed bound semantics;
- symbolic mate;
- partial root evidence;
- empty/unavailable root evidence;
- compatible child reanalysis;
- incompatible child analysis regime;
- failed child analysis.

Additional rejection tests cover:

- M18 candidate/batch drift;
- rehashed M21 authorization and launch-reference drift;
- M16 presentation-reference drift;
- M19 grounded-feedback-reference drift;
- M20 truth-status promotion;
- M20 qualification status contradicting its judgments;
- invalid progressive dependency combinations;
- malicious model overclaim isolated from the true M15/M16 sections;
- deterministic projection and source immutability;
- strict local CLI input behavior.

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

## Explicit non-claims

M25 does not establish:

- correctness of arbitrary engine output beyond existing M3/M4/M15 qualification;
- semantic truthfulness of arbitrary model prose;
- correctness or completeness of an arbitrary evaluator;
- pedagogical optimality or tutoring efficacy;
- production UI usability, accessibility, localization, or visual quality;
- provider/vendor selection, credentials, retries, costs, rate limits, or latency;
- deployment readiness or production QA.

M25 is the stable semantic handoff a future UI can render without reconstructing
authority relationships from lower-level repository artifacts.
