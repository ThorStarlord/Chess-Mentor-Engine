# M34 — Hermetic Reviewed-Coaching Recovery Reconciliation

M34 adds a content-addressed dry-run recovery surface over the existing M24/M26/M27 execution chain. It reconciles synthetic or fake-adapter attempt histories against one already-persisted, mechanically verified M26 target run and determines whether that historical prefix was complete or was eligible for a manually authorized full-M26 restart.

## Boundary

M34 is HERMETIC_VALIDATION only.

It does not:

- call a provider or evaluator;
- execute or authorize a retry;
- accept a credential parameter;
- select production vendors, timeouts, backoff, or rate-limit policy;
- establish external side-effect idempotency;
- persist failed-attempt detail strings, request payloads, model prose, or evaluator rationales;
- mutate M24, M25, M26, M27, M31, M32, or M33 artifacts;
- establish model truth, coaching quality, production recovery correctness, privacy approval, or security approval.

The authority chain remains:

```text
M24 -> classifies one adapter invocation, automatic_retry=false
M26 -> atomically persists one successful reviewed-coaching result
M27 -> mechanically verifies the persisted M26/M25/M24 chain
M31 -> validates supplied complete manual retry histories + synthetic-canary privacy
M34 -> dry-runs recovery/restart reconciliation against one persisted M26 target
```

## Why recovery is orchestration-scoped

`run_persistent_reviewed_coaching()` persists its artifacts atomically only after the selected provider/evaluator path succeeds. If a provider succeeds but the evaluator fails, that provider result is not a durable M26 checkpoint.

Therefore M34 never claims it can resume from an unpersisted provider side effect. A retryable partial failure produces:

```text
state = resume_eligible
restart_scope = full_m26_orchestration
requires_manual_external_authority = true
automatic_retry = false
external_side_effect_idempotency_established = false
```

This is a plan classification only. Production policy must decide whether a real restart is safe and appropriate.

## Target model

M34 requires one persisted M26 run as the canonical successful target. Before building a plan it rebuilds a one-run M27 ledger, so the target M26 run, M25 review, M19/M20 optionality, M24 request/response bindings, and source fingerprints must still pass existing mechanical validation.

The persisted target is intentionally historical: a `resume_eligible` M34 result says that the supplied fake history prefix is mechanically compatible with the next attempt that is already represented by the target run. It does not schedule or execute that attempt.

For external targets, all persisted M24 roles must share one M26 orchestration attempt number. Supported role sets are:

```text
[]
[model_coach_provider]
[model_coach_provider, model_coaching_evaluator]
```

## Attempt reconciliation

For supplied histories:

- every M24 record must preserve the native M24 schema, content identity, `automatic_retry=false`, claim scope, and authority boundary;
- endpoint, request reference, and timeout must match the corresponding persisted target role;
- provider attempts define the global attempt sequence and must be unique and contiguous from attempt 1;
- evaluator history may exist only for the same attempt after provider success;
- a failed provider blocks an evaluator invocation in that attempt;
- a later M26 attempt is legal only after the preceding overall attempt failed with M24 `timeout` or `transient` and `retryable=true`;
- permanent and other non-retryable failures cannot reconcile to a later target;
- a complete supplied history must end on the persisted target attempt and the final successful provider/evaluator records must equal the exact M24 records persisted by M26;
- a recovery prefix must end exactly one attempt before the target and must end in a retryable M24 failure;
- the persisted target attempt must remain within the caller's bounded `max_attempts` admission limit.

The plan stores only bounded attempt summaries: role, attempt number, success/failure, failure kind, retryable flag, and whether a successful execution equals the persisted target execution. It does not copy failure detail text.

## Content-addressed artifact

A passing plan is stored as:

```text
m34.reviewed-coaching-recovery-reconciliation.v1
```

Its dependencies are the exact M26 run and M27 ledger. It also carries references to the exact M25 review and persisted target M24 execution artifacts, plus fingerprints for:

- M26 run;
- M27 ledger;
- M25 review;
- optional M19 model coaching;
- optional M20 model evaluation;
- target M24 executions;
- the bounded, detail-free recovery history summary.

Repeated construction from the same mechanically relevant history is content-idempotent and resolves to the same M34 artifact reference.

`validate_persisted_reviewed_coaching_recovery_plan()` re-resolves the target M26 run, rebuilds its M27 ledger, and rejects stale or substituted M25/M20/source identities and fingerprints.

## Qualification

Focused M34 suite:

```bash
python -m pytest tests/test_m34_reviewed_coaching_recovery_reconciliation.py -rs
```

Execution/recovery regression:

```bash
python -m pytest \
  tests/test_m24_provider_conformance.py \
  tests/test_m26_persistent_reviewed_coaching.py \
  tests/test_m27_reviewed_coaching_execution_ledger.py \
  tests/test_m31_execution_envelope_preflight.py \
  tests/test_m34_reviewed_coaching_recovery_reconciliation.py -rs
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

Repository CI additionally runs the independent Stockfish witness on the exact candidate head.

## Positive hermetic scenarios

The focused suite qualifies:

- timeout failure prefix -> manual full-M26 restart classification;
- transient failure prefix -> manual full-M26 restart classification;
- provider success followed by evaluator transient failure -> partial-failure restart classification;
- multi-attempt history ending in the exact persisted successful target;
- deterministic M26 runs with zero external execution history;
- repeated content-idempotent plan construction.

## Negative / rejection scenarios

The focused suite rejects:

- permanent/non-retryable failure followed by a later target attempt;
- duplicate attempt numbers;
- non-contiguous provider attempt histories;
- final successful M24 records that differ from the target persisted by M26;
- cross-run/stale request substitutions;
- forged `automatic_retry=true` records;
- stale/rehashed M25 review or M20 evaluator fingerprints during persisted revalidation;
- cross-participant target selection.

## Claim ceiling

M34 proves only deterministic repository-local reconciliation of supplied fake execution histories against an already-persisted mechanically verified target. `resume_eligible` is not authorization to call an external service. It does not prove that a provider is idempotent, that duplicate billing or side effects cannot occur, that retry/backoff is operationally correct, or that a production recovery procedure is safe.
