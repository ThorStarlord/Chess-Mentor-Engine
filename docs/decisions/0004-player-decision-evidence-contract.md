# ADR 0004 — Player Decision Evidence Contract

## Status

Accepted for M5A. Production implementation is not authorized by this ADR alone.

## Context

M1 through M4 now provide a qualified objective evidence-acquisition path:

```text
canonical chess state
→ deterministic board features
→ provenance-bound engine evidence
→ objective diagnostic position selection
```

The next milestone crosses from objective chess evidence into direct evidence about
what a player reports thinking at one selected decision point.

That transition creates a new epistemic risk. A player response can be useful without
being objectively correct, complete, causal, or stable. Prompting can also change the
reported decision before engine reveal. If the production system collapses raw player
language, prompt effects, analyst coding, and engine conclusions into one mutable
record, later learner diagnosis will be structurally unreliable.

The repository already contains frozen research instruments that establish useful
measurement boundaries. Pilot 003 separates a minimal spontaneous-response stage from
a standardized probe and freezes both before engine reveal. Pilot 004 demonstrates
that a participant may be instrument-aware, so a minimal prompt cannot automatically
be interpreted as probe-naive cognition.

M5 therefore needs a production evidence contract that preserves those epistemic
boundaries without rewriting the historical research artifacts or treating one pilot
instrument as universal product truth.

## Decision

M5 will capture provenance-rich player decision evidence under this authority split:

```text
objective chess truth
!= participant self-report
!= analyst/model coding
!= learner diagnosis
```

The initial production path is:

```text
DiagnosticCandidate
+ CanonicalPosition / PositionContextPacket
        |
        v
PlayerDecisionContext
        |
        v
PromptPresentation
        |
        v
PlayerResponseEvidence
        |
        v
EvidenceFreeze
        |
        v
optional later pre-reveal stage(s)
        |
        v
ObjectiveEvidenceReveal
```

## Decision 1 — Raw participant evidence is first-class and immutable

Free-text responses are preserved verbatim. Structured values are participant evidence
only when the participant explicitly submitted them through a structured capture
surface.

Values inferred from prose by an analyst or model are separate coding records and
must never overwrite the raw response.

## Decision 2 — Prompt identity is evidence provenance

Prompt wording, question order, stage role, response constraints, and version are part
of the evidence context.

Changing material prompt content creates a new prompt-definition identity/version.
Prompt changes must not be treated as invisible UI copy edits when those changes can
affect what the participant reports.

## Decision 3 — Evidence stages remain separate

The initial stage taxonomy distinguishes at least:

```text
MINIMAL_RESPONSE
STANDARDIZED_PROBE
POST_REVEAL_REFLECTION
ORIGINAL_GAME_RECOLLECTION
```

Responses from different stages are separate records. Later responses must not be
merged backward into earlier evidence.

In particular:

```text
A1 minimal response
!= A2 probed response
!= post-engine reflection
!= recollection of the historical game
```

## Decision 4 — Freeze is a first-class immutable event

A response becomes immutable when frozen. Corrections, clarifications, or amendments
are append-only records that cite the original frozen evidence.

The application must not silently edit a frozen A1 response after A2 or engine reveal.

## Decision 5 — Objective reveal timing is part of evidence validity

For a pre-engine capture protocol, required participant stages must be frozen before
objective chess/engine evidence is revealed.

The system must record the reveal event explicitly. If reveal occurs early, the data
is preserved with deviation/exposure provenance rather than erased or falsely labeled
clean.

## Decision 6 — Exposure and instrument awareness are provenance

M5 records information exposures relevant to interpreting the response, including the
ability to represent:

- position context shown;
- later-stage prompt exposure;
- engine evidence exposure;
- selection-rationale exposure;
- expected-discrepancy or hypothesis exposure;
- prior-report exposure;
- participant-reported external analysis;
- facilitator hints;
- known instrument awareness.

A minimal prompt does not prove probe-naive cognition.

## Decision 7 — Observation, probing, and tutoring are distinct

M5 preserves:

```text
observation
!= diagnostic probing
!= tutoring intervention
```

A probe-induced decision change is valid evidence about the interaction. It is not
silently erased, and it is not proof that the probe is an effective teaching
intervention.

Prompts that teach a chess-solving routine or materially hint at the answer are outside
the clean initial measurement boundary and must be recorded as intervention-like
exposure/deviation if encountered.

## Decision 8 — Player-reported move is not objective move truth

M5 distinguishes:

```text
player-reported move
!= canonical historical played move
!= engine-preferred move
```

A structured board selection may be deterministically normalized to UCI because the
participant directly selected a concrete move on a known position.

Ambiguous free text remains ambiguous. Illegal reported moves remain player evidence
and are marked as such rather than silently corrected.

## Decision 9 — Initial production M5 is bound to qualified M4 selection

The first production M5 implementation requires a qualified canonical position and M4
`DiagnosticCandidate` reference.

Historical Pilot 001–004 records are not retroactively rewritten into production M5
records. A future explicit import/adaptation process may map them while retaining their
original provenance, but it must not pretend they were captured by the production
runtime.

## Decision 10 — Research instruments are compatible references, not universal product truth

The frozen Pilot 003 and Pilot 004 instruments inform the M5 contract.

When production intentionally reproduces Pilot 003, it must be able to preserve:

```text
A0 position state
→ A1 response frozen
→ A2 standardized-probe response frozen
→ E objective evidence reveal
```

and the exact frozen prompt definitions used by that research instrument.

Production may later evaluate other prompt definitions. Such changes require new
prompt identities/versions and their own evidence claims.

## Decision 11 — Stage-change records cannot manufacture participant truth

M5 may deterministically compare fields explicitly submitted by the participant
between stages, such as selected move or numeric confidence.

If a change must be inferred from prose, it is analyst/model coding. It must cite the
underlying response records and remain separate from participant authority.

## Decision 12 — M5 is evidence capture, not Reasoning Discrepancy

M5 may record what the player reported and the exposure/timing conditions under which
they reported it.

M5 must not emit claims such as:

- `poor calculation`;
- `failed candidate generation`;
- `missed opponent resource`;
- `tunnel vision`;
- `bad planning`;
- `weak strategic understanding`;
- `needs tactics training`.

Those claims require M6 or later contracts.

## Decision 13 — M5 claim ceiling

A qualified M5 may eventually claim only that Chess Mentor Engine can capture and
preserve provenance-rich player decision evidence tied to a canonical selected
position, including prompt, stage, raw/structured response, freeze, timing, and
information-exposure state.

It may not claim:

- objective correctness of a reported explanation;
- causal cognitive mechanism;
- stable learner weakness;
- recurrence;
- contradiction of a learner hypothesis;
- pedagogical value;
- intervention efficacy;
- learning, transfer, or mastery.

## Consequences

### Positive

- later discrepancy analysis can cite immutable pre-engine evidence;
- prompt effects are measurable instead of overwritten;
- instrument awareness is explicit rather than guessed;
- raw self-report remains distinguishable from coding;
- post-reveal reflection cannot contaminate earlier evidence silently;
- historical research boundaries remain preserved;
- M6 receives a defensible evidence substrate instead of a summarized narrative.

### Costs

- the evidence model contains more records and timestamps than a simple response blob;
- prompt versioning becomes a product concern;
- contaminated/deviating evidence must be retained and handled explicitly;
- ambiguous free-text moves may remain unresolved;
- append-only correction is more complex than in-place editing;
- production UX must respect information boundaries during evidence collection.

These costs are preferable to manufacturing false certainty about player reasoning.

## Alternatives considered

### Store one mutable `player_reasoning` text field per position

Rejected. It would erase stage order, prompt effects, amendments, freeze state, and
engine-exposure provenance.

### Parse free text immediately into structured cognition fields

Rejected as participant authority. Parsed structure may be useful later as coding, but
must remain downstream of the preserved raw response.

### Treat Pilot 003's instrument as the permanent product prompt

Rejected. It is a frozen research instrument, not yet validated as universal product
interaction design. Production must version prompt definitions explicitly.

### Ignore instrument awareness

Rejected because Pilot 004 intentionally demonstrates a participant can be aware of
the later instrument before a minimal prompt.

### Discard contaminated or deviating responses

Rejected. Preserve the evidence and mark the exposure/deviation; exclusion belongs to
later analysis policy.

### Start M6 discrepancy inference in the same milestone

Rejected. M5 must first prove trustworthy player evidence capture before comparing it
to objective chess demands.

## Implementation sequence authorized by this ADR

This ADR authorizes planning for the following bounded sequence. Each step still
requires implementation qualification:

```text
M5B immutable evidence model
→ M5C capture/freeze state machine
→ M5Q full M5 qualification
```

M6 Reasoning Discrepancy is unauthorized until M5Q is qualified.

## Related records

- `docs/architecture/player-decision-evidence.md`
- `docs/architecture/m4-qualification.md`
- `docs/decisions/0003-diagnostic-position-selection-contract.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-003/pilot-protocol.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-003/reasoning-instrument.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-003/evidence-schema.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-003/information-boundary.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-003/contamination-policy.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-004/pilot-protocol.md`
- `docs/research/first-product-validation/pilots/FPV-PILOT-004/reasoning-instrument.md`
- `docs/product/repository-build-status.md`
