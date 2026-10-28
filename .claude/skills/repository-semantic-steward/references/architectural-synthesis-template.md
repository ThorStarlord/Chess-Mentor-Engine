# Architectural Synthesis

Author this when a multi-option architecture comparison should outlive the
session (procedure: `architecture-exploration.md`; concepts:
`docs/semantic-architecture/prospective-reasoning-ontology.md`). It is optional:
a task report is enough when nobody will need the comparison later. A single
concrete proposal goes to `architectural-review` as a `proposed_direction`.

Everything here is prospective. Options, transitions and consequences are
proposals or hypotheses; the preference, if any, is provisional and attributed.
Nothing in the artifact selects, authorizes or proves anything.

## 1. Governing Intent and Scope

Name the question, the target repository and exact revision, the governing
sources (accepted strategy, ADRs, owner intent, constraints) and what is out of
scope. Say whether this is exploration only or a bounded architecture choice.

## 2. Target Possibilities

The `poss:` records (or goals, when no possibility is recorded) the options
would serve, with their current disposition. List none when the synthesis
serves a goal directly.

## 3. Current Architecture

Observed elements the options would reuse or change, each with its source
(file and line, claim id, contract). Mark `NOT_ASSESSED` gaps; do not infer
absence from an incomplete search.

## 4. Architecture Options

At least two materially different structures, each with an `arch:` id: target
structure, what it reuses, proposed transitions (what would change, never what
has changed), what it requires, and assumptions. Mark counterfactual options.

## 5. Option Comparison

Qualitative and attributed (who, when). Choose the lenses that can change the
choice; no scores, weights or ranks. Give each option's comparison outcome and
reason.

## 6. Consequence Exploration

Optional depth on a provisional preference: conditional effects with `conseq:`
ids, category (`benefit`, `risk`, `constraint`, `opportunity`, `mixed`),
mechanism, counterevidence, and what would change the decision. Keep observed
premises apart from assumptions. Stop when the next layer cannot change the
decision, and say so. Write "Not performed" with the reason when no preference
warrants it.

Typed `conditional_consequences` are optional; when present, every
`conditional_consequence_refs` entry must resolve to one and each one must be
cited by an option. A consequence stays a prediction: observed effects of a
built change go to RECONCILE or a `change_impact_analysis`, not back into this
artifact.

## 7. Provisional Preference and Feedback

Either a provisional preference (option, attribution, rationale, scope) or no
preference with its reason. Record each consequence that changed or confirmed
the comparison and its feedback outcome: `REAFFIRM`, `REVISE_PREFERENCE`,
`REOPEN_ALTERNATIVES`, `INVESTIGATE`, `DEFER`, `NO_CHANGE`,
`OWNER_DECISION_REQUIRED` or `THESIS_REVIEW_REQUIRED`. The outcome returns to
the controller (`using-sensemaking`), which may revisit breadth or synthesis;
it selects nothing by itself.

## 8. Unresolved Questions

Decision-changing uncertainty only. Add reconsideration conditions and any
derived possibility or candidate responsibility in their own sections if useful.

## 9. Authority and Claim Boundaries

```text
provisional preference != selection != authorization
consequence hypothesis != observed effect
proposed structure     != existing component
```

## 10. Evidence

Sources inspected, at the stated revision, and the original sources behind any
decisive knowledge-index result.

## 11. Machine-Readable Summary

`provisional_preference` may be `null`; then state `no_preference_reason` and
mark no option `PROVISIONALLY_PREFERRED`.

The validator checks references outside the artifact for shape only. Before
the artifact becomes final, run it with `--resolve-references`: every cited id
should be defined here or recorded in reviewed knowledge, and a transition
`target_ref` should be an existing path, a claim id or `new:<name>`. An id
defined nowhere (an assumption name with no statement) cannot be reconstructed
later.

```yaml
artifact_id: architectural_synthesis
schema_version: 1
analysis_ref: "<stable reference to this artifact>"
target_repository: owner/repository
target_source_identity: "main@<sha>"
governing_intent_refs:
  - docs/product-strategy.md
target_possibility_refs:
  - poss:example-possibility
current_architecture_refs:
  - "src/module.py:10"
architecture_options:
  - option_id: arch:example-local-change
    title: "<short name>"
    proposed_structure: "<target structure>"
    reuses_refs:
      - "src/module.py"
    proposed_transitions:
      - target_ref: "src/module.py"
        change: "<what would change>"
    assumption_refs:
      - hyp:example-assumption
    conditional_consequence_refs:
      - conseq:example-benefit
    comparison_outcome: PROVISIONALLY_PREFERRED
    comparison_reason: "<why, under which lenses>"
  - option_id: arch:example-new-boundary
    title: "<short name>"
    proposed_structure: "<target structure>"
    proposed_transitions:
      - target_ref: "new:example-component"
        change: "<what would be added>"
    assumption_refs: []
    conditional_consequence_refs: []
    comparison_outcome: RETAINED_ALTERNATIVE
    comparison_reason: "<why it stays an alternative>"
option_comparison:
  attribution: "agent, <date>"
  lenses:
    - "<lens>"
  summary: "<qualitative comparison>"
provisional_preference:
  option_id: arch:example-local-change
  status: PROVISIONAL
  attribution: "agent, <date>, no authority"
  rationale: "<why preferred for now>"
  scope: "<conditions under which the preference holds>"
preference_feedback:
  - consequence_ref: conseq:example-benefit
    outcome: REAFFIRM
    effect: "<what the consequence did to the comparison>"
conditional_consequences:
  - consequence_id: conseq:example-benefit
    effect: "<predicted effect, conditional>"
    category: benefit
    mechanism: "<how it would follow>"
    assumption_refs:
      - hyp:example-assumption
    observed_premise_refs: []
    counterevidence: "<what argues against it, or what is unknown>"
    would_change_decision_if: "<observation that would change the comparison>"
consequence_stop_reason: "<why a further layer would not change the decision>"
derived_possibility_refs: []
candidate_responsibility: null
reconsideration_conditions:
  - "<evidence that would reopen the comparison>"
unresolved_questions:
  - "<decision-changing question>"
implementation_authority_established_by_artifact: false
semantic_truth_established: false
created_at: "<ISO date>"
immutable: true
```
