# Adapted PRD methodology

**Methodological provenance:** adapted from `lucasgaravelli/pm-skills-claude-code@21cbb2903d740d10fc65c667aea97d3ee8657349`, `.claude/commands/prd.md`, while preserving Sensemaking's existing `to-prd` scope-expansion authority.

## Core method

A useful PRD connects four things without collapsing their evidence states:

1. **Problem and audience** — who experiences what problem/opportunity, with evidence and uncertainty visible.
2. **Solution scope** — what is proposed now, what is excluded, and what requires explicit scope approval.
3. **Outcome contract** — what observable user/business outcomes would count as success, including proposed targets and guardrails.
4. **Delivery context** — constraints, dependencies, risks, sequencing, and unresolved decisions.

## Problem and opportunity

Prefer a concise problem statement supported by durable evidence. Record the intended audience and why the problem matters now. Market size, churn impact, frequency, revenue effect, or severity are observations only when evidence exists; otherwise label them as estimates or unknowns.

## Audience

Use existing persona/segment evidence when available. Distinguish primary users, secondary users, buyers/admins when relevant, and explicit non-audience boundaries. Do not invent demographic or firmographic precision merely to fill a template.

## Solution

Describe the proposed experience and major capabilities in user terms. For each material feature, state which problem/opportunity it addresses and the minimum scope necessary for the current decision.

Keep detailed story decomposition downstream. A PRD may include representative scenarios but should not duplicate the full `user-stories` artifact.

## Metrics and success

Define:

- primary outcome(s);
- baseline, if actually known;
- proposed target or threshold;
- decision horizon;
- guardrail/health measures where consequential;
- instrumentation or measurement gaps.

A proposed target is not evidence that the current baseline has that value.

## Constraints, dependencies, and risks

Capture relevant technical, operational, legal, budget, schedule, team, integration, accessibility, performance, privacy, or scale constraints. Unknown dependencies stay unresolved.

Risks may be summarized in the PRD; deeper launch/risk analysis belongs to `pre-mortem`.

## Sequencing

A PRD may state phases or dependency order when useful, but dates and effort estimates are proposals unless supported by explicit planning evidence/commitment. Do not transform illustrative upstream roadmap dates into commitments.

## Approval and scope

Sensemaking's existing scope-expansion contract is authoritative:

- `exact_match` — stays within the user's stated goal;
- `core_with_expansion` — preserves the goal but proposes additional scope;
- `diverged` — meaningfully changes direction and requires escalation.

Any material expansion must remain pending until explicitly approved. Upstream methodology does not override this authority boundary.

## Claim ceiling

A well-formed PRD is a specification artifact. It is not customer validation, implementation approval, delivery proof, or evidence that success metrics have already been achieved.
