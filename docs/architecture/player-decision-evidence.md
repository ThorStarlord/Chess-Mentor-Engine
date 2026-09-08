# M5 — Player Decision Evidence

## Status

**M5A — Player Decision Evidence contract is frozen. Production implementation has not started.**

M1–M4 remain the qualified upstream objective evidence substrate. This document
freezes the first production boundary for direct player-reported evidence without
promoting self-report into objective chess truth, analyst/model inference, learner
diagnosis, or pedagogy.

M5 crosses an important authority boundary:

```text
objective chess evidence
!= player-reported evidence
!= analyst/model coding
!= learner diagnosis
```

M5 records what the player was shown, what the player reported, when that report was
frozen, and what information the player had been exposed to. M5 does not decide
whether the report is correct, why the player thought it, whether a stable weakness
exists, or what should be taught.

## Upstream boundary

The initial production M5 path is downstream of qualified M4 selection:

```text
DiagnosticCandidate / DiagnosticCandidateBatch
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
optional later-stage prompt / response / freeze
        |
        v
ObjectiveEvidenceReveal
```

For the initial implementation, production Player Decision Evidence must bind to a
qualified canonical position and M4 `DiagnosticCandidate`. Historical research
artifacts remain separate and immutable; they are not retroactively converted into
production M5 records merely because the new schema is compatible with their ideas.

## Authority model

### Objective chess authority

M1–M4 remain authoritative for:

- canonical position identity and FEN;
- legal chess state;
- objective engine evidence;
- decision comparison;
- M4 selection signals, policy, candidate identity, and batch identity.

### Participant authority

The participant is authoritative only for what they explicitly submitted through the
M5 capture surface, for example:

- raw free-text response;
- an explicitly selected move;
- explicitly selected candidate moves;
- explicitly submitted expected reply or continuation;
- stated objective/plan;
- stated uncertainty;
- explicitly submitted confidence.

A participant report is evidence about the participant's report. It is not objective
chess truth.

### Deterministic application authority

Deterministic application logic may own:

- stage identity and ordering;
- prompt/version identity;
- canonical position/candidate linkage;
- timestamps and freeze/reveal events;
- immutable fingerprints;
- exact structured fields directly submitted by the participant;
- deterministic normalization when a structured interaction makes the meaning
  unambiguous, such as a board-click move converted to UCI.

Deterministic normalization does not make the response correct.

### Analyst/model coding

Any structure inferred from free text rather than explicitly submitted by the
participant is separate `ANALYST_CODING` or later model coding. It must cite the raw
response it was derived from and must never overwrite participant evidence.

Examples include:

- extracting an implied candidate move from prose;
- inferring that a sentence expresses a plan;
- assigning a reasoning-process code;
- deciding that a reply changed between stages when the participant did not explicitly
  state the change;
- interpreting uncertainty or confidence from tone.

Initial M5 production implementation does not need to implement analyst/model coding.
The contract freezes the separation so later layers cannot silently collapse it.

## Core records

The exact Python names may evolve during implementation, but the following semantic
records are frozen.

### `PlayerDecisionContext`

Binds one evidence-gathering attempt to its upstream objective context.

Conceptually:

```yaml
context_id:
participant_id:
session_id:
position_id:
game_id:
diagnostic_candidate_id:
diagnostic_batch_id: optional
position_context_packet_ref:
selection_policy_ref:
created_at:
```

`participant_id` is an application identity, not a cognitive profile. The initial
implementation should use pseudonymous/stable application identifiers rather than
embedding unnecessary personally identifying data into evidence fingerprints.

### `PromptDefinition`

A versioned definition of a prompt or prompt set.

Conceptually:

```yaml
prompt_definition_id:
name:
version:
stage_kind:
content:
response_schema:
provenance:
```

Prompt content is evidence provenance. Changing wording, question order, response
constraints, or structured response fields creates a new prompt-definition identity
or version.

The frozen Pilot 003/004 instruments remain research definitions. Production may
reference an equivalent frozen prompt definition when intentionally reproducing that
instrument, but the Pilot wording is not universal product truth.

### `PromptPresentation`

Records what was actually shown to a participant.

Conceptually:

```yaml
presentation_id:
context_id:
stage_id:
prompt_definition_id:
position_packet_ref:
shown_at:
rendered_content_fingerprint:
information_available_before_presentation:
```

The presentation record must be sufficient to audit whether later-stage information,
engine evidence, selection rationale, or hints were available before a response was
frozen.

### `PlayerResponseEvidence`

Immutable participant-authored evidence for one presentation.

Conceptually:

```yaml
response_id:
context_id:
stage_id:
presentation_id:
participant_id:
raw_response:
structured_response: optional
submitted_at:
frozen_at:
response_fingerprint:
```

`raw_response` preserves the participant's original language exactly when free text is
used.

`structured_response` contains only values the participant explicitly submitted
through structured controls. It must not contain values extracted from prose by an
analyst or model.

### `ExposureEvent`

Records information exposure relevant to interpreting the evidence state.

Conceptually:

```yaml
exposure_event_id:
context_id:
participant_id:
kind:
occurred_at:
source:
details:
```

Initial kinds should be able to represent at least:

```text
POSITION_CONTEXT_SHOWN
LATER_STAGE_PROMPT_SHOWN
ENGINE_EVIDENCE_SHOWN
SELECTION_RATIONALE_SHOWN
EXPECTED_DISCREPANCY_SHOWN
PRIOR_REPORT_SHOWN
EXTERNAL_ANALYSIS_REPORTED
FACILITATOR_HINT
INSTRUMENT_AWARENESS_RECORDED
OTHER
```

Exposure events are provenance. M5 may preserve an operator-supplied awareness state
such as `known_aware`, `known_unaware`, or `unknown`, but it must not infer probe-naive
cognition merely because an A1/minimal prompt was used.

### `EvidenceFreeze`

Freezing is a first-class event, not a mutable boolean casually flipped on a response.

Conceptually:

```yaml
freeze_id:
context_id:
stage_id:
response_id:
frozen_at:
response_fingerprint:
```

After freeze, the response content is immutable. Corrections or clarifications are
append-only new records that cite the original response/freeze; they do not replace
it.

### `ObjectiveEvidenceReveal`

Records when objective chess/engine evidence became available to the participant.

Conceptually:

```yaml
reveal_id:
context_id:
revealed_at:
position_analysis_refs:
decision_comparison_ref:
selection_signal_refs:
rendered_content_fingerprint:
```

The initial pre-engine evidence states require all relevant participant response
stages to be frozen before this reveal.

## Stage model

M5 distinguishes evidence stage from prompt wording.

The initial stage kinds are:

```text
MINIMAL_RESPONSE
STANDARDIZED_PROBE
POST_REVEAL_REFLECTION
ORIGINAL_GAME_RECOLLECTION
```

Only the first two are required for Pilot-003-style two-stage elicitation. The initial
production implementation may support a minimal-only capture path or a minimal+probe
path, but it must never merge their responses into one mutable narrative.

### Minimal response

A minimal-response stage is intended to capture what the participant chooses to report
under the corresponding prompt definition.

It must not automatically be labeled `spontaneous cognition` or `probe-naive
reasoning`. Pilot 004 demonstrates why: an instrument-aware participant can answer a
minimal prompt while already knowing the later instrument.

### Standardized probe

A standardized-probe stage is separate evidence collected after the minimal response
has been frozen and before objective evidence reveal.

For a clean reproduction of Pilot 003, the exact six frozen questions and their order
must be represented by one versioned prompt definition. Production may later evaluate
other prompt definitions, but changing the questions is a new instrument version, not
an invisible implementation detail.

### Post-reveal reflection

Post-reveal reflection is valid evidence but has a different epistemic status because
objective chess evidence is already known. It must never overwrite or be merged into
pre-reveal evidence.

### Original-game recollection

A recollection of what the participant remembers thinking during the historical game
is distinct from a fresh-position decision response. Memory after the game is not the
same evidence as contemporaneous reasoning.

## State sequence

The canonical clean two-stage sequence is:

```text
A0 decision context prepared
→ A1 minimal prompt presented
→ A1 response submitted
→ A1 frozen
→ A2 standardized probe presented
→ A2 responses submitted
→ A2 frozen
→ E objective evidence revealed
```

M5 must reject or explicitly mark invalid/contaminated sequences such as:

```text
engine reveal before A1 freeze
engine reveal between A1 and A2 in a protocol requiring both pre-engine
A2 prompt shown before A1 freeze in a clean two-stage run
response mutation after freeze
later-stage response written into an earlier stage
```

The application may preserve a deviating sequence as evidence with explicit exposure
and deviation provenance. It must not erase the data merely because the sequence was
contaminated.

## Research compatibility

M5A is informed by, but does not rewrite, the frozen research instruments.

### Pilot 003 compatibility

Pilot 003 freezes:

```text
A0 position state
→ A1 Stage A response frozen
→ A2 Stage B response frozen
→ E engine/objective evidence revealed
```

Its Stage A prompt is:

> What do you think about this position, and what would you play?

Its Stage B instrument asks the same six questions in the same order for every
position, covering additional candidates, strongest opponent reply, expected
continuation, objective, uncertainty, and confidence.

Production M5 can represent this exactly through versioned prompt definitions and
separate immutable response stages.

### Pilot 004 compatibility

Pilot 004 intentionally uses an instrument-aware P01. Therefore M5 freezes the rule:

```text
minimal prompt
!= proof of probe-naive cognition
```

Instrument awareness and other relevant prior exposure belong to provenance.

### No retroactive migration

M5A does not mutate Pilot 001–004 files, exposure classifications, participant records,
checksums, or outcomes. A later explicit import/adaptation task may map historical
research evidence into a production-compatible export, but such a mapping must retain
original provenance and may not pretend the historical records were captured by the
production M5 runtime.

## Prompt leakage and information boundary

Before a pre-engine stage is frozen, the participant-facing surface must not expose
information prohibited by that stage's protocol.

For a Pilot-003-style clean run, this includes:

- later-stage probe questions before A1 freeze;
- engine answers;
- internal candidate/control classifications;
- selection rationale;
- expected discrepancy or learner hypothesis;
- chess hints or heuristics not included in the frozen prompt definition.

The boundary applies to UI text, filenames, headings, generated summaries, status
messages, notifications, and operator-facing automation that may become visible to the
participant.

## Observation, probing, and tutoring are distinct

M5 preserves these as different interaction classes:

```text
observation
!= diagnostic probing
!= tutoring intervention
```

A probe may change the participant's move, candidates, plan, reply expectation, or
confidence. That change is valid evidence about the effect of the probe. It is not
silently treated as contamination or as proof that the probe is pedagogically useful.

Prompts that teach a solving heuristic, name a tactical motif, direct attention to a
piece/square, strongly imply the answer is wrong, or prescribe a training routine are
outside the initial measurement contract and should be recorded as intervention-like
exposure/deviation if encountered.

## Player-reported move semantics

M5 must distinguish:

```text
player reported move
!= canonical historical played move
!= engine best move
```

A structured board-click move can be deterministically normalized to UCI because the
participant directly chose a concrete move on a known position. A move mentioned in
free text may be ambiguous. If normalization is not unambiguous, preserve the raw text
and an explicit unresolved state rather than guessing.

Move legality may be checked deterministically, but an illegal reported move remains
player evidence. It should be marked `illegal_for_position` or equivalent; it must not
be silently corrected into a legal move.

## Decision-change evidence

When multiple pre-reveal stages exist, M5 may record an explicit stage-change record
for fields directly submitted by the participant, for example:

```text
reported move changed
explicit candidate set changed
expected reply changed
expected continuation changed
stated objective/plan changed
confidence changed
```

If the change has to be inferred from free text, the derived comparison is
`ANALYST_CODING`, not participant truth.

A changed answer remains valid evidence. It is not an error to erase.

## Identity and immutability

Stable fingerprints must bind at least:

```text
canonical position/context identity
participant/session identity
stage identity
prompt definition/version
rendered prompt fingerprint
raw/structured response content
submission/freeze provenance
relevant exposure state
```

The exact fingerprint decomposition will be fixed during M5B implementation, but these
inputs may not be omitted if doing so would allow materially different evidence to
share one identity.

Frozen response content is append-only. Later coding, normalization, disagreement,
objective reveal, diagnosis, or pedagogy must create downstream records rather than
mutating the original response.

## What M5 may claim

A qualified M5 may eventually claim only that Chess Mentor Engine can capture and
preserve provenance-rich player decision evidence tied to a canonical selected
position, including stage, prompt, response, freeze, timing, and information-exposure
state.

M5 may report facts such as:

- the participant explicitly chose move X in this stage;
- the participant explicitly listed candidates A/B/C;
- the participant stated reply Y or plan Z;
- confidence was explicitly submitted as 3/5;
- the response was frozen before objective evidence reveal;
- a later probe preceded a changed submitted move;
- engine evidence had already been exposed before a later reflection.

## Claims prohibited in M5

M5 must not claim:

- the participant's reasoning was objectively correct merely because they reported it;
- an omitted move was never considered;
- a reported explanation is the causal reason the move was chosen;
- `poor calculation`, `tunnel vision`, `missed opponent resource`, `bad planning`, or
  another Reasoning Discrepancy;
- recurrence or stable learner weakness;
- that a control contradicts a learner hypothesis;
- that a selected position is pedagogically valuable;
- that probing or tutoring caused learning;
- transfer or mastery.

These require M6+ or research-specific analysis under separate claim ceilings.

## Initial implementation sequence

### M5A — contract freeze

This document and ADR 0004 freeze the Player Decision Evidence boundary.

Status after M5A:

> **M5A CONTRACT FROZEN — PRODUCTION IMPLEMENTATION NOT STARTED**

### M5B — immutable evidence model

Implement only the data model and deterministic identity/serialization layer for:

- `PlayerDecisionContext`;
- `PromptDefinition`;
- `PromptPresentation`;
- `PlayerResponseEvidence`;
- `ExposureEvent`;
- `EvidenceFreeze`;
- `ObjectiveEvidenceReveal`.

No interactive session state machine yet.

### M5C — capture/freeze state machine

Implement stage ordering, presentation/capture/freeze transitions, reveal gating,
append-only amendments, and explicit deviation/exposure handling.

Do not implement Reasoning Discrepancy.

### M5Q — full M5 qualification

Qualify the complete capture path against deterministic fixtures including clean,
instrument-aware, contaminated, amended, ambiguous-move, illegal-move, minimal-only,
two-stage, and post-reveal cases.

M6 is unauthorized until M5Q passes.

## Qualification gates

M5 may be declared qualified only when all applicable gates pass:

```text
raw participant response preserved verbatim
structured participant input separated from inferred coding
prompt definition/version provenance preserved
position/candidate provenance preserved
stage ordering deterministic and auditable
A1/A2 or equivalent pre-reveal stages remain separate
freeze is immutable and append-only
objective reveal cannot silently precede required pre-engine freezes
exposure/instrument-awareness provenance preserved
illegal/ambiguous reported moves are not silently corrected
deviations/contamination are preserved rather than erased
post-reveal reflection remains epistemically separate
historical research artifacts remain unchanged
no Reasoning Discrepancy or learner diagnosis
no pedagogical-effectiveness claim
pytest passes
Ruff passes
exact candidate-head CI passes
post-merge CI passes
```

## Explicitly deferred

M5A does not implement or freeze:

- Reasoning Discrepancy taxonomy (M6);
- recurrence or learner hypotheses (M7);
- LLM interpretation of participant free text;
- automatic cognitive-trait extraction;
- tutoring dialogue or Socratic intervention logic;
- pedagogical ranking;
- training assignment;
- transfer/mastery;
- persistent learner state;
- UI design beyond the information-boundary requirements needed for evidence validity.

## Governing principle

> Player self-report is evidence about what the player reported under a specific
> information state. Preserve that evidence before trying to explain it.
