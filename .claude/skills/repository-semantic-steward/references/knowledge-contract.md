# Typed, source-bound knowledge contract

The canonical model and validator live in `src/sensemaking_skills/semantic_architecture/knowledge.py` and `knowledge_sources.py`. **Use the implementation's actual currently accepted types**; do not invent an unvalidated ontology. Current v1 families include goal, non_goal, domain_concept, capability, constraint, invariant, contract, component, source, verification, decision, alternative, incident, lesson, hypothesis, opportunity and observation. The bootstrap candidate adds a mechanically observed `directory` kind.

Relations include `serves_goal`, `requires_capability`, `constrained_by`, `depends_on`, `implemented_by`, `tested_by`, `decided_by`, `supersedes`, `contradicts`, `derived_from`, `affected_by_change`, `learned_from`, `candidate_opportunity_for`, `defines`, `references`; the bootstrap candidate adds lexical `contained_in`.

## Authoring

Write a reviewed, Git-tracked file under `.sensemaking/knowledge/*.json`:

```json
{
  "schema_version": 1,
  "claims": [
    {
      "id": "cap:book-reentry",
      "kind": "capability",
      "statement": "Show the current Book and its working Chapter state when reopening the workspace",
      "authority_kind": "document",
      "authority_ref": "docs/product/book-workspace.md",
      "evidence_refs": ["file:docs/product/book-workspace.md"],
      "epistemic_status": "declared"
    },
    {
      "id": "comp:workspace-session",
      "kind": "component",
      "statement": "Restores the open Book and Chapter when the workspace reopens",
      "authority_kind": "code",
      "authority_ref": "src/workspace/session.py",
      "evidence_refs": ["file:src/workspace/session.py"],
      "epistemic_status": "observed"
    }
  ],
  "relations": [
    {
      "id": "rel:book-reentry-implemented-by-session",
      "subject": "cap:book-reentry",
      "predicate": "implemented_by",
      "object": "comp:workspace-session",
      "evidence_refs": ["file:src/workspace/session.py"]
    }
  ]
}
```

A file contains exactly `schema_version`, `claims` and `relations`; put revision or provenance notes in claim attributes or the session receipt, not new top-level keys. Every claim needs `id`, `kind`, `statement`, `authority_kind`, `authority_ref` and `evidence_refs`. Every relation needs `id`, `subject`, `predicate`, `object` and `evidence_refs` (the source that establishes the relation itself). Run `semantic knowledge-proposal-check` on each file before treating it as reviewed knowledge; a file that has not passed it is a draft.

The example paths are illustrative, not a claim that the documents exist. All `file:` references and authority paths must resolve to legitimate tracked evidence on the target repository before a committed index is built.

### Hard boundaries

- `epistemic_status=observed` requires source-inspected evidence, not a design aspiration.
- A declared decision/status may be a *document observation*, without thereby verifying policy authority.
- `authority_verified`, `semantic_truth_established` and `action_authorized` cannot be author-promoted.
- Evidence must be locally source-linked, currentness-reconciled and properly scoped. Histories and uncertainty are legitimate first-class outcomes.
- A dependency relation must be sourced in actual architecture/code evidence; same-directory placement and syntax-only imports are insufficient.
- Only accepted domain ownership workflows can change target-repository canonical/product state.

## Target domain ontology

A target repository's domain ontology (its concepts, states, rules and boundaries) is expressed as knowledge instances of the existing vocabulary, not as new types:

- a domain noun or distinction is a `domain_concept`; confusable terms use `distinct_from` or `synonym_of` (schema_version 2);
- a user-visible behavior is a `capability` linked to its `component` (with `owned_paths` in v2) by `implemented_by`;
- a product rule is an `invariant` or `constraint`; a placement, naming or dependency rule is an `architecture_rule` with `rule_type`, `severity` and `applies_to`;
- states and their transitions are `lifecycle_state` claims linked by `transitions_to`; data movement is `flows_to`; meaningful partitions are `layer` and `bounded_context` with `belongs_to`;
- intent is `goal` and `non_goal`; governing choices are `decision` claims cited by `decided_by`.

Areas not yet assessed go in the bootstrap coverage report, not in claims. A new type is justified only through [schema evolution](schema-evolution.md).

## Product possibility records

A retained product possibility (a potential future of the product; conceptual model in `docs/semantic-architecture/product-possibility-ontology.md` of the Sensemaking Skills repository) uses existing kinds and predicates:

- an `opportunity` claim with a stable `poss:<slug>` id and `attributes.concept: ProductPossibility`; dimensions (alignment, ambition, horizon, realization) and an append-only `disposition_history` live in attributes. Speculative or synthesized possibilities are `hypothetical` with `authority_kind: hypothesis`;
- the realized ability is a separate `capability` claim linked by `implemented_by`; mechanically observed implementation evidence is an `observation` claim (`observed`, authority `code` or `document`) the capability `references`;
- `requires_capability` only for a genuine prerequisite; `contradicts` for a conflict with a non-goal or decision; `derived_from` for origin; a shared premise is one `hypothesis` claim that each possibility `references`;
- relations without a matching predicate (`extends`, `complements`, `alternativeTo`, weaker enabling) use `references` with `attributes.conceptual_relation`, and every relation records `attributes.establishment` (`inferred`, `ratified`, `hypothesized`);
- cite the record of origin as evidence; cite a curated library only where it is that origin. Evidence matches by file, so extra citations add re-inspection noise;
- construction paths and evidence prerequisites are not possibilities: keep paths in their analyses and prerequisites as `hypothesis` claims;
- classify before retaining: an engineering alternative (implementation approach, repair, refactor or declined responsibility) is not a possibility. It stays in the report or decision history, or becomes an `alternative` claim linked to the reviewed `decision` that declined it. An architecture option is an `arch:` record (next section). A declined responsibility yields a `poss:` record only when the product future it points to is stated apart from the task.

A possibility record is memory, not a backlog item or authorization.

## Prospective reasoning records

Retained architecture options and consequences (conceptual model in `docs/semantic-architecture/prospective-reasoning-ontology.md` of the Sensemaking Skills repository) also use existing kinds:

- an architecture option is an `alternative` claim with an `arch:` id, `hypothetical`, with its target structure, reused capabilities, requirements, comparison and any provisional preference in attributes. A preference is never a `decision` claim;
- a consequence is a `hypothesis` claim with a `conseq:` id, its category, assumptions, mechanism and what would change the decision in attributes; observed premises are `observation` claims it `references`;
- an option `requires_capability` an existing capability it reuses; a proposed change to an existing contract or component is `references` with `conceptual_relation: proposesChangeTo`, never `affected_by_change`;
- `proposesToRealize`, `mayProduce`, `mayEnable`, `alternativeTo` and `challenges` use `references` with `attributes.conceptual_relation`; a possibility produced by a consequence is `derived_from` it;
- construction paths stay in their analyses; cite them as `<analysis path>#PATH-n` in attributes.

Retain only options and consequences that would change a later decision. Once an option is built, anchor it so file-level `context-for` reaches it (reconciliation reference, prospective records bullet). The comparison itself (option structures, transitions, lenses, the provisional preference and its feedback) belongs in an `architectural_synthesis` artifact ([template](architectural-synthesis-template.md)); records cite it as `analysis_ref`.

## Existing CLI

```bash
sensemaking-skills semantic knowledge-orient --repo . --repository owner/repo --target-ref "$REF" --json
sensemaking-skills semantic knowledge-build --repo . --repository owner/repo --target-ref "$REF" --db /outside/index.sqlite --include-repository-structure --json
sensemaking-skills semantic knowledge-query --db /outside/index.sqlite --repository owner/repo --target-ref "$REF" --operation explain --subject cap:book-reentry --json
sensemaking-skills semantic knowledge-audit --db /outside/index.sqlite --repo . --repository owner/repo --indexed-ref "$OLD_SHA" --current-ref "$REF" --json
```

No `knowledge-build` operation accepts a dirty checkout; use a clean detached snapshot/worktree. The database path must stay outside target checkout; the generated SQLite file is not a reviewed semantic source. Query results describe declared edges and indexed source, not a validated complete graph.
