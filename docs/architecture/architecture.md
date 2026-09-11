# Architecture: implemented boundaries through M34 + K0–K7

> **Current implementation authority:**
> [`../product/repository-build-status.md`](../product/repository-build-status.md)
>  
> **Latest repository handoff:** [`../../STATUS.md`](../../STATUS.md)  
> **Contributor orientation:** [`../../CONTEXT.md`](../../CONTEXT.md)

This document is the current high-level architecture map. Detailed historical
contracts remain in `docs/architecture/`, ratified decisions in `docs/decisions/`,
and operational/qualification detail in `docs/runbooks/`.

The numbered milestone boundary is **M34 — Hermetic Reviewed-Coaching Recovery
Reconciliation**. The repository additionally has a qualified post-M34 **Chess
Knowledge Ontology program K0–K7**. The K labels do not consume provisional M35+
roadmap labels.

The architecture remains an authority graph: each layer may consume qualified
upstream evidence, but must not silently inherit authority it does not own.

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

                         CHESS KNOWLEDGE SEMANTICS

canonical chess subject
   |
   v
K0-K3 versioned concept registry / vocabulary
   |
   | concept definition only
   v
K4 provenance-bound concept assertion
   |
   +--> K5 conservative deterministic detectors
   |
   +--> K6 model-consumable sidecar -----------+
   |     bound to unchanged M19 request        |
   |                                           |
   +--> K7 learner-knowledge projection        |
         + existing M7C recurrence assessment  |
         + preserves M7C relation verbatim     |
                                               |
                         PARTICIPANT EVIDENCE  |
                                               |
explicit candidate selection + capture consent|
   |                                           |
   v                                           |
M21 authorization / candidate launch           |
   |                                           |
   v                                           |
M5 frozen participant decision evidence        |
   |                                           |
   v                                           |
M8 capture / freeze / reveal / compare          |
                                               |
                         LEARNER INFERENCE     |
                                               |
M6 position-local reasoning discrepancy        |
   |                                           |
   v                                           |
M7 / M7C participant-specific hypothesis       |
recurrence / contradiction ledger <---- K7 ----+

                         DETERMINISTIC TUTOR GROUNDING

compared M8 session + exact M15/M6 + optional active-current M7
   |
   v
M16 deterministic grounded mentor feedback

                         MODEL / EVALUATOR BOUNDARIES

M16 grounding
   |
   +--> M19 model request -> optional M24 provider execution -> M19 model prose
   |       ^
   |       |
   |       +---- optional K6 ontology sidecar; M19 identity unchanged
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

The ontology is cross-cutting rather than a mandatory new pipeline. Not every
application invokes K4–K7, and K6/K7 do not replace M19 or M7C authority.

## 2. Layer ownership and authority

| Layer | Principal implementation | Authority owned | Authority explicitly not owned |
| --- | --- | --- | --- |
| Chess substrate | M1–M2, `chess/` | Canonical games/positions, legality, deterministic context/features, source provenance | Player cognition, pedagogy |
| Engine evidence | M3, `analysis/` | Versioned UCI analysis evidence, score/bound/mate/partial/failure semantics, engine provenance | Move-quality taxonomy, learner diagnosis |
| Selection | M4/M18, `selection/` | Objective played-decision comparison, explicit diagnostic policy, candidates/controls | Participant choice, universal blunder thresholds |
| Chess knowledge definition | K0–K3, `chess_knowledge/` | Stable concept identity, definitions, hierarchy/relationships, crosswalks, detection metadata, authority ceilings, pedagogy metadata | Concept occurrence, participant cognition, learner diagnosis, best move |
| Chess knowledge assertion | K4 | Provenance-bound claim about an exact chess subject with explicit status/authority/evidence | Participant evidence, learner recurrence, intervention selection |
| Chess knowledge detection | K5 | Deterministic assertions for the explicitly qualified mechanical subset | Automatic detection of all concepts, strategic interpretation |
| Participant evidence | M5, `evidence/` | Raw/frozen participant responses, timing/exposure/capture provenance | Objective chess truth, recurring weakness claims |
| Learning inference | M6–M7/M7C, `learning/` | Position-local discrepancy, participant-specific hypotheses, contradiction/challenge/recurrence evidence | Causal cognitive mechanisms, permanent traits |
| Learner knowledge projection | K7 | Descriptive attachment of exact ontology assertions to already-classified M7C recurrence units | Recurrence classification, M7 mutation, causal learner traits |
| Tutor state | M8/M13/M21/M23 | Controlled state transitions, authorization/consent binding, replayable persistence | Automatic diagnosis or training selection |
| Training/outcomes | M9–M11 | Applicability-driven interventions, bounded outcome/transfer evidence, longitudinal state | Intervention causality, automatic mastery |
| Presentation | M15 | Deterministic projection of exact qualified chess evidence | New chess semantics or model interpretation |
| Deterministic feedback | M16 | Exact session-local factual mentor grounding | Arbitrary generative prose, pedagogical optimality |
| Model language | M19 | Request/model provenance for generated language | Semantic truth or safety of arbitrary prose |
| Model ontology sidecar | K6 | Exact ontology context plus binding to one unchanged valid M19 request | M19 schema/identity change, new M16 factual authority, automatic provider adoption |
| Model evaluation | M20 | Bounded evaluator judgments under a frozen policy | Objective truth, complete model safety proof |
| Execution seam | M24 | Request/endpoint identity, execution provenance, failure classification | Vendor approval, automatic retry policy, credential architecture |
| Review runtime | M25–M30 | Authority-separated review, atomic persistence, mechanical verification, deterministic rendering/navigation | Authentication, privacy approval, production UI quality |
| Consumer delivery | M32 | Exact machine-readable review delivery fidelity | Browser/device/a11y/usability correctness |
| Deterministic trace | M33 | Component-level M16 source traceability | Model/evaluator truth, pedagogy |
| Recovery reconciliation | M34 | Hermetic classification of supplied synthetic retry histories against persisted targets | Retry authorization/execution, external-side-effect idempotency |
| Local durability | `storage/` | Immutable artifacts, dependency verification, replay/rebuild support | Independent reinterpretation of domain claims |

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

### 3.2 Concept definition is not concept assertion is not learner inference

K0–K3 define a shared semantic vocabulary. K4 assertions say that a registered
concept applies, does not apply, or is otherwise supported within an explicit claim
scope and authority. Neither step establishes what a participant perceived or a
recurring learner pattern.

```text
registered concept
!=
asserted concept occurrence
!=
participant perception
!=
learner hypothesis
```

### 3.3 Registry coverage is not detector coverage

K5 automatically detects only the exact mechanical subset for which operational
semantics and near-miss rejection behavior have been qualified. A concept may be
registered for human/model/external use while remaining intentionally undetected.

External taxonomy tags also remain external authority even when the external label
maps exactly to an internal concept ID.

### 3.4 Strategic semantics do not become engine semantics

Strategic principles and qualitative evaluation factors are explanatory vocabulary.
They do not decompose a Stockfish score, and a candidate plan is neither a proven
best move nor an M9 training intervention.

### 3.5 M7C remains recurrence authority

K7 consumes an exact M7C hypothesis assessment and attaches position-level ontology
assertions to its recurrence units. It copies each source relation exactly:

```text
supports
contradicts
successful_counterexample
context_exception
unclear
mixed
```

Ontology presence does not classify recurrence. The same concept may legitimately
occur in both supporting and contradictory units. Missing K7 coverage means missing
ontology evidence, not concept absence.

### 3.6 K6 does not modify M19 authority

K6 validates an existing M19 request, constructs a separate ontology context, and
binds the two by exact ID/fingerprint. The M19 request itself is not extended or
refingerprinted.

```text
M19 request identity
+
K6 ontology context identity
-> K6 sidecar binding

sidecar binding != new M19 request identity
sidecar context != M16 deterministic authority
```

### 3.7 Position-local discrepancy is not a stable trait

M6 stays position-local. M7/M7C may accumulate participant-specific evidence across
contexts, but recurrence remains descriptive evidence rather than a causal
psychological mechanism.

### 3.8 Participant selection and evidence-capture consent are separate

M21/M23 require explicit candidate selection and explicit capture consent. One may
not be inferred from the other.

### 3.9 Information sequencing is part of correctness

M5/M8 pre-reveal capture is meaningful only when objective analysis/diagnostic
rationale has not already contaminated the intended measurement stage. Repository
qualification cannot prove a future frontend displayed information in the correct
order.

### 3.10 Presentation must preserve engine semantics

M15 and downstream consumer surfaces preserve White versus decision-mover
perspective, symbolic mate, exact/bounded scores, partial/unavailable/failure states,
child-analysis status, compatibility state, and exact source identity. Consumers do
not get to invent new score semantics.

### 3.11 M16 is the deterministic factual grounding ceiling

M16 is deterministic and bound to exact M15/M6 plus optional complete active-current
M7 evidence. M19 and K6 may consume that grounding, but downstream model-authored
prose does not inherit M16's authority.

### 3.12 Evaluator acceptance is bounded judgment, not truth

M20 can say `pass`, `fail`, or `unclear` under its policy. It cannot promote its
result into objective chess evidence or prove pedagogical effectiveness.

### 3.13 Persistence is append-oriented and replay-verifiable

Important session/review artifacts are immutable/content-addressed or append-only
where defined. Mutating workflows verify prior state and persist successor evidence
rather than silently rewriting history.

### 3.14 Review, delivery, trace, and recovery keep their claim ceilings

M27 proves mechanical execution consistency, M32 exact consumer semantics, M33
component-level deterministic provenance, and M34 supplied-history recovery
consistency. None establishes arbitrary model truth, production UI quality, retry
authority, or pedagogical efficacy.

## 4. Current operational surfaces

Installed commands remain:

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

M31–M34 and K0–K7 remain Python API / hermetic qualification surfaces. The ontology
program introduces no production CLI command.

The installed operator path is intentionally local/reference-oriented. Participant
scoping is not authentication; the static review surface is not a production UI;
application-supplied provider adapters are not a repository-selected vendor stack.

## 5. Persistence and provenance model

The repository strongly prefers explicit references and fingerprints over inference
from rendered text.

K4 extends that rule to chess semantics: every knowledge assertion identifies its
exact concept fingerprint, ontology fingerprint, subject, evidence refs, provenance,
authority class, qualifiers, claim scope, and time.

K6 binds exact M19 request identity beside exact ontology-context identity. K7 binds
exact M7C assessment identity beside exact ontology assertion bundles. Neither
consumer bridge infers authority from prose.

Cross-layer consumers should use exact artifact identity, declared source pointers,
schema versions, participant scope, content fingerprints, and replay/rebuild
validation where available.

## 6. Optional versus mandatory downstream layers

The architecture deliberately avoids forcing every run through every layer.

Examples:

- engine analysis may exist without participant evidence or ontology assertions;
- an ontology concept may be registered without an automatic detector;
- K4 assertions may exist without K6 or K7 projection;
- a participant-authorized tutor session may exist without M19 model prose;
- K6 is adopted only by an explicit model consumer and does not modify existing M19
  provider paths;
- K7 may cover only a subset of M7C recurrence units and reports uncovered units
  explicitly;
- M20 evaluation is not required to make M16 factual grounding valid;
- M31/M34 remain optional qualification/reconciliation surfaces;
- training and longitudinal mutation remain explicit downstream decisions rather
  than automatic consequences of analysis, ontology, or coaching.

This prevents one orchestration or semantic layer from becoming an accidental god
object.

## 7. Current productization boundary

The repository has strong local contracts and qualification but intentionally stops
short of claiming a production end-user system.

Not yet established:

- hosted authentication/authorization or multi-user tenancy;
- production database/retention architecture;
- production LLM/evaluator vendor selection and credential transport;
- automatic retry/backoff/rate-limit policy or external-side-effect idempotency;
- production privacy/security approval;
- browser/device correctness, accessibility, localization, or usability;
- semantic safety/correctness of arbitrary model prose;
- complete automatic detection of the ontology vocabulary;
- causal learner traits or automatic hypothesis mutation from ontology evidence;
- automatic/optimal intervention selection from ontology pedagogy metadata;
- empirical tutoring efficacy, transfer, mastery, or intervention-caused improvement.

These are explicit external/human/product authority gates, not omissions lower-level
artifacts may silently paper over.

## 8. Architecture evolution policy

Future work should begin from live `main` and the current build-status authority.
Recommendations in `STATUS.md` or the build plan remain candidate work until a fresh
bounded package queue is approved.

The ontology foundation now enables product-facing work without requiring another
large semantic-infrastructure phase. Likely next architecture questions are:

1. a deterministic participant learner-state read model that can optionally consume
   K7 concept context while preserving M7/M9/M10/M11 authority;
2. hypothesis-evidence synthesis and contradiction search that reuse M7C rather than
   creating a parallel recurrence engine;
3. explicit teaching-priority/intervention-matching policies that may use ontology
   principles/plans/pedagogy metadata without silently inheriting M9 authority;
4. operator exposure when a concrete consumer needs M32/M33 or ontology read models;
5. external frontend/provider/privacy/security/usability/efficacy adoption only when
   the corresponding real authority gates can be exercised.

New infrastructure should increasingly be pulled by one of those concrete product
needs rather than built speculatively.
