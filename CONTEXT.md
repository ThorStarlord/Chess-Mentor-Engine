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

The repository remains in foundation, product-discovery, and early bounded product-development work. No complete production domain model or end-to-end implementation architecture should be considered frozen yet.

M1 — Trustworthy Chess Evidence Substrate — is qualified and provides deterministic PGN ingestion into `SourceProvenance`, `CanonicalGame`, `CanonicalPosition`, and engine-free `PositionContextPacket` records. This is a bounded implementation contract, not evidence that the broader architecture is settled. It deliberately excludes engine evaluation, player reasoning, learner diagnosis, pedagogy, persistence, and UI. See [the M1 architecture note](docs/architecture/chess-evidence-substrate.md) and [the repository build plan](docs/product/chess-mentor-engine-repository-build-plan.md).

M2 — Deterministic Chess Feature Extraction — is qualified and derives an engine-free `PositionFeaturePacket` from a canonical position. The bounded feature surface contains legal moves, legal checks, legal captures, geometric square attackers, same-color piece defenders, and absolute king pins. Geometric attack is explicitly distinct from legal action. M2 remains objective chess evidence only; it adds no evaluation, threat labels, player reasoning, learner diagnosis, pedagogy, persistence, or UI. See [the M2 architecture note](docs/architecture/deterministic-chess-features.md) and [ADR 0001](docs/decisions/0001-chess-rules-provider-boundary.md).

M3A — Engine Evidence Contract — is designed and frozen for implementation, but no engine provider or evaluation runtime has been implemented yet. The contract fixes White-perspective score normalization, disjoint centipawn/mate representations, mate normalization to winner plus plies-to-mate, MultiPV/request identity, engine provenance, request/result fingerprints, and explicit complete/partial/terminal/failure semantics. The first implementation step is a precomputed provider; only afterward may an external UCI provider be added. No engine binary bundling is authorized by this contract. See [the M3 architecture note](docs/architecture/engine-evidence.md) and [ADR 0002](docs/decisions/0002-engine-evidence-contract.md).

The current product-discovery direction is to test an evidence-backed recurring decision diagnosis with regular online players approximately rated 1400-1800. This is a working hypothesis, not a permanent rating boundary. See [product discovery](docs/product/product-discovery.md) for the reasoning and validation plan.

The first validation protocol is designed and frozen, but not executed. Product validation remains authoritative for claims about learner diagnosis and tutoring value. See [the experiment protocol](docs/research/first-product-validation/README.md).

Pilot 001 produced a mixed, participant-specific result. P01 reported that the analysis was not helpful because the board context was not included. Pilot 002 produced a mixed, participant-specific result: board context improved explanation and direct player evidence added information, but responses were sparse. Pilot 003 freezes a clean instrument-calibration design but remains blocked on unexposed P02. Pilot 004 is a separate, explicitly instrument-aware N-of-1 design for P01 and does not replace Pilot 003. None of these pilots changes the frozen main protocol.
