# Chess Mentor Engine context

> **Current implementation authority:**
> [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
>  
> **Latest repository handoff:** [`STATUS.md`](STATUS.md)  
> **Repository overview:** [`README.md`](README.md)  
> **Architecture map:**
> [`docs/architecture/architecture.md`](docs/architecture/architecture.md)

## Product and authority

Chess Mentor Engine is a persistent chess-learning system intended to convert
objective chess evidence into individualized teaching decisions without collapsing
chess truth, chess-knowledge semantics, participant self-report, learner inference,
tutoring, deterministic feedback, model-authored language, model-output evaluation,
review mechanics, and pedagogy into one authority layer.

The central questions remain distinct:

```text
What is objectively happening on the board?
Which registered chess concepts describe that evidence, and under what authority?
What did the player actually notice, consider, and expect?
What participant-specific explanation is currently supported strongly enough to affect teaching?
What did deterministic grounding say versus what a model rendered?
What execution/review mechanics were verified versus what still requires human/external authority?
What later evidence supports practice success, transfer, or longitudinal change?
```

Learner-model conclusions remain bounded product hypotheses, not claims that the
system has established causal cognitive mechanisms.

## Current implementation boundary

The numbered milestone sequence is qualified through **M34 — Hermetic
Reviewed-Coaching Recovery Reconciliation**. On top of M34, the repository now also
has a separately labeled, qualified **Chess Knowledge Ontology program K0–K7**.

The K labels do not consume the provisional M35+ labels in the product build plan.
Use `docs/product/repository-build-status.md` for the moving implementation boundary,
`STATUS.md` for the latest handoff,
`docs/runbooks/chess-knowledge-ontology-program.md` for the ontology restart path,
and `docs/runbooks/m32-m34-milestone-runbook.md` for the previous numbered milestone.

### Capability sequence

- **M1–M4:** canonical PGN/game/position provenance, deterministic chess
  context/features, normalized UCI evidence, objective played-decision comparison,
  and bounded diagnostic selection.
- **M5–M7:** frozen participant decision evidence, position-local discrepancy facts
  and assessments, participant-specific learner hypotheses, contradiction/challenge
  evidence, recurrence policies, and append-only hypothesis lifecycle.
- **M8–M11:** controlled evidence-aware tutoring, explicit intervention
  applicability/selection, bounded practice/transfer evidence, and append-only
  longitudinal learner state.
- **M12–M18:** local evidence/artifact inspection, replay-verified persistent tutor
  transitions, engine-backed analysis, deterministic evaluation presentation,
  grounded mentor feedback, analysis-to-presentation bridging, and diagnostic move
  analysis queues.
- **M19–M22:** provider-neutral model-language rendering, bounded model-output
  evaluation, participant-authorized candidate-to-tutor launch, and hermetic
  cross-layer fidelity qualification.
- **M23–M27:** installed diagnostic-to-persistent-tutor bridging, provider/evaluator
  execution conformance, authority-separated coach review, persistent reviewed
  coaching, and a mechanically verified execution ledger.
- **M28–M31:** deterministic local review rendering, persisted-review bridging,
  participant-scoped package/navigation/export, and hermetic synthetic-canary/manual
  retry-history preflight.
- **M32–M34:** exact machine-consumer review delivery, deterministic M16 feedback
  tracing, and hermetic reviewed-coaching recovery reconciliation.
- **K0–K3:** ontology authority, strict registry/validation, stable concept IDs,
  tactical/Lichess crosswalks, position features, strategic principles, qualitative
  evaluation factors, candidate plans, and pedagogy metadata.
- **K4–K5:** provenance-bound knowledge assertions plus conservative deterministic
  detectors for a deliberately narrow mechanical subset.
- **K6:** model-consumable ontology context bound beside an unchanged M19 request.
- **K7:** typed ontology projection over existing M7C recurrence units while
  preserving M7C support/contradiction relations exactly.

## Current operational path

The principal product path remains:

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound engine evidence
-> objective played-decision comparison / bounded diagnostic selection
-> M15 deterministic evaluation presentation
-> M18 diagnostic candidate batch
-> explicit participant candidate selection + separate capture consent
-> M23 cme-candidate-tutor
-> M21 authorization / launch
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
-> explicit M9 training applicability / selection
-> M10 outcome / transfer evidence
-> append-only M11 longitudinal learner state
```

The ontology is a cross-cutting semantic layer:

```text
canonical chess subject
-> K0–K3 concept definition / registry
-> optional K4 assertion
-> optional K5 deterministic detector

K4 assertion bundle
   +--> K6 model sidecar + exact unchanged M19 request
   +--> K7 learner projection + exact existing M7C assessment
```

Not every application invokes every optional layer. Every arrow remains an authority
boundary.

## Separation of responsibilities

### Objective chess authority

`chess/`, M3 engine evidence, M4 comparison/selection, and M15 presentation own
canonical board state, legal actions, exact source provenance, qualified low-level
features, normalized engine judgments, and score/perspective semantics. Mate,
bounds, partial results, unavailable states, terminal states, and compatibility
states are preserved rather than coerced into fake precision.

Objective chess authority does not establish player cognition, learner traits, or
pedagogical effectiveness.

### Chess-knowledge definition authority

K0–K3 own the registered vocabulary: stable concept identity, human-readable
semantics, hierarchy/relationships, external crosswalks, detector-support metadata,
authority ceilings, and pedagogy metadata.

A concept definition is not an assertion that the concept occurs in a position.
Registry membership is not detector availability. A strategic principle is not an
engine-score component, and a candidate plan is not a best move or an M9 training
intervention.

### Chess-knowledge assertion authority

K4 represents bounded claims against exact position/move subjects with explicit
status, authority class, evidence refs, provenance, qualifiers, ontology fingerprint,
claim scope, and content-addressed identity.

Deterministic facts, engine-derived claims, external taxonomy tags, heuristic
assessments, model interpretations, and human ratifications remain different
assertion authorities.

An assertion remains chess-content evidence. It does not establish what a
participant perceived and does not directly create a learner hypothesis.

### Deterministic ontology detector authority

K5 may assert only its explicitly qualified mechanical subset. Position detectors
cover check/checkmate, absolute pin, bishop pair, open/semi-open files,
isolated/doubled/passed pawns, and pawn islands. Move-transition detectors cover
promotion/underpromotion, moved-piece fork, discovered check, and double check.

Do not infer that other registered tactics, principles, evaluation factors, or plans
are automatically detected. Extending detector scope requires exact semantics and
positive plus near-miss/rejection qualification.

### Diagnostic-selection authority

M4 owns explicit versioned selection policy and deterministic candidate/control
batching. M18 orchestrates that policy over a selected game interval. Neither M18
nor M23 silently selects a candidate for the participant.

### Participant-authorization authority

M21 records candidate selection and capture consent as distinct participant
decisions. M23 operationalizes and persists that exact contract. Candidate selection
is never evidence-capture consent.

### Participant-evidence authority

M5 raw/frozen player responses and exposure state remain distinct from engine and
ontology evidence. Diagnostic rationale revealed before capture may contaminate the
pre-reveal measurement boundary; repository qualification does not prove what a
future UI displayed at a given moment.

### Learning-inference authority

M6 describes position-local discrepancies. M7/M7C represents bounded
participant-specific recurring hypotheses with support, contradiction, challenge,
provenance, recurrence policy, and lifecycle. Recurrence is not a causal cognitive
mechanism, permanent trait, or automatic training eligibility decision.

K7 does not replace M7C. It attaches exact ontology assertions to already-classified
M7C recurrence units and preserves the source relation verbatim. The same concept may
occur in both supporting and contradictory units.

### Tutor-state authority

M8 owns controlled capture/freeze/reveal/comparison/explanation transitions. M13
persists and replay-verifies those transitions. Completing or comparing an M8
session does not automatically mutate M7/M11 or select M9 training.

### Training/outcome authority

M9 selects interventions only through explicit applicability rules. M10 records
predeclared bounded outcome/transfer evidence. Practice completion, successful
performance, near transfer, far transfer, real-game transfer, causality, and mastery
remain separate claims. M11 derives longitudinal learner state from exact current
hypothesis revisions and eligible evidence.

Ontology pedagogy metadata may inform future policy design but does not itself grant
M9 applicability or selection authority.

### Deterministic feedback authority

M16 composes deterministic session-local mentor feedback from exact M15/M6 and
optional complete active-current M7 evidence. It does not invoke a model and remains
the deterministic factual grounding ceiling.

### Model-language authority

M19 may ask an application-supplied provider to render prose from the exact M16
request. Provenance establishes which request reached which model run; it does not
establish semantic correctness, safety, or pedagogical effectiveness.

K6 adds an optional sidecar. It validates and references an existing M19 request by
exact identity; it does not insert keys into or refingerprint that request. The
sidecar provides registered definitions, assertion authority, qualifiers,
relationships, and anti-promotion instructions to an explicitly adopting consumer.

### Model-output evaluation authority

M20 records bounded `pass` / `fail` / `unclear` judgments under a frozen evaluation
policy. M20 acceptance is not objective chess truth and does not turn evaluator
rationale into deterministic evidence.

### Execution-conformance authority

M24 classifies one application-owned provider/evaluator adapter invocation, binds
endpoint/request identity, and records deterministic execution provenance.
Production vendor selection, automatic retry/backoff policy, credentials, privacy
approval, cost controls, and latency SLOs remain external decisions.

M31 can validate synthetic canaries and already-supplied manual retry histories. It
never executes a retry and accepts only test canary material.

### Persistence/review authority

M25 assembles an authority-separated coach-review read model. M26 atomically persists
reviewed-coaching outputs without advancing M8. M27 mechanically verifies the exact
persisted execution chain. M28 deterministically renders M25. M29 resolves persisted
review chains. M30 provides participant-scoped navigation/export.

Participant scoping is an integrity boundary, not hosted authentication.

### Consumer-delivery and trace authority

M32 preserves exact machine-consumer semantics. M33 traces every substantive M16
component back to exact deterministic source authority. Neither establishes browser
quality, semantic truth of arbitrary model prose, or pedagogical efficacy.

### Recovery-reconciliation authority

M34 classifies supplied synthetic M24 multi-attempt histories against one
already-persisted mechanically verified M26 target as `complete` or
`resume_eligible`. It never executes or authorizes retry and does not establish
external-side-effect idempotency or production recovery correctness.

## Contracts contributors must preserve

```text
objective chess truth != participant self-report != learner inference
concept definition != concept assertion != learner inference
registered concept != automatically detectable concept
external taxonomy tag != deterministic CME detector result
ontology concept presence != M7C hypothesis relation
K7 descriptive projection != recurrence reclassification or learner mutation
K6 ontology sidecar != M19 request identity or M16 factual authority
heuristic principle != engine-evaluation decomposition
strategic plan != best move != M9 training intervention
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
engine analysis != evaluation presentation != grounded feedback != model coaching
M16 deterministic grounding != M19 model prose
request provenance != semantic correctness of model prose
M20 evaluator acceptance != objective chess truth
participant candidate selection != capture consent
M23 operator/persistence != M6/M7/M9 authority
M24 execution conformance != vendor approval or retry authority
M27 mechanically_verified != semantic truth
M30 participant navigation != authentication or privacy approval
M32 machine-consumer fidelity != production UI quality or model truth
M33 deterministic traceability != model/evaluator authority
M34 resume eligibility != retry authorization, execution, or side-effect idempotency
```

## CLI and API boundaries

Installed commands remain:

```text
cme
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

The `cme` command exposes game/position inspection, bounded engine analysis,
diagnostic queue construction, artifact inspection, and persistent tutor actions.
K0–K7 introduce no production CLI command. Their public Python API is exposed under
`chess_mentor_engine.chess_knowledge` and documented in
`docs/runbooks/chess-knowledge-ontology-program.md`.

## Productization boundary

The repository still stops short of claiming:

- hosted authentication/authorization or multi-user tenancy;
- production database/retention architecture;
- production LLM/evaluator vendor selection and credential transport;
- automatic retry/backoff/rate-limit policy or external-side-effect idempotency;
- production privacy/security approval;
- browser/device correctness, accessibility, localization, or usability;
- semantic safety/correctness of arbitrary model prose;
- complete automatic detection of the ontology vocabulary;
- causal learner traits, automatic intervention efficacy, or mastery;
- empirical tutoring efficacy or intervention-caused improvement.

Future work should increasingly be pulled by a concrete learner/tutor/product need,
then add the minimum additional infrastructure required to preserve these authority
boundaries.
