# M33 Deterministic Mentor-Feedback Trace Surface

M33 is a repository-local, machine-readable provenance surface over the exact
persisted M16 deterministic mentor feedback already qualified through the
M26/M27/M30/M32 review chain.

It does **not** generate new coaching, reinterpret chess evidence, evaluate model
semantics, advance tutor state, execute providers, or claim pedagogical quality.

## Contract

The trace schema is:

```text
m33.deterministic-mentor-feedback-trace.v1
```

M33 resolves one exact participant-scoped M30 package, rebuilds the M32 delivery
bundle, loads the exact M26 source checkpoint and M16 artifact, and requires the
M25 deterministic-grounding content to equal that persisted M16 record.

For each non-empty line in each substantive M16 section, M33 records:

- a stable section-local component identity and ordinal;
- SHA-256 of the exact M16 component text, without copying the text;
- the source authority (`M15`, `M6`, or `M7`);
- a deterministic source pointer into the compact source index;
- the source fields from which the deterministic component is derived.

The source index retains exact M15 presentation, M6 comparison/assessment/assertion,
and optional M7 context/revision identities and fingerprints. Optional M19 model
coaching and M20 evaluator output are represented only by presence and exact source
fingerprint. Their prose and judgments are never copied into M33 components.

## Authority boundary

M33 explicitly records that it does not:

```text
create objective chess facts
create learner hypotheses
evaluate model semantics
copy M19 model prose
copy M20 evaluator judgments
advance tutor state
execute external calls
```

M33 traceability is mechanical provenance. It is not semantic truth evaluation,
model-quality approval, learner diagnosis, or tutoring-efficacy evidence.

## Python API

```python
from chess_mentor_engine.mentor_feedback_trace import (
    build_persisted_mentor_feedback_trace_surface,
    validate_mentor_feedback_trace_surface,
    validate_persisted_mentor_feedback_trace_surface,
)

trace = build_persisted_mentor_feedback_trace_surface(
    store=store,
    participant_id="P01",
    package_artifact_id=package_id,
)

validate_mentor_feedback_trace_surface(trace)
validate_persisted_mentor_feedback_trace_surface(
    store=store,
    participant_id="P01",
    trace=trace,
)
```

The detached validator checks schema, source-reference shape, participant scope,
source authority, component coverage, source-pointer legality, separation
boundaries, and content-addressed trace identity.

The persisted validator additionally rebuilds M33 from the exact M30 package. This
is the required check for same-authority pointer drift, component omission, content
hash drift, or source-fingerprint substitution that an attacker also rehashed into
a superficially self-consistent detached trace.

## Qualification

Focused package tests:

```bash
python -m pytest tests/test_m33_deterministic_mentor_feedback_trace.py
python -m ruff check src/chess_mentor_engine/mentor_feedback_trace.py \
  tests/test_m33_deterministic_mentor_feedback_trace.py
```

Native repository gate:

```bash
python -m pytest
python -m ruff check .
```

Independent engine witness remains the repository CI Stockfish job. A regular
pytest run that skips the external-engine integration suite is not an independent
Stockfish pass.

## Rejection coverage

M33 qualification includes rejection of:

- M16/M15, M16/M6, and M16/M7 identity or fingerprint drift;
- deterministic M16 section-content or evidence-reference drift;
- rehashed authority promotion into M19/M20;
- component omission, content-hash drift, and same-authority source-pointer drift
  when checked against persisted sources;
- rehashed M6 source-fingerprint substitution;
- cross-participant source references;
- forged M30 package selection;
- wrong requested participant scope.

The package intentionally performs no live provider call, credential handling,
retry execution, deployment, destructive migration, or subjective production QA.
