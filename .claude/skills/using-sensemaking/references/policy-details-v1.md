# Inline policy sections moved out of SKILL.md (verbatim)

Moved from `SKILL.md` to keep the core skill short. Text is unchanged. The full policies live in the reference files named under each heading.

### Warrant / Choice Policy v0

For a consequential contemplated target, ask:

> **What does the current evidence, state, constraints, and authority warrant for this specific target?**

Name the target first. Useful targets include claims, inquiries, responsibilities, actions, continue/stop/escalate choices, closure claims, protected transitions, and strategic directions.

```text
warrant for target A
!= warrant for target B

WARRANTED
!= authorized
!= executed
!= successful

candidate set exists
!= one candidate must be selected
```

When several materially credible targets exist, compare only what matters to the current decision: target-specific support, nearest warrant gap, smallest sufficient intervention, reversibility, currentness, and authority. Select one when commitment is actually needed; otherwise preserve alternatives or return `NO_SELECTION`.

Read `references/warrant-choice-policy-v0.md` when explicit target adjudication or choice is material.

### Metareasoning Policy v0

When the real question is **how to spend the next unit of reasoning/action effort**, select the smallest useful control move:

```text
ACT
INQUIRE
CHALLENGE
EXPLORE
VERIFY
ESCALATE
STOP
```

Use `ACT` when an already-selected authorized bounded responsibility is sufficiently warranted and more thinking is not worth its cost.

Use `INQUIRE` when Inquiry Policy has identified decision-changing evidence worth obtaining.

Use `CHALLENGE` for consequential, low-reversibility, conflicting, or weakly supported commitments.

Use `EXPLORE` when the frame or option set may be too narrow.

Use `VERIFY` when a consequential result, repair, or closure claim still needs direct confirmation.

Use `ESCALATE` when the real gap is owner intent, higher-scope commitment, protected authority, or external control.

Use `STOP` when no additional effort is warranted.

```text
control move selected
!= responsibility authorized

cheap + reversible + low consequence + information-producing
-> acting can dominate thinking longer
```

Keep this implicit for obvious local work. Read `references/metareasoning-policy-v0.md` when control-mode selection is consequential or ambiguous.

