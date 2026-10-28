---
name: owner-decision-capsule
description: package an owner-reserved repository or product decision into explicit options, tradeoffs, reversibility, deferral effects, and authority consequences without selecting for the owner.
---

# owner-decision-capsule

Use when the decisive missing premise is owner preference, policy, risk appetite,
or reserved authority rather than repository evidence.

Produce:

`artifacts/owner_decision_capsule.md`

## Procedure

1. State the exact owner decision.
2. Explain why repository inquiry cannot decide it.
3. Check **option-set adequacy** before packaging the choice. Ask whether the
   represented options cover the materially credible trajectories already
   grounded by the current strategic state, or whether they all inherit one
   downstream/proxy framing while a credible upstream trajectory is omitted.
4. If the option set is materially incomplete, **do not manufacture another
   option and do not emit a misleading binary capsule**. Return control upstream
   with `OPTION_SET_INCOMPLETE` and the evidence-grounded reason that
   construction-path/frontier synthesis must be reopened.
5. Otherwise, present only materially credible options.
6. For each option describe what it unlocks, material tradeoffs, reversibility,
   deferral consequence, and authority that would be granted if selected.
7. Separate repository facts from preference-sensitive judgment.
8. Do not select an option or fabricate owner authorization.
9. Write the canonical template and validate it.

```text
owner decision packet != owner decision made
option exists != option recommended automatically
two represented options != option set necessarily complete
OPTION_SET_INCOMPLETE != owner decision
desired delegation != granted authority
```
