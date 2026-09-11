# ADR 0012 — Chess Knowledge Ontology authority contract

**Status:** Accepted  
**Scope:** Repository-only semantic vocabulary and knowledge assertions  
**Decision owner:** Chess Mentor Engine repository

## Context

Chess Mentor Engine already separates objective chess evidence, participant evidence,
reasoning discrepancy, learner hypotheses, interventions, model rendering, evaluator
judgment, and longitudinal outcomes. The next product phase needs stable semantic
identities for tactical motifs, strategic principles, evaluation factors, plans, and
pedagogical concepts.

Without a first-class vocabulary, downstream systems would tend to pass ad-hoc text
labels such as `fork`, `bad bishop`, or `center control`. Those labels are useful for
language generation but insufficient as evidence contracts: they do not identify the
ontology version, detection method, authority ceiling, external taxonomy relation, or
whether the label describes vocabulary versus a claim about one concrete position.

The repository also already has M7C recurrence assessment. The ontology must not
create a parallel learner-recurrence authority.

## Decision

Create a versioned **Chess Knowledge Ontology (CKO)** as a sibling domain to chess,
analysis, evidence, learning, evaluation, training, and coaching.

The foundational invariant is:

```text
ChessConcept definition
        !=
position/move KnowledgeAssertion
        !=
ReasoningDiscrepancy
        !=
LearnerHypothesis / recurrence assessment
```

A definition states what a concept means. It is not evidence that the concept occurs
in a position. An assertion may claim that a concept applies to a bounded position,
move, or move sequence, but must carry derivation provenance, evidence references,
exact ontology identity, and an authority class. Learner-level conclusions continue
to require the existing M6/M7 evidence chain.

## Concept domains

CKO v1 supports these semantic kinds:

- concept groups;
- rule facts;
- position features;
- tactical motifs;
- mating patterns;
- defensive resources;
- strategic principles;
- evaluation factors;
- plans;
- pedagogical concepts.

A concept has a stable machine identifier independent of display wording, for
example `tactic.deflection`. IDs are never recycled for a different meaning.

## Assertion authority classes

The ontology/assertion layer distinguishes:

```text
rule_derived
deterministic_position_fact
deterministic_sequence_pattern
engine_derived
external_taxonomy_tag
heuristic_assessment
model_interpretation
human_ratified
```

These classes are claim ceilings, not confidence scores and not an ordinal ranking.

Important examples:

```text
absolute pin                    -> deterministic_position_fact
move creates a double check     -> deterministic_sequence_pattern
engine score                    -> engine_derived
Lichess puzzle theme            -> external_taxonomy_tag
initiative                      -> heuristic_assessment
prophylactic model explanation  -> model_interpretation
explicit coach ratification     -> human_ratified
```

A detector may assert only the default authority registered for its concept. Engine,
external, model, human, and deterministic-system provenance are restricted to their
corresponding authority families.

## External taxonomy policy

External vocabularies such as Lichess puzzle themes are compatibility mappings, not
CME authority.

A mapping records both an external identifier and a semantic relation:

```text
exact
broader
narrower
related
```

One external identifier may intentionally map to multiple CME concepts. For example,
a broad external `pin` label may map to both `tactic.absolute_pin` and
`tactic.relative_pin`; consumers may not silently choose one without additional
evidence.

External taxonomy assertions retain `external_taxonomy_tag` authority even for an
exact mapping. External taxonomy drift must be explicit. Unknown themes are not
silently promoted into new ontology concepts.

## Assertion identity policy

Position/move assertions are content-addressed artifacts. Their exact identity binds:

- concept ID and concept fingerprint;
- ontology fingerprint;
- chess subject identity;
- assertion status and authority;
- qualifiers;
- exact evidence references;
- source provenance/version/fingerprint;
- claim scope;
- explicit timezone-aware creation timestamp.

Deterministic assertions use `present` or `absent`; uncertainty must use a weaker or
different derivation authority rather than weakening a supposedly deterministic
claim in place.

Assertion bundles may group only assertions for the same exact subject and ontology
identity. Bundling does not increase assertion authority.

## Strategic-principle policy

Chess principles are heuristics, not laws. A principle definition may contain
applicability, conflicts, prerequisites, and exceptions. The presence of a position
feature does not by itself prove that a principle was violated or that a specific
move was best.

## Evaluation policy

An evaluation factor is not an arithmetic decomposition of an engine score.

The repository may state that White has favorable space or an unfavorable pawn
structure when the relevant assessment authority supports those claims. It may not
pretend these factors numerically sum to Stockfish's score unless a separately
qualified method establishes such a decomposition.

## Learner-authority policy

CKO does not authorize any of the following shortcuts:

```text
motif present
-> player noticed motif

motif present + bad move
-> player missed motif

motif missed once
-> recurring learner weakness

recurring concept label
-> causal cognitive explanation

concept assertion
-> training intervention selected
```

M6/M7/M9/M10/M11 remain authoritative for their existing responsibilities. M7C
recurrence assessment remains the recurrence authority; future ontology integration
may attach typed concept references to its evidence without replacing its policy,
contradiction review, independence rules, or lifecycle.

## LLM policy

Ontology context may constrain and enrich model language, but it does not make model
prose objective truth. M16 remains the deterministic mentor-grounding ceiling unless
a later explicit contract extends it. M19 remains a language-rendering boundary.

## Versioning

The ontology has separate schema and content versions.

- New compatible concepts or mappings may advance the content minor version.
- Wording clarifications that preserve meaning may advance a patch version.
- A semantic meaning change must use a new stable concept ID or a clearly versioned
  breaking change.
- Deprecated concepts remain addressable; IDs are not silently reused.

## Consequences

### Positive

- Stable concept identities can connect engine evidence, explanation, learner
  evidence, and training without relying on free-text labels.
- Deterministic and heuristic concepts can coexist without authority collapse.
- Lichess interoperability becomes explicit rather than structurally controlling.
- Position/move claims become independently traceable and tamper-evident.
- Future recurrence and teaching-policy work can use durable semantic references.

### Costs

- Ontology curation and detector qualification are separate work.
- A concept being present in the registry does not imply automatic detection.
- Some concepts will remain heuristic or human/model interpreted.
- Assertions add identity/provenance objects that downstream consumers must preserve.

## Rejected alternatives

### Use only Lichess puzzle tags

Rejected because the external vocabulary mixes tactical motifs with mating patterns,
phase labels, puzzle metadata, evaluation buckets, and source categories, and it does
not define CME's learner/evidence authority.

### Hard-code strings directly in prompts

Rejected because free-text labels have no stable identity, provenance, version, or
claim ceiling.

### Let the LLM identify all concepts from FEN

Rejected because this would move chess-knowledge assertion authority into the model
and defeat the repository's evidence-first architecture.

### Treat an exact external mapping as detector evidence

Rejected because semantic crosswalk accuracy does not prove that CME independently
derived the concept from the supplied position or move sequence.

### Create a new recurrence engine around ontology concepts

Rejected because M7C already owns qualified participant-specific recurrence
assessment. Ontology integration must compose with that system rather than bypass it.
