# Strategic Repository Analysis

## 1. Governing Intent and Scope

State owner intent, repository-owned product authority, target repository, exact
source identity when available, and analysis/implementation authority boundary.
When mechanically addressable governing authority files materially condition the
analysis, list them explicitly in `governing_authority_refs`. This is provenance
for currentness inspection, not a semantic claim that file change invalidates strategy.

## 1A. Strategic Continuity (when continuing prior analysis)

When a materially relevant prior strategic analysis exists, identify its stable
reference, declare the continuity disposition (`REAFFIRM | CONTINUE | REVISE |
SUPERSEDE | CLOSE`), identify the prior selected path when applicable, and state
why the relationship holds. Use `NEW` when explicitly creating a new analysis
lineage.

## 2. Current System Model

Describe the current repository/product as a system: purpose, major capabilities,
architecture/control surfaces, current qualification/release posture when
material, constraints, and claim ceilings.

## 3. Capability and Limitation Map

| Capability | State | Evidence | Strategic relevance |
| --- | --- | --- | --- |
| ... | ESTABLISHED / PARTIAL / MISSING / DEFERRED / BLOCKED / CLAIMED_UNVERIFIED / OUT_OF_SCOPE | ... | ... |

## 4. Strategic Frontier

List only current decision-relevant repository/product boundaries that pass the
Strategicity Gate. For new `schema_version: 2` artifacts, each frontier entry
must identify its evidence references, affected capability identifiers, and a
short semantic explanation of the strategic consequence.

When the Strategic Exploration Funnel ran, state the possibility coverage
first: systems and user outcomes considered, retained possibilities recalled,
counterfactuals considered, areas left unexamined, and whether an excluded
direction could overturn this frontier.

```text
repository-relevant finding != strategic frontier
bounded repair != construction path
```

## 5. Candidate Construction Paths

For each path include:

### PATH-1 — <name>

- **Future state:**
- **Why plausible:**
- **Frontier grounding:** which Strategic Frontier entries this path responds to.
- **Builds on:** capability-map identifiers plus concise explanation where useful.
- **Requires:** capability-map identifiers plus concise explanation where useful.
- **Construction sequence:**
- **Path transitions (optional):** stable conceptual transition references such as
  `PATH-1/T1` when later work would otherwise be difficult to reconstruct. A
  transition is strategic provenance, not a roadmap task.
- **Architecture basis (optional):** `possibility_refs` (`poss:` possibilities the
  path would advance) and `architecture_option_refs` (`arch:` options it would
  use), with the comparing `architectural_synthesis` in top-level
  `architecture_synthesis_refs`. Use them only when such records exist and a later
  reader would need the basis. Citing an option on a path neither selects nor
  authorizes it; only the strategic disposition selects a path.
- **Dependencies:**
- **Unlocks:**
- **Risks / tradeoffs:**
- **Reversibility:**
- **Evidence gaps:**
- **Assumptions:** decision-relevant premises this path depends on, when useful.
- **Reassessment triggers:** concrete changes that should cause the path judgment
  to be reconsidered.

Repeat for each materially distinct path.

If no coherent construction path is currently warranted/representable, explicitly state
that and use `construction_paths: []` plus `path_comparison: []` in the machine
summary. Do not invent a placeholder path. A `BUILD` disposition still requires a
selected real path.

## 6. Qualitative Path Comparison

Compare paths using:

- mission relevance;
- decision value;
- blocking power;
- evidence sufficiency / resolvability;
- consequence of error;
- deferral cost;
- reversibility;
- authority availability;
- dependency.

For new v2 artifacts, derive the smallest warranted intervention only after the
strategic disposition/path judgment. Historical v1 artifacts may retain the
legacy tenth comparison lens.

Do not use numeric scores or weighted ranking.

## 7. Decision-Changing Uncertainty

State the uncertainty that could materially change the strategic judgment, what
it could change, whether inquiry is warranted, the smallest sufficient evidence,
and the correct evidence source.

## 7A. Decision Assumptions and Reassessment Triggers

Record only premises whose failure could materially change the strategic judgment.
Each assumption should have a stable identifier, evidence references, and one or
more reassessment triggers. Do not use confidence scores or probability fields.

## 8. Strategic Synthesis

Explain the semantic judgment across the candidate paths and why the disposition
follows from current evidence.

## 9. Warranted Direction

Declare one semantic disposition:

`BUILD | INVESTIGATE | DEFER | NO_CHANGE | OWNER_DECISION | THESIS_REVIEW`

If BUILD, identify the selected path and candidate bounded repository
responsibility.

If INVESTIGATE, identify the bounded evidence-producing responsibility.

## 10. Authority and Claim Boundaries

Explicitly state implementation authority, protected owner/external decisions,
and the claim ceiling.

## 11. Evidence

List decision-changing evidence with relative repository references and stable
line/range or identifier where available.

## 12. Machine-Readable Summary

```yaml
schema_version: 2
artifact_id: strategic_repository_analysis
analysis_ref: "SRA-<stable-reference>"
continuity:
  prior_analysis_ref: null
  disposition: NEW
  prior_selected_path_id: null
  reason: "No prior analysis is being continued."
target_repository: owner/repository
target_source_identity: "<commit/tree/ref or documented-unverified>"
governing_intent: "<owner/repository strategy statement>"
governing_authority_refs:
  - docs/product-strategy.md
architecture_synthesis_refs:  # optional
  - artifacts/architectural_synthesis.md
capability_states:
  - capability_id: example-capability
    state: ESTABLISHED
    evidence_refs:
      - path/to/file.md:L10-L20
  - capability_id: needed-capability
    state: MISSING
    evidence_refs:
      - path/to/other-file.md:L30-L40
strategic_frontier:
  - frontier_id: FRONTIER-1
    statement: "<decision-relevant boundary>"
    evidence_refs:
      - path/to/file.md:L10-L20
    affected_capability_ids:
      - example-capability
    strategic_consequence: "<how resolving this could materially change the repository future>"
construction_paths:
  - path_id: PATH-1
    name: "<path name>"
    future_state: "<coherent future state>"
    frontier_refs:
      - FRONTIER-1
    why_plausible: "<why current evidence and governing intent support this trajectory>"
    builds_on_capability_ids:
      - example-capability
    required_capability_ids:
      - needed-capability
    construction_sequence:
      - "<coarse step>"
    path_transitions:
      - transition_ref: PATH-1/T1
        transition: "<conceptual capability-state transition>"
    possibility_refs:  # optional
      - poss:example-possibility
    architecture_option_refs:  # optional
      - arch:example-option
    dependencies:
      - "<dependency>"
    unlocks:
      - "<what becomes possible>"
    risks:
      - "<material risk/tradeoff>"
    reversibility: "<qualitative explanation>"
    evidence_gaps:
      - "<material assumption/gap>"
    assumptions:
      - "<decision-relevant premise>"
    reassessment_triggers:
      - "<observable condition that should trigger reconsideration>"
path_comparison:
  - path_id: PATH-1
    lenses:
      mission_relevance: "<qualitative judgment>"
      decision_value: "<qualitative judgment>"
      blocking_power: "<qualitative judgment>"
      evidence_sufficiency: "<qualitative judgment>"
      consequence_of_error: "<qualitative judgment>"
      deferral_cost: "<qualitative judgment>"
      reversibility: "<qualitative judgment>"
      authority_availability: "<qualitative judgment>"
      dependency: "<qualitative judgment>"
decision_changing_uncertainty:
  statement: "<uncertainty or none>"
  could_change: "<which strategic judgment>"
  inquiry_warranted: false
  evidence_needed: "<smallest sufficient evidence or none>"
  source: repository_evidence
decision_assumptions:
  - assumption_id: ASSUMPTION-1
    statement: "<premise that could change the judgment if false>"
    evidence_refs:
      - path/to/file.md:L10-L20
    reassessment_triggers:
      - "<condition that should trigger strategic reconsideration>"
strategic_disposition: BUILD
selected_path_id: PATH-1
candidate_repository_responsibility: "<bounded responsibility or null>"
candidate_path_transition_ref: PATH-1/T1
smallest_warranted_intervention: "<intervention or null>"
implementation_authority_established_by_artifact: false
semantic_truth_established: false
created_at: "YYYY-MM-DDTHH:MM:SSZ"
immutable: true
```

## Schema compatibility

New canonical analyses use `schema_version: 2`. Historical strategic analyses
without `schema_version` are legacy v1 and remain valid without mutation. The
v2 grounding fields strengthen reconstructibility; they do not authorize a
deterministic judgment about whether a frontier/path is strategically correct.

## Path-transition boundary

Path transition identity is optional and exists only to make a selected strategic
trajectory reconstructible across later responsibilities and reconciliations.

```text
path transition != roadmap item
path transition != backlog item
path transition != authorized responsibility
transition established != next transition selected
```

Do not add scheduling/project-management fields such as priority, deadline, estimate,
percent complete, assignee, start/due date, blocked-by, or automatic next-transition
selection.
