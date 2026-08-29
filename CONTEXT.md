# Chess Mentor Engine context

## Product

Chess Mentor Engine is a persistent chess learning system intended to convert objective chess evidence into individualized teaching decisions.

## Current product hypothesis

The system may eventually combine:

- chess-engine analysis;
- game-history analysis;
- persistent learner modeling;
- misconception hypotheses;
- personalized curriculum selection;
- targeted exercises;
- adaptive explanation;
- mastery and progress evidence.

These remain hypotheses until validated.

## Fundamental separation of responsibilities

The following authority layers are provisional and should be refined through architecture work.

### Objective chess authority

Potentially owned by deterministic chess tooling or engines:

- legal moves;
- board state;
- tactical and positional evaluation;
- principal variations;
- tablebase truth;
- objective move comparisons.

### Application authority

Potentially owned by deterministic application logic:

- provenance;
- attempt history;
- evidence aggregation;
- progress state;
- curriculum bookkeeping;
- persistence rules.

### Tutoring intelligence

Potentially owned partly by model-based reasoning:

- pedagogical explanations;
- Socratic questioning;
- misconception hypotheses;
- lesson framing;
- adaptive presentation.

## Critical product distinction

```text
What is the best move?
Why is it the best move?
Why did this player fail to find it?
```

The third question is the primary differentiation hypothesis.

## Current stage

The repository is in the foundation and product-discovery stage. No production domain model or implementation architecture should be considered frozen yet.

The current product-discovery direction is to test an evidence-backed recurring decision diagnosis with regular online players approximately rated 1400-1800. This is a working hypothesis, not a permanent rating boundary. See [product discovery](docs/product/product-discovery.md) for the reasoning and validation plan.

The first validation protocol is designed and frozen, but not executed. Product validation should happen before domain modeling or implementation. See [the experiment protocol](docs/research/first-product-validation/README.md).
