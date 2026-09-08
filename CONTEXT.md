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

Current implementation status is tracked in [the repository build-status record](docs/product/repository-build-status.md). The older [repository build plan](docs/product/chess-mentor-engine-repository-build-plan.md) remains authoritative for conceptual sequencing and historical planning rationale, but its time-sensitive `Current recommendation` section is historical where it conflicts with the build-status record or this context file.

M1 — Trustworthy Chess Evidence Substrate — is qualified and provides deterministic PGN ingestion into `SourceProvenance`, `CanonicalGame`, `CanonicalPosition`, and engine-free `PositionContextPacket` records. This is a bounded implementation contract, not evidence that the broader architecture is settled. It deliberately excludes engine evaluation, player reasoning, learner diagnosis, pedagogy, persistence, and UI. See [the M1 architecture note](docs/architecture/chess-evidence-substrate.md) and [the repository build plan](docs/product/chess-mentor-engine-repository-build-plan.md).

M2 — Deterministic Chess Feature Extraction — is qualified and derives an engine-free `PositionFeaturePacket` from a canonical position. The bounded feature surface contains legal moves, legal checks, legal captures, geometric square attackers, same-color piece defenders, and absolute king pins. Geometric attack is explicitly distinct from legal action. M2 remains objective chess evidence only; it adds no evaluation, threat labels, player reasoning, learner diagnosis, pedagogy, persistence, or UI. See [the M2 architecture note](docs/architecture/deterministic-chess-features.md) and [ADR 0001](docs/decisions/0001-chess-rules-provider-boundary.md).

M3 — Engine Evidence — is qualified under the frozen contract in ADR 0002. The repository provides provider-neutral engine-evidence records and request/result fingerprints, a fixture-backed `PrecomputedAnalysisProvider`, and an external `UciAnalysisProvider` that accepts an explicitly supplied engine executable rather than bundling one. The UCI provider records executable and engine provenance, normalizes centipawn and mate scores into the frozen White-perspective contract, supports MultiPV and depth/nodes/movetime requests, validates candidate roots and complete principal variations against the qualified chess-rules substrate, and preserves explicit complete/partial/terminal/failure semantics. Qualification combines deterministic fake-UCI protocol tests with an external Ubuntu Stockfish 16 witness over the frozen M3 position corpus. No engine binary is bundled, and M3 still adds no diagnostic position selection, player reasoning, learner diagnosis, pedagogy, persistence, or UI. See [the M3 architecture note](docs/architecture/engine-evidence.md) and [ADR 0002](docs/decisions/0002-engine-evidence-contract.md).

M4 — Diagnostic Position Selection — is qualified under the frozen ADR 0003 contract. M4B `DecisionComparison` derives the actual played move from canonical game history, independently replays that move to the canonical child FEN, compares compatible complete exact M3 evidence from mover perspective, preserves mate and terminal outcomes symbolically, and keeps partial/failure/bound/incompatible/engine-inversion states explicit. M4C `SelectionSignal` + `DiagnosticCandidate` derives deterministic objective signals from matching M2/M3/M4B evidence, preserves successful decisions and raw top-candidate separation without universal thresholds, suppresses ordered engine-derived signals when evidence is partial, and records immutable candidates with explicit policy identity and eligibility-signal provenance. M4D `SelectionPolicy` + `DiagnosticCandidateBatch` evaluates objective signals under explicit versioned policy configuration, records inspectable threshold/rule matches, supports operational successful controls, applies quotas and per-game caps, rejects policy-configuration drift through a full policy fingerprint, and constructs deterministic bounded batches with source-pool provenance, exclusions, and visible size/control/quota shortfalls. M4D deliberately defers near-duplicate similarity heuristics until a precise deterministic rule exists. M4Q then qualified the complete bounded selection path against the frozen 12-category M4A corpus plus terminal, partial, bound, failure, inversion, incompatible-analysis, deterministic replay, policy-version, exclusion, and shortfall cases. The exact M4 claim remains objective only: Chess Mentor Engine can derive transparent, provenance-rich objective decision comparisons and use versioned deterministic policies to select bounded candidate sets containing both potentially informative decisions and successful controls. M4 does not infer why a player made a move, a stable learner weakness, recurrence, pedagogical value, intervention efficacy, or learning. M5 — Player Decision Evidence — is now authorized next but has not started. See [the frozen M4A contract](docs/architecture/diagnostic-position-selection.md), [the M4B implementation record](docs/architecture/decision-comparison.md), [the M4C implementation record](docs/architecture/selection-signals-and-candidates.md), [the M4D implementation record](docs/architecture/selection-policy-and-batches.md), [the full M4 qualification record](docs/architecture/m4-qualification.md), [ADR 0003](docs/decisions/0003-diagnostic-position-selection-contract.md), and [the current build-status record](docs/product/repository-build-status.md).

The current product-discovery direction is to test an evidence-backed recurring decision diagnosis with regular online players approximately rated 1400-1800. This is a working hypothesis, not a permanent rating boundary. See [product discovery](docs/product/product-discovery.md) for the reasoning and validation plan.

The first validation protocol is designed and frozen, but not executed. Product validation remains authoritative for claims about learner diagnosis and tutoring value. See [the experiment protocol](docs/research/first-product-validation/README.md).

Pilot 001 produced a mixed, participant-specific result. P01 reported that the analysis was not helpful because the board context was not included. Pilot 002 produced a mixed, participant-specific result: board context improved explanation and direct player evidence added information, but responses were sparse. Pilot 003 freezes a clean instrument-calibration design but remains blocked on unexposed P02. Pilot 004 is a separate, explicitly instrument-aware N-of-1 design for P01 and does not replace Pilot 003. None of these pilots changes the frozen main protocol.
