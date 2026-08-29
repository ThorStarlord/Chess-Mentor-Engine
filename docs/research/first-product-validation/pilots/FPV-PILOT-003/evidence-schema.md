# Pilot 003 evidence schema

Preserve raw participant language separately from analyst coding and objective chess evidence.

```yaml
position_id:
  stage_a:
    raw_response:
    chosen_move:
    explicitly_reported_candidates:
    explicitly_reported_features:
    explicitly_reported_plan:
  stage_b:
    raw_responses:
    additional_candidates:
    expected_opponent_reply:
    expected_continuation:
    stated_objective:
    uncertainty:
    confidence:
  decision_change:
    move_changed:
    candidate_set_changed:
    expected_reply_changed:
    plan_changed:
    confidence_changed:
  objective_evidence:
    fen:
    played_move:
    engine_evidence:
    provenance:
  provenance:
    pre_engine: true
    exposure_class:
    response_order:
```

Structured values derived from free text must be labeled `ANALYST CODING`. They must not replace the raw response or be treated as participant truth.

## Research coding taxonomy

Use zero, one, or multiple codes where supported: feature recognition, candidate generation, opponent-resource identification, calculation, position evaluation, plan formation, and confidence/calibration. `UNCLEAR` and uncodable responses are valid.

## Reasoning Discrepancy

Record a traceable difference between reported pre-engine reasoning and the objective demands or consequences of the position. It is local evidence, not a cognitive defect, stable weakness, personality trait, or learner-model fact.
