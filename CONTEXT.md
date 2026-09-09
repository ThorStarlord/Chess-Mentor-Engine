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

The bounded evidence stack now extends through M15:

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

Recent promotion sequence:

```text
M11 Longitudinal Learner State        MERGED - PR #43
M12 Local Evidence CLI                MERGED - PR #44
M13 Persistent Tutor Session CLI      MERGED - PR #45
M14 Engine-Backed Analysis CLI        MERGED - PR #46
M15 Evaluation Presentation Contract  CURRENT IMPLEMENTATION - PR #47
```

M14 was qualified at exact head `c2e1ded12ae3dd40402c67ddb713db7f6c38fdbc`
in CI run `34411793232` and merged as
`6112b3a970c3b2a4b10b58a6cb3b438d332e605e`. The hardened M15 runtime head
`45dd5706530347a7f74d7e9bb745a3d0dcd2e501` passed both repository CI jobs in
run `34412594441`: 566 native tests passed with 8 intentional external-engine
skips, Ruff passed, and the independent Stockfish witness passed. PR #47 remains
the authority for the final documentation-bearing head and merge provenance.

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
fail closed on evidence drift. It does not define move-quality thresholds or tutor
language.

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

**Human/model judgment:** explanation authorship, semantic discrepancy coding,
hypothesis evidence relations/challenge review, pedagogical applicability, exposure
classification, and outcome scoring retain explicit provenance. M13-M15 do not
fabricate these judgments.

## Contracts contributors must preserve

```text
objective chess truth != participant self-report != analyst/model coding
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
engine analysis != evaluation presentation != mentor explanation
```

M14 owns the engine-backed evidence package. M15 owns only a versioned,
deterministic projection of exact M3/M4 records. It is not authorization to turn
centipawns, mates, bounds, partial results, incompatible regimes, or engine failures
into unversioned frontend labels or learner diagnoses. Grounded mentor language
remains a separate downstream authority.

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

M15 is currently a Python API rather than a new CLI mutation:

```python
from chess_mentor_engine.presentation import build_evaluation_presentation
```

The presentation API consumes exact M3/M4 records. It does not run an engine,
modify M14 archives, round centipawns into pawn floats, convert PVs to SAN, or
assign `inaccuracy`, `mistake`, or `blunder` labels.

M13 likewise does not generate engine analysis, M6 assessments, M7 hypotheses,
explanation prose, training decisions, or automatic M11 mutations. Those records
must come from their owning contracts.

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
```

## Current claim ceiling and stop boundary

The repository can now preserve a longitudinal evidence history, expose selected
qualified capabilities through a local CLI, and project exact engine/comparison
evidence into a deterministic UI-safe read model. It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- intervention-caused improvement, automatic mastery, or universal thresholds;
- automatic M6 discrepancy generation from engine evidence;
- automatically generated mentor prose grounded in a validated feedback contract;
- autonomous M7/M11 mutation from tutoring or M14 analysis;
- a web UI, authenticated hosted service, or production multi-user persistence;
- empirical tutoring efficacy.

The next work package is grounded mentor feedback over verified evidence. It must
remain separate from both M14 engine analysis and M15 presentation semantics; it is
not part of M15.

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