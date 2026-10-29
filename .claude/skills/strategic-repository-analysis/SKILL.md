---
name: strategic-repository-analysis
description: analyze a repository at level 3 to model its current capability state, generate coherent evidence-grounded or hypothesis-grounded construction paths, compare them qualitatively, identify decision-changing uncertainty, and produce a strategic repository analysis without selecting work mechanically.
---

# strategic-repository-analysis

Produce a first-class **Strategic Repository Analysis** for a repository whose
future construction direction is materially open.

Use this Skill when the user asks questions such as:

- How could this repository be developed from here?
- What are the plausible strategic directions for this product/repository?
- What could this repository become?
- Compare the main ways we could construct or evolve this repository.
- What should we build next at the repository/product level when no task has
  already been selected?
- Analyze the repository strategically rather than merely diagnosing one weak
  boundary.

Do **not** use this Skill for an already-localized implementation task whose
repository-level direction is already settled.

## Responsibility

This Skill owns one responsibility:

> Turn current repository evidence + governing intent into a reconstructible
> Level-3 strategic decision space.

It produces:

`artifacts/strategic_repository_analysis.md`

The active semantic agent owns the analysis. No deterministic tool selects the
best path.

## Inputs

Use the smallest sufficient input set:

1. target repository;
2. owner/user intent or governing product strategy when available;
3. current repository evidence;
4. an existing `repository_sensemaking_brief` when it is current and
   decision-relevant;
5. current strategic state / ADRs / release state when they materially constrain
   the analysis.

Do not require a Campaign merely to run this analysis.

## Procedure

### 1. Establish governing intent and authority

Distinguish:

- owner-supplied intent;
- repository-owned product strategy / ADR authority;
- inferred purpose;
- implementation authority.

A strategic request grants authority to analyze. It does not automatically
grant authority to implement the resulting direction.

If the target has a `.sensemaking/` pack, use its `intent.md`, non-goals,
and relevant domain decisions as **navigation** to existing authority. Confirm
material claims against their current cited sources. Missing packs, stale
summaries, and unverified hypotheses are not reasons to defer an otherwise
grounded, authorized improvement. Inspect live code or user-visible behavior
where the strategic choice depends on it.

### 1B. Optional cross-episode semantic grounding

When reviewed architecture records exist at the target revision, layers and
bounded contexts are useful pointers for the system model in step 3. Treat
them as declared claims and verify any that matter to the frontier.

For architecture-heavy, long-horizon decisions, when the owner-selected
ADR 0031 knowledge index exists **at the target Git revision**, query relevant
goals, capabilities, decision history, contradictions, explicit
relationships and retained product possibilities (`poss:` records; funnel
section 4) before comparing construction paths. See
`../../docs/semantic-architecture/persistent-knowledge-cli.md`.
Treat results as source pointers and defeasible claims, not a complete
option set, normative authority, or evidence that an apparent gap is a
missing product capability. Inspect underlying artifacts, recognize stale
revisions, and keep independent divergent exploration possible. Do not
build a compulsory ontology merely to start this Skill.

For architecture-heavy alternatives, the optional Repository Semantic Steward
[architecture exploration](../repository-semantic-steward/references/architecture-exploration.md)
reference connects existing source-grounded queries to divergence, qualitative
comparison and adversarial challenge. Architectural **options** are not
automatically Strategic Frontier candidates or construction paths; the
Level-3 funnel and active agent retain that semantic responsibility.

### 1A. Test goal fitness before treating the stated objective as the frontier

A stated objective remains authoritative owner input, but it may be a terminal
outcome, an instrumental milestone/proxy, a constraint, an evidence/qualification
state, or unclear. Do not silently reinterpret the owner's goal; test whether
optimizing the stated objective would also satisfy the governing product intent.

Use current repository and owner evidence to distinguish:

```text
STATED_OBJECTIVE
-> what the owner explicitly asked for

OBJECTIVE_ROLE
-> terminal | milestone | proxy | constraint | evidence_state | unclear

GOVERNING_INTENT
-> explicit product/owner intent supported by current evidence

GOAL_FIT
-> aligned | partial | conflicting | unresolved
```

Look for a concrete counterexample: could the stated objective be satisfied while
a material governing objective remains unsatisfied? If yes, emit a goal-fit
warning and keep both facts visible rather than replacing the owner's objective.

```text
goal obedience
!= goal diagnosis

stated milestone authoritative
!= milestone sufficient proxy for governing intent

milestone satisfied
!= product objective satisfied
```

Read `references/goal-fitness-and-completion-v1.md` when the objective may be a
milestone, proxy, qualification state, or other downstream representation of
product completion.

### 2. Verify current repository state

Use the authorized repository-access surface.

Prefer measured/current evidence over stale roadmap or status claims. Treat
documented state as documented until independently verified when the distinction
could change the strategic analysis.

Reuse `repo-sensemaker` evidence when it is current. Run repository diagnosis
first only when doing so would materially improve the strategic model.

### 2A. Establish strategic continuity when relevant

If a prior `strategic_repository_analysis` materially governs the current
decision, do not silently overwrite it. Give the new analysis a stable
`analysis_ref` and declare a continuity relationship:

```text
NEW | REAFFIRM | CONTINUE | REVISE | SUPERSEDE | CLOSE
```

Record the prior analysis reference, prior selected path when applicable, and a
short semantic reason. Continuity is authored judgment; deterministic tools may
project it but may not infer it.

When mechanically addressable repository authority files materially condition
the analysis, declare them in `governing_authority_refs`. This lets later
currentness inspection identify that an authority reference changed; the
mechanical observation does not decide that the governing commitment changed
semantically or that strategy must reopen.

### 3. Build the current-system model

Describe the repository as a system/product, connecting intended user
workflows to domain relationships, current capabilities, and the outcome they
enable. Look for material **unmet user outcomes**, unnecessary complexity,
and leverage between existing capabilities, rather than treating a module
inventory or the easiest visible defect as the opportunity map.

- purpose and primary use;
- major capabilities;
- important architecture/control boundaries;
- qualification/release posture where relevant;
- major constraints and claim ceilings.

Do not reduce the repository to a file inventory. When a semantic foundation
already exists (the Steward's BOOTSTRAP or reviewed records), start from it and
verify what matters rather than rebuilding it.

### 3B. Run the Strategic Exploration Funnel before frontier convergence

At a genuine Level-3 `ANALYZE` or `REOPEN_ANALYSIS` boundary, do not converge
on the first visible defect, next issue, or most mechanically legible surface.

Run the **Strategic Exploration Funnel**:

```text
SYSTEM MAP
-> BREADTH EXPLORATION
-> POSSIBILITY COVERAGE ASSESSMENT
-> FRONTIER CANDIDATE SYNTHESIS
-> DEPTH DRILL
-> CONSTRUCTION PATH SYNTHESIS
-> COMPARATIVE SELECTION
```

Map major product/control systems and their important relationships, then scan
both **within systems** and **across systems** for material deficiencies,
unrealized leverage, compositional gaps, autonomy opportunities, simplification,
and new product value.

Breadth exploration is divergent. Do not select the Strategic Frontier until
the breadth landscape is sufficient to make omission of a more important
repository-wide opportunity unlikely merely because another problem was easier
to see. Make that judgment explicit as the **possibility coverage assessment**
(funnel section 4) and record the areas it left unexamined in the artifact.

Then compress material observations into grounded **frontier candidates**.
Advance only the strongest/material candidates to a proportional depth drill.
Only after that depth drill should construction paths be synthesized.

Preserve:

```text
frontier candidate
!= construction path

breadth observation
!= Level-3 frontier automatically

repository-wide
!= inspect every file

coverage before convergence
!= exhaustive inventory
```

Read `references/strategic-exploration-funnel-v1.md` whenever this funnel runs.

Do **not** repeat the funnel during an already-settled
`RESPONSIBILITY / EXECUTE / VERIFY / RECONCILE` continuation unless returned
evidence genuinely reopens Level 3.

### 3A. Check product/completion layers when downstream milestones are in play

When the stated objective involves release, qualification, packaging, validation,
route completion, integration, or another milestone that could be downstream of
actual product completion, establish the relevant completion layers before
forming the Strategic Frontier.

Use domain-appropriate layers; do not force software/game wording onto every
repository. A useful generic distinction is:

```text
implementation exists
!= integration/reachability complete
!= content/behavior complete
!= intended user/product experience complete
!= release/qualification complete
```

The analysis need not prove subjective perfection. It must establish whether a
material prerequisite completion state is evidenced, contradicted, or unresolved
when that state could make the apparent frontier premature.

A highly legible verification surface must not crowd out a less mechanically
legible but more consequential product-completion gap merely because CI, SHAs,
validators, or packaging are easier to inspect.

### 4. Build the capability / limitation map

Classify decision-relevant capabilities using only:

```text
ESTABLISHED
PARTIAL
MISSING
DEFERRED
BLOCKED
CLAIMED_UNVERIFIED
OUT_OF_SCOPE
```

Each current-state entry needs evidence or an explicit owner-intent source.
The capability map describes what is currently established, partial, missing,
deferred, blocked, claimed, or out of scope; it is not a requirement that a
future capability already have empirical proof before it may appear inside a
strategic hypothesis.

```text
present-state claim
-> evidence or explicit owner-intent source

future-state possibility
-> strategic grounding + explicit assumptions

future success claim
-> returned evidence after action
```

Do not turn the states into maturity numbers.

### 5. Form the Strategic Frontier

When the Strategic Exploration Funnel ran, form the Strategic Frontier from the
depth-qualified frontier candidates rather than directly from the first
repository tension observed. The breadth landscape may contain many useful
observations; only the small set that passes the Strategicity Gate and depth
comparison belongs at Level 3.

Before admitting a repository tension **or opportunity** into the Strategic
Frontier, apply the **Strategicity Gate**:

> Would resolving or pursuing this boundary materially change at least one of
> the repository/product future capability state, product boundary, major
> architecture/control boundary, dependency structure, authority/thesis
> commitment, or the materially different future development that becomes
> possible?

Only boundaries or opportunities that pass that semantic test belong on the
Strategic Frontier. A useful maintenance action, local defect, stale status
projection, routine dependency update, or already-selected bounded
implementation task may still warrant lower-level work without becoming a
Level-3 construction path.

An opportunity may be admitted even when the future capability does not yet
exist. Ground it in current repository capability/leverage, governing intent,
an adjacent user/problem, or another explicit strategic basis. Do not require
evidence that the proposed future has already succeeded.

```text
repository issue exists != strategic frontier
useful maintenance exists != construction trajectory
bounded repair warranted != Level-3 BUILD warranted
repository-relevant work != strategic repository evolution
opportunity not yet built != opportunity not strategically representable
```

Identify the small set of unresolved boundaries **and unexploited opportunities**
that could materially change progress toward the governing mission.

Before treating an instrumental milestone as the active frontier, reconcile it
against the goal-fitness and completion-layer checks above. If a prerequisite
product state is materially incomplete or unresolved, represent that fact in the
frontier instead of allowing the downstream milestone to become the whole
strategic problem.

For new canonical `schema_version: 2` artifacts, each frontier entry records
decision-changing evidence references, affected capability identifiers, and a
short `strategic_consequence` explaining why the boundary is Level-3 material.
For opportunity-driven entries, evidence references should ground the present
capability, leverage, problem, or intent; they do not need to prove the future
outcome. The semantic agent judges that consequence; the validator checks only
shape and references.

Exclude attractive but non-decision-relevant ideas.

### 6. Generate coherent construction paths

When the Strategic Exploration Funnel ran, synthesize construction paths **after**
frontier-candidate depth analysis. Do not create detailed construction paths for
every breadth observation merely because it was surfaced.

Generate 2–5 paths when multiple futures are materially plausible.

Use one path when only one coherent construction trajectory is materially represented.
Use zero paths when no construction trajectory is currently warranted/representable and
the strategic conclusion is reached before construction selection.

```text
zero real paths
> manufactured alternative

BUILD
-> requires a selected real path
```

#### Strategic Hypothesis Admission

Do a generative pass before converging on evidence sufficiency. A path may be a
strategic hypothesis rather than an already-demonstrated future.

A **real strategic path** is:

```text
coherent with governing intent
+ compatible with known repository reality
+ materially distinct future capability state
+ plausible mechanism from present capabilities/opportunities to that future
+ explicit decision-relevant assumptions
+ no known material contradiction
```

A path is **manufactured** when it exists mainly to satisfy path-count symmetry,
is materially indistinguishable from another path, contradicts governing
intent/current repository reality, or depends on hidden/invented premises.

```text
real strategic path
!= empirically validated future

speculative path
!= manufactured path

ambitious
!= ungrounded

strategic grounding
!= prior validation

absence of evidence for future success
!= evidence that the future is strategically unwarranted
```

For a hypothesis-driven path, use existing v2 fields rather than creating a new
schema: state the core hypothesis and causal/mechanistic story in
`why_plausible`; declare material premises in decision-relevant assumptions;
and use reassessment triggers to state observations that would materially
strengthen or weaken the path.

Each path must describe:

- future state;
- why it is plausible;
- Strategic Frontier boundary or boundaries it responds to;
- capabilities it builds on;
- required capabilities/changes;
- coarse construction sequence;
- dependencies;
- what it unlocks;
- material risks/tradeoffs;
- reversibility;
- evidence gaps;
- decision-relevant assumptions when useful;
- reassessment triggers for assumptions whose failure could change the path;
- optional lightweight `path_transitions` with stable references such as
  `PATH-2/T1` when later work would otherwise be difficult to place inside the
  trajectory.

A path transition names a conceptual capability-state transition. It is not a
task, milestone, schedule entry, status percentage, or automatic next action.
A path is a coherent future trajectory, not a backlog.

For new canonical `schema_version: 2` artifacts, path grounding is explicit:
`frontier_refs`, `why_plausible`, `builds_on_capability_ids`, and
`required_capability_ids` must connect the path to declared frontier and
capability-map identifiers. Mechanical reference integrity does not establish
that the path is strategically good.

One path is valid when additional alternatives would be artificial. Zero paths
is valid when even one construction path would be artificial or premature.
Do not use zero paths merely because a coherent future is unvalidated; first
test whether it qualifies as a strategically grounded hypothesis under the
admission rules above.

For path distinctness, capability-state grounding, coarse construction
sequencing, comparison discipline, the **orthogonality challenge**, and
anti-backlog rules, read
`references/construction-path-synthesis-v1.md`.

Before converging on the path set, challenge whether all candidate paths are
solving the same framed downstream problem. If so, ask whether that frame is
itself premature or subordinate to another grounded Strategic Frontier. Do not
force a third path; admit an orthogonal path only when it is strategically real.

Do not generate a path merely because a generic category exists. Two paths are
materially distinct only when they imply a different future capability state,
dependency structure, authority/thesis requirement, major risk, or set of
later possibilities.

### 7. Compare paths qualitatively

When multiple frontier candidates advanced to depth, compare the strategic value
of the candidate frontiers as well as the construction paths within the selected
frontier. Preserve enough rationale for an owner-visible Strategic Exploration
Summary without exposing private scratch reasoning.

Use the canonical strategic-comparison lenses:

1. mission relevance;
2. decision value;
3. blocking power;
4. evidence sufficiency / resolvability;
5. consequence of error;
6. deferral cost;
7. reversibility;
8. authority availability;
9. dependency.

For legacy v1 artifacts, the historical tenth
`smallest_warranted_intervention` comparison lens remains valid for backward
compatibility. New `schema_version: 2` artifacts derive the smallest warranted
intervention only **after** the strategic disposition/path judgment.

```text
strategic warrant
-> path/disposition selection
-> smallest warranted intervention

cheap or local intervention
!= strategically preferable future
```

Apply a commission/omission symmetry check while interpreting the lenses:

- **risk of commission:** what becomes costly, constraining, or misleading if
  this path is pursued and its assumptions are wrong?
- **risk of omission:** what opportunity, leverage, learning rate, strategic
  optionality, or mission progress is lost if the path is not pursued?

Use `deferral cost`, `decision value`, and `reversibility` to express this
without adding another schema field or numeric score.

```text
risk of building wrong
!= only strategic risk

risk of not building
= strategically relevant when omission changes mission progress or optionality
```

Do not assign numeric scores, weighted totals, tiers, or a deterministic winner.

Explain the judgment.

### 8. Identify decision-changing uncertainty

Ask what unresolved premise could actually change the strategic conclusion.

Then apply Inquiry Policy v0:

```text
uncertainty exists
!= inquiry required
```

If inquiry is warranted, name the smallest sufficient evidence and correct
source:

- repository_evidence
- empirical
- owner_intent
- external_environment

`INVESTIGATE` does not imply an experiment. Prefer the lowest-cost evidence
source strong enough for the strategic decision. Existing evidence, reading,
inspection, verification, owner/external clarification, a bounded probe, or
cheap reversible construction may resolve the uncertainty without a separate
experiment.

When an empirical experiment is materially considered, apply
`../using-sensemaking/references/experiment-economy-v1.md`:

```text
uncertainty exists
!= experiment required

experiment possible
!= experiment warranted

cheap reversible construction
may be the cheapest sufficient inquiry

research-grade isolation
!= default product-development evidence
```

Require plausible experimental outcomes to change the strategic disposition or
path judgment. Count total experiment overhead, including isolation,
evaluation, interpretation, documentation, delay, and opportunity cost. Use
only the minimum sufficient experimental rigor and control only confounders
that could invalidate the decision-relevant inference.

Residual uncertainty about whether a strategically grounded future will
succeed does not by itself prohibit `BUILD`. If the contemplated construction
is bounded, reversible, authorized, sufficiently safe, and information-producing,
compare build-now learning against inquiry delay rather than demanding prior
proof of success.

```text
residual uncertainty
!= BUILD prohibited

bounded reversible construction
+ coherent strategic hypothesis
+ acceptable downside
may warrant BUILD before future success is demonstrated
```

If no inquiry is warranted, say so.

### 8A. Record decision assumptions when they matter

Record only premises whose failure could materially change the strategic
judgment. Give each a stable identifier, evidence references, and explicit
reassessment triggers.

```text
assumption recorded
!= confidence score
!= generic belief database

trigger observed
!= strategy automatically changed
```

### 9. Synthesize one strategic disposition

Choose semantically:

```text
BUILD
INVESTIGATE
DEFER
NO_CHANGE
OWNER_DECISION
THESIS_REVIEW
```

For `BUILD`, nominate one candidate bounded repository responsibility and the
smallest warranted intervention. `BUILD` does not require prior empirical
proof that the selected future will succeed. It requires sufficient strategic
warrant for the bounded next responsibility: coherent grounding, acceptable
downside, appropriate reversibility, explicit material assumptions, and
independent implementation authority.

For `INVESTIGATE`, nominate the bounded evidence-producing responsibility, not
a broad research program. Do not default that responsibility to an experiment;
state why cheaper evidence sources or reversible construction are insufficient
before recommending experimental work.

For `OWNER_DECISION`, state the exact owner decision rather than disguising it
as repository investigation. When a durable owner-facing decision surface is
useful, produce an `owner_decision_capsule`; the capsule does not select for the
owner.

For `THESIS_REVIEW`, identify the governing commitment that Level 3 cannot
silently rewrite. When the review must be carried across contexts, produce a
`thesis_review_packet`; the packet does not ratify a Level-4 disposition.

When decision-changing evidence comes from outside repository authority and must
remain reconstructible, use an `external_evidence_packet` to preserve bounded
source/currentness provenance.

### 10. Write and validate the artifact

Use:

`references/strategic-repository-analysis-template.md`

New canonical analyses emit `schema_version: 2`. Historical artifacts without a
`schema_version` remain legacy v1 and must continue to validate without
mutation.

Then validate:

```bash
python scripts/validate-artifact.py strategic_repository_analysis artifacts/strategic_repository_analysis.md
python scripts/validate-strategic-repository-analysis.py artifacts/strategic_repository_analysis.md
```

Mechanical PASS does not establish strategy correctness.

## Required boundary statements

Preserve these distinctions in the artifact:

```text
strategic analysis != implementation authorization
repository-relevant work != strategic repository evolution
bounded repair != construction path
construction path != backlog
path transition != roadmap item
path transition != authorized responsibility
transition established != next transition selected
path comparison != numeric ranking
frontier candidate != construction path
breadth exploration != exhaustive repository inventory
depth drill != deep analysis of every observation
resume existing strategy != rerun breadth exploration
mechanically valid != semantically correct
candidate responsibility != authorized execution
strategic warrant precedes intervention minimization
INVESTIGATE != EXPERIMENT
cleaner evidence != more valuable evidence
strategic grounding != prior validation
speculative path != manufactured path
absence of evidence for future success != evidence that the future is strategically unwarranted
stated milestone != terminal product intent automatically
milestone completion != prerequisite product completion
verification legibility != strategic importance
path-set comparison != proof that the option set is complete
```

## Output behavior

The artifact should be useful to a fresh owner or coding agent without hidden
conversation context. When it continues a prior analysis, the lineage and
reassessment assumptions should be reconstructible from the artifact itself.

Do not append an implementation plan unless the strategic disposition and
authority independently warrant one.

When later evidence returns against this analysis, use
`strategic-repository-reconciliation` if the claim/assumption/path/strategic
effect itself must become a durable artifact.

Do not automatically create a Campaign, issue, PR, execution handoff, or code
change from this Skill.

When composed by `using-sensemaking`, return the artifact to that controller:
the disposition and suggested continuation are evidence for its next choice,
not an instruction to implement (return convention:
`../using-sensemaking/references/adaptive-skill-composition-v1.md`, section 5).
An architectural synthesis may revise or reopen a path here, and consequence
findings may send the controller back to breadth.
