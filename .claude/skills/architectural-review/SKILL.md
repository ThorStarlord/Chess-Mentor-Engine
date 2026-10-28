# Architectural Review Skill

Evaluates proposed architectural responses against principal-engineer judgment: capability abstraction vs. features, bottleneck detection, user experience inversion, architectural risk mapping, and quantifiable success validation.

---

## Workflow

**Input**: 
- Artifact: `repository_sensemaking_brief` (from repo-sensemaker diagnostic)
- Named input: `proposed_direction` (user-supplied architecture proposal)

**Output**:
- Artifact: `architectural_review_recommendation` (decision + risk analysis)

**Invocation**: Invoke this Skill directly when the active agent has selected the architectural-review responsibility. Supply the current `repository_sensemaking_brief` and a concrete `proposed_direction` as the two bounded inputs.

---

## Boundary Rules

1. **Do not re-diagnose the repository.** Consume `repository_sensemaking_brief` as the authoritative workflow input for the diagnosis/evidence it records, while preserving the brief's currentness, evidence limits, and epistemic distinctions. Do not silently upgrade every upstream sentence into ratified semantic truth.

2. **Evidence reuse**: When citing evidence from the brief, reference sections directly (e.g., "See brief, section X, evidence Y"). Do not re-cite repository files independently. Preserve whether the brief treated the evidence as observed, derived, inferred, documented/unverified, contradicted, or unresolved where that distinction changes the verdict.

3. **Proposed response evaluation**: Evaluate whether the *proposed* response architecturally addresses the identified fog, not whether the fog classification is correct. Leave fog validation to repo-sensemaker. An observed dependency or file relation is not by itself an architectural violation: establish the relevant boundary/contract/intent before making that inference.

4. **Insufficient brief handling**: If the brief is incomplete or insufficient, return `investigate_first` and identify the bounded evidence that is missing. Do not manufacture a workflow route, supplement the brief independently, or infer missing architecture intent from directory shape alone.

5. **Output decision outcomes**: Every recommendation must result in one of: `pursue`, `pursue_narrowed`, `investigate_first`, `defer`, or `reject`. Decisions must be actionable and justified with specific risks, constraints, conditions, and the evidence that could change the verdict when material.

6. **Optional Section 15 awareness** (candidate, unratified — see `docs/candidate/architecture-decision.md`, Decision 4). If the brief has a Section 15 `extended_analysis` block, you may use two of its fields; absence of Section 15 changes nothing about this workflow.
   - `consequential_boundary.is_demonstrated_weakness: true` means the weakness **described by `consequential_boundary` itself** is independently, currently demonstrated (not just plausible). Before applying this to your verdict, establish what `consequential_boundary.description` actually names — **do not assume it refers to Section 6's `weakest_boundary` merely because both appear in the same brief.** Section 15 is deliberately allowed to name a different boundary than Section 6 (see the template's own note on this); co-occurrence is not equivalence, and this rule does not require the two sections to agree.
     - If the proposal under review addresses the boundary `consequential_boundary` describes, but only partially: that's narrower than what the evidence supports — pushes toward `pursue_narrowed` rather than `pursue`, because the verdict should say so rather than imply full resolution.
     - If the proposal was never targeting the boundary `consequential_boundary` describes at all — a separate, disclosed, `is_demonstrated_weakness: true` defect that the proposal doesn't touch and isn't a partial cut at — note it explicitly as a separate finding in your risk analysis (the calling agent should know it exists and remains open), but do not let its mere presence narrow the verdict on the proposal's own target. Unaddressed-and-unrelated is not the same failure mode as addressed-but-incomplete.
   - `domain` (a list) names every fog dimension genuinely implicated. If any value in `domain` is outside this review's own competence (e.g. a `product` domain value when you're evaluating pure architectural merit), say so explicitly in the recommendation as an out-of-lens disclosure — do not silently stay quiet about it, and do not expand scope to cover it yourself.
   This does not change Boundary Rule 1 (still do not re-diagnose) or Boundary Rule 4 (still return `investigate_first` for an insufficient brief) — it only adds two optional inputs to the reasoning in Boundary Rules 2-3 above. It does not introduce any requirement that Section 6 and Section 15 agree with each other.

---

## Semantic Reasoning Alignment (Phase 9)

This Skill participates in the shared Sensemaking Reasoning Model through the architectural-review lens. Read [Semantic Reasoning Alignment](./references/semantic-reasoning-alignment.md) when evaluating a decision-changing proposal.

The minimum discipline is:

```text
inherited target/currentness
-> inherited evidence
-> bounded Component/Layer/Boundary/Contract model where needed
-> architectural claim + epistemic status
-> risk / contradiction / uncertainty
-> verdict + conditions
-> explicit limits
```

Key rules:

- inherited evidence remains evidence; it is not automatically `RATIFIED` truth;
- `A depends on B` may be observed/derived while `A violates boundary X` remains an inference requiring the boundary rule and its authority;
- file/folder names do not automatically establish semantic components or layers;
- a risk introduced by a proposal may be `HYPOTHESIZED` even when the current repository has no observed defect of that kind;
- validator success establishes the artifact's mechanical contract, not the correctness of the architectural verdict;
- if missing evidence could change the verdict, prefer `investigate_first` over hidden assumption completion.

Use epistemic labels only where they clarify material reasoning; do not turn the recommendation into ontology boilerplate.

---

## Execution Protocol

1. **Parse inputs**: Load `repository_sensemaking_brief` and `proposed_direction` as separate contexts. Preserve the brief's target/currentness boundary and explicit limits.

2. **Analyze proposed response**: Map the proposal against the brief's fog classification and evidence:
   - Does it address the identified weaknesses?
   - Does it introduce new risks or bottlenecks?
   - Does it preserve existing authority boundaries?
   - Which architectural relations are evidenced, and which conclusions are inferred from those relations?

3. **Risk identification**: Enumerate specific risks, not generic concerns. Distinguish current-evidence-backed risks from proposal-contingent hypotheses when the distinction matters. Examples of sufficient specificity:
   - ❌ "This could become another source of truth" (vague)
   - ✅ "Workspace becomes second orchestration layer, conflicting with identity model authority" (specific, bounded, testable)

4. **Decision reasoning**: Provide explicit reasoning for each decision type:
   - **pursue**: Proposal addresses fog with acceptable risk profile
   - **pursue_narrowed**: Proposal is sound only under specific constraints (list them)
   - **investigate_first**: Propose additional investigation or validation steps needed before proceeding
   - **defer**: Proposal is sound but timing/priority makes it incorrect now (specify conditions for reconsideration)
   - **reject**: Proposal creates unacceptable risks or architectural violations (specify kill conditions)

5. **Success measures**: For any `pursue` decision, define how success will be measured:
   - Metric: What will be measured
   - Baseline: Current state
   - Target: Desired outcome
   - Method: How measurement will be performed

6. **State explicit limits**: Identify inherited assumptions, out-of-lens domains, unavailable evidence, or unresolved architecture intent that the recommendation does not establish.

---

## References

- [Artifact Contract](../workflow-planner/references/artifact-contracts.yaml): `architectural_review_recommendation`
- Historical workflow registry identity: `architectural-review-planning-workflow` is compatibility-only provenance, not the current invocation path.
- [Skill Registry](../workflow-planner/references/skill-registry.yaml): `architectural-review`
- [Design Document](../../docs/skill-design-architectural-review.md): Full specification
- [Template](./references/architectural-review-template.md): Artifact template
- [Trigger Policy](./references/architectural-review-trigger-policy.md): When to invoke this skill
- [Semantic Reasoning Alignment](./references/semantic-reasoning-alignment.md): Phase 9 evidence/claim/architecture boundary
- [Shared Reasoning Model](../../docs/semantic-architecture/reasoning-model.md): Repository-wide semantic lifecycle

---

## Invocation Prerequisite

This Skill requires two explicit inputs:

1. a current `repository_sensemaking_brief`;
2. a concrete `proposed_direction`.

The active agent may supply those inputs from current repository context or durable artifacts. The Skill does **not** require `workflow-runtime.py`, a session directory, `--from-session`, or the historical `architectural-review-planning-workflow` wrapper.

The wrapper remains compatibility-only historical identity for reconstructing earlier experiments. It does not grant current execution authority or define the current product path.

## Regression Testing

Current live tests are artifact/validator and Skill-contract tests, especially `tests/test_architectural_review_recommendation_validator.py` and the architectural-review artifact fixtures. Historical runner-wrapper acceptance/runtime tests are quarantined under `tests/quarantine-retired-runner/` because the wrapper is no longer a current execution route.

---

## References by Role

**For agents**: Read the artifact template, trigger policy, and semantic-reasoning alignment reference to understand when and how to invoke this skill.

**For implementation**: See the full design document in `docs/skill-design-architectural-review.md`.

**For validation**: The specialized validator `validate-architectural-review-recommendation.py` enforces decision consistency and required fields. It does not establish architectural truth.
