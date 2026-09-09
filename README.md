# Chess Mentor Engine

Chess Mentor Engine is a persistent chess-learning system that turns
provenance-bound chess evidence into participant-specific diagnostic and training
decisions without collapsing objective analysis, learner inference, tutoring, and
pedagogy into one opaque layer.

Repository description: Persistent AI chess tutor that learns how you think,
diagnoses recurring mistakes, and turns game evidence into personalized training.

## Start here

The [post-M10 milestone runbook](docs/runbooks/post-m10-milestone-runbook.md) is the
entry point for the three completed features: corrected UCI evidence, durable
artifacts/verified M8 recovery, and M10 outcome/transfer evidence. It includes
setup, API examples, validation commands, human protocols, and failure handling.

Use [current build status](docs/product/repository-build-status.md) for the exact
merged feature/CI provenance and claim limits, and the
[architecture overview](docs/architecture/architecture.md) for layer ownership.
The three-feature queue is complete in PRs #39, #40, and #41. This documentation
pass does not authorize M11 or any further runtime feature.

## Product thesis and implemented scope

Chess engines can answer what is objectively happening in a position. A tutor
should also help answer why a particular player missed it, whether the pattern
recurs, and what bounded practice may be appropriate next.

```text
objective chess evidence
-> frozen player decision evidence
-> position-local reasoning discrepancy
-> participant-specific recurring hypothesis
-> evidence-aware tutoring / explicit training-intervention selection
-> separate practice and transfer evidence
```

Each arrow is a separate authority boundary, not an automatic end-to-end command.
M1-M10 are implemented and qualified within their bounded software contracts:

| Surface | What is available |
| --- | --- |
| M1-M4 | Deterministic chess evidence, provenance-bound engine analysis, decision comparison and diagnostic selection, including successful controls. |
| M5 | Immutable participant evidence, capture/freeze, exposure/deviation provenance and objective reveal. |
| M6-M7 | Local discrepancy facts and assessments; participant-specific hypothesis, recurrence, challenge-review and lifecycle records. |
| M8 | Controlled tutoring with pre-reveal information boundaries and explanation provenance. |
| M9 | Versioned training definitions, explicit applicability mappings and conservative `selected / ineligible / unclear` decisions. |
| M10 | Predeclared policies, frozen attempts, completion/observation ledgers and independent practice/near/far/real-game evidence assessments. |
| Local storage | Immutable SQLite-backed JSON artifacts, exact prompt dependencies, canonical comparison fingerprints and verified M8 recovery. |

The UCI provider is now `0.2`: Black-root bounds are normalized into White
ordering and explicit invalid MultiPV ranks are rejected. See the
[compatibility note](docs/architecture/uci-evidence-contract-repair.md).

Qualified software behavior is not proof of mastery, intervention-caused
improvement, or empirical tutoring value. M11 longitudinal learner state,
production-grade persistence services, an end-user CLI/UI, and broader product
workflows remain outside the qualified scope.

## Getting started

Use Python 3.11 or newer. From the repository root, in a POSIX shell:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -c "import chess_mentor_engine.analysis; import chess_mentor_engine.storage; import chess_mentor_engine.evaluation"
```

See the consolidated runbook for Windows interpreter commands and the Ubuntu CI
platform boundary. Stockfish is an explicitly configured external executable; no
engine binary is bundled.

There is **no end-user product CLI** and no installed `cme` command. The features
are Python package APIs; pytest, Ruff, and compilation commands are development
and qualification tools.

## Using the APIs

**Engine evidence:** instantiate `UciAnalysisProvider` with the external engine
path and explicit options, construct `AnalysisRequest`, then call `analyze` with
a canonical position. Inspect failure/partial/terminal status, score bounds,
termination and provenance before consumption. The consolidated runbook contains
a minimal example. Never relabel historical `0.1` evidence as repaired output.

**M7 hypotheses:** use `chess_mentor_engine.learning` to create/revise hypotheses,
attach exact M6 evidence, run recurrence assessment, record challenge review, and
rebuild `HypothesisLedgerSnapshot`. Supported recurrence is not a causal cognitive
mechanism, permanent trait, or automatic training eligibility.
See `tests/test_m7_qualification.py` and the
[M7-M9 runbook](docs/runbooks/m7-m9-milestone-runbook.md).

**M8 tutoring:** use `chess_mentor_engine.tutoring` in this order:

```text
start_tutor_session
-> present_tutor_position
-> present_tutor_capture_stage
-> capture_tutor_response
-> freeze_tutor_response
-> [optional planned probe: present/capture/freeze]
-> reveal_tutor_objective_evidence
-> record_tutor_reasoning_comparison
-> [optional] attach_tutor_hypothesis_context
-> record_tutor_explanation
-> complete_tutor_session
```

All planned pre-reveal responses must be frozen. M6 comparison binds the exact
final capture; attached M7 context must be complete, active and current.
See `tests/test_m8_qualification.py`.

**M9 selection:** use `chess_mentor_engine.training` to define exercises and an
intervention, build a registry, record an explicit hypothesis/intervention mapping,
define the selection policy, and call `select_training_intervention`. Multiple
applicable mappings remain `unclear`; the selector does not rank by text similarity
or infer effectiveness. See `tests/test_m9_qualification.py`.

**Durability and M8 recovery:** use `LocalArtifactStore`, `save_tutor_session`, and
`load_tutor_session`. Supply exact definitions for every planned prompt and retain
the returned reference in an application checkpoint. Recovery verifies integrity
and replays transitions before returning a resumable session; later saves append
snapshots. See the [storage runbook](docs/runbooks/durable-artifacts-and-replay.md).
Participant filtering is not authentication; protect the plaintext database and
supply additional upstream archival dependencies explicitly.

**M10 outcomes:** define `OutcomePolicy`, then call `define_evaluation_plan` with
an exact selected M9 decision/intervention. Append frozen attempts, record practice
completion and rubric-bound observations, and call `assess_outcome_evidence` on
the complete known ledger. Read each dimension and its exclusions separately.
`mastery` and `causal_effect` remain `not_established`; there is no automatic M7
revision or M11 state update. See the
[M10 runbook](docs/runbooks/m10-outcome-transfer-evidence.md) and
`tests/test_outcome_evidence.py` / `tests/test_m10_qualification.py`.

## Validation commands

With the installed environment, from the repository root:

```bash
# Feature 1: existing provider tests plus normalization/rank regressions
python -m pytest tests/test_uci_provider.py tests/test_uci_evidence_contract.py
# Feature 2: storage, integrity, replay and fresh-process recovery
python -m pytest tests/test_artifact_store.py tests/test_tutor_storage.py
# Feature 3: outcome contract plus M9/M1/storage integration
python -m pytest tests/test_outcome_evidence.py tests/test_m10_qualification.py
# Existing upstream milestone boundaries
python -m pytest tests/test_m7_qualification.py tests/test_m8_qualification.py tests/test_m9_qualification.py
# Full regression, lint and supplemental syntax gate
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

After configuring `STOCKFISH_EXECUTABLE` to an actual external engine, run:

```bash
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

An unconfigured engine causes eight intentional skips, not a successful engine
witness. The [consolidated runbook](docs/runbooks/post-m10-milestone-runbook.md)
includes the exact Ubuntu installation/configuration sequence. CI runs pytest and
Ruff on Python 3.11 and an independent Stockfish job on pull requests into `main`
and pushes to `main`. No standalone static type checker is configured; lint,
syntax compilation and imports must not be described as type-checker validation.

## Human operational protocol

Preserve source and actor/version/instruction/run provenance for judgments where
the corresponding schema requires it. M7 evidence relations and challenge review,
M8 explanation authorship, and M9 pedagogical applicability remain explicit human
or model judgments. Freeze participant responses before objective reveal.

Before M10 collection, declare the criterion, rubric, contexts and delay. Record
actual exposure and assistance; unknown is not clean or unexposed. Preserve
failures, scorer disagreement and exclusions. Completion is not success, and
supported transfer is not causality or mastery. Never backdate an evaluation plan
to make previously studied evidence prospective.

For recovery, choose the intended checkpoint, keep consistent backups, restore
exact dependencies, and investigate mismatches rather than silently repairing
history. Generic M10 archival is not typed M10 recovery. The consolidated runbook
and linked feature runbooks contain the detailed operating steps.

## Documentation map

- [Post-M10 milestone runbook](docs/runbooks/post-m10-milestone-runbook.md): consolidated feature use, verification and human handoff.
- [Current build status](docs/product/repository-build-status.md): authoritative milestone/claim status and merged qualification provenance.
- [Architecture overview](docs/architecture/architecture.md): implemented boundaries versus historical hypotheses.
- [UCI repair](docs/architecture/uci-evidence-contract-repair.md): score/rank behavior and provider-version compatibility.
- [Durable artifacts and verified replay](docs/architecture/durable-artifacts-and-replay.md): storage/recovery and legacy limits.
- [M7 qualification](docs/architecture/m7-qualification.md), [M8 tutoring](docs/architecture/evidence-aware-tutor-session.md), and [M9 training](docs/architecture/training-intervention-registry.md): upstream contracts.
- [M10 outcome evidence](docs/architecture/outcome-transfer-evidence.md) and [ADR 0009](docs/decisions/0009-outcome-transfer-evidence-contract.md): protocol-bound evaluation and claim limits.
- [Decision records](docs/decisions/README.md), [CONTEXT.md](CONTEXT.md), [product definition](docs/product/product-definition.md), and [product discovery](docs/product/product-discovery.md): contributor orientation and remaining hypotheses.
