# M44 — Learner Progress Reference Surface

## Purpose

M44 makes the qualified learner-intelligence chain inspectable without creating a new
learner, chess, pedagogical, or execution authority.

The local reference experience answers:

```text
What does CME currently represent about this participant?
Why is a learner hypothesis at its current status?
What evidence supports or challenges it?
Which chess concepts are involved?
What training / transfer state is currently recorded?
What remains uncertain and what could change the assessment?
What does M40 propose next?
What M43 challenge/control candidates or M41 training candidates were supplied?
```

M44 is deliberately a repository-local reference surface, not a production frontend.

## Composition chain

```text
M36 current learner-state read model
        +
M39 exact evidence syntheses
        +
M40 ranked next-session plan
        +
optional M43 evidence-acquisition plans
        +
optional M41 intervention candidate sets
        +
exact ontology snapshot for display semantics
        |
        v
m44.learner-progress-view.v1
        |
        v
m44.learner-progress-reference-surface.v1
```

The presentation model is separated from HTML rendering. The renderer consumes an
already-built content-addressed view and has no inference or selection logic.

## Source validation

M44 fails closed unless:

- M36 and M40 identify the same participant and exact read model;
- the supplied M39 synthesis set exactly matches the synthesis refs frozen into M40;
- every M39 synthesis matches its current M36 hypothesis revision, statement, scope,
  participant, and read-model identity;
- every optional M43 plan binds the same exact M40 plan/proposal/current revision;
- every optional M41 set binds the same exact M40 plan/proposal/current revision;
- every M41 set binds the exact ontology fingerprint supplied to M44;
- optional M43/M41 inputs are unique per hypothesis.

Extra or missing M39 records are rejected rather than silently changing the learner
story presented by the view.

## Hypothesis presentation model

Each `LearnerProgressHypothesis` preserves:

- exact current hypothesis revision;
- M40 priority rank and next action, when present;
- M36 statement, scope, lifecycle, M9 state, and M10 outcome dimensions;
- M39 status reasons, evidence counts, traceable recurrence units, evidence gaps, and
  change conditions;
- ontology concept IDs, preferred names, kinds, and instructional recognition cues;
- optional M43 candidate kinds/source game/source position/semantic coverage;
- optional M41 intervention refs and match statuses;
- M41 unverified prerequisites and matching gaps.

Hypotheses represented by M40 preserve M40 order. Other M36 hypotheses remain visible
but are explicitly unranked by the current M40 plan.

## Authority labels

The rendered reference surface keeps the repository's conceptual separations visible:

```text
objective chess evidence
participant evidence
learner hypothesis / M7C status
ontology chess concept
pedagogical candidate
next-action policy
```

The important invariants remain:

```text
M44 rendering != learner inference
ontology concept != learner weakness
M43 candidate != M7C contradiction
M41 candidate != M9 selection
M40 proposal != execution authorization
M10 evidence state != mastery
```

The view and surface both keep causality/mastery outside their claim ceiling.

## Missing data

Optional layers are rendered as unavailable/not supplied rather than converted into
negative evidence.

Examples:

```text
no M43 plan supplied
!= no contradictory evidence exists

no M41 set supplied
!= no intervention could apply

no ontology context supplied by upstream learner evidence
!= concept absent from the position or learner
```

## Ontology use

M44 resolves stable concept IDs through the exact ontology snapshot supplied by the
caller and renders preferred names plus existing recognition questions.

Recognition questions are visibly instructional cues. They are not presented as proof
that a participant did or did not recognize the concept.

M44 requires no new ontology schema. As with M41, the current K0–K7 semantic substrate
is sufficient for the v1 consumer.

## HTML safety and determinism

The renderer:

- uses static semantic HTML/CSS only;
- escapes all source text before insertion;
- loads no external scripts, fonts, analytics, or network resources;
- has deterministic output for one exact content-addressed M44 view;
- validates the view fingerprint before rendering.

The resulting surface is independently content-addressed from the exact view ref,
rendered HTML, schema, and claim scope.

## Claim ceiling

```text
claim_scope = local_reference_presentation_only
causal_effect = not_established
mastery = not_established
```

M44 does not establish:

- production browser/device/accessibility quality;
- user approval or usability;
- a new learner hypothesis;
- recurrence truth;
- intervention applicability or selection;
- intervention efficacy;
- transfer or mastery;
- permission to execute M40/M43/M41 proposals.

## Qualification focus

Qualification must cover:

- coherent M36/M39/M40 composition;
- optional M41 and optional M43 composition;
- exact M40 priority ordering;
- explicit missing optional layers;
- HTML escaping of learner/evidence text;
- missing/extra M39 rejection;
- cross-participant M43/M41 rejection;
- deterministic view/surface rebuilds and tamper rejection;
- full repository regressions plus independent Stockfish witness.
