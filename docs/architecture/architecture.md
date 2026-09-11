# Architecture: implemented boundaries through M34

> **Current implementation authority:**
> [`../product/repository-build-status.md`](../product/repository-build-status.md)
>  
> **Latest completed milestone handoff:** [`../../STATUS.md`](../../STATUS.md)  
> **Contributor orientation:** [`../../CONTEXT.md`](../../CONTEXT.md)

This document is the current high-level architecture map. Detailed historical
contracts remain in `docs/architecture/`, ratified decisions in `docs/decisions/`,
and operational/qualification detail in `docs/runbooks/`.

The implementation boundary is **M34 — Hermetic Reviewed-Coaching Recovery
Reconciliation**. The architecture is intentionally an authority graph: each layer
may consume qualified upstream evidence, but must not silently inherit authority it
does not own.

## 1. System shape

```text
                         OBJECTIVE CHESS

PGN / source
   |
   v
M1-M2 canonical game / position / deterministic context
   |
   v
M3 provenance-bound UCI engine evidence
   |
   v
M4 played-decision comparison + diagnostic selection
   |
   v
M15 deterministic evaluation presentation
   |
   v
M18 auditable diagnostic candidate/control batch

                         PARTICIPANT EVIDENCE

explicit candidate selection + separate capture consent
   |
   v
M21 authorization / candidate-to-session launch
   |
   v
M5 frozen participant decision evidence
   |
   v
M8 controlled capture / freeze / reveal / compare state

                         LEARNER INFERENCE

M6 position-local reasoning discrepancy
   |
   v
M7 participant-specific hypothesis / recurrence / contradiction ledger

                         DETERMINISTIC TUTOR GROUNDING

compared M8 session + exact M15/M6 + optional complete active-current M7
   |
   v
M16 deterministic grounded mentor feedback

                         MODEL / EVALUATOR BOUNDARIES

M16 grounding
   |
   +--> M19 model request -> optional M24 provider execution -> M19 model prose
   |
   +--> M20 evaluation request -> optional M24 evaluator execution -> M20 judgment

                         PERSISTED REVIEW RUNTIME

M26 reviewed-coaching orchestration
   |
   +--> atomic append-only M26 run lineage
   |
   v
M25 authority-separated coach-review read model
   |
   v
M27 mechanical reviewed-coaching execution ledger
   |
   v
M29 persisted review -> M28 deterministic local reference surface
   |
   v
M30 participant-scoped review package / navigation / export
   |
   v
M32 exact machine-consumer review delivery bundle
   |
   v
M33 deterministic M16 feedback trace

                         EXECUTION SAFETY / RECOVERY

optional M31 synthetic-canary + manual-retry-history preflight
optional M34 synthetic multi-attempt recovery reconciliation

                         PEDAGOGY / LONGITUDINAL EVIDENCE

M9 explicit intervention applicability / selection
   |
   v
M10 bounded practice / transfer evidence
   |
   v
M11 append-only longitudinal learner state
```

Not every application invokes every optional downstream branch. This is a qualified
capability graph, not a claim that one command automatically performs the entire
system.

## 2. Layer ownership and authority

| Layer | Principal implementation | Authority owned | Authority explicitly not owned |
| --- | --- | --- | --- |
| Chess substrate | M1–M2, `chess/` | Canonical games/positions, legality, deterministic context/features, source provenance | Player cognition, pedagogy |
| Engine evidence | M3, `analysis/` | Versioned UCI analysis evidence, score/bound/mate/partial/failure semantics, engine provenance | Move-quality taxonomy, learner diagnosis |
| Selection | M4/M18, `selection/` | Objective played-decision comparison, explicit versioned diagnostic policy, candidates/controls | Participant choice, universal blunder thresholds |
| Participant evidence | M5, `evidence/` | Raw/frozen participant responses, timing/exposure/capture provenance | Objective chess truth, recurring weakness claims |
| Learning inference | M6–M7, `learning/` | Position-local discrepancy, participant-specific hypotheses, contradiction/challenge/recurrence evidence | Causal cognitive mechanisms, permanent traits |
| Tutor state | M8/M13/M21/M23, `tutoring/` + CLIs | Controlled state transitions, authorization/consent binding, replayable persistence | Automatic diagnosis, automatic training selection |
| Training/outcomes | M9–M11 | Applicability-driven interventions, bounded outcome/transfer evidence, longitudinal state | Intervention causality, mastery from drill completion alone |
| Presentation | M15, `presentation/` | Deterministic projection of exact qualified chess evidence | New chess semantics or model interpretation |
| Deterministic feedback | M16, `feedback/` | Exact session-local factual mentor grounding | Arbitrary generative prose, pedagogical optimality |
| Model language | M19, `coaching/` | Request/model provenance for generated language | Semantic truth or safety of arbitrary prose |
| Model evaluation | M20, `coaching/` | Bounded evaluator judgments under a frozen policy | Objective truth, complete model safety proof |
| Execution seam | M24 | Detached request/endpoint identity, execution provenance, failure classification | Vendor approval, automatic retry policy, credential architecture |
| Review runtime | M25–M30 | Authority-separated review, atomic persistence, mechanical verification, deterministic rendering/navigation | Authentication, privacy approval, production UI quality |
| Consumer delivery | M32, `review_delivery.py` | Exact machine-readable review delivery fidelity | Browser/device/a11y/usability correctness |
| Deterministic trace | M33, `mentor_feedback_trace.py` | Component-level M16 source traceability | Model/evaluator truth, pedagogy |
| Recovery reconciliation | M34, `execution_recovery_reconciliation.py` | Hermetic classification of supplied synthetic retry histories against persisted targets | Retry authorization/execution, external-side-effect idempotency |
| Local durability | `storage/` | Immutable artifacts, dependency verification, replay/rebuild support | Independent re-interpretation of domain claims |

## 3. Core invariants

### 3.1 Objective chess truth is not learner inference

A bad engine outcome can justify an objective comparison. It cannot by itself prove
why the player moved, what they saw, or whether a recurring cognitive weakness
exists.

```text
engine evidence
!=
participant self-report
!=
learner hypothesis
```

### 3.2 Position-local discrepancy is not a stable trait

M6 stays position-local. M7 may accumulate participant-specific evidence across
contexts, but recurrence remains descriptive evidence rather than a causal
psychological mechanism.

```text
one discrepancy
!=
recurrence
!=
causal trait
```

### 3.3 Participant selection and evidence-capture consent are separate

M21/M23 require explicit candidate selection and explicit capture consent. One may
not be inferred from the other.

### 3.4 Information sequencing is part of correctness

M5/M8 pre-reveal capture is meaningful only when objective analysis/diagnostic
rationale has not already contaminated the intended measurement stage. Repository
qualification cannot prove a future frontend displayed information in the correct
order; that remains a UI/human QA gate.

### 3.5 Presentation must preserve engine semantics

M15 and all downstream consumer surfaces preserve:

- White versus decision-mover perspective;
- symbolic mate rather than numericizing mate;
- exact versus bounded scores;
- partial/unavailable/failure states;
- child-analysis status;
- compatibility state;
- exact source identity and engine provenance.

Consumers do not get to invent new score semantics.

### 3.6 M16 is the deterministic factual grounding ceiling

M16 is deterministic and bound to exact M15/M6 plus optional complete active-current
M7 evidence. It may be used as model input, but downstream model-authored prose does
not inherit M16's deterministic authority.

```text
M16 deterministic grounding
-> M19 model request
-> M19 prose

request binding != semantic verification
```

### 3.7 Evaluator acceptance is bounded judgment, not truth

M20 can say `pass`, `fail`, or `unclear` under its policy. It cannot promote its
result into objective chess evidence or prove pedagogical effectiveness.

### 3.8 Persistence is append-oriented and replay-verifiable

Important session/review artifacts are immutable/content-addressed or append-only
where defined. Mutating workflows load and verify prior state, apply one qualified
transition/orchestration, and persist successor evidence rather than silently
rewriting history.

### 3.9 Review surfaces cannot collapse authority labels

M25/M28/M29/M30 organize and render already-qualified sources. They must preserve the
difference among objective evidence, participant evidence, learner inference,
deterministic feedback, model prose, and evaluator judgment.

### 3.10 Consumer fidelity is explicit

M32 creates `m32.persisted-review-delivery-fidelity.v1` as a stable exact-content
consumer bundle over one participant-scoped M30 package. It rejects semantic,
authority, source, participant, ordering, and fingerprint drift.

M32 does not establish frontend quality.

### 3.11 Deterministic feedback provenance is mechanically traceable

M33 creates `m33.deterministic-mentor-feedback-trace.v1`. Every substantive M16
component is represented by a stable component identity, ordinal, content hash,
source authority, source pointer, and source-field declaration.

M19/M20 presence may be recorded as metadata but never promoted into deterministic
source authority.

### 3.12 Recovery planning is not retry authority

M34 creates `m34.reviewed-coaching-recovery-reconciliation.v1` from supplied
synthetic M24 multi-attempt histories and one already-persisted mechanically verified
M26 target.

A result may be `complete` or `resume_eligible`. `resume_eligible` means only that
the supplied history is mechanically consistent with a bounded recovery plan. It is
not permission to call a provider. Retryable partial failures use a full-M26 restart
scope to avoid silently reusing unpersisted external side effects.

## 4. Current operational surfaces

Installed commands:

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

M31–M34 remain Python API / hermetic qualification surfaces. M32–M34 add no new
production CLI command.

The installed operator path is intentionally local/reference-oriented. Participant
scoping is not authentication; the static review surface is not a production UI;
application-supplied provider adapters are not a repository-selected vendor stack.

## 5. Persistence and provenance model

The repository strongly prefers explicit references and fingerprints over inference
from rendered text.

Cross-layer consumers should use exact artifact identity, declared source pointers,
schema versions, participant scope, content fingerprints, and replay/rebuild
validation where available.

Do not derive provenance from prose when M27/M32/M33 provide a mechanical path.

Key examples:

```text
M26 run
-> exact persisted M16/M19/M20/M25/M24-related artifacts
-> M27 mechanical execution ledger
-> M29 persisted-review resolution
-> M30 participant package
-> M32 delivery bundle
-> M33 deterministic feedback trace
```

M34 additionally binds the exact persisted M26/M27 target when reconciling supplied
synthetic execution histories.

## 6. Optional versus mandatory downstream layers

The architecture deliberately avoids forcing every run through every layer.

Examples:

- engine analysis may exist without participant evidence;
- a participant-authorized tutor session may exist without M19 model prose;
- reviewed coaching may omit provider/evaluator execution when no adapter is
  supplied;
- M20 evaluation is not required to make M16 factual grounding valid;
- M31/M34 are optional qualification/reconciliation surfaces;
- training and longitudinal mutation remain explicit downstream decisions rather
  than automatic consequences of analysis/coaching.

This keeps authority changes visible and prevents one orchestration layer from
becoming an accidental god object.

## 7. Current productization boundary

The repository has strong local contracts and qualification but intentionally stops
short of claiming a production end-user system.

Not yet established:

- hosted authentication/authorization or multi-user tenancy;
- a production database/retention architecture;
- production LLM/evaluator vendor selection and credential transport;
- automatic retry/backoff/rate-limit policy or external-side-effect idempotency;
- production privacy/security approval;
- browser/device correctness, accessibility, localization, or usability;
- semantic safety/correctness of arbitrary model prose;
- empirical tutoring efficacy or intervention-caused improvement.

These are not implementation omissions that lower-level artifacts may silently
paper over. They are explicit external/human/product authority gates.

## 8. Architecture evolution policy

Future milestones should begin from live `main` and the current build-status
authority. Recommendations in `STATUS.md` or the build plan are candidate work until
a fresh bounded package queue is approved.

The next likely architecture questions are:

1. exposing M32 delivery and M33 trace artifacts through explicit operator surfaces;
2. creating a cross-surface hermetic consumer regression contract over M30/M32/M33;
3. defining the external adoption boundary for a real frontend/provider/privacy/
   security/retry environment.

None of those recommendations grant themselves production authority.

## 9. Historical architecture context

Older architecture documents and ADRs remain valuable records of how the system
reached the current design. Some describe only M1–M10-era boundaries or candidate
future concepts that later milestones refined.

Treat those as historical design provenance. For present-tense implementation
claims use:

```text
docs/product/repository-build-status.md
-> current implementation / qualification authority

STATUS.md
-> latest completed milestone handoff

this file
-> current high-level authority map

individual ADRs/runbooks
-> detailed historical decision / qualification evidence
```

Do not rewrite historical ADRs merely to make them read as if M34 already existed at
the time.