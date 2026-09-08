# 0002 — Engine evidence contract

**Status:** Accepted for M3 implementation  
**Date:** 2026-09-08

## Context

M1 qualified canonical game/position evidence and M2 qualified deterministic
engine-free board features. The next layer needs engine judgment, but introducing a
Stockfish process directly into application code would make provider-specific score,
MultiPV, process, and failure conventions leak throughout the repository.

Engine analysis also differs fundamentally from M1/M2 deterministic evidence. A
search result can vary with engine version, options, search limits, thread count,
runtime environment, and implementation details even when the source board is
identical.

Before implementing any engine process integration, Chess Mentor Engine therefore
needs a frozen normalized contract for what engine evidence means.

## Decision

### 1. Keep engine providers behind a normalized boundary

Introduce a provider contract equivalent to:

```text
ChessAnalysisProvider
analyze(CanonicalPosition, AnalysisRequest)
    → PositionAnalysis | AnalysisFailure
```

Downstream code consumes normalized records and must not parse UCI output or depend
on Stockfish-native score conventions.

### 2. Canonical evaluation perspective is White

All normalized evaluations use a fixed White perspective.

For centipawn scores:

```text
positive → favors White
negative → favors Black
```

The side to move does not change the stored sign convention.

### 3. Centipawn and mate scores are disjoint types

Do not encode forced mate as an extreme centipawn sentinel.

Centipawn evidence stores a signed integer score plus an explicit score bound.

Mate evidence stores:

```text
winner: white | black
plies_to_mate: non-negative integer
```

Provider adapters must translate their native convention into this representation.
For UCI adapters, native `score mate N` uses moves rather than plies and negative
values mean the engine side is being mated. That provider convention is normalized
before evidence reaches downstream code.

### 4. Preserve score bounds

Engine scores can be:

```text
exact
lower
upper
```

A lower/upper bound must not be silently promoted to an exact evaluation.

### 5. Best move derives from ranked candidate line 1

`CandidateLine` is the canonical root-candidate representation.

It contains at least:

```text
rank
root_move_uci
evaluation
pv_uci
```

`best_move` is derived from rank 1 rather than stored independently.

### 6. MultiPV is part of evidence identity

The requested MultiPV count is part of `AnalysisRequest` and the request
fingerprint. Results produced under different MultiPV values are not treated as the
same analysis conditions even when their top move matches.

### 7. Search limit and safety timeout are separate

The first M3 slice supports exactly one primary engine search limit:

```text
depth
nodes
movetime_ms
```

A provider supervisor timeout is a separate application safety boundary. Both are
recorded.

Clock-management searches, infinite search, ponder, mate-search limits, and
restricted search moves are deferred.

### 8. Provenance is mandatory and completeness is explicit

A normalized analysis records provider identity, engine identity/version where
known, normalized engine options, and available executable/artifact hashes.

Missing binary/artifact hashes are allowed when a provider cannot establish them,
but their absence must not be hidden or replaced with fabricated identity.

### 9. Request fingerprint and result fingerprint are different

The request fingerprint identifies normalized analysis conditions, including source
FEN, provider/engine identity, options, limits, timeout, and MultiPV.

The result fingerprint identifies the exact normalized result record.

Two analyses may share a request fingerprint and legitimately have different result
fingerprints. Engine evidence is provenance-bound; M3 does not promise byte-for-byte
search determinism.

### 10. Engine analysis is rooted in board state, while provenance remains linked to the game

Request identity uses source FEN rather than game-specific `position_id` alone so
future compatible caching/reuse of identical board states remains possible.

Every stored analysis still records the requesting `position_id` for audit and game
provenance.

No persistent cache is authorized in M3.

### 11. Played-move loss is derived later

A `PositionAnalysis` describes one root board state.

Do not mix `evaluation_before`, `evaluation_after_played_move`, or centipawn-loss
fields into the same root analysis. Later diagnostic selection compares analyses of
distinct positions explicitly.

### 12. Complete, partial, terminal, and failed outcomes are distinguishable

Valid normalized analysis can be:

```text
complete
partial
terminal
```

If no trustworthy normalized evidence exists, return an explicit failure such as:

```text
ENGINE_NOT_FOUND
ENGINE_START_FAILED
ENGINE_CRASHED
ANALYSIS_TIMEOUT
PROTOCOL_ERROR
INVALID_ENGINE_OUTPUT
UNSUPPORTED_REQUEST
CANCELLED
```

Timeout/crash must not masquerade as a successful analysis with an empty line set.

### 13. Implement a precomputed provider before a UCI provider

The first implementation step is normalized models plus a
`PrecomputedAnalysisProvider` using frozen fixtures.

Only after that contract is qualified should an external UCI/Stockfish adapter be
implemented.

### 14. Do not bundle an engine executable in the first M3 slice

The first UCI provider will use an explicitly configured external executable
path/command.

Bundling or redistributing an engine binary requires a separate explicit
licensing/distribution decision and is not authorized by this ADR.

## Consequences

### Positive

- Engine-specific process and score conventions stay outside downstream product
  logic.
- Player and learner layers can cite stable engine-evidence records without knowing
  which provider produced them.
- Mate semantics are unambiguous and do not depend on score sentinels.
- MultiPV and search-limit changes remain visible in evidence identity.
- Partial/failure evidence cannot be mistaken for a chess conclusion.
- Future precomputed, UCI, or other providers can share one domain representation.
- Future position-analysis caching remains possible without confusing board identity
  with game provenance.

### Costs

- Provider adapters must perform explicit score/perspective normalization.
- Provenance handling is more verbose than storing a raw engine number.
- Engine results under identical requests may still differ, so research workflows
  must not assume bitwise search determinism.
- A separate engine-distribution decision remains necessary if the product later
  wants to bundle a binary.

## Alternatives rejected for M3

### Store engine-native signed scores directly

Rejected because consumers would need provider-specific perspective and mate
knowledge and could silently invert evaluations.

### Encode mate as a huge centipawn value

Rejected because mate and centipawn judgments have different semantics.

### Couple the domain directly to Stockfish/UCI

Rejected because Stockfish is a provider candidate, not the engine-evidence domain
model.

### Store `best_move` independently from candidate rank 1

Rejected because duplicated authoritative fields can diverge.

### Call engine output deterministic when request inputs match

Rejected because search can vary even under nominally identical conditions.

### Bundle Stockfish as part of initial M3 implementation

Rejected for the first slice because executable distribution is a separate
licensing/product decision and is unnecessary to prove the provider contract.

## Deferred decisions

This ADR does not decide:

- WDL normalization;
- tablebase contracts;
- persistent analysis caching;
- cloud engine APIs;
- engine binary redistribution;
- cross-engine score calibration;
- diagnostic teaching thresholds;
- player reasoning or learner inference.

## Revisit triggers

Revisit this ADR if:

- a provider cannot faithfully map into the normalized evaluation model;
- WDL/tablebase evidence becomes necessary to the next validated product slice;
- a persistent analysis cache is introduced;
- engine binary bundling/distribution is proposed;
- cross-engine comparison becomes a product requirement;
- M3 implementation evidence demonstrates that a frozen field or invariant is
  materially insufficient.

## Evidence basis

- M1 and M2 are qualified on `main`.
- M2 established the rule that deterministic chess facts remain distinct from
  engine evaluation.
- The repository roadmap already places engine abstraction before diagnostic
  position selection and learner evidence.
- UCI mate reporting uses moves rather than plies and uses signed mate distance;
  provider adapters therefore need an explicit normalization boundary.
