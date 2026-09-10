# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Current implementation boundary:** M25 — Coach Review Read Model & Presentation Contract, QUALIFIED / MERGED PR #59.  
**Post-feature `main` baseline:** `13db09f7cf4c066c49988875e89760ce204c2515`.  

This file is the concise moving authority for repository state. Historical
qualification detail remains in feature PRs, runbooks, ADRs, architecture records,
and Git history. See [`STATUS.md`](../../STATUS.md) for the completed M23–M25
milestone handoff. Software qualification is not empirical tutoring efficacy.

## Milestone board

```text
M1  - Trustworthy Chess Evidence Substrate       QUALIFIED
M2  - Deterministic Chess Feature Extraction     QUALIFIED
M3  - Engine Evidence                            QUALIFIED
M4  - Diagnostic Position Selection              QUALIFIED
M5  - Player Decision Evidence                   QUALIFIED
M6  - Reasoning Discrepancy                      QUALIFIED
M7  - Learner Hypothesis Ledger / M7Q            QUALIFIED
M8  - Evidence-Aware Tutor Session               QUALIFIED
M9  - Training Intervention Registry             QUALIFIED
M10 - Bounded Outcome / Transfer Evidence        QUALIFIED - MERGED PR #41
M11 - Longitudinal Learner State                 QUALIFIED - MERGED PR #43
M12 - Local Evidence CLI                         QUALIFIED - MERGED PR #44
M13 - Persistent Tutor Session CLI               QUALIFIED - MERGED PR #45
M14 - Engine-Backed Analysis CLI                 QUALIFIED - MERGED PR #46
M15 - Evaluation Presentation Contract           QUALIFIED - MERGED PR #47
M16 - Grounded Mentor Feedback Composer          QUALIFIED - MERGED PR #48
M17 - Analysis-to-Presentation CLI Bridge        QUALIFIED - MERGED PR #49
M18 - Diagnostic Move-Analysis Queue             QUALIFIED - MERGED PR #50
M19 - Provenance-Bound Mentor Coaching           QUALIFIED - MERGED PR #51
M20 - Model Coaching Evaluation Contract         QUALIFIED - MERGED PR #53
M21 - Candidate-to-Tutor Orchestration           QUALIFIED - MERGED PR #54
M22 - End-to-End Evaluation Fidelity Matrix      QUALIFIED - MERGED PR #55
M23 - Diagnostic-to-Persistent-Tutor Bridge      QUALIFIED - MERGED PR #57
M24 - Provider / Evaluator Execution Conformance QUALIFIED - MERGED PR #58
M25 - Coach Review Read Model                    QUALIFIED - MERGED PR #59
```

Supporting repairs/capabilities remain part of this baseline, including the UCI
provider/evidence repair, durable artifacts + verified M8 replay, and prior milestone
documentation consolidations.

## Recent promotion provenance

| Milestone | Qualified/final head | Merged commit | Qualification |
| --- | --- | --- | --- |
| M20 / PR #53 | `583ccda3a357605bc9ff2318ce85bc940031730b` | `2d57b953ee8336a5bdd05f00f48905d000158691` | run `34481292153`: 616 passed, 8 intentional skips, Ruff PASS, Stockfish PASS |
| M21 / PR #54 | `537c9d9751103bc5c0569fa26b12a229cc47a6fe` | `20ddff116aa501f2644bfcdbef69d4c173d93763` | run `34483038324`: 633 passed, 8 intentional skips, Ruff PASS, Stockfish PASS |
| M22 / PR #55 | `10e7dac9ef0b6ebafce9b5d307ec99e1fd254ca5` | `7f59c6add7ffe042d8c2b65d6273867673b6d74b` | run `34484791539`: 648 passed, 8 intentional skips, Ruff PASS, Stockfish PASS |
| M23 / PR #57 | `8131685b434f52066e375e0914a2cf3ecf13c4c9` | `105fed42425a28d2733485b832e42ff656812279` | run `34499329989`: 659 passed, 8 intentional skips, Ruff PASS, Stockfish PASS |
| M24 / PR #58 | `e44ae84749de7820e9d403019ec7bddb5687639e` | `14f51b5e763f26b5c0608ecce8a237271641a94c` | run `34500991230`: 686 passed, 8 intentional skips, Ruff PASS, Stockfish PASS |
| M25 / PR #59 | `9927171cb5f09bf0274d0e2c36e9ab736a90baee` | `13db09f7cf4c066c49988875e89760ce204c2515` | run `34502823382`: 709 passed, 8 intentional skips, Ruff PASS, Stockfish PASS |

M23–M25 are complete. A new milestone must begin from live `main`, reconcile this
status authority and `STATUS.md`, and establish a fresh bounded package queue before
implementation.

## Current evidence / operator path

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound engine evidence
-> objective played-decision comparison / bounded diagnostic selection
-> M15 deterministic evaluation presentation
-> M18 diagnostic candidate batch
-> explicit participant candidate selection + separate capture consent
-> M23 cme-candidate-tutor
-> M21 authorization/launch
-> exact M5 PlayerDecisionContext
-> persisted replay-verifiable M8 state=selected
-> M13 tutor capture / freeze / reveal / compare workflow
-> position-local M6 discrepancy + optional bounded M7 context
-> M16 deterministic grounded mentor feedback
-> M19 model request
-> M24 provider execution conformance
-> M19 bound model coaching
-> M20 evaluation request
-> M24 evaluator execution conformance
-> M20 bounded model-output evaluation
-> M25 authority-separated coach-review read model
-> explicit M9 training applicability/selection
-> M10 outcome / transfer evidence
-> append-only M11 longitudinal learner state
```

Not every application must invoke every downstream layer. Each arrow remains an
authority boundary.

## Current operational surfaces

### Installed local commands

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
cme-candidate-tutor
cme-coach-review
```

`cme analyze` and `cme diagnose` require an explicit external UCI executable or PATH
name. `cme-candidate-tutor` itself performs no engine or model call; it consumes the
exact M18 JSON, exact PGN, participant authorization inputs, capture protocol/prompts,
and local artifact database. `cme-coach-review` reads a local M25 JSON bundle only.

### M23 — Diagnostic-to-persistent tutor bridge

M23 closes the former gap between M18/M21 and replay-verified M13 persistence. It
revalidates the exact diagnostic queue and PGN, records separate selection and
capture consent, invokes native M21, creates only M5 plus M8 `state=selected`, and
atomically persists exact lineage. It does not create M6/M7/M9 authority.

### M24 — Provider/evaluator execution conformance

M24 wraps M19/M20 execution with detached immutable requests, explicit endpoint
identity, content-addressed execution provenance, and fail-closed classifications:

```text
invalid_request
request_mutation
timeout
transient
permanent
malformed_response
identity_mismatch
chronology_violation
```

Only timeout/transient results are marked retryable. M24 performs no automatic retry,
chooses no provider, and does not establish semantic truth.

### M25 — Coach-review read model

M25 projects already-qualified records into a content-addressed application-facing
read model with frozen section separation:

```text
objective_evidence        M15
diagnostic_selection      M18
participant_authority     M21
tutor_state               M8
deterministic_grounding   M16
model_coaching             M19
model_evaluation           M20
```

Optional downstream layers remain `null`. M25 mechanically validates source
identities and dependencies but does not invent missing evidence, rewrite model
prose, promote evaluator acceptance to truth, or create a production UI.

## Qualification commands

Focused current milestone:

```bash
python -m pytest tests/test_m23_diagnostic_to_persistent_tutor_cli.py
python -m pytest tests/test_m24_provider_conformance.py
python -m pytest tests/test_m25_coach_review_read_model.py
```

Principal milestone regression:

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

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The Stockfish witness requires `STOCKFISH_EXECUTABLE`; a skipped suite is not an
independent engine pass. Pull-request CI remains the merge authority. No standalone
static Python type checker is configured.

See the consolidated
[M23–M25 milestone runbook](../runbooks/m23-m25-milestone-runbook.md).

## Current claim ceiling

The repository now has qualified deterministic chess/evidence contracts, persistent
bounded tutor state, an operational diagnostic-to-persistent-tutor bridge,
provider-neutral model/evaluator execution conformance, and an application-facing
read model that preserves authority separation. It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- optimal/effective intervention selection, intervention-caused improvement, or
  automatic mastery;
- universal engine-evaluation or move-quality thresholds;
- automatic M6 diagnosis generation from engine output;
- automatic M7/M11 mutation from tutor, analysis, or model-coaching calls;
- semantic correctness, safety, or pedagogical quality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary M20 evaluator;
- a production LLM/evaluator provider, vendor SDK, credential flow, transport,
  automatic retry policy, production latency/cost budget, or secrets architecture;
- correct disclosure/consent behavior in an external end-user UI;
- production UI usability, accessibility, localization, or visual correctness;
- a web UI, authenticated hosted service, production multi-user persistence, or
  deployment readiness;
- empirical tutoring efficacy.

M16 remains the deterministic grounding ceiling. M19 proves request/model provenance,
not model quality. M20 records bounded evaluator judgments, not objective truth. M21
is participant-authorized orchestration, not inference. M23 operationalizes and
persists that path without broadening authority. M24 qualifies execution mechanics,
not a provider. M25 qualifies a read model, not a production interface.
