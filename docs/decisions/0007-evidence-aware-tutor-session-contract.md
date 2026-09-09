# ADR 0007 — Evidence-Aware Tutor Session Contract

**Status:** Accepted  
**Milestone:** M8 — Evidence-Aware Tutor Session  
**Scope:** bounded orchestration over already-qualified M4–M7 evidence

## Context

M7 closes the repository's first qualified cross-position learner-hypothesis boundary.
The next product risk is no longer whether the repository can represent objective
chess evidence, player self-report, local discrepancy, or recurrence. The next risk is
whether those authorities can be presented to a player in one controlled interaction
without destroying the very evidence the system is trying to learn from.

A tutor session is therefore an information-sequencing problem before it is a pedagogy
problem.

The desired interaction is:

```text
selected diagnostic position
→ deterministic position presentation
→ minimal participant response
→ optional standardized diagnostic probe
→ immutable freeze of all planned pre-reveal evidence
→ qualified objective evidence reveal
→ exact M6 reasoning comparison
→ optional complete active-current M7 hypothesis context
→ provenance-bearing explanation
→ immutable completed session
```

The central safety/correctness requirement is:

```text
what the participant could know before responding
!= what the tutor may know internally
```

If engine output, discrepancy labels, expected errors, or learner hypotheses leak into
the pre-reveal interaction, the resulting participant evidence is no longer a clean
observation of the original decision process.

## Decision 1 — M8 is orchestration, not a new epistemic authority

M8 does not recompute or reinterpret M4, M5, M6, or M7 evidence.

It may bind and sequence exact qualified records from those layers, but the source
records retain their original authority domains.

```text
M4 objective selection
!= M5 participant evidence
!= M6 local discrepancy
!= M7 descriptive recurrence
!= M8 session orchestration/explanation
```

## Decision 2 — Pre-reveal interaction is observation/probing only

M8 v1 accepts only a pre-reveal `CaptureProtocol` consisting of:

```text
MINIMAL_RESPONSE
```

or:

```text
MINIMAL_RESPONSE
→ STANDARDIZED_PROBE
```

All stages must be `pre_reveal`.

The permitted interaction classes are:

```text
MINIMAL_RESPONSE      → observation
STANDARDIZED_PROBE    → diagnostic_probing
```

`tutoring_intervention` is not permitted before freeze/reveal.

## Decision 3 — Position presentation is deterministic M1 context only

The pre-reveal board presentation is derived from the exact
`PositionContextPacket` already bound into the M5 `PlayerDecisionContext`.

The M8 implementation validates its fingerprint before presentation.

The initial rendered surface may contain deterministic orientation such as:

- move number;
- side to move;
- FEN;
- ASCII board.

It must not require or accept engine evaluation, M4 selection rationale, M6 discrepancy
assertions, or M7 hypothesis content.

## Decision 4 — Freeze is a hard gate before objective reveal

M8 delegates participant evidence capture and freezing to the qualified M5 capture
state machine.

Objective evidence cannot be revealed until every planned pre-reveal stage has an
immutable `EvidenceFreeze`.

M8 does not provide a permissive bypass around this boundary.

## Decision 5 — Objective reveal reuses M5 provenance

Objective evidence reveal is recorded through M5 `ObjectiveEvidenceReveal` and its
associated exposure provenance.

M8 may present the rendered objective evidence but does not rewrite the earlier
participant response, freeze, or capture history.

## Decision 6 — Comparison must bind the exact final revealed capture snapshot

An M6 `ReasoningDiscrepancyContext` is eligible for M8 only if its
`capture_session_ref` matches the exact current M8 capture-session identity and
snapshot fingerprint.

This prevents a pre-reveal or otherwise stale M6 context from being silently attached
after objective reveal changes the evidence history.

M8 also revalidates:

- M6 context identity/fingerprint;
- M6 assessment identity/fingerprint;
- exact assessment/assertion correspondence;
- assertion identity/fingerprint;
- M6 policy consistency;
- participant, position, and game identity;
- chronology.

## Decision 7 — M7 context must be complete for active current hypotheses

If M7 context is attached, M8 accepts the exact `HypothesisLedgerSnapshot` plus the
material `HypothesisRevision` records for **every active current ledger entry**.

A caller may not cherry-pick one favorable active hypothesis while omitting another.

Retired and superseded hypotheses remain preserved in the M7 snapshot history but are
not presented as current active context.

M8 revalidates the snapshot and revision identities before attachment.

## Decision 8 — Explanation is provenance-bearing derived session content

M8 may record an explanation only after exact M6 comparison has entered the session.

The explanation records:

- exact comparison ID/fingerprint;
- optional exact M7 hypothesis-context ID/fingerprint;
- rendered explanation text;
- author kind (`human`, `model`, or `template`);
- author/run/version identity;
- instruction fingerprint;
- timestamp.

Its claim scope is fixed to:

```text
session_local_evidence_explanation
```

The explanation is not promoted into objective chess truth, participant self-report,
M6 discrepancy evidence, or M7 recurrence evidence.

## Decision 9 — Session history is immutable and replayable

`TutorSession` is an immutable snapshot. Every transition appends a
content-addressed `TutorSessionEvent` with a contiguous sequence number and explicit
from/to state.

The initial state vocabulary is:

```text
selected
presented
capturing
frozen
revealed
compared
explained
completed
```

A completed session can be deterministically replayed from its stored exact artifacts
and event chain.

## Decision 10 — M8 does not authorize M9

M8 deliberately does not define:

- training eligibility;
- intervention IDs;
- exercise definitions;
- curriculum selection;
- intervention effectiveness;
- learning state;
- transfer state;
- mastery state.

A supported M7 descriptive recurrence may be visible as bounded context in a session,
but it is not automatically a reason to prescribe an intervention.

## Consequences

### Positive

- information leakage becomes an executable sequencing invariant;
- M5 evidence remains immutable and reusable;
- M6 and M7 provenance is preserved rather than flattened;
- explanations are auditable without being confused with evidence;
- the complete local tutoring interaction is deterministic and replayable;
- M9 can later make intervention-selection decisions from a clean boundary.

### Costs

- callers must supply exact upstream records rather than loose IDs;
- session orchestration is intentionally strict about chronology and fingerprints;
- M8 does not yet provide an end-user UI or exercise library;
- explanation quality is not established merely because explanation provenance is
  recorded.

## Rejected alternatives

### Let the LLM run the whole interaction as one free-form conversation

Rejected because it collapses information boundaries and makes replay/provenance
unreliable.

### Reveal engine evidence before freezing the participant response

Rejected because it contaminates the diagnostic evidence M5/M6 depend on.

### Select only whichever learner hypothesis seems useful for an explanation

Rejected because selective context can manufacture a misleading tutoring narrative.

### Treat explanation text as a training intervention

Rejected because explanation provenance and intervention efficacy are different
product claims. Intervention selection belongs to M9.
