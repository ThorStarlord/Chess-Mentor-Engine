# Architecture: implemented boundaries and remaining hypotheses

**Current status authority:** [repository build status](../product/repository-build-status.md).  
**Operations:** [post-M10 milestone runbook](../runbooks/post-m10-milestone-runbook.md).

## Implemented bounded architecture

M1-M10 have qualified bounded software contracts. The three-feature queue adds
corrected UCI normalization (PR #39), local durability and verified M8 recovery
(PR #40), and protocol-bound outcome/transfer evidence (PR #41). This is not a
production end-user application or an empirically validated learning system.

| Boundary | Implementation | Authority retained |
| --- | --- | --- |
| M1-M2 | `chess/` | Canonical games/positions, provenance, deterministic context and low-level rules/features. |
| M3 | `analysis/` | Provenance-bound engine judgment, explicit completeness/failure and exact/bounded scores; not player cognition. |
| M4 | `selection/` | Objective decision comparison and versioned diagnostic selection, including successful controls. |
| M5 | `evidence/` | Participant-reported evidence, exposure/deviation provenance, freezes and objective reveal. |
| M6-M7 | `learning/` | Position-local discrepancies and participant-specific recurring hypotheses, not causal cognitive traits. |
| M8 | `tutoring/` | Controlled capture/freeze/reveal/comparison/explanation transitions and immutable event/snapshot history. |
| M9 | `training/` | Versioned exercises/interventions and explicit applicability-driven selection. |
| M10 | `evaluation/` | Predeclared evaluation plans, frozen attempts, completion/observation ledgers and separate outcome dimensions. |
| Local infrastructure | `storage/` | Immutable JSON artifacts and verified M8 recovery; no new diagnostic or pedagogical authority. |

The evidence relationship is:

```text
canonical chess state + engine evidence
-> objective comparison / selection
-> frozen participant evidence
-> local discrepancy / recurring descriptive hypothesis
-> controlled tutor session / explicit intervention selection
-> predeclared attempts and authored outcome observations
-> separate practice, near-transfer, far-transfer and real-game evidence
```

This is an authority map, not a claim that one automatic CLI command invokes every
step. Completing M8 does not automatically select training, run M10, revise M7, or
create M11 learner state. Human/model authoring remains explicit at the applicable
judgment boundaries.

### Cross-cutting integrity contracts

- UCI provider `0.2` converts both scores and bounds to White-perspective ordering,
  validates explicit MultiPV ranks, and preserves historical provider identities.
  See [UCI repair](uci-evidence-contract-repair.md) and
  [the M3 contract](../decisions/0002-engine-evidence-contract.md).
- Storage remains outside domain operations. It verifies declared dependencies,
  reconstructs typed M8 records, and replays existing transitions. It does not
  independently requalify all external evidence. Comparison assertions are
  canonicalized before hashing and serialization. See
  [durability and replay](durable-artifacts-and-replay.md).
- M10 binds the exact selected M9 artifacts and declared policy. Practice completion
  is not success; supported transfer evidence is not mastery or causal efficacy.
  Generic M10 archival is available, but typed M10 recovery and automatic migration
  are not. See [M10 architecture](outcome-transfer-evidence.md) and
  [ADR 0009](../decisions/0009-outcome-transfer-evidence-contract.md).

## Historical architecture hypothesis

The original foundation-stage hypothesis below remains discovery context, not a
frozen end-to-end architecture. Its original M1-only status is historical; use the
implemented map above and current build status for operational decisions.

Chess Mentor Engine may eventually use a flow like this:

```text
Game ingestion
-> Chess analysis
-> Evidence extraction
-> Learner modeling
-> Pedagogical diagnosis
-> Learning planning
-> Practice / interaction
-> Evaluation
-> Learner-state update
```

This is a direction for discovery, not a committed end-to-end implementation plan.
M11 longitudinal learner-state updates and CLI/UI productization remain unstarted
and require separate authorization. [M1](chess-evidence-substrate.md) was the first
bounded implementation, not the only currently implemented slice.

### Original tentative system split

1. **Deterministic chess layer.** Legal moves, board states, engine analysis,
   tablebase results, and other objective chess evidence were candidate concerns.
   This list does not claim that every candidate, including tablebases, is built.
2. **Learner-state and application layer.** Provenance, history, evidence
   aggregation, progress state, and persistence rules were candidate concerns.
3. **Model-assisted tutoring layer.** Explanations, Socratic interaction,
   misconception hypotheses, lesson framing, and adaptive presentation were
   candidate concerns.

Use the later milestone contracts for implemented ownership. Broader integration
and product-value assumptions still need validation.

### Original candidate concepts

Game, Position, Move Decision, Chess Evidence, Player, Learner Profile, Skill or
Concept, Mistake Pattern, Misconception Hypothesis, Diagnosis, Learning Goal,
Intervention, Exercise, Attempt, Mastery Evidence, Review, and Provenance were
discovery candidates. Some now have bounded implementations above; inclusion in
this historical list alone does not establish a production domain object.

The possible hierarchy of Chess Knowledge, Learner Model, Learning Plan, Practice,
and Instruction should not be copied mechanically from another system or accepted
without domain modeling.
