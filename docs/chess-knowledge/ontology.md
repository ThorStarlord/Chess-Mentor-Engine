# Chess Knowledge Ontology

**Schema:** `chess-knowledge-ontology.v1`  
**Current composed content version:** `1.1.0`  
**Authority:** Semantic vocabulary and assertion metadata; not learner-state or engine authority.

## Purpose

The Chess Knowledge Ontology (CKO) is the semantic bridge between Chess Mentor
Engine's qualified chess evidence and human-readable coaching concepts.

It exists so the repository can represent, without conflating:

```text
board / move facts
        ↓
tactical or strategic concepts
        ↓
positional assessment factors
        ↓
plans / move rationale
        ↓
pedagogical explanation
```

The ontology is deliberately not a replacement for engine analysis, participant
evidence, M6 reasoning discrepancy, M7 learner hypotheses, M9 intervention selection,
M10 transfer evidence, M11 longitudinal state, M16 deterministic feedback, or M19
model rendering.

## Core invariant

```text
concept definition != concept assertion != learner inference
```

`ChessConcept` answers **what does this concept mean?**

A later `KnowledgeAssertion` answers **what evidence supports saying this concept
applies here?**

M6/M7 answer **what does this position-level evidence and repeated participant-local
evidence justify saying about the learner?**

No layer may silently skip the one below it.

## Concept kinds

| Kind | Typical examples | Typical assertion authority |
| --- | --- | --- |
| `rule_fact` | check, legal state | rule-derived |
| `position_feature` | isolated pawn, open file | deterministic position fact |
| `tactical_motif` | fork, absolute pin | deterministic or sequence pattern where qualified |
| `mating_pattern` | back-rank mate | often heuristic/pattern-derived until detector-qualified |
| `defensive_resource` | fortress, perpetual check | often heuristic |
| `strategic_principle` | develop pieces, trade pieces when ahead | heuristic |
| `evaluation_factor` | king safety, activity, space | heuristic or engine-supported interpretation |
| `plan` | create pawn break, improve worst piece | contextual proposal |
| `pedagogical_concept` | recognition cue, calculation habit | instructional |

Concept groups exist only to organize the graph and should not normally be asserted
against positions.

## Stable identity

Machine IDs use lowercase dotted namespaces, for example:

```text
tactic.fork
tactic.absolute_pin
position.isolated_pawn
principle.opening.tempo_economy
evaluation.king_safety
plan.improve_worst_piece
```

Display names and translations may change while IDs remain stable. An ID must never
be reused for a different semantic concept.

## Detection support

Every concept declares one of:

```text
none
    vocabulary/group only; no detector implied

deterministic
    current concept is suitable for position-local deterministic derivation

sequence_based
    requires a move or move-sequence transition, not a static label

heuristic
    depends on contextual interpretation or an explicitly bounded heuristic

external_only
    currently imported/mapped from an external taxonomy only
```

Detection support is a capability classification, not proof that a detector already
exists. Detector implementation and detector qualification remain separate.

## Authority classes

Every future assertion must use an explicit authority class:

```text
rule_derived
deterministic_position_fact
deterministic_sequence_pattern
engine_derived
heuristic_assessment
model_interpretation
human_ratified
```

These classes prevent a useful coaching label from being mistaken for a stronger
kind of evidence.

## Relationships

The ontology supports explicit graph relationships including:

```text
related_to
requires
enables
exploits
prevents
supports
commonly_conflicts_with
overrides_under_condition
is_evidence_for
is_not_sufficient_for
```

Parent links form the concept hierarchy. Graph validation rejects unknown parents,
unknown relation targets, duplicate IDs, ambiguous aliases, forbidden exact external
mapping collisions, and parent cycles.

## Strategic conflicts

Principles are not universal laws. The ontology represents conflicts explicitly.
Examples in content version 1.1 include:

```text
trade pieces when materially ahead
vs
preserve piece pressure when a space advantage depends on congestion

opening king safety
vs
active king use in the endgame

opening pawn-move restraint
vs
execute a concrete pawn break
```

The presence of both principles is not an ontology contradiction. The position and
qualified evidence determine relevance.

See [`strategic-principles.md`](strategic-principles.md).

## Evaluation factors are not score decomposition

The ontology may support statements such as:

```text
space: favorable for White
pawn structure: unfavorable for White
king safety: approximately balanced
```

Those statements do not imply an arithmetic decomposition of a Stockfish score.
Engine score identity and provenance remain under the engine-analysis contract.

See [`positional-evaluation.md`](positional-evaluation.md).

## Plans are separate from moves and interventions

A plan such as `plan.create_pawn_break` is a contextual chess objective. It is not a
claim that a particular move is engine-best, and it is not an M9 training
intervention.

See [`plans.md`](plans.md) and [`pedagogy.md`](pedagogy.md).

## External mappings

External taxonomies are mapped through explicit namespaces. The first mapping
namespace is:

```text
lichess.puzzle_theme
```

Mappings declare whether the external term is `exact`, `broader`, `narrower`, or
`related` to the CME concept. Multiple internal concepts may intentionally be
returned for one broader external label.

See [`lichess-compatibility.md`](lichess-compatibility.md).

## Machine-readable sources

The default registry is composed from versioned resource fragments:

```text
src/chess_mentor_engine/chess_knowledge/data/ontology.v1.json
    tactical / mating / defensive vocabulary

src/chess_mentor_engine/chess_knowledge/data/strategy.v1.json
    rule facts / position features / strategic principles /
    evaluation factors / plans
```

The current registry content version is the latest fragment version, `1.1.0`. Every
fragment is independently validated, then the combined graph is validated again.
This catches collisions between concept families while allowing the vocabulary to
grow without turning one JSON file into an unmaintainable monolith.

Runtime loading uses only the Python standard library.

The registry exposes deterministic document and per-concept fingerprints so later
artifacts can bind to exact ontology semantics.

## Current implementation boundary

The registry now includes tactical vocabulary, Lichess compatibility mappings,
mechanically representable rule/position features, strategic principles, positional
evaluation factors, plans, and selected pedagogical metadata.

Position-specific assertion objects, qualified detectors, coaching-context
projection, and learner-evidence integration are later packages in this ontology
program.

The ordering remains intentional:

```text
vocabulary
-> assertion contract
-> detector qualification
-> coaching projection
-> learner integration
```

A vocabulary entry must not be mistaken for evidence merely because it exists.

## Non-goals

CKO v1 does not claim:

- comprehensive coverage of all chess literature;
- automatic detection of every registered concept;
- causal decomposition of Stockfish evaluations;
- that a motif present on the board was perceived by the participant;
- that one missed motif establishes a learner weakness;
- that a heuristic principle determines the best move;
- that external taxonomy tags are objective CME evidence;
- that ontology-enriched model prose is semantically correct merely because it is
  grounded to registered concepts.

## Extension rule

New ontology work should be pulled by a concrete analysis, learner, tutoring, or
consumer need. Prefer a small well-defined concept with clear authority over a broad
vocabulary whose semantics cannot be qualified.
