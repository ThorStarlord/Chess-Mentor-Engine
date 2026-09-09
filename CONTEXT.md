# Chess Mentor Engine context

## Product and authority

Chess Mentor Engine is a persistent chess-learning system intended to convert
objective chess evidence into individualized teaching decisions without collapsing
chess truth, participant self-report, analyst/model interpretation, tutoring, and
pedagogy into one authority layer.

The central questions remain distinct:

```text
What is objectively happening on the board?
What did the player actually notice, consider, and expect?
What participant-specific explanation is currently supported strongly enough to affect teaching?
```

The third question is a product hypothesis, not a claim that the system has
established a causal cognitive mechanism.

Use [current build status](docs/product/repository-build-status.md) as the current
implementation/qualification authority. Historical milestone details remain in
architecture records, ADRs, runbooks, and Git history. Frozen research protocols
and pilot artifacts are not superseded by software qualification.

## Current implementation

The bounded evidence stack now extends through M16:

- **M1-M4:** canonical PGN/game/position provenance, deterministic chess context and
  features, normalized UCI evidence, objective played-decision comparison, and
  bounded diagnostic candidate selection.
- **M5-M7:** frozen participant decision evidence, position-local discrepancy facts
  and assessments, participant-specific descriptive learner hypotheses,
  contradiction/challenge evidence, recurrence policies, and append-only lifecycle.
- **M8-M10:** controlled evidence-aware tutoring, explicit hypothesis/intervention
  applicability and conservative training selection, then separate
  practice/near/far/real-game outcome evidence.
- **M11:** append-only longitudinal learner state bound to an exact current M7
  snapshot/revision, with optional exact M10 outcome evidence for that same
  revision. It does not create scalar weakness scores, causal claims, or mastery.
- **M12:** installed read-only `cme` surface for deterministic PGN inspection,
  engine-free position packets, and verified participant-scoped artifact reads.
- **M13:** persistent `cme tutor ...` workflow. Every write verifies and replays the
  exact prior M8 checkpoint, applies one existing state transition, and appends a
  successor checkpoint.
- **M14:** bounded `cme analyze` workflow over qualified M3/M4 contracts. It analyzes
  an exact canonical position with an explicit UCI engine, reanalyzes the exact
  canonical child when required for out-of-MultiPV played moves, preserves native
  comparison semantics, and can optionally archive the complete evidence package
  in an existing participant-scoped local artifact store.
- **M15:** deterministic `chess_mentor_engine.presentation` projection over exact
  M3/M4 records. It makes White versus original decision-mover score perspective,
  ordering bounds, symbolic mate, evidence quality, PVs, engine identity, and exact
  evidence references explicit without creating new chess judgments.
- **M16:** deterministic `chess_mentor_engine.feedback` composition after an exact
  M8/M6 comparison. It verifies the same M3/M4 evidence through M15, preserves every
  M6 assertion, optionally preserves complete active-current M7 context, emits
  bounded reflection questions, and may record the result through the existing M8
  explanation transition with template provenance.

Recent promotion sequence:

```text
M11 Longitudinal Learner State        MERGED - PR #43
M12 Local Evidence CLI                MERGED - PR #44
M13 Persistent Tutor Session CLI      MERGED - PR #45
M14 Engine-Backed Analysis CLI        MERGED - PR #46
M15 Evaluation Presentation Contract  MERGED - PR #47
M16 Grounded Mentor Feedback Composer CURRENT IMPLEMENTATION - PR #48
```

M15 was qualified at exact head `275bafceb949fc564b80a5f0b09b062514d7602c`
in CI run `34412807819` and merged as
`c93faf74cb1d7b54d05853cd4775a57c725cfc7b`. The repaired M16 runtime head
`f3118f9d0d56de3499aa6f2b7bb72bc5d7ed4ac2` passed both repository CI jobs in
run `34413596649`: native tests and Ruff passed, and the independent Stockfish
witness passed. PR #48 and Git history remain authoritative for the final
documentation-bearing head and merge provenance.

## Separation of responsibilities

**Objective chess authority:** deterministic chess tooling owns canonical board
state, legal actions, exact source provenance, and qualified low-level features.
Engine providers supply versioned evaluation/PV evidence with explicit
partial/bounded/failure states. M4 comparisons preserve mate, terminal, inversion,
and compatibility semantics instead of manufacturing a universal human-readable
score.

**Presentation authority:** M15 may project exact M3/M4 evidence into an explicit
read model, including a decision-mover score view and evidence-quality labels. It
must preserve the canonical White evaluation, reverse ordering bounds when the
perspective reverses, keep mate symbolic, preserve fingerprints/provenance, and
fail closed on evidence drift. It does not define move-quality thresholds or learner
diagnoses.

**Feedback-composition authority:** M16 may turn already-qualified M15/M6 and
optional complete active-current M7 evidence into deterministic session-local
feedback. It must verify the exact M4/M3 references already bound into the tutor
session, preserve every M6 assertion, retain every attached active M7 revision, and
keep non-exact objective evidence non-exact. Its reflection questions are not M9
training selections. M16 v1 is template-driven and does not invoke an LLM.

**Participant-evidence authority:** raw/frozen player responses and their exposure
state remain distinct from objective engine evidence. Later structured coding does
not silently replace raw self-report.

**Learning-inference authority:** M6/M7 describe bounded position discrepancies and
participant-specific recurring hypotheses. Recurrence is not a causal cognitive
mechanism, permanent trait, or automatic training eligibility.

**Pedagogy/outcome authority:** M9 selects only through explicit versioned
applicability rules. M10 measures bounded outcome/transfer evidence under a
predeclared protocol. Practice completion, successful exercise performance,
transfer, causality, and mastery remain different claims.

**Application/persistence authority:** deterministic code owns sequencing, exact
identities, participant scope, integrity checking, replay, and append-only storage.
Checksums are integrity mechanisms, not signatures; participant filtering is not
authentication.

**Human/model judgment:** semantic discrepancy coding, hypothesis evidence
relations/challenge review, pedagogical applicability, exposure classification, and
outcome scoring retain explicit provenance. M16 does not create those judgments.
Future model-authored language must remain provenance-bearing and must not silently
replace M6/M7 authority.

## Contracts contributors must preserve

```text
objective chess truth != participant self-report != analyst/model coding
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
engine analysis != evaluation presentation != grounded feedback != model coaching
```

M14 owns the engine-backed evidence package. M15 owns only a versioned,
deterministic projection of exact M3/M4 records. M16 owns deterministic composition
from those exact records plus existing M6/M7 evidence; it is not authorization to
invent new chess truth, causal learner diagnoses, training prescriptions, or
unversioned model claims.

## CLI and API boundaries

The project is a Python 3.11+ package and has an installed `cme` command. Current
bounded commands include:

```text
cme games inspect
cme position packet
cme analyze
cme artifacts list/show/verify
cme tutor ...
```

`cme position packet` remains deterministic and engine-free. `cme analyze` requires
an explicit external UCI executable or PATH name. Optional M14 archival requires an
existing artifact database plus an explicit participant; it never creates a new
learner or tutor state record.

M15 and M16 are currently Python APIs rather than new CLI mutations:

```python
from chess_mentor_engine.presentation import build_evaluation_presentation
from chess_mentor_engine.feedback import (
    compose_grounded_mentor_feedback,
    record_grounded_mentor_feedback,
)
```

The M15 presentation API consumes exact M3/M4 records. The M16 composer additionally
requires an exact compared M8 TutorSession whose M6 context already binds the
supplied M3/M4 evidence. Neither API runs a new engine or changes upstream evidence.
M16 v1 does not invoke a model, assign training, or mutate M7/M11.

M13's `cme tutor explain` command remains an explicit-input explanation surface; it
is not silently replaced by M16.

## Development and qualification

The full repository gate is:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish test requires `STOCKFISH_EXECUTABLE`; skipped external-engine tests
are not a successful witness. Pull-request CI is the merge gate. Ruff/tests/imports
and syntax compilation do not constitute a standalone static type-checker pass;
none is currently configured.

Focused current surface suites include:

```bash
python -m pytest tests/test_m11_qualification.py
python -m pytest tests/test_m12_cli.py
python -m pytest tests/test_m13_persistent_tutor_cli.py
python -m pytest tests/test_m14_engine_analysis_cli.py
python -m pytest tests/test_m15_evaluation_presentation.py
python -m pytest tests/test_m16_grounded_mentor_feedback.py
```

## Current claim ceiling and stop boundary

The repository can now preserve a longitudinal evidence history, expose selected
qualified capabilities through a local CLI, project exact engine/comparison evidence
into a deterministic UI-safe read model, and compose deterministic grounded
session-local feedback after an exact tutor comparison. It still does **not**
establish:

- causal cognitive diagnosis or permanent learner traits;
- intervention-caused improvement, automatic mastery, or universal thresholds;
- automatic M6 discrepancy generation from engine evidence;
- model/LLM-generated free-form coaching quality;
- autonomous M7/M11 mutation from tutoring or analysis;
- a web UI, authenticated hosted service, or production multi-user persistence;
- empirical tutoring efficacy.

Any future model-backed coaching or user-interface work must consume the versioned
M16 grounding boundary rather than weakening M3/M4/M6/M7 provenance.

## Research and product hypotheses

The broader product hypothesis remains a persistent tutor that learns from a
player's decision evidence over time and chooses bounded practice based on
inspectable support, contradiction, and outcomes. Implemented software contracts do
not settle the full production architecture or validate tutoring benefit.

The first formal product-validation protocol remains separate from the synthetic
software qualification corpus. See
[product discovery](docs/product/product-discovery.md),
[product definition](docs/product/product-definition.md), and the frozen research
artifacts under `docs/research/`.

The [repository build plan](docs/product/chess-mentor-engine-repository-build-plan.md)
preserves conceptual sequencing and historical rationale. Its older time-sensitive
stage statements do not override this current status authority or later accepted
contracts.