# Chess Mentor Engine context

## Product and authority

Chess Mentor Engine is a persistent chess-learning system intended to convert
objective chess evidence into individualized teaching decisions. Its central
questions remain distinct:

```text
What is the best move?
Why is it the best move?
Why did this player fail to find it?
```

The third question is the differentiation hypothesis, not a claim that the system
has established a player's causal cognitive mechanism.

Read [current build status](docs/product/repository-build-status.md) for current
implementation and qualification. Read the
[post-M10 milestone runbook](docs/runbooks/post-m10-milestone-runbook.md) for setup,
feature usage, tests, recovery, and human operating requirements. The
[architecture overview](docs/architecture/architecture.md) separates implemented
boundaries from early hypotheses.

This context consolidates the previous M1-M8 orientation after PRs #39-#41.
Detailed milestone histories remain in their architecture/decision records and
Git history; frozen research protocols and pilot artifacts are unchanged.
The implementation baseline for this documentation pass is
`f8adde83400fb77ecf2a1e3cb9a5ead820136ab6`.

## Current implementation

M1-M10 are qualified only within their bounded software contracts:

- **M1-M4:** canonical PGN/game/position/provenance, deterministic context and chess
  features, normalized engine evidence, objective decision comparison and
  versioned diagnostic position selection with successful controls.
- **M5-M7:** participant evidence capture/freeze/exposure, position-local discrepancy
  facts and authored assessments, participant-specific descriptive hypotheses,
  explicit challenge evidence, recurrence policies, and append-only lifecycle.
- **M8-M9:** controlled evidence-aware tutoring and explicit, provenance-bearing
  hypothesis-to-intervention applicability followed by conservative selection.
- **M10:** predeclared criterion/rubric/context policies, frozen attempts,
  documented practice completion, authored observations, and separate practice,
  near-transfer, far-transfer, and real-game evidence assessments.

The completed three-feature queue is:

```text
Feature 1 - UCI Evidence Contract Repair          MERGED - PR #39
Feature 2 - Durable Artifacts and Verified Replay MERGED - PR #40
Feature 3 - M10 Outcome and Transfer Evidence     MERGED - PR #41
```

UCI provider `0.2` normalizes score bounds into White ordering and rejects invalid
explicit MultiPV ranks. Historical provider `0.1` artifacts are not rewritten.
Local SQLite-backed storage provides immutable JSON artifacts, declared dependency
validation, and typed M8 recovery by verified replay. Tutor comparisons order
assertions before hashing and serialization. These are integrity improvements,
not new evidence of playing strength or teaching effectiveness.

## Separation of responsibilities

**Objective chess authority:** deterministic chess tooling owns canonical board
state, legal actions and qualified low-level features. Engine providers supply
provenance-bound evaluation/PV evidence with explicit partial/bounded/failure
states; engine judgment is not participant reasoning.

**Application authority:** deterministic code owns evidence identity, sequencing,
bookkeeping, exact references, declared-policy evaluation, and local persistence.
M8 freezes all planned pre-reveal responses before objective reveal. Recovery uses
the same transitions and does not bypass those gates.

**Human/model judgment:** explanation authorship, semantic coding,
hypothesis-evidence relations/challenge review, pedagogical applicability, context
classification, exposure declarations, and outcome scoring retain explicit
provenance. The deterministic system must not fabricate those judgments or promote
missing information into certainty.

## Contracts contributors must preserve

```text
objective chess truth != participant self-report != analyst/model coding
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
```

M9 may select only under its versioned eligibility and explicit applicability
rules; multiple applicable mappings remain `unclear`. M10 accepts an exact
`selected` decision and does not upgrade `ineligible` or `unclear` results.

M10 plans must precede attempts. Preserve raw evidence, failures, uncertainty,
scorer disagreement, exclusions, and complete known history. `unexposed` requires
scoped evidence/attestation; unknown exposure or assistance remains unknown.
Repeated positions/coders cannot inflate independent evidence counts. Even with
supported transfer dimensions, `mastery` and `causal_effect` remain
`not_established`. M10 does not automatically revise M7.

Keep native evidence fingerprints separate from storage-envelope digests. Require
exact prompts for M8 recovery and explicit upstream dependencies for archival
closure. Reject mismatches rather than silently rewriting history. The database
is plaintext; scope filtering is not authentication and checksums are not
signatures. Generic M10 JSON archival does not imply typed M10 recovery.

## Development and stop boundary

This is a Python 3.11+ package, not a TypeScript project. There is no product CLI.
Use the root installation and validation commands in the consolidated runbook;
the full CI platform is Ubuntu/Python 3.11. Ruff/tests/syntax compilation do not
constitute a standalone static type-checker pass. External Stockfish must be
configured explicitly, and skipped integration tests are not a Stockfish pass.

M11 longitudinal learner state, CLI/UI/richer LLM productization, typed M10
recovery/migration, and broader empirical product validation remain separate work.
Neither documentation consolidation nor a supported outcome assessment authorizes
another implementation milestone. The three-feature queue is complete.

## Research and product hypotheses

The broader product hypothesis may eventually combine engine and game-history
analysis, persistent learner modeling, misconception hypotheses, personalized
curriculum, targeted exercises, adaptive explanation, and mastery/progress
evidence. Implemented contracts do not settle the full production architecture or
validate the entire hypothesis.

The current discovery direction remains evidence-backed recurring decision
diagnosis with regular online players approximately rated 1400-1800, not a
permanent rating boundary. See
[product discovery](docs/product/product-discovery.md) and
[product definition](docs/product/product-definition.md).

The first validation protocol is designed and frozen but not executed. Product
validation remains authoritative for claims about learner diagnosis and tutoring
value. See [the protocol](docs/research/first-product-validation/README.md).
Pilot 001 was mixed and participant-specific: P01 reported that missing board
context made the analysis unhelpful. Pilot 002 was mixed and participant-specific:
board context improved explanation and direct player evidence added information,
but responses were sparse. Pilot 003 freezes clean instrument calibration and
remains blocked on unexposed P02. Pilot 004 is a separate instrument-aware N-of-1
design for P01 and does not replace Pilot 003. None changes the frozen main
protocol. Software qualification in PRs #39-#41 is not a new participant study.

The [repository build plan](docs/product/chess-mentor-engine-repository-build-plan.md)
retains conceptual sequencing and historical rationale. Its time-sensitive
recommendations, and early stage-status statements in historical records, do not
override current build status or later accepted ADRs.
