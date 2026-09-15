# Post-V1 Local Product-Use Observation Runbook

## Purpose

This runbook exercises the post-V1 development surface without making a learning-validation claim.

The repository may establish that it can:

- guide one exact selected M8 checkpoint through baseline capture and freeze;
- preserve exact M8 persistence and replay verification;
- persist immutable participant-scoped observations about product use;
- persist bounded participant self-report;
- deterministically summarize those observations.

It does **not** establish learner improvement, tutor efficacy, causal intervention benefit, or mastery.

```text
claim_scope = descriptive_local_product_use_only
learning_effect = not_established
tutor_efficacy = not_established
mastery = not_established
```

## Authority boundary

The post-V1 guided path is deliberately narrower than an autonomous tutor:

```text
qualified V1 inputs
    |
    v
cme-local-tutor start
    |
    v
exact selected persisted M8 checkpoint
    |
    v
cme-local-tutor review
    |
    +-- present exact position through M8
    +-- present protocol-bound baseline prompts through M8
    +-- capture participant-authored responses through M8
    +-- freeze those responses through M8
    +-- persist descriptive product-use observations
    |
    v
M8 baseline-freeze boundary
```

`review` stops there. It does not reveal objective evidence, attach a reasoning comparison, generate an explanation, complete the tutor session, or execute an M46 action.

If the operator wants the qualified M46 proposal for the newly frozen checkpoint, use the existing `cme-local-tutor next` command. That command still produces a proposal only; existing M8 surfaces remain execution/exposure authority.

## 1. Create the selected M8 checkpoint

Use the established V1 composition path. The exact inputs remain the M18 diagnostic queue, M44 learner-progress view, optional M42 transfer plans, exact PGN, M5 capture protocol, and prompt definitions.

```bash
cme-local-tutor start game.pgn \
  --diagnostic-json diagnostic.json \
  --learner-progress-json learner-progress.json \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --protocol-json capture-protocol.json \
  --prompts-json prompts.json \
  --selection-decision selected \
  --capture-consent granted \
  --recorded-at 2026-09-15T09:00:00-03:00 \
  --created-at 2026-09-15T09:01:00-03:00 \
  --create-db
```

Retain the returned exact M8 session artifact ID.

## 2. Prepare the exact position packet

`review` consumes structural JSON for the exact `PositionContextPacket` corresponding to the selected M8 position. It does not infer or replace that packet.

Use the repository's existing position-packet surface or another qualified path that emits the exact structural record required by M8.

## 3. Run guided baseline capture

```bash
cme-local-tutor review \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --position-json position-context.json \
  '<selected-session-artifact-id>'
```

Human-facing prompts are written to stderr. The final machine-readable result is JSON on stdout.

A successful result records:

```text
baseline_frozen = true
abandoned = false
m46_execution = not_performed
next_authority = cme-local-tutor next
learning_effect = not_established
tutor_efficacy = not_established
mastery = not_established
```

If EOF or interrupt occurs after a checkpoint exists, the exact M8 history already persisted remains intact and a descriptive `session_abandoned` observation is recorded. The observation does not rewrite the tutor session.

## 4. Inspect the post-freeze M46 proposal when needed

The guided `review` command does not generate or execute a participant-facing M46 action. To inspect the qualified proposal, call the existing surface with the final frozen session artifact ID:

```bash
cme-local-tutor next \
  --diagnostic-json diagnostic.json \
  --learner-progress-json learner-progress.json \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --created-at 2026-09-15T09:10:00-03:00 \
  '<frozen-session-artifact-id>'
```

Optional exact M42 transfer-plan arguments remain governed by the V1 local-tutor contract.

The proposal is not automatically executed by the post-V1 observation package.

## 5. Record bounded participant self-report

After a review, explicit participant feedback can be persisted against one exact M8 checkpoint:

```bash
cme-local-tutor feedback \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --review-relevance 4 \
  --workflow-clarity 3 \
  --would-review-again 5 \
  --note "Useful position; setup still feels technical." \
  '<session-artifact-id>'
```

All three ratings are integers from 1 through 5. The optional note is participant-authored self-report.

These values may describe perceived relevance, clarity, and willingness to repeat the review. They do not become objective chess truth, learner inference, or tutor-efficacy evidence.

## 6. Build a descriptive report

```bash
cme-local-tutor report \
  --db ./mentor.sqlite3 \
  --participant P01
```

The report is participant-scoped and deterministic. It may contain:

- observation counts by bounded event type;
- recorded action names when an observation explicitly carries one;
- explicit participant-feedback metadata.

It always retains:

```text
claim_scope = descriptive_local_product_use_summary_only
learning_effect = not_established
tutor_efficacy = not_established
mastery = not_established
```

## External evidence boundary

Real repeated sessions are outside repository-only qualification. When they are run, use the observations to identify product friction without promoting self-report into stronger authority.

Useful questions include:

- Is setup the dominant friction?
- Are M45-selected positions often perceived as irrelevant?
- Is the terminal interaction itself preventing repeated use?
- Are participants willing to repeat the review?
- Does observed friction point to an existing authority owner such as M45 or M46?

Do not answer "did CME improve chess skill?" from this observation package. That requires a separate empirical design and stronger evidence.

## Repository qualification

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests tools
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The exact candidate also requires the independent `release-distribution` and `stockfish-integration` CI jobs to pass.

## Stop condition

After enough real use exposes a dominant bottleneck, reconcile the repository again and write a fresh bounded decision/implementation plan.

Do not automatically create M47, K8, a browser UI, hosted infrastructure, or an adaptive-policy rewrite merely because this observation surface exists.
