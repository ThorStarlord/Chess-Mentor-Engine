# Pre-mortem methodology

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/pre-mortem.md`.

## Reverse-imagination method

Assume the bounded initiative has failed, then reason backward about plausible causes. The purpose is to surface risks that ordinary forward planning misses, not to claim those failures have happened.

Generate a broad initial set, then collapse duplicates and distinguish evidence strength.

## Risk classes

### Tiger

A material risk with current evidence or a sufficiently direct causal/operational basis that it warrants active treatment.

A Tiger should cite its evidence. A hypothetical concern without support should not be promoted into this class merely because it sounds severe.

### Paper tiger

A concern that appears serious but available evidence/controls make it materially less likely or lower consequence. Record why it is being downgraded and what evidence would reverse that assessment.

### Elephant

A consequential issue or assumption that is not adequately discussed/owned. Elephants often require investigation before they can be classified as known risks or dismissed.

## Urgency

For Tigers:

- `launch_blocking` — must be resolved or explicitly dispositioned before the relevant launch/release decision;
- `fast_follow` — bounded post-launch remediation is acceptable under the current claim/authority boundary;
- `track` — monitor defined signals and escalate if thresholds/conditions occur.

Do not infer a calendar deadline when none exists.

## Mitigation contract

For consequential risks capture:

- impact and probability as qualitative or evidence-supported quantitative assessments;
- mitigation action;
- owner role (not an invented person);
- due date/condition when known;
- success criterion;
- evidence refs;
- escalation signal.

## Recommendation

`go`, `go_with_conditions`, `no_go`, and `insufficient_evidence` are analysis outcomes. They are not external-action authority.

## Claim ceiling

The pre-mortem helps expose failure modes and mitigation needs. It does not certify security, legal compliance, market readiness, implementation quality, or launch success.