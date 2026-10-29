# Schema evolution — domain-specific richness without uncontrolled types

Start with the stable common vocabulary. A target's domain ontology is a set of knowledge instances in that vocabulary (knowledge contract, "Target domain ontology"); an unfamiliar domain is not a schema gap. Domain terms such as Auteur's StoryIdentity, Working proposal, Book Workspace, accepted Expression and Layer-4 Expression may first be `domain_concept`, `capability`, `contract` or `component` with sourced, scoped attributes.

Escalate to a reusable schema/domain pack only when concrete engineering questions cannot faithfully distinguish necessary meanings with supported types and relationships.

For each proposed extension:
1. Preserve examples from actual source and current questions that fail under existing vocabulary.
2. Explain the missing distinction and alternatives (attributes, reference, controlled typed extension, no change).
3. Define stable identities, relationship direction and epistemic/authority meaning.
4. Prove compatibility with old Git-authored records, snapshots, queries and currentness audits.
5. Specify migrations and reversible validation, including historical re-index behavior.
6. Obtain the required schema/owner authority before a permanent shared ontology change.

Avoid repository-specific type proliferation, sweeping renames, compulsory schema-v2 migrations, or treating generated classifications as architectural truth. A target can have rich concepts without modifying Sensemaking's universal schema.

## Recorded extension: architecture and ontology (ADR 0033)

Passed this gate: `docs/semantic-architecture/architecture-ontology-competency-v1.md`
tested 15 questions; eight were not expressible. The additions target
those needs plus the explicitly justified `exposes` contract-clarification predicate (path-scoped rules, cardinality, lifecycle,
layers and contexts, data flow, confusable terms). Version-1 documents and the
store version are unchanged.
