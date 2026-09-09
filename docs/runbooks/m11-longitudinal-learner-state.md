# M11 longitudinal learner-state runbook

## Scope

M11 records exact M7 state over time and can attach exact M10 outcome evidence for the same M7 revision. It is a Python API, not an end-user command.

## Minimal operation

```python
from chess_mentor_engine.longitudinal import (
    LongitudinalProvenance,
    project_learner_state,
    record_hypothesis_state,
    start_learner_state,
)

state = start_learner_state(participant_id=participant_id)
state, event = record_hypothesis_state(
    state,
    event_key=source_occurrence_key,
    ledger_snapshot=m7_snapshot,
    hypothesis_revision=current_m7_revision,
    rationale="Record the current evidence state without promotion.",
    provenance=LongitudinalProvenance(
        actor_kind="deterministic",
        actor_id="learner-state-recorder",
        actor_version="1",
        instruction_fingerprint=recorder_contract_fingerprint,
        run_id=run_id,
    ),
    observed_at=observed_at,
    recorded_at=recorded_at,
    evaluation_plan=m10_plan,          # optional; pair with assessment
    outcome_assessment=m10_assessment, # optional; pair with plan
)
current = project_learner_state(state, created_at=snapshot_time)
```

When no exact M10 assessment exists for the current M7 revision, omit both M10 arguments. Never attach an assessment to a newer revision merely because the topic or hypothesis text appears similar.

## Rejection behavior

Treat `LongitudinalStateError` as a failed evidence append. Do not rewrite old history to make a mismatched record fit. Reconcile the exact upstream M7/M10 identities and chronology, then retry with the correct immutable records.

Important rejection cases include tampered M7 identity, participant mismatch, stale/noncurrent revision, M10 plan/revision mismatch, assessment/plan mismatch, backdated observation, revision regression, lifecycle resurrection, and conflicting reuse of an event key.

## Qualification commands

From the repository root after `python -m pip install -e ".[dev]"`:

```bash
python -m pytest tests/test_m11_qualification.py
python -m pytest tests/test_m7_qualification.py tests/test_m10_qualification.py
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

The repository's PR CI remains the full native qualification gate and separately runs the configured external Stockfish witness. M11 adds no new engine behavior; the Stockfish job protects the existing analysis substrate against regression.

## Claim ceiling

A projected longitudinal state is a traceable current view over history. It does not establish causal learning, mastery, intervention efficacy, or a permanent weakness score. Those claims remain outside M11 even when M10 transfer dimensions are supported.
