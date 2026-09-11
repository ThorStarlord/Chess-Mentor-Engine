# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Numbered milestone boundary:** M34 — Hermetic Reviewed-Coaching Recovery Reconciliation, QUALIFIED / MERGED PR #71.  
**Qualified post-M34 program:** Chess Knowledge Ontology K0–K7, QUALIFIED / MERGED PRs #75–#80.  
**Current `main` feature baseline:** `0ca0dc42ef84a3f9a6c120b1dc0561d00a73603c`.  

This file is the concise moving authority for repository state. Historical
qualification detail remains in feature PRs, runbooks, Git history, and milestone
handoffs. See [`STATUS.md`](../../STATUS.md) for the latest repository handoff,
[`docs/runbooks/chess-knowledge-ontology-program.md`](../runbooks/chess-knowledge-ontology-program.md)
for the K0–K7 qualification/restart path, and the
[M32–M34 milestone runbook](../runbooks/m32-m34-milestone-runbook.md) for the prior
numbered milestone. Software qualification is not empirical tutoring efficacy.

## Numbered milestone board

```text
M1  - Trustworthy Chess Evidence Substrate                 QUALIFIED
M2  - Deterministic Chess Feature Extraction               QUALIFIED
M3  - Engine Evidence                                      QUALIFIED
M4  - Diagnostic Position Selection                        QUALIFIED
M5  - Player Decision Evidence                             QUALIFIED
M6  - Reasoning Discrepancy                                QUALIFIED
M7  - Learner Hypothesis Ledger / M7Q                      QUALIFIED
M8  - Evidence-Aware Tutor Session                         QUALIFIED
M9  - Training Intervention Registry                       QUALIFIED
M10 - Bounded Outcome / Transfer Evidence                  QUALIFIED - MERGED PR #41
M11 - Longitudinal Learner State                           QUALIFIED - MERGED PR #43
M12 - Local Evidence CLI                                   QUALIFIED - MERGED PR #44
M13 - Persistent Tutor Session CLI                         QUALIFIED - MERGED PR #45
M14 - Engine-Backed Analysis CLI                           QUALIFIED - MERGED PR #46
M15 - Evaluation Presentation Contract                     QUALIFIED - MERGED PR #47
M16 - Grounded Mentor Feedback Composer                    QUALIFIED - MERGED PR #48
M17 - Analysis-to-Presentation CLI Bridge                  QUALIFIED - MERGED PR #49
M18 - Diagnostic Move-Analysis Queue                       QUALIFIED - MERGED PR #50
M19 - Provenance-Bound Mentor Coaching                     QUALIFIED - MERGED PR #51
M20 - Model Coaching Evaluation Contract                   QUALIFIED - MERGED PR #53
M21 - Candidate-to-Tutor Orchestration                     QUALIFIED - MERGED PR #54
M22 - End-to-End Evaluation Fidelity Matrix                QUALIFIED - MERGED PR #55
M23 - Diagnostic-to-Persistent-Tutor Bridge                QUALIFIED - MERGED PR #57
M24 - Provider / Evaluator Execution Conformance           QUALIFIED - MERGED PR #58
M25 - Coach Review Read Model                              QUALIFIED - MERGED PR #59
M26 - Persistent Reviewed-Coaching Operator                QUALIFIED - MERGED PR #61
M27 - Reviewed-Coaching Execution Ledger                   QUALIFIED - MERGED PR #62
M28 - Local Coach-Review Reference Surface                 QUALIFIED - MERGED PR #63
M29 - Persisted Review -> Reference Surface Bridge         QUALIFIED - MERGED PR #65
M30 - Participant-Scoped Review Package & Navigation       QUALIFIED - MERGED PR #66
M31 - Execution-Envelope Privacy & Retry Preflight         QUALIFIED - MERGED PR #67
M32 - Persisted Review Delivery Fidelity Contract          QUALIFIED - MERGED PR #69
M33 - Deterministic Mentor-Feedback Trace Surface          QUALIFIED - MERGED PR #70
M34 - Reviewed-Coaching Recovery Reconciliation            QUALIFIED - MERGED PR #71
```

M35+ labels in planning documents remain provisional. The K program was intentionally
implemented under a separate label namespace and does not consume those milestone
numbers.

## Qualified post-M34 Chess Knowledge Ontology program

```text
K0  - Ontology authority / ADR foundation                  QUALIFIED - PR #75
K1  - Versioned ontology registry and validation           QUALIFIED - PR #75
K2  - Tactical vocabulary + Lichess crosswalk              QUALIFIED - PR #75
K3  - Strategy / evaluation / feature / plan vocabulary    QUALIFIED - PR #76
K4  - Provenance-bound knowledge assertions                QUALIFIED - PR #77
K5  - Conservative deterministic concept detectors         QUALIFIED - PR #78
K6  - Authority-preserving M19 coaching sidecar             QUALIFIED - PR #79
K7  - M7C-preserving learner-knowledge projection           QUALIFIED - PR #80
```

The program's central invariant is:

```text
concept definition != concept assertion != learner inference
```

## Recent promotion provenance

| Package | Qualified/final head | Merge commit | Qualification |
| --- | --- | --- | --- |
| M32 / PR #69 | `3381a85be5035dea5b426aac0d88d57317b80ffb` | `ae4bbe7c925855df9082c41bd46b4fea7d930bc8` | run `34553450225`: full gate PASS |
| M33 / PR #70 | `761c0af847e84050ba7697ada6e8aa3e0b68a930` | `4eadb996b8c4036c793515d2457fe363c81cb40d` | run `34554448292`: full gate PASS |
| M34 / PR #71 | `5e784e2662441d880e65589bc6413b9ff0b38f9f` | `9e896bf955de24acaf6dc5d0503147eaaae3c1e4` | run `34555466776`: full gate PASS |
| K0–K2 / PR #75 | `5e76400ed0df80ad845c07bfdedec08e3c46af45` | `f52b3773b773883d1ac9f476d563c70433bdeb63` | run `34590630613`: full gate PASS |
| K3 / PR #76 | `ecd5bf19517d9e8a657f1c2f1044596bc5e3f88b` | `a0c6dcb01060e84f2b9ac1b517a39873720a4b7a` | run `34591111549`: full gate PASS |
| K4 / PR #77 | `2d7537b260007613b81e720be683b531b2f8bc55` | `fd43a0a416aceb33444b7f2b62edf1d2e5767872` | run `34591799180`: full gate PASS |
| K5 / PR #78 | `be0cffdbe73c3b37e998ea805f87ae7a80493cf8` | `b417d170b69de271635fb24b666bea2f6f290d2e` | run `34592343696`: full gate PASS |
| K6 / PR #79 | `eb3dcc7a06485a40c6a9fdcd9a2429c16a597bdf` | `8653b058e2ed7af598a80c9293bbc51d3e5da2bf` | run `34592709220`: full gate PASS |
| K7 / PR #80 | `f4cb0721d9769b067985d253be4659e8ccd888bd` | `0ca0dc42ef84a3f9a6c120b1dc0561d00a73603c` | run `34595432067`: 857 passed, 8 intentional regular-job skips, Ruff/compile/Stockfish PASS |

“Full gate” means full repository pytest, Ruff, `compileall`, and the independent
Stockfish job on the exact final PR head. A skipped Stockfish suite in the regular
pytest job is not treated as the independent-engine witness.

## Current evidence / operator path

The existing qualified product path remains intact:

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
-> replay-verified persisted M8 state=compared
-> M26 reviewed-coaching operator
   -> M16 deterministic grounded feedback
   -> optional M19 request / M24 provider execution / M19 coaching
   -> optional M20 request / M24 evaluator execution / M20 bounded evaluation
   -> M25 authority-separated coach-review read model
   -> atomic append-only M26 run lineage
-> M27 mechanical reviewed-coaching execution ledger
-> M29 persisted review -> M28 deterministic reference surface
-> M30 participant-scoped review package / navigation / export
-> M32 machine-readable persisted review delivery bundle
-> M33 deterministic M16 mentor-feedback trace
-> optional M31 synthetic-canary/manual-retry preflight
-> optional M34 hermetic multi-attempt recovery reconciliation
-> explicit M9 training applicability/selection
-> M10 outcome / transfer evidence
-> append-only M11 longitudinal learner state
```

The Chess Knowledge Ontology is a cross-cutting semantic layer over that path rather
than a replacement pipeline:

```text
canonical chess subject
-> K0–K3 registered concept definition
-> optional K4 provenance-bound assertion
-> optional K5 deterministic detector for the qualified mechanical subset

exact K4 assertion bundle
   +--> K6 knowledge context -> exact binding to unchanged M19 request
   +--> K7 knowledge projection + existing M7C recurrence assessment
        -> M7C relation preserved verbatim
```

Not every application must invoke the ontology. Each transition remains an authority
boundary.

## Current operational surfaces

Installed local commands remain:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

K0–K7 add no new production CLI command. They are currently Python API/reference
surfaces. `cme analyze` and `cme diagnose` still require an explicitly supplied UCI
executable or PATH name. Reviewed-coaching/provider execution still occurs only
through explicitly supplied M24-compatible application adapters.

### K0–K3 — ontology definition layer

The default registry is a strict composed, versioned ontology with stable IDs,
relationships, external crosswalks, pedagogy metadata, and deterministic
fingerprints. It includes tactical concepts, rule/position features, strategic
principles, qualitative evaluation factors, and candidate plans.

Registry membership defines vocabulary. It does not prove concept presence and does
not mean every concept has an automatic detector.

### K4 — assertion layer

`KnowledgeAssertion` and `KnowledgeAssertionBundle` represent bounded,
content-addressed claims about exact chess subjects. Assertions carry exact ontology
identity, authority class, evidence refs, provenance, qualifiers, claim scope, and
time.

External tags, deterministic facts, engine-derived claims, heuristic assessments,
model interpretations, and human ratifications remain distinct authorities.

### K5 — deterministic detector layer

K5 automatically detects only mechanically qualified concepts: check/checkmate,
absolute pin, bishop pair, open/semi-open files, isolated/doubled/passed pawns, pawn
islands, promotion/underpromotion, moved-piece fork, discovered check, and double
check.

Context-heavy tactics/strategy remain registered without being falsely automated.

### K6 — model-consumer sidecar

K6 projects exact assertion bundles into `KnowledgeCoachingContext` and binds them to
an already-valid M19 request through `KnowledgeModelBinding`. The referenced M19
request is not modified or refingerprinted. Model consumers receive explicit
anti-authority-promotion instructions.

### K7 — learner-consumer projection

K7 projects exact position-level assertion bundles onto an existing M7C assessment.
It preserves each recurrence-unit relation exactly and reports descriptive
per-concept counts. Partial ontology coverage remains explicit.

K7 does not decide recurrence. M7C remains authoritative for support, contradiction,
counterexample, context-exception, unclear, and mixed relations.

## Qualification commands

Focused ontology program:

```bash
python -m pytest \
  tests/test_chess_knowledge_ontology.py \
  tests/test_chess_knowledge_assertions.py \
  tests/test_chess_knowledge_detectors.py \
  tests/test_chess_knowledge_projection.py \
  tests/test_chess_knowledge_learner_projection.py -rs
```

Relevant M7C/M19 regressions:

```bash
python -m pytest \
  tests/test_hypothesis_recurrence_assessment.py \
  tests/test_hypothesis_recurrence_provenance.py \
  tests/test_m19_provenance_bound_model_coaching.py -rs
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

Pull-request CI remains the merge authority. No standalone static Python type checker
is configured.

## Current claim ceiling

The repository now has qualified M1–M34 evidence/tutoring/review/recovery contracts
plus a qualified Chess Knowledge Ontology definition/assertion/detector/projection
program.

It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- automatic or empirically optimal hypothesis formation;
- optimal/effective intervention selection, intervention-caused improvement, or
  automatic mastery;
- universal engine-evaluation or move-quality thresholds;
- automatic M6 diagnosis generation from engine output;
- automatic M7/M11 mutation from ontology assertions, tutor calls, analysis, or
  model coaching;
- automatic detection of every registered chess concept;
- semantic correctness of a heuristic, model, external, or human assertion merely
  because it uses a registered concept ID;
- arithmetic decomposition of engine evaluation into ontology evaluation factors;
- strategic plans as best-move authority;
- M9 intervention authority from ontology pedagogy metadata alone;
- semantic correctness, safety, or pedagogical quality of arbitrary model prose;
- semantic completeness/correctness of an arbitrary M20 evaluator;
- a production LLM/evaluator provider, vendor SDK, credential flow, automatic
  retry/backoff policy, latency/cost budget, or secrets architecture;
- external-side-effect idempotency or production recovery correctness;
- production privacy/security approval;
- correct disclosure/consent behavior in an external end-user UI;
- production UI usability, accessibility, localization, visual correctness, or
  browser/device compatibility;
- hosted authentication/authorization, multi-user production persistence,
  observability, or deployment readiness;
- empirical tutoring efficacy.

M16 remains the deterministic grounding ceiling. M19 proves request/model
provenance, not model quality. M20 records bounded evaluator judgments, not objective
truth. M7C remains recurrence authority. K5 owns only its explicitly qualified
mechanical detector subset. K6 is a sidecar, not an M19 authority change. K7 is a
descriptive projection, not learner-state mutation.
