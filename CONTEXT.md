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

The bounded evidence stack now extends through M14:

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

Recent promotion sequence:

```text
M11 Longitudinal Learner State        MERGED - PR #43
M12 Local Evidence CLI                MERGED - PR #44
M13 Persistent Tutor Session CLI      MERGED - PR #45
M14 Engine-Backed Analysis CLI        CURRENT PACKAGE - PR #46
```

The M14 runtime implementation candidate `d36b20e4747a39cc2257e47b04b5be98ad8131e7`
passed both repository CI jobs in run `34411545018`: native full test/lint and the
independent external Stockfish witness. The final documentation-bearing candidate
must pass the same exact-head gates before PR #46 may merge.

## Separation of responsibilities

**Objective chess authority:** deterministic chess tooling owns canonical board
state, legal actions, exact source provenance, and qualified low-level features.
Engine providers supply versioned evaluation/PV evidence with explicit
partial/bounded/failure states. M4 comparisons preserve mate, terminal, inversion,
and compatibility semantics instead of manufacturing a universal human-readable
score.

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
classification, and outcome scoring retain explicit provenance. M13 and M14 do not
fabricate these judgments.

## Contracts contributors must preserve

```text
objective chess truth != participant self-report != analyst/model coding
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
engine analysis != UI presentation semantics != mentor explanation
```

M14 specifically preserves this last separation. Its package exposes the native
M3/M4 evidence needed downstream, but it is not authorization to turn centipawns,
mates, bounds, partial results, incompatible regimes, or engine failures into
unversioned frontend labels.

## CLI boundaries

The project is a Python 3.11+ package and now has an installed `cme` command.
Current bounded commands include:

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
```

## Current claim ceiling and stop boundary

The repository can now preserve a longitudinal evidence history and expose selected
qualified capabilities through a local CLI. It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- intervention-caused improvement, automatic mastery, or universal thresholds;
- a final UI-safe evaluation/read-model contract;
- automatic M6 discrepancy generation from engine evidence;
- automatically generated mentor prose grounded in a validated feedback contract;
- autonomous M7/M11 mutation from tutoring or M14 analysis;
- a web UI, authenticated hosted service, or production multi-user persistence;
- empirical tutoring efficacy.

The next work packages must remain separate: first define evaluation presentation
semantics, then build grounded mentor feedback over verified evidence. Neither is
part of M14.

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
