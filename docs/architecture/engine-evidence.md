# M3 — Engine Evidence Contract

## Status

**Contract frozen for M3 implementation. Implementation has not started.**

This document defines how Chess Mentor Engine will represent engine judgment without
making any particular engine, executable, or UCI process the domain model. M1 and M2
remain the qualified deterministic chess-truth substrate.

The contract is constrained by ADR 0002.

## Boundary

M3 will add provider-produced objective evaluation evidence on top of the qualified
position substrate:

```text
CanonicalPosition
+ PositionContextPacket
+ PositionFeaturePacket
        ↓
ChessAnalysisProvider
        ↓
PositionAnalysis
```

M3 does **not** infer player reasoning, diagnose a learner, select pedagogy, or claim
that an engine score explains why a player chose a move.

```text
deterministic chess fact
≠ engine judgment
≠ player evidence
≠ learner inference
```

## Engine evidence is provenance-bound, not deterministic truth

M1/M2 outputs are designed to be deterministic for the same canonical input. Engine
search is different. Search results can vary with engine version, options, search
limits, thread count, runtime environment, and implementation details.

M3 therefore freezes the **request and provenance semantics**, not a claim that two
identical requests must return byte-identical results.

A stored analysis means:

> this engine/provider produced this normalized evidence for this position under
> these recorded conditions.

It does not mean:

> every compatible engine run must reproduce the same score or principal variation.

## Domain concepts

The initial M3 implementation should introduce concepts equivalent to:

```text
ChessAnalysisProvider
AnalysisRequest
AnalysisLimit
EngineProvenance
PositionAnalysis
CandidateLine
Evaluation
AnalysisMetrics
AnalysisTermination
AnalysisFailure
```

Names may change during implementation only if semantics remain identical or ADR
0002 is deliberately revised.

## Analysis request

An `AnalysisRequest` is separate from the position being analyzed.

Initial request fields:

```yaml
multipv: 1
search_limit:
  kind: depth | nodes | movetime_ms
  value: positive_integer
supervisor_timeout_ms: positive_integer | null
```

### Search limit

Exactly one primary search limit is allowed in the first M3 slice:

- `depth`;
- `nodes`;
- `movetime_ms`.

Clock-management searches, `go infinite`, `go mate`, ponder mode, and restricted
`searchmoves` are deferred.

### Supervisor timeout

The provider's wall-clock safety timeout is not the same thing as the engine search
limit.

For example:

```text
search limit: depth 20
supervisor timeout: 30 seconds
```

means the engine is asked to reach depth 20 but the application will stop waiting
if the external process exceeds the safety boundary.

Both values belong in provenance/request identity.

## Canonical evaluation perspective

Every normalized M3 evaluation uses a fixed **White perspective**.

For centipawn evaluations:

```text
positive → favors White
negative → favors Black
zero     → neutral engine score
```

The canonical representation is conceptually:

```yaml
kind: centipawn
perspective: white
centipawns: 84
bound: exact | lower | upper
```

`perspective` is frozen as `white` for M3. It is explicit in serialized evidence so
consumers never need to infer sign convention from side to move.

Centipawn values are engine scores, not probabilities and not cross-engine universal
units. Comparisons must remain aware of engine provenance and settings.

## Forced-mate evaluation

Forced mate is **not** represented by a sentinel centipawn value such as `100000`.

The canonical mate representation is conceptually:

```yaml
kind: mate
perspective: white
winner: white | black
plies_to_mate: positive_integer | 0
bound: exact | lower | upper
```

`plies_to_mate = 0` is reserved for an already terminal checkmated position if a
provider returns such normalized evidence.

Provider adapters are responsible for translating their native mate convention into
this representation.

For a UCI engine, `score mate N` is reported in moves rather than plies, and a
negative value means the engine side is being mated. A UCI adapter must therefore
combine the raw score convention with the root side to move and normalize it to:

```text
winner + plies_to_mate
```

The raw provider convention must not leak into downstream learner or tutoring code.

## Score bounds

UCI-style engines may report a score as a lower or upper bound rather than an exact
score. M3 preserves this distinction:

```text
exact
lower
upper
```

A bounded score must never be silently promoted to an exact score.

## Candidate line

A normalized engine candidate is conceptually:

```yaml
rank: 1
root_move_uci: e2e4
evaluation:
  kind: centipawn
  perspective: white
  centipawns: 32
  bound: exact
pv_uci:
  - e2e4
  - e7e5
  - g1f3
```

Optional per-line search metrics may be attached when the provider supports them.

### Invariants

- `rank` starts at 1.
- Returned ranks are ordered and contiguous from 1 through the number of valid
  returned candidates.
- `root_move_uci` is legal in the source position.
- A non-empty PV begins with `root_move_uci`.
- Every PV move is legal when replayed from the previous PV state.
- The evaluation is the provider's root-position judgment for that candidate line;
  it is not described as the evaluation of the final PV leaf.

`best_move` is derived from candidate rank 1. It is not duplicated as an independent
stored field that could disagree with the first line.

## MultiPV semantics

`multipv` is part of the analysis request and request fingerprint.

A request for `multipv = 5` asks for up to five ranked root candidates. It does not
mean the engine has proved those are the globally correct top five moves.

Changing MultiPV can change search behavior and scores. Therefore analysis produced
under `multipv = 1` and `multipv = 5` is not treated as identical evidence even when
rank 1 happens to be the same move.

A provider may return fewer lines than requested. The result must then be marked
according to the completion rules rather than fabricating missing ranks.

## Engine provenance

Every `PositionAnalysis` records provenance sufficient to identify the producing
system as far as the provider can establish it.

Initial fields are conceptually:

```yaml
provider_name:
provider_version:
protocol: precomputed | uci | other
engine_name:
engine_version:
engine_author: null | string
binary_sha256: null | sha256
engine_options:
  - [Hash, "128"]
  - [Threads, "1"]
engine_artifacts:
  - name: optional-artifact-name
    sha256: optional-sha256
```

Engine options are stored in deterministic key order.

`binary_sha256` and auxiliary artifact hashes are optional because not every
provider owns or can inspect a local executable. Their absence lowers reproducibility
strength and must not be hidden.

Modern engine evaluation may depend on auxiliary artifacts such as neural-network
weights. The contract allows such artifacts to be recorded without making any
specific engine format mandatory.

## Analysis metrics

Result metrics describe what the provider actually reports achieving, not only what
was requested.

Candidate fields include:

```yaml
depth:
seldepth:
nodes:
time_ms:
nps:
hashfull_per_mille:
tablebase_hits:
```

All are optional unless a specific provider promises them.

Requested limit and achieved metrics must remain separate.

## Position analysis

A successful or partially successful normalized analysis is conceptually:

```yaml
position_id:
fen:
request_fingerprint:
result_fingerprint:
status: complete | partial | terminal
request: ...
provenance: ...
lines: [...]
metrics: ...
termination: ...
```

The source FEN is stored alongside `position_id` as an audit guard. It must match the
canonical position being analyzed.

### Complete

The provider completed normally and returned a valid normalized result for the
request.

### Partial

The provider returned some valid evidence but did not complete normally or returned
fewer valid results than required for a complete result. Partial evidence remains
explicitly partial.

### Terminal

The source position is terminal and no root candidate move exists. Terminal is not
an engine failure.

## Termination

Termination reason is separate from result status. Initial normalized reasons:

```text
completed
terminal_position
timeout
cancelled
engine_crash
protocol_error
```

A `partial` result may, for example, retain valid lines while recording `timeout` as
its termination reason.

## Failure semantics

If no trustworthy normalized engine evidence can be returned, providers return or
raise an explicit `AnalysisFailure` rather than an empty successful analysis.

Initial failure codes:

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

Failure details must not contain fabricated candidate lines or evaluations.

Human-readable diagnostics may be stored, but secrets, arbitrary environment dumps,
and unbounded stderr must not become canonical evidence.

## Request and result fingerprints

M3 separates two hashes.

### Request fingerprint

The request fingerprint identifies the normalized analysis conditions. It is derived
from canonical serialized values equivalent to:

```text
source FEN
+ provider identity/version
+ engine identity/version
+ available binary/artifact identities
+ normalized engine options
+ search limit
+ supervisor timeout
+ MultiPV count
```

The request fingerprint says **which analysis conditions were requested/identified**.
It does not promise the engine will reproduce the same output.

### Result fingerprint

The result fingerprint hashes the normalized `PositionAnalysis` result payload,
excluding the fingerprint field itself.

It identifies the exact normalized evidence record that was produced.

Two results can share a request fingerprint but have different result fingerprints.
That is valid engine evidence, not automatically corruption.

## Position reuse and game provenance

Engine analysis is fundamentally rooted in board state, so request identity uses the
canonical source FEN rather than game-specific `position_id` alone.

The stored `PositionAnalysis` still records `position_id` so the evidence remains
traceable to the game/research context that requested it.

This permits future caching/reuse of compatible analysis for identical positions
without confusing board identity with game provenance.

No persistent cache is implemented in M3.

## Played-move comparison is not part of PositionAnalysis

M3 analyzes one root position at a time.

It does not store independent fields such as:

```text
evaluation_before
evaluation_after_played_move
centipawn_loss
```

inside a single root analysis.

Those are derived comparisons between multiple position analyses and belong to the
later diagnostic-position-selection layer.

This prevents one engine record from mixing evidence from different board states.

## Provider interface boundary

The future provider contract should be equivalent to:

```text
analyze(CanonicalPosition, AnalysisRequest)
    → PositionAnalysis | AnalysisFailure
```

Downstream code consumes normalized M3 records and does not parse UCI text, manage
process pipes, or depend on Stockfish-specific score conventions.

## Implementation order

M3 implementation should proceed in two steps.

### Step 1 — Precomputed provider

Implement the normalized models plus a `PrecomputedAnalysisProvider` backed by frozen
fixtures.

Purpose:

- prove provider/domain separation;
- test serialization, score semantics, mate normalization, MultiPV, partial/terminal
  behavior, and failures without requiring an engine executable;
- provide stable fixtures for downstream tests.

### Step 2 — External UCI provider

Only after the normalized contract is qualified should an external UCI/Stockfish
adapter be implemented.

The initial adapter should receive an explicitly configured executable path/command.
Chess Mentor Engine does not bundle an engine binary in the first M3 slice.

Bundling or redistributing an engine executable requires a separate explicit
licensing/distribution decision and is not authorized by this contract.

## Qualification corpus

M3 implementation should qualify against fixed positions including at least:

- normal starting position;
- tactical position;
- quiet/positional position;
- side to move in check;
- forced mate;
- already checkmated terminal position;
- custom-FEN position;
- promotion position;
- MultiPV position;
- the research board-context position used by prior pilots.

## Qualification invariants

M3 is not qualified until tests establish all applicable invariants:

- M1 and M2 suites remain green;
- White-perspective centipawn normalization is correct for both sides to move;
- mate evidence normalizes to winner + plies-to-mate without numeric sentinels;
- exact/lower/upper bounds are preserved;
- MultiPV ranks are deterministic and valid;
- candidate root moves and PVs replay legally from the source FEN;
- best move derives from rank 1 rather than a duplicate field;
- request fingerprints change when material analysis conditions change;
- identical requests may legally produce distinct result fingerprints;
- provider/engine provenance is preserved;
- complete, partial, terminal, and failure states are distinguishable;
- timeout and engine crash do not masquerade as successful empty analysis;
- no engine binary is bundled implicitly;
- pytest, Ruff, and repository CI pass.

## Explicitly deferred

M3 does not yet freeze or implement:

- WDL probability normalization;
- tablebase evidence contracts;
- cloud-engine providers;
- persistent analysis cache/storage;
- engine-strength calibration across versions;
- cross-engine score equivalence;
- subjective tactical motif labels;
- diagnostic position selection;
- centipawn-loss teaching thresholds;
- player reasoning;
- learner hypotheses;
- tutoring or pedagogy.

Those require later milestones or explicit ADRs.