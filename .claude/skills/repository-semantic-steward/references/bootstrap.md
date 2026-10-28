# BOOTSTRAP — First-visit semantic foundation

## Purpose

Construct a useful domain and architecture model that survives the coding agent's context, not a file catalog. It is the **default first responsibility** when `using-sensemaking` takes a repository-level request and no adequate semantic model exists (ADR 0034 in the Sensemaking Skills repository); its result is the foundation for possibility exploration, not a selection. Normal input includes contradictory documentation, missing architecture files, partial migrations, historic mistakes, active PR stacks and unknown components.

## Three layers

| Layer | Holds | Rule |
| --- | --- | --- |
| **Framework ontology** | Sensemaking's shared vocabulary ([knowledge contract](knowledge-contract.md)) | Never extended because a domain uses unfamiliar nouns |
| **Target domain ontology** | The product's concepts, states, invariants, boundaries and rules | Expressed with the framework vocabulary (knowledge contract, "Target domain ontology") |
| **Target knowledge instances** | What the repository contains, proposes, decides and does not know | Source-linked, status-labelled, reviewed records |

Building a repository-specific ontology is not adding global schema types. Propose a narrow extension only when a real distinction cannot be represented ([schema evolution](schema-evolution.md)).

## Procedure

1. **Source identity:** Record repo, exact SHA and worktree state; read governing instructions. Current worktree may be dirty; use a separate clean worktree for index commands. When the CLI is available, `semantic knowledge-orient` against clean HEAD gives path orientation; inspect missing document conventions, truncation and non-Python source coverage, and search manually beyond recognized paths where important.
2. **Governing intent:** Retrieve current product goals, non-goals and accepted authority (owner decisions, ADRs, product documents). Date and scope contradictory claims; newer files are not automatically stronger authority.
3. **Domain discovery:** Identify the essential nouns, behaviors, states, domain distinctions and product rules. Separate application domain concepts from repository knowledge types, and note which terms must not be conflated.
4. **System discovery:** Identify the major capabilities and meaningful architectural and control boundaries. Trace capabilities to actual runtime owners, APIs and source paths; inspect JavaScript, SQL or other unsupported languages directly when needed; never infer runtime coupling from directories.
5. **Relationship discovery:** Trace important dependencies, ownership, lifecycle, persistence and data flow from original sources, with the tests that protect them.
6. **Evidence separation:** Mark what is observed, declared, hypothesized, contested and not assessed. Note discrepancies between declared architecture, tests and code; keep unverified interpretations hypothetical or contested. Mark areas `NOT_ASSESSED` rather than invent missing edges.
7. **Ontology representation:** Encode the useful domain and architecture knowledge with the existing vocabulary in `.sensemaking/knowledge/*.json`, split by meaningful owner boundaries. Cite current original sources instead of copying document passages wholesale. With schema_version 2, model each top-level component and each ADR still in force, or list it explicitly as `NOT_ASSESSED`; add `layer`, `bounded_context` and `architecture_rule` records only where a real rule or distinction needs one, and give every rule a `rule_type`, `severity` and `applies_to` scope. No minimum entry count is required.
8. **Review and persistence:** Validate claim contracts, source references and provenance (`knowledge-proposal-check` on committed or staged files) when authorized to write; use the normal PR review path for consequential conclusions. Build the SQLite snapshot externally at the new revision. If no Sensemaking CLI is installed, install it pinned before writing records (Steward `SKILL.md`, "Verify and pin the CLI"). If that is impossible, label the records as unvalidated drafts in the report and receipt; never present them as reviewed knowledge.
9. **Coverage report:** State the systems adequately represented, the areas not assessed, unsupported source formats, truncated selection, significant unresolved questions and the most valuable deepening opportunities. Put it in the task report and the session receipt; it is not a knowledge claim.
10. **Return to the controller:** Hand the foundation and coverage report back to `using-sensemaking`. A bootstrap selects no direction; possibility exploration is the controller's usual next responsibility for a repository-level goal.

## Missing or read-only knowledge

- **No `.sensemaking/` files:** start from the repository's actual source, product documents and history. That is a normal first visit.
- **Without write authority:** produce a source-grounded **provisional** model and coverage report in the task output. The controller may continue from it, but say that it was not persisted and later agents will not inherit it. Never claim retention.
- **Not required:** running product code, an exhaustive code inventory or a fixed graph density.

## Suggested competency questions

- What is the repository for; which outcomes and non-goals govern it?
- Which domain concepts must not be conflated?
- Which components own a named user-visible capability and persistence boundary?
- What evidence establishes an actual dependency versus an inferred association?
- Which tests protect a declared invariant, and which claimed guarantees remain unverified?
- What are the important rejected alternatives, open decisions and architecture debt?
- What changed since the latest reviewed understanding?
- Could a fresh agent answer an unfamiliar cross-system engineering question from sources reachable through the model?

## Stop rule

Bootstrap once per materially new target or inadequate knowledge foundation, then enrich incrementally. A later session retrieves and deepens; it does not repeat the bootstrap. Neither document count nor graph density is a completion metric. Finish with inspectable domain and architecture value and an honest coverage report.
