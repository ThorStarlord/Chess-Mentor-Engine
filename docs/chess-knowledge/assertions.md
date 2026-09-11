# Chess Knowledge Assertions

**Schema:** `chess-knowledge-assertion.v1`  
**Bundle schema:** `chess-knowledge-assertion-bundle.v1`

## Purpose

A `ChessConcept` defines vocabulary. A `KnowledgeAssertion` binds one concept to a
specific chess subject with exact provenance, evidence references, ontology identity,
and authority.

```text
ChessConcept
    "what does fork mean?"

KnowledgeAssertion
    "under detector X v1, move Nxf7 creates tactic.fork in position P"

ReasoningDiscrepancy / LearnerHypothesis
    "what participant evidence justifies saying about this player's reasoning"
```

These are deliberately separate authorities.

## Subject types

Assertions can bind to:

```text
position
move
move_sequence
position_comparison
```

Every subject includes a canonical `position_id`; game/ply identity can be included
when available. Move and move-sequence subjects must carry their exact UCI move data.
A position comparison must name both position identities.

## Evidence references

Every assertion requires at least one exact evidence reference. Supported reference
families include:

```text
canonical_position
position_features
engine_analysis
move_sequence
external_tag
human_review
model_output
```

References carry both a stable source ID and a SHA-256 fingerprint. An assertion
therefore cannot be validated against a semantically different evidence artifact that
merely reuses the same display label.

## Provenance

Assertion provenance records:

```text
source_kind
source_id
source_version
source_fingerprint
optional run_id
```

Source kind constrains authority:

| Source | Required assertion authority |
| --- | --- |
| detector | the registered concept's declared default assertion authority |
| engine | `engine_derived` |
| external taxonomy | `external_taxonomy_tag` |
| model | `model_interpretation` |
| human | `human_ratified` |
| deterministic system rule | rule/deterministic authority only |

This is a claim ceiling, not a confidence ranking.

## External taxonomy authority

`external_taxonomy_tag` is intentionally separate from CME detector authority.

For example, importing a Lichess `fork` tag can create:

```text
concept: tactic.fork
status: supported
authority: external_taxonomy_tag
source: lichess.puzzle_theme
```

That means the external source classified its item with a tag whose crosswalk is
exact enough for this ontology concept. It does **not** mean a CME detector proved the
fork.

For a broader mapping such as Lichess `pin`, the projection yields both internal pin
subtypes with `plausible` status:

```text
tactic.absolute_pin  plausible  external_taxonomy_tag
tactic.relative_pin  plausible  external_taxonomy_tag
```

A downstream consumer may not silently choose one subtype.

## Deterministic assertions

Rule/position/sequence deterministic authorities must use binary assertion status:

```text
present
absent
```

They cannot use `plausible` or `supported`, because uncertainty belongs to a weaker
or different derivation contract rather than a supposedly deterministic claim.

## Identity

Assertion fingerprints include:

```text
schema version
concept ID + exact concept fingerprint
exact ontology fingerprint
subject
status + authority
qualifiers
evidence refs
provenance
claim scope
created-at timestamp
```

The content fingerprint determines the assertion ID (`cka_<digest prefix>`).

Bundles use the same principle and bind to exact assertion references. Given the same
inputs—including the same explicit timestamp—the same assertion/bundle rebuilds to
the same ID and fingerprint.

## Bundles

A `KnowledgeAssertionBundle` contains assertions for one exact subject and one exact
ontology version/fingerprint. Mixed-subject assertions are rejected.

Bundles are useful for later detector output and coaching projection, but bundling
does not strengthen the authority of any individual assertion.

## Learner boundary

An assertion cannot establish:

```text
that the participant perceived the concept
that the participant failed because of the concept
that the concept is a recurring weakness
that training on the concept is applicable
that an intervention caused improvement
```

Those claims remain under the existing participant-evidence, M6/M7, M9, and M10/M11
contracts.

## Validation failures are intentional

Validation rejects at least:

- unknown ontology concept IDs;
- stale concept or ontology fingerprints;
- concept-group assertions;
- detector authority drift;
- source/authority mismatches;
- deterministic assertions expressed as uncertainty;
- malformed subject shapes;
- missing or duplicate evidence references;
- duplicate qualifier names;
- mixed-subject bundles;
- tampered content-addressed identities.
