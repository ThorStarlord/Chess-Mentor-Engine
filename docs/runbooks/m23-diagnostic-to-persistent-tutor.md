# M23 Diagnostic-to-Persistent-Tutor Operator Bridge

M23 closes the local workflow seam between the qualified M18 diagnostic queue, the
M21 participant-authorized candidate launch, and the replay-verified M13/M8 local
artifact workflow.

M23 adds no chess-evaluation, learner-inference, training-selection, model-provider,
or pedagogical authority. It is an operator/persistence bridge over already-qualified
contracts.

## Boundary

The supported local path is:

```text
exact PGN used by M18
        +
exact cme diagnose JSON
        +
explicit participant candidate selection
        +
separate explicit capture consent
        +
exact M5 capture protocol/prompts
        |
        v
cme-candidate-tutor
        |
        +--> revalidate M18 queue/policy/source-pool/batch integrity
        +--> revalidate exact PGN/game/candidate provenance
        +--> invoke native M21 authorization + launch
        +--> create native M5 PlayerDecisionContext
        +--> create only M8 state=selected
        +--> atomically persist lineage + prompts + M8 checkpoint
        |
        v
cme tutor present-position ...
```

The persisted dependency lineage is:

```text
m18.diagnostic-analysis-queue.v1
        |
        v
m21.candidate-tutor-authorization.v1
        |
        v
m21.candidate-tutor-launch.v1
        |
        v
m8.tutor-session.v1
```

The M8 checkpoint also depends on the exact stored M5 prompt definitions required by
the capture protocol.

## Command

M23 deliberately uses a separate installed operator command instead of changing the
semantics of `cme tutor start`:

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

`--create-db` is required only when the database does not yet exist. Candidate
selection and capture consent are separate required arguments; neither is inferred
from the other.

On success the command returns the exact M18/M21 lineage references plus the
persisted M8 `ref`. Continue the existing replay-verified workflow using that exact
artifact ID, for example:

```bash
cme tutor status \
  --db ./mentor.sqlite3 \
  --participant P01 \
  '<ref.artifact_id>'
```

Then continue with the normal M13 transitions beginning with `present-position`.

## Validation performed before persistence

M23 fails closed before database creation or writes when any required source contract
cannot be preserved. The operator checks:

- exact M18 queue v1 top-level shape;
- exact source-window metadata and position count;
- M18 selection-policy fingerprint continuity;
- batch policy identity/fingerprint and requested-size continuity;
- source-pool cardinality, candidate ordering, and the native source-pool fingerprint
  bound into the batch;
- exact candidate payload continuity between the source pool and batch;
- exact supplied PGN source hash, game identity, and candidate root ply;
- native M21 candidate, batch, authorization, canonical-game, and consent checks;
- native M8 capture-protocol validity and exact prompt completeness;
- native M8 replay before any storage mutation.

The final write is one `LocalArtifactStore.put_many(...)` transaction containing the
M18 queue, M21 authorization, M21 launch, prompt artifacts, and initial M8 checkpoint.
The command then reloads the checkpoint through `load_tutor_session` and reports
`verified_replay = true` only after successful recovery.

## Rejection examples

The M23 hermetic suite covers, among other cases:

- candidate selection declined;
- evidence-capture consent declined;
- impossible `declined + granted` authorization;
- source-pool selection drift;
- batch-candidate/source-signal drift;
- selection-policy drift;
- wrong PGN source;
- missing selected candidate;
- incomplete prompt dependencies;
- repeated identical invocation/idempotence;
- handoff into the existing `cme tutor status` replay path.

These cases require no production credentials or live service calls.

## Authority ceiling

M23 does **not**:

- choose a diagnostic candidate for the participant;
- infer consent;
- infer that a participant identifier must match a PGN header name;
- expose engine rationale as clean pre-reveal participant evidence;
- create M6 reasoning-discrepancy authority;
- create or mutate M7 learner hypotheses;
- select M9 training;
- generate mentor/model language;
- establish pedagogical efficacy or production UX correctness.

The participant identifier remains an application-provided storage/evidence scope,
not an identity claim derived from PGN metadata.

## Qualification

Focused local/CI checks:

```bash
python -m pytest tests/test_m23_diagnostic_to_persistent_tutor_cli.py
python -m pytest \
  tests/test_m13_persistent_tutor_cli.py \
  tests/test_m18_diagnostic_analysis_queue.py \
  tests/test_m21_diagnostic_candidate_tutor_orchestration.py \
  tests/test_m23_diagnostic_to_persistent_tutor_cli.py
python -m ruff check .
python -m compileall -q src tests
```

Full repository merge gate remains:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The independent Stockfish witness remains CI/external-engine qualification of the
existing engine integration. M23 itself does not invoke an engine or any live model
provider.

## Deferred external authority

Still deferred after M23:

- human review of disclosure/consent wording and actual UI timing;
- browser accessibility, localization, and visual QA;
- authentication/authorization for a hosted multi-user service;
- production model/evaluator provider selection and credentials;
- empirical tutoring efficacy or causal learner-diagnosis claims.
