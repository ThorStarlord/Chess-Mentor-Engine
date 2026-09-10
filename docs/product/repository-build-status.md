# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Current implementation boundary:** M22 — End-to-End Evaluation Fidelity Matrix, QUALIFIED / MERGED PR #55.  
**Post-milestone `main` baseline:** `7f59c6add7ffe042d8c2b65d6273867673b6d74b`.  

This file is the concise moving authority for repository state. Historical
qualification details remain in feature PRs, runbooks, ADRs, architecture records,
and Git history. See [`STATUS.md`](../../STATUS.md) for the completed M20–M22
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
M17 - Analysis-to-Presentation CLI Bridge         QUALIFIED - MERGED PR #49
M18 - Diagnostic Move-Analysis Queue             QUALIFIED - MERGED PR #50
M19 - Provenance-Bound Mentor Coaching           QUALIFIED - MERGED PR #51
M20 - Model Coaching Evaluation Contract         QUALIFIED - MERGED PR #53
M21 - Candidate-to-Tutor Orchestration           QUALIFIED - MERGED PR #54
M22 - End-to-End Evaluation Fidelity Matrix      QUALIFIED - MERGED PR #55
```

Supporting repairs/capabilities remain part of this baseline:

```text
UCI evidence contract repair / provider 0.2      MERGED - PR #39
Durable artifacts + verified M8 replay           MERGED - PR #40
Post-M10 documentation consolidation             MERGED - PR #42
M17-M19 milestone handoff                         MERGED - PR #52
```

## Recent promotion provenance

| Milestone | Qualified/final head | Merged commit | Qualification |
| --- | --- | --- | --- |
| M17 / PR #49 | `c91ffa33a0797e0894f1f2dc519600be39f6afcc` | `4672a2b5dc34cae736be8e260f439afe6acfb1e6` | run `34435288183`: 582 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M18 / PR #50 | `65297abd366bf092a60ed4fa202e2e51bb1950cd` | `00bab82dc963bff005c9753b498f1e50a8c513d4` | run `34436086912`: 589 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M19 / PR #51 | `f465a7f5355d8e9304a557cbbc26971d1aa18c27` | `25672c1b375181b6eb48e4ee9c8283e16dc12665` | run `34436883416`: 598 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M20 / PR #53 | `583ccda3a357605bc9ff2318ce85bc940031730b` | `2d57b953ee8336a5bdd05f00f48905d000158691` | run `34481292153`: 616 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M21 / PR #54 | `537c9d9751103bc5c0569fa26b12a229cc47a6fe` | `20ddff116aa501f2644bfcdbef69d4c173d93763` | run `34483038324`: 633 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M22 / PR #55 | `10e7dac9ef0b6ebafce9b5d307ec99e1fd254ca5` | `7f59c6add7ffe042d8c2b65d6273867673b6d74b` | run `34484791539`: 648 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |

M20–M22 are complete. Any next milestone must begin from live `main`, reconcile this
status authority and `STATUS.md`, then establish a new bounded package queue before
implementation.

## Current evidence path

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound engine evidence
-> objective played-decision comparison / bounded diagnostic selection
-> deterministic evaluation presentation projection
-> explicit participant candidate selection + capture consent
-> frozen participant decision evidence
-> position-local reasoning discrepancy
-> participant-specific hypothesis + contradiction/challenge evidence
-> controlled evidence-aware tutor session
-> deterministic grounded session-local mentor feedback
-> provenance-bound model language rendering
-> explicit bounded model-output evaluation
-> explicit training applicability / selected | ineligible | unclear
-> predeclared outcome protocol
-> practice / near / far / real-game outcome evidence
-> append-only longitudinal learner state
```

M22 separately qualifies covered cross-layer fidelity invariants over:

```text
M3/M4 -> M15 -> M16 -> M19 -> M20
```

Every arrow remains an authority boundary.

## Current product surfaces

### M12-M13 — Local evidence and persistent tutor CLI

The installed `cme` command provides deterministic PGN/position inspection,
participant-scoped artifact reads, and replay-verified append-only M8 tutor
transitions. M13 does not generate explanation text; `cme tutor explain` records
explicitly supplied text and provenance.

### M14-M18 — Engine analysis, presentation, and diagnostic queue

M14 adds bounded external-UCI analysis through:

```text
cme analyze <pgn> --ply-index N --engine <uci> ...
```

M17 adds the opt-in `--with-presentation` bridge through qualified M15. M15 preserves
canonical White scores, decision-mover projection, bound direction, symbolic mate,
partial/failure states, engine identity, and exact evidence references.

M18 adds:

```text
cme diagnose <pgn> --policy <selection-policy.json> --engine <uci> ...
```

It analyzes an explicit game window and produces the native deterministic
`DiagnosticCandidateBatch` plus an auditable source pool. It does not embed universal
move-quality thresholds or manufacture exact values from weak evidence.

### M16 — Deterministic grounded mentor feedback

M16 remains the deterministic factual grounding ceiling:

```text
chess_mentor_engine.feedback.compose_grounded_mentor_feedback
chess_mentor_engine.feedback.record_grounded_mentor_feedback
```

It recomputes M15, verifies exact M3/M4 evidence already bound into the M6/M8
context, preserves M6 and optional complete active-current M7 context, and keeps
non-exact evidence non-exact.

### M19 — Provenance-bound model coaching

M19 exposes provider-neutral model-language APIs:

```text
build_model_coaching_request
bind_model_coaching_response
record_model_coaching_response
run_model_coaching
ModelCoachingGeneration
ModelCoachProvider
```

Accepted records retain:

```text
grounding_status = request_bound_not_semantically_verified
claim_scope = session_local_model_rendering
```

Model provenance proves what grounded request reached what model run; it does not
establish semantic correctness or pedagogical quality.

### M20 — Bounded model-output evaluation

M20 exposes:

```text
build_model_coaching_evaluation_request
bind_model_coaching_evaluation
run_model_coaching_evaluation
ModelCoachingEvaluationGeneration
ModelCoachingEvaluationJudgment
```

The request is rebuilt from exact M16/M19 sources before evaluation. M20 v1 requires
one verdict for each frozen dimension:

```text
grounding_consistency
objective_chess_consistency
evidence_sufficiency
uncertainty_preservation
mate_and_bound_preservation
learner_inference_scope
authority_boundary
```

Aggregate outcomes are accepted, rejected, or inconclusive under the M20 policy.
Every result still states:

```text
truth_status = not_established_by_m20_evaluation
claim_scope = bounded_model_output_quality_assessment
```

M20 does not select or endorse a production evaluator.

### M21 — Diagnostic candidate to tutor session

M21 exposes:

```text
record_candidate_tutor_authorization
start_candidate_tutor_session
```

Candidate selection and evidence-capture consent are separate participant decisions.
Launch requires exact M18 candidate/batch/source identity plus exact canonical game
binding. M21 derives the M1 position context internally, creates only M5 decision
context plus initial M8 `state=selected`, and stops.

It does not choose candidates, expose diagnostic rationale as clean pre-reveal input,
create M6/M7 learner inference, select M9 training, or generate mentor language.

### M22 — End-to-end evaluation fidelity qualification

M22 introduces no production runtime authority. Its machine-readable matrix and
regression suite cover eight semantic regimes across native M3/M4/M15 contracts and
an exact M15/M16/M19/M20 lineage.

The matrix verifies preservation of:

- canonical White versus decision-mover perspective;
- exact versus bounded/non-exact semantics;
- lower/upper bound reversal for Black mover projection;
- symbolic mate without centipawn sentinels;
- partial/unavailable/incompatible/failure states;
- source fingerprints and evidence references;
- fail-closed behavior for rehashed cross-layer semantic drift.

See the [M22 runbook](../runbooks/m22-end-to-end-evaluation-fidelity-matrix.md).

## Qualification commands

Focused current milestone:

```bash
python -m pytest tests/test_m20_model_coaching_evaluation.py
python -m pytest tests/test_m21_diagnostic_candidate_tutor_orchestration.py
python -m pytest tests/test_m22_end_to_end_evaluation_fidelity.py
```

Focused mentor/evaluation path:

```bash
python -m pytest \
  tests/test_m15_evaluation_presentation.py \
  tests/test_m16_grounded_mentor_feedback.py \
  tests/test_m19_provenance_bound_model_coaching.py \
  tests/test_m20_model_coaching_evaluation.py \
  tests/test_m22_end_to_end_evaluation_fidelity.py
```

Engine/comparison contracts:

```bash
python -m pytest tests/test_uci_provider.py tests/test_uci_evidence_contract.py
python -m pytest tests/test_decision_comparison.py
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The final command requires `STOCKFISH_EXECUTABLE`; skips are not an independent
engine pass. CI runs Python 3.11 native tests/lint plus a separate external Stockfish
witness. No standalone static type checker is configured.

## Current claim ceiling

The repository now has qualified deterministic chess/evidence contracts, persistent
bounded tutor state, a diagnostic analysis queue, participant-authorized candidate
launch, deterministic grounded feedback, a provider-neutral model-language boundary,
a bounded model-output-evaluation contract, and a hermetic cross-layer fidelity
matrix. It still does **not** claim:

- causal cognitive diagnosis or permanent learner traits;
- optimal/effective intervention selection;
- intervention-caused improvement or automatic mastery;
- universal engine-evaluation or move-quality thresholds;
- globally complete exposure history;
- automatic M6 diagnosis generation from engine output;
- automatic M7/M11 mutation from tutor, analysis, or model-coaching calls;
- semantic correctness, safety, or pedagogical quality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary M20 evaluator;
- a production LLM/evaluator provider, provider transport, retry/rate-limit policy,
  cost/latency/privacy policy, or secrets architecture;
- correct disclosure/consent behavior in an external end-user UI;
- a web UI, authenticated hosted service, or production multi-user persistence;
- empirical tutoring efficacy.

M16 remains the deterministic grounding ceiling. M19 proves request/model provenance,
not model quality. M20 records bounded evaluator judgments, not objective truth. M21
is participant-authorized orchestration, not inference. M22 proves only the covered
repository fidelity invariants.
