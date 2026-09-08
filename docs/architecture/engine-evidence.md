# M3 — Engine Evidence Contract

## Status

**M3 — Engine Evidence is qualified. M3A contract, M3B precomputed provider, and M3C external UCI provider are implemented/frozen at their intended boundaries.**

This document defines how Chess Mentor Engine represents engine judgment without
making any particular engine, executable, or UCI process the domain model. M1 and M2
remain the qualified deterministic chess-truth substrate.

The contract is constrained by ADR 0002.

## Boundary

M3 adds provider-produced objective evaluation evidence on top of the qualified
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

The M3 implementation introduces concepts equivalent to:

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

Names may change only if semantics remain identical or ADR 0002 is deliberately
revised.

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
negative value means the engine/root side is being mated. The UCI adapter combines
the raw convention with root side to move and normalizes it to:

```text
winner + plies_to_mate
```

For a positive UCI mate distance `N`, the normalized mate distance is `2*N - 1`
plies and the winner is the root side. For a negative distance `-N`, the normalized
distance is `2*N` plies and the winner is the opposite side.

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

M3B and M3C use the same shared candidate/PV legality validator so precomputed and
external engine evidence cross the same chess-truth gate.

## MultiPV semantics

`multipv` is part of the analysis request and request fingerprint.

A request for `multipv = 5` asks for up to five ranked root candidates. It does not
mean the engine has proved those are the globally correct top five moves.

Changing MultiPV can change search behavior and scores. Therefore analysis produced
under `multipv = 1` and `multipv = 5` is not treated as identical evidence even when
rank 1 happens to be the same move.

A provider may return fewer lines than requested. The result must then be marked
according to the completion rules rather than fabricating missing ranks.

For the UCI provider, `MultiPV` is owned by `AnalysisRequest`; callers cannot also set
it independently through the generic engine-option list. When a request requires
multiple lines, the external engine must advertise the UCI `MultiPV` option.

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

The qualified external UCI provider resolves an explicitly configured executable,
records the executable SHA-256, captures UCI `id name` and optional `id author`, and
records the effective option set used for the request.

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

The UCI provider currently normalizes corresponding `info` fields when supplied by
the engine.

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

The external UCI provider may preserve validated ranked lines as partial evidence
after a supervisor timeout or engine crash rather than discarding trustworthy output
that arrived before termination.

### Terminal

The source position is terminal and no root candidate move exists. Terminal is not
an engine failure.

The external provider detects terminal positions using the qualified chess substrate
and does not require a meaningless engine `bestmove` for a position with no legal
root move.

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

If no trustworthy normalized engine evidence can be returned, providers return an
explicit `AnalysisFailure` rather than an empty successful analysis.

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
and unbounded stderr must not become canonical evidence. The UCI subprocess provider
keeps stderr diagnostics bounded.

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

The provider contract is equivalent to:

```text
analyze(CanonicalPosition, AnalysisRequest)
    → PositionAnalysis | AnalysisFailure
```

Downstream code consumes normalized M3 records and does not parse UCI text, manage
process pipes, or depend on Stockfish-specific score conventions.

Two providers are qualified against this boundary:

```text
PrecomputedAnalysisProvider
UciAnalysisProvider
```

## Implementation record

M3 was implemented in three bounded steps: contract freeze, precomputed-provider
proof, then external-UCI runtime integration.

### M3A — contract freeze

ADR 0002 and this architecture contract froze the evaluation, provenance, identity,
MultiPV, completion, termination, and failure semantics before any external engine
process was introduced.

### M3B — precomputed provider

The normalized models plus `PrecomputedAnalysisProvider` are implemented and
qualified. The provider is backed by frozen fixtures and validates candidate root
moves and every PV move against the qualified chess rules substrate before returning
normalized evidence.

Purpose:

- prove provider/domain separation;
- test serialization, score semantics, forced-mate evidence, MultiPV,
  partial/terminal behavior, and failures without requiring an engine executable;
- provide stable fixtures for downstream tests.

#### M3B qualification record

Qualified candidate head:

```text
a9ae94c339aa47fe3c21fe767c6e6f45f7e2b0c2
```

Merge commit on `main`:

```text
18d43a1b5cb53fde83c827ce9fca7574aff4d88c
```

Qualification evidence:

- 35 repository tests passed on the exact candidate head;
- Ruff passed;
- M1 and M2 suites remained green;
- centipawn and mate evidence types were exercised;
- a legal forced-mate PV passed through the precomputed provider;
- MultiPV completeness was enforced;
- illegal root moves and illegal PV continuations were rejected;
- complete, partial, terminal, explicit failure, and unsupported-request behavior
  were distinguished;
- request fingerprints changed when material request conditions changed;
- identical request fingerprints were shown to permit distinct result fingerprints;
- no UCI process, Stockfish binary, learner model, diagnosis, pedagogy, database, or
  UI was introduced.

The merge commit is tree-identical to the qualified candidate head, and `main` CI
passed again after merge.

### M3C — external UCI provider

`UciAnalysisProvider` is implemented and qualified behind the same normalized
provider boundary. It receives an explicitly configured external engine executable;
Chess Mentor Engine does not bundle or redistribute an engine binary.

The provider implements:

- executable path/command resolution;
- fresh subprocess isolation per analysis;
- UCI `uci`/`uciok` handshake and engine identity capture;
- configured option validation against advertised UCI options;
- request-owned `MultiPV` negotiation;
- `isready`, `ucinewgame`, and readiness gates;
- `position fen ...`;
- `go depth`, `go nodes`, and `go movetime`;
- centipawn normalization to fixed White perspective;
- mate normalization to winner plus plies-to-mate;
- exact/lower/upper score-bound preservation;
- normalized search metrics;
- `bestmove`/rank-1 consistency checking;
- shared root/PV legality validation;
- supervisor timeout handling;
- partial evidence retention when valid lines precede timeout/crash;
- explicit missing/start/crash/protocol/timeout/invalid-output failures;
- bounded subprocess diagnostics and controlled shutdown;
- executable SHA-256 provenance.

#### M3C implementation qualification

Qualified implementation candidate head:

```text
69bfb43fa422b529609f1b1b6ca3d62b00d1c11c
```

Implementation merge commit:

```text
10daa4b9347c68dc42d33cfb1f6c532368c8b360
```

The exact implementation candidate passed:

- 51 repository unit/contract tests with the external integration tests skipped when
  no engine witness was configured;
- Ruff;
- two real external Stockfish 16 integration tests covering the prior research
  board-context position under MultiPV and a forced mate.

The implementation merge commit is tree-identical to the qualified candidate head,
and both post-merge CI jobs passed.

#### M3C complete frozen qualification corpus

Before declaring M3 fully qualified, the frozen M3A corpus requirement was re-read
and the real-engine corpus was expanded rather than weakening the contract.

Qualification-only candidate head:

```text
4034d3e23ab67c7dc600f970ff75debe2aaf5ddc
```

Qualification-corpus merge commit:

```text
54343f6789d0586a7fa4607478eb4efc4cfba348
```

The final external Stockfish 16 corpus covers:

- normal starting position;
- prior research tactical/board-context position;
- quiet/positional position;
- side to move in check;
- forced mate;
- already checkmated terminal position;
- custom-FEN position;
- promotion position;
- MultiPV through the research position.

On the qualification candidate and again after merge:

- the generic job reported 51 passed and 8 intentionally skipped external-engine
  tests, with Ruff passing;
- the separately configured external Stockfish job reported 8/8 integration tests
  passing;
- Ubuntu 24.04 installed Stockfish 16 (`16-1build1`) at CI runtime;
- the Stockfish executable remained external to the repository;
- the qualification merge commit is tree-identical to the exact green candidate.

This closes the frozen M3 qualification corpus without changing its claim ceiling.

## Qualification verdict

> **M3 — ENGINE EVIDENCE: QUALIFIED**

The qualified scope establishes that Chess Mentor Engine can normalize and audit
engine evidence through both frozen precomputed fixtures and an external UCI engine
while preserving the M3 epistemic/provenance boundary.

It does **not** establish that engine evaluation explains player reasoning, that a
large evaluation loss is a useful teaching opportunity, or that any learner
hypothesis is valid.

## Qualification invariants

The qualified M3 evidence establishes all applicable frozen invariants:

- M1 and M2 suites remain green;
- White-perspective centipawn normalization is exercised for both root colors;
- mate evidence normalizes to winner + plies-to-mate without numeric sentinels;
- exact/lower/upper bounds are preserved;
- MultiPV ranks are valid and request-owned;
- candidate root moves and PVs replay legally from the source FEN;
- best move derives from rank 1 and external `bestmove` must agree with it;
- request fingerprints change when material analysis conditions change;
- identical requests may legally produce distinct result fingerprints;
- provider/engine provenance is preserved, including external executable SHA-256;
- complete, partial, terminal, and failure states are distinguishable;
- timeout and engine crash do not masquerade as successful empty analysis;
- no engine binary is bundled implicitly;
- the frozen real-engine position corpus passes against external Stockfish;
- pytest, Ruff, and repository CI pass.

## Explicitly deferred

M3 does not freeze or implement:

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
