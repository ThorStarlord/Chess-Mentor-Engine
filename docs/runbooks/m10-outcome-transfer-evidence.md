# Operating M10 outcome and transfer evidence

## Before collecting outcomes

Keep the exact selected M9 decision, registered intervention/exercises, M7 revision,
and all underlying sources. Define the outcome criterion, versioned scoring
rubric, near/far/game context definitions, independent-position/session minima,
and post-practice delay before collecting the evidence. These are authored
protocol choices, not built-in validated mastery thresholds.

Create `OutcomePolicy` and pass it with the actual M9 objects, participant ID,
authorship provenance, rationale, and creation timestamp to
`define_evaluation_plan`. Start `OutcomeLedger(plan)`. The plan must predate
attempts, including original game decisions later imported for assessment.

## Capture and scoring order

1. Use `reference_outcome_position(canonical_position)` for the exact M1 position.
2. Construct `EvaluationAttempt` with the plan and exact exercise references, an
   occurrence key, raw response/source, start/freeze/record timestamps, and declared
   evidence kind/context rationale. Retain source evidence references.
3. Record completion fields from the bound M9 schema. Set `completed=True` only
   when the supplied fields document completion. Do not use success as a synonym.
4. Explicitly record prior exposure, assistance, history scope and provenance.
   `unexposed` requires references to the inspected history/attestation. Unknown
   remains unknown. Retain observed early feedback; it becomes an exclusion.
5. Call `append_evaluation_attempt`. Preserve the returned ledger as a new snapshot.
6. After the selected practice block, call `record_practice_completion` with its
   exact completed-practice attempt references. This is not a dosage/efficacy claim.
7. Collect fresh transfer attempts under the already declared context and delay.
   For real games, include a matching `canonical_game` source reference.
8. Call `record_outcome_observation` for each score. Its provenance instruction
   fingerprint must equal the policy's scoring-rubric fingerprint. Cite scoring
   evidence and a rationale. Keep contrary and uncertain judgments.
9. Call `assess_outcome_evidence` on the complete known ledger, specifying the
   exact practice-completion reference and an assessment timestamp.

Repeated attempts and agreeing coders cannot inflate the independent sample count.
A later success cannot erase the first failure on the same position. Review all
exclusion reasons and uncertain results rather than editing the input history.

## Generic archival persistence

The existing storage API can archive a ledger and its assessment without adding a
new typed loader. Given actual `ledger` and `assessment` values from the API:

```python
from chess_mentor_engine.storage import LocalArtifactStore

store = LocalArtifactStore("learner-evidence.sqlite")
ledger_ref = store.put(
    kind="outcome_ledger",
    artifact_id=ledger.record_id,
    participant_id=ledger.plan.participant_id,
    payload=ledger.to_dict(),
)
assessment_ref = store.put(
    kind="outcome_assessment",
    artifact_id=assessment.record_id,
    participant_id=assessment.participant_id,
    payload=assessment.to_dict(),
    dependencies=(ledger_ref,),
)
archived = store.get(assessment_ref, participant_id=assessment.participant_id)
assert archived.payload == assessment.to_dict()
```

Add separately archived source artifacts as explicit storage dependencies when a
closed archival package is required. Generic storage does not discover the full
upstream graph, authenticate the observer, or establish scientific validity.
Do not replace native M10 fingerprints with storage-envelope digests.

## Reading a result

Read each dimension separately: `insufficient`, `supported`, `not_supported`,
`mixed`, or `unclear`. A supported dimension is criterion evidence conditional on
the supplied scope and protocol. It is not causal improvement or mastery. The
result deliberately retains `causal_effect = mastery = "not_established"`.
Use it for explicit human review; it does not automatically revise M7 or create M11.

## Verification

```bash
pytest tests/test_outcome_evidence.py tests/test_m10_qualification.py
pytest
ruff check .
python -m compileall -q src tests
pytest tests/integration/test_stockfish_uci.py
```

The final command requires `STOCKFISH_EXECUTABLE`. Preserve frozen research
artifacts; these software tests are not a replacement for learner experiments.
