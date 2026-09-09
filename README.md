# Chess Mentor Engine

Chess Mentor Engine is a persistent chess-learning system that turns provenance-bound chess evidence into participant-specific diagnostic and training decisions without collapsing objective analysis, learner inference, tutoring, and pedagogy into one opaque layer.

Repository description: Persistent AI chess tutor that learns how you think, diagnoses recurring mistakes, and turns game evidence into personalized training.

## Product thesis

Chess engines can answer what is objectively happening in a position. A tutor should also help answer why a particular player missed it, whether the pattern recurs, and what bounded practice may be appropriate next.

```text
objective chess evidence
        ↓
player decision evidence
        ↓
position-local reasoning discrepancy
        ↓
participant-specific recurring hypothesis
        ↓
evidence-aware tutoring session
        ↓
explicit training-intervention selection
        ↓
separate practice and transfer evidence
```

The repository treats each arrow as a separate authority boundary with explicit provenance and qualification gates.

## Current repository status

The repository is no longer a minimal package. Milestones M1 through M10 are implemented and qualified through the following bounded surfaces:

- **M1-M4:** deterministic chess evidence, engine evidence, decision comparison, and diagnostic position selection;
- **M5:** immutable Player Decision Evidence capture, freeze, exposure/deviation provenance, and objective reveal;
- **M6:** position-local Reasoning Discrepancy facts, coding, assertions, and assessment;
- **M7:** participant-specific Learner Hypothesis Ledger, recurrence assessment, challenge review, and append-only lifecycle state;
- **M8:** replayable Evidence-Aware Tutor Session orchestration with hard pre-reveal information boundaries and explanation provenance;
- **M9:** versioned Training Intervention Registry, explicit hypothesis-to-intervention applicability mappings, and deterministic `selected / ineligible / unclear` decisions;
- **M10:** predeclared outcome policies, immutable attempt/completion/observation ledgers, and separate conservative practice/near/far/real-game evidence assessments. This qualifies software behavior, not mastery or intervention-caused improvement.

Bounded local durability is available through `chess_mentor_engine.storage`: immutable SQLite-backed JSON artifacts, exact prompt dependencies, and verified M8 session recovery. This adds recovery infrastructure without introducing a new diagnostic or learning milestone.

Automatic mastery, causal effectiveness, longitudinal learner state, production-grade persistence services, CLI/UI productization, and broader end-user workflows remain outside the qualified claim surface.

See [the current build-status record](docs/product/repository-build-status.md), [the M7-M9 milestone runbook](docs/runbooks/m7-m9-milestone-runbook.md), [the M10 runbook](docs/runbooks/m10-outcome-transfer-evidence.md), and [the local storage architecture](docs/architecture/durable-artifacts-and-replay.md).

## Development principles

- Start with evidence and preserve its provenance.
- Keep objective chess analysis separate from participant evidence and pedagogical interpretation.
- Treat learner diagnoses as bounded hypotheses, not hidden truths.
- Freeze participant evidence before revealing objective analysis.
- Require explicit applicability provenance before selecting a training intervention.
- Prefer `ineligible` or `unclear` to an unsupported prescription.
- Keep outcome evidence, intervention effectiveness, learning, transfer, and mastery separate from intervention selection.

## Getting started

Use Python 3.11 or newer. Create a virtual environment and install the project with development dependencies:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

There is **no end-user product CLI yet**. The qualified M7-M10 capabilities are Python package APIs. The command-line interface currently exists for development and validation only.

## Using the M7-M10 APIs

### M7 — learner-hypothesis qualification

Use `chess_mentor_engine.learning` to create/revise participant-specific hypotheses, attach exact M6 evidence, run versioned recurrence assessment, record contradiction/counterexample/competing-explanation review, and rebuild the current `HypothesisLedgerSnapshot`.

Important boundary:

```text
supported_recurrence
!= causal cognitive mechanism
!= permanent learner trait
!= automatic training eligibility
```

For an executable corpus, see `tests/test_m7_qualification.py`.

### M8 — evidence-aware tutor session

Use `chess_mentor_engine.tutoring` in this order:

```text
start_tutor_session
→ present_tutor_position
→ present_tutor_capture_stage
→ capture_tutor_response
→ freeze_tutor_response
→ [optional standardized probe: present/capture/freeze]
→ reveal_tutor_objective_evidence
→ record_tutor_reasoning_comparison
→ [optional] attach_tutor_hypothesis_context
→ record_tutor_explanation
→ complete_tutor_session
```

The M8 state machine rejects objective reveal before all planned pre-reveal evidence is frozen and rejects stale/mismatched M6/M7 provenance. See `tests/test_m8_qualification.py` for a complete replayable example.

### M9 — training intervention registry

Use `chess_mentor_engine.training` to:

```text
define_exercise
→ define_training_intervention
→ build_intervention_registry
→ record_hypothesis_intervention_mapping
→ define_intervention_selection_policy
→ select_training_intervention
```

A current active M7 hypothesis with `supported_recurrence` is necessary but not sufficient. M9 also requires an explicit provenance-bearing applicability mapping to an exact registered intervention. Multiple applicable mappings resolve to `unclear`, not an opaque ranking.

See `tests/test_m9_qualification.py` for executable examples.

### M10 — outcome and transfer evidence

Use `chess_mentor_engine.evaluation` to declare an `OutcomePolicy` and call `define_evaluation_plan` with an exact selected M9 decision and intervention. Append frozen attempts, document practice completion, record rubric-bound observations, then call `assess_outcome_evidence` on the complete known ledger.

Practice, near transfer, far transfer, and real-game evidence are assessed separately. Exposure, assistance, early feedback, timing, position reuse, insufficient independence, and coder disagreement remain visible. `supported` means criterion evidence under the declared scope and protocol; `mastery` and `causal_effect` stay `not_established`.

See [the M10 runbook](docs/runbooks/m10-outcome-transfer-evidence.md), `tests/test_outcome_evidence.py`, and `tests/test_m10_qualification.py`. No automatic M7 revision or M11 learner-state change is introduced.

### Local durability and M8 recovery

Use `LocalArtifactStore`, `save_tutor_session`, and `load_tutor_session` from `chess_mentor_engine.storage`. Saving requires the exact definitions for every planned prompt. Recovery checks storage integrity and replays the existing M8 transitions before returning a resumable session; advancing and saving creates a new snapshot rather than overwriting earlier evidence.

See [the storage/recovery runbook](docs/runbooks/durable-artifacts-and-replay.md) for usage and failure handling. The local database is plaintext, participant scoping is not authentication, and external archival dependencies beyond embedded M8 inputs and prompts must be supplied explicitly. Recovery does not establish learning, mastery, or independent qualification of every upstream claim.

## Validation commands

Run the focused milestone and storage suites:

```bash
pytest tests/test_m7_qualification.py
pytest tests/test_m8_qualification.py
pytest tests/test_m9_qualification.py
pytest tests/test_outcome_evidence.py tests/test_m10_qualification.py
pytest tests/test_artifact_store.py tests/test_tutor_storage.py
```

Run the full regression and lint gates:

```bash
pytest
ruff check .
```

Run the external Stockfish witness after installing Stockfish and exposing its executable as `STOCKFISH_EXECUTABLE`:

```bash
pytest tests/integration/test_stockfish_uci.py
```

The GitHub Actions workflow runs the full test/lint job and an independent Ubuntu Stockfish integration job on pull requests to `main` and pushes to `main`.

## Human operational protocol

The system intentionally retains human/model judgment at specific boundaries:

1. **M7 hypothesis mapping and review:** support, contradiction, counterexample, context exception, and competing explanations must remain explicit and provenance-bearing.
2. **M8 information sequencing:** the operator must not reveal engine/objective evidence before the planned participant-response stages are frozen. Explanation comes only after comparison.
3. **M9 pedagogical applicability:** a human or model must explicitly author whether an intervention is `applicable`, `not_applicable`, or `unclear`; the deterministic selector does not infer this from text similarity.
4. **M10 outcomes and effectiveness claims:** context classification, exposure scope, and rubric-bound scores require provenance. Selecting or completing an intervention does not establish that it worked; even supported transfer evidence does not establish causality or mastery.

The detailed operational checklists are in [the M7-M9 milestone runbook](docs/runbooks/m7-m9-milestone-runbook.md) and [the M10 runbook](docs/runbooks/m10-outcome-transfer-evidence.md).

## Documentation map

- [Current build status](docs/product/repository-build-status.md) — authoritative milestone/claim status.
- [M7 full qualification](docs/architecture/m7-qualification.md) — learner-hypothesis qualification record.
- [M8 Evidence-Aware Tutor Session](docs/architecture/evidence-aware-tutor-session.md) — tutoring-session architecture and qualification.
- [M9 Training Intervention Registry](docs/architecture/training-intervention-registry.md) — intervention registry, applicability, selection, and qualification.
- [M10 Outcome and Transfer Evidence](docs/architecture/outcome-transfer-evidence.md) — immutable outcomes, exposure and independence gates, and conservative assessments.
- [M7-M9 milestone runbook](docs/runbooks/m7-m9-milestone-runbook.md) — setup, validation commands, usage order, and human protocols.
- [Durable artifacts and verified replay](docs/architecture/durable-artifacts-and-replay.md) — local storage, recovery, legacy compatibility, and claim limits.
- [Decision records](docs/decisions/README.md) — architecture decision-record conventions.
- [CONTEXT.md](CONTEXT.md) — orientation for contributors and coding agents.
- [Product definition](docs/product/product-definition.md) and [product discovery](docs/product/product-discovery.md) — product hypotheses and validation direction.
