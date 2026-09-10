# M23–M25 Milestone Runbook

This runbook is the compact restart surface for the completed M23–M25 milestone:

```text
M23  diagnostic queue -> participant-authorized persistent tutor start
M24  provider/evaluator execution conformance around M19/M20
M25  authority-separated coach-review read model
```

It supplements the package-specific runbooks. It does not expand any package's
authority or replace the full repository qualification gate.

## Install

Use Python 3.11 or newer:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Installed command surfaces after M25:

```bash
cme --help
cme-candidate-tutor --help
cme-coach-review --help
```

## M23 — Start a persistent tutor session from an exact M18 candidate

First produce or retain the exact JSON emitted by `cme diagnose`. Then explicitly
select one candidate and separately grant capture consent:

```bash
cme-candidate-tutor game.pgn \
  --diagnostic-json diagnostic.json \
  --candidate-id candidate_... \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --protocol-json capture-protocol.json \
  --prompts-json prompts.json \
  --selection-decision selected \
  --capture-consent granted \
  --recorded-at 2026-09-10T12:00:00-03:00 \
  --created-at 2026-09-10T12:01:00-03:00 \
  --create-db
```

`--create-db` is required only when the local database does not yet exist. The
operator revalidates the M18 queue and exact PGN provenance, invokes the native M21
authorization/launch contract, creates only M5 plus initial M8 `state=selected`, and
atomically persists the lineage.

On success, continue through the existing M13 replay-verified workflow using the
returned M8 artifact reference:

```bash
cme tutor status \
  --db ./mentor.sqlite3 \
  --participant P01 \
  '<ref.artifact_id>'
```

Then use the normal explicit transitions:

```text
cme tutor present-position
cme tutor present-stage
cme tutor respond
cme tutor freeze
cme tutor reveal
cme tutor compare
cme tutor attach-hypothesis
cme tutor explain
cme tutor complete
```

M23 does not choose a candidate, infer consent, generate M6/M7 inference, select
training, or create model language.

Package runbook:
[`m23-diagnostic-to-persistent-tutor.md`](m23-diagnostic-to-persistent-tutor.md).

## M24 — Run provider/evaluator adapters through the conformance seam

M24 is a Python API rather than a CLI. Future provider code should target the neutral
execution seam instead of embedding vendor semantics into M19/M20:

```python
from chess_mentor_engine.coaching import (
    ModelCoachEndpoint,
    ModelEvaluatorEndpoint,
    PermanentExternalExecutionError,
    TransientExternalExecutionError,
    execute_model_coach_provider,
    execute_model_coaching_evaluator,
    run_conformant_model_coaching,
    run_conformant_model_coaching_evaluation,
)
```

The qualified layer handles detached immutable requests, exact endpoint identity,
content-addressed execution provenance, and fail-closed failure classification.
Only `timeout` and `transient` are marked retryable. M24 itself performs no automatic
retry and supplies no production transport.

Use fake adapters for repository/hermetic qualification. Real vendor SDKs,
credentials, live timeout behavior, retry tuning, costs, privacy approval, and vendor
selection remain external authority.

Package runbook:
[`m24-provider-evaluator-conformance.md`](m24-provider-evaluator-conformance.md).

## M25 — Build and inspect the authority-separated review bundle

M25 accepts a local JSON object whose optional downstream records are explicit
`null`. The required top-level shape is:

```json
{
  "evaluation_presentation": {},
  "diagnostic_candidate": null,
  "diagnostic_batch": null,
  "authorization": null,
  "launch": null,
  "tutor_state": null,
  "grounded_feedback": null,
  "model_coaching": null,
  "model_evaluation": null
}
```

Inspect it locally:

```bash
cme-coach-review path/to/m25-bundle.json
```

The command performs no engine call, provider call, network request, credential use,
persistence mutation, or deployment. It produces the content-addressed
`m25.coach-review-read-model.v1` projection with these authority layers kept
structurally distinct:

```text
objective_evidence        M15
diagnostic_selection      M18
participant_authority     M21
tutor_state               M8
deterministic_grounding   M16
model_coaching             M19
model_evaluation           M20
```

Missing downstream layers remain absent. M19 prose never becomes objective evidence,
and M20 acceptance retains
`truth_status = not_established_by_m20_evaluation`.

Package runbook:
[`m25-coach-review-read-model.md`](m25-coach-review-read-model.md).

## Focused milestone qualification

Run each package suite independently:

```bash
python -m pytest tests/test_m23_diagnostic_to_persistent_tutor_cli.py
python -m pytest tests/test_m24_provider_conformance.py
python -m pytest tests/test_m25_coach_review_read_model.py
```

Run the principal M23–M25 regression path:

```bash
python -m pytest \
  tests/test_m13_persistent_tutor_cli.py \
  tests/test_m18_diagnostic_analysis_queue.py \
  tests/test_m21_diagnostic_candidate_tutor_orchestration.py \
  tests/test_m23_diagnostic_to_persistent_tutor_cli.py \
  tests/test_m19_provenance_bound_model_coaching.py \
  tests/test_m20_model_coaching_evaluation.py \
  tests/test_m24_provider_conformance.py \
  tests/test_m25_coach_review_read_model.py
```

For the objective-evaluation fidelity lineage as well, include M15/M16/M22:

```bash
python -m pytest \
  tests/test_m15_evaluation_presentation.py \
  tests/test_m16_grounded_mentor_feedback.py \
  tests/test_m22_end_to_end_evaluation_fidelity.py \
  tests/test_m23_diagnostic_to_persistent_tutor_cli.py \
  tests/test_m24_provider_conformance.py \
  tests/test_m25_coach_review_read_model.py
```

## Full repository merge gate

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

The ordinary full pytest command intentionally skips the external Stockfish witness
when `STOCKFISH_EXECUTABLE` is unavailable. To run that witness explicitly:

```bash
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

A skipped external-engine suite is not an independent-engine pass. Pull-request CI
runs the normal test/lint job and a separate Stockfish integration job; merge only
when both are green on the exact candidate head.

## Qualification evidence for the completed milestone

```text
M23 / PR #57 / head 8131685b434f52066e375e0914a2cf3ecf13c4c9
CI 34499329989: 659 passed, 8 external-engine skips, Ruff PASS, Stockfish PASS

M24 / PR #58 / head e44ae84749de7820e9d403019ec7bddb5687639e
CI 34500991230: 686 passed, 8 external-engine skips, Ruff PASS, Stockfish PASS

M25 / PR #59 / head 9927171cb5f09bf0274d0e2c36e9ab736a90baee
CI 34502823382: 709 passed, 8 external-engine skips, Ruff PASS, Stockfish PASS
```

## External/human gates still deferred

Repository qualification does not settle:

- disclosure/consent wording or timing in a real user interface;
- accessibility, localization, visual design, or usability;
- production LLM/evaluator vendor selection;
- credentials, secrets, privacy/security, retention, or transmitted-data approval;
- provider-specific live retries, rate limits, timeout behavior, cost/latency SLOs,
  or incident response;
- semantic/pedagogical correctness of arbitrary model output or evaluator quality;
- empirical tutoring efficacy, causal learner diagnosis, mastery, or transfer;
- hosted auth, multi-user persistence, observability, or deployment readiness.

These remain explicit human/external authority gates rather than hidden prerequisites
for continued repository-only or hermetic development.
