# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Current implementation boundary:** M15 — Evaluation Presentation Contract, PR #47.  
**Pre-M15 merged baseline:** `6112b3a970c3b2a4b10b58a6cb3b438d332e605e` (M14 merge).  

This file is the concise moving authority for repository state. Historical
qualification details remain in feature PRs, ADRs, architecture records, runbooks,
and Git history. Software qualification is not empirical tutoring efficacy.

## Milestone board

```text
M1  - Trustworthy Chess Evidence Substrate       QUALIFIED
M2  - Deterministic Chess Feature Extraction     QUALIFIED
M3  - Engine Evidence                            QUALIFIED
M4  - Diagnostic Position Selection              QUALIFIED
M5  - Player Decision Evidence                   QUALIFIED
M6  - Reasoning Discrepancy                      QUALIFIED
M7  - Learner Hypothesis Ledger / M7Q            QUALIFIED
M8  - Evidence-Aware Tutor Session               QUALIFIED
M9  - Training Intervention Registry             QUALIFIED
M10 - Bounded Outcome / Transfer Evidence        QUALIFIED - MERGED PR #41
M11 - Longitudinal Learner State                 QUALIFIED - MERGED PR #43
M12 - Local Evidence CLI                         QUALIFIED - MERGED PR #44
M13 - Persistent Tutor Session CLI               QUALIFIED - MERGED PR #45
M14 - Engine-Backed Analysis CLI                 QUALIFIED - MERGED PR #46
M15 - Evaluation Presentation Contract           CURRENT IMPLEMENTATION - PR #47
```

Supporting repairs/capabilities remain part of this baseline:

```text
UCI evidence contract repair / provider 0.2      MERGED - PR #39
Durable artifacts + verified M8 replay           MERGED - PR #40
Post-M10 documentation consolidation             MERGED - PR #42
```

## Recent promotion provenance

| Milestone | Qualified/final head | Merged commit | Qualification |
| --- | --- | --- | --- |
| M10 / PR #41 | `a1aaebd086e1a3006e2ec67c8e8584f495ff6bb4` | `f8adde83400fb77ecf2a1e3cb9a5ead820136ab6` | implementation run `34347340917`; post-merge run `34347734365` |
| M11 / PR #43 | `975fbbf70a62ba2a0ca11a8fae7afbc06d8179eb` | `aa62bb4e7e1f83433086c2c77fc4af3fc6ed2b62` | run `34373923454` |
| M12 / PR #44 | `36f86d92e4c698b6898f337b54a7bdf6da25fd00` | `ff66e7e8768d3f95422c2bb0172f54f01cc72da7` | run `34375086055` |
| M13 / PR #45 | `c42a9acc435395909cb8760d9cb1e81ef653796b` | `1d9ffdd587eada992afd8ca613351895f240e3f5` | run `34378413147` |
| M14 / PR #46 | `c2e1ded12ae3dd40402c67ddb713db7f6c38fdbc` | `6112b3a970c3b2a4b10b58a6cb3b438d332e605e` | run `34411793232`: 554 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M15 / PR #47 | runtime-qualified head `45dd5706530347a7f74d7e9bb745a3d0dcd2e501` | see PR #47 for final merge SHA | runtime run `34412594441`: 566 passed, 8 intentional skips, Ruff PASS, Stockfish PASS |

PR #47 and Git history are authoritative for the final documentation-bearing M15
candidate, its exact-head CI run, and merge SHA. Any candidate-head change requires
a fresh full CI and independent Stockfish pass before merge.

## Current evidence path

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound engine evidence
-> objective played-decision comparison / bounded diagnostic selection
-> deterministic evaluation presentation projection
-> frozen participant decision evidence
-> position-local reasoning discrepancy
-> participant-specific hypothesis + contradiction/challenge evidence
-> controlled evidence-aware tutor session
-> explicit training applicability / selected | ineligible | unclear
-> predeclared outcome protocol
-> practice / near / far / real-game outcome evidence
-> append-only longitudinal learner state
```

M12-M14 expose selected capabilities through the local `cme` command. M15 is a
Python presentation API over already-qualified M3/M4 records; it does not collapse
those authority boundaries or create new chess truth.

## M11 — Longitudinal learner state

M11 records exact participant-specific M7 state over time and may attach exact M10
outcome evidence only for the same hypothesis revision. The event/ledger model is
append-oriented and deterministic. Exact retries are idempotent; conflicting event
identity reuse, revision regression, participant mismatch, stale snapshots, and
terminal lifecycle resurrection fail closed.

M11 preserves M7 lifecycle/status authority and M10 outcome dimensions. It does not
create a scalar weakness score, infer causal learning, assert mastery, automatically
revise M7, or carry old M10 evidence onto a newer M7 revision.

See the [M11 runbook](../runbooks/m11-longitudinal-learner-state.md) and ADR 0010.

## M12 — Local evidence CLI

M12 introduced the installed `cme` command with bounded read-only operations:

```text
cme games inspect
cme position packet
cme artifacts list
cme artifacts show
cme artifacts verify
```

The position packet is deterministic and engine-free. Artifact operations require
an exact participant scope and an existing database; missing databases are not
created by reads. See the [M12 runbook](../runbooks/m12-local-evidence-cli.md).

## M13 — Persistent tutor session CLI

M13 added controlled append-only `cme tutor ...` mutations over the qualified M8
state machine. Every mutation verifies/replays an exact prior checkpoint, applies
one native M8 transition, replay-validates the result, and appends an immutable
successor checkpoint.

M13 does not generate prompts, engine analysis, M6 assessments, M7 hypotheses,
mentor prose, M11 learner-state mutations, or training decisions. See the
[M13 runbook](../runbooks/m13-persistent-tutor-cli.md).

## M14 — Engine-backed analysis CLI

M14 adds:

```text
cme analyze <pgn> --ply-index N --engine <uci> ...
```

The command runs the exact canonical root through the qualified M3 UCI provider and
passes the result to native M4 played-decision comparison. When a complete root
MultiPV does not contain the canonical played move, M14 reanalyzes the exact
canonical child under the same request/provider configuration. M4 remains the
authority for whether root/child regimes are compatible.

The output preserves native M3/M4 evidence, including White-perspective centipawns,
symbolic mate, score bounds, partial evidence, terminal relations, engine-evidence
inversion, incompatible analysis regimes, explicit engine failures, and provenance.
M14 may optionally archive the complete package as `m14.analysis-package.v1` in an
**existing** participant-scoped artifact database. It does not implicitly create a
database or mutate M7, M8, M9, M10, or M11.

See the [M14 runbook](../runbooks/m14-engine-analysis-cli.md).

## M15 — Evaluation presentation contract

M15 introduces `chess_mentor_engine.presentation.build_evaluation_presentation` as
a deterministic projection over exact M3 `PositionAnalysis` / `AnalysisFailure`
records and one M4 `DecisionComparison`.

The `m15.evaluation-presentation.v1` output preserves:

- canonical White centipawn values and bounds;
- an explicit original decision-mover view, including correct bound reversal for
  Black;
- symbolic mate as winner + plies-to-mate rather than a centipawn sentinel;
- explicit `exact`, `bounded`, `partial`, `terminal`, `incompatible`, and
  `unavailable` evidence quality;
- ranked UCI PVs and engine identity/provenance;
- request/result fingerprints and exact M4 evidence references.

Projection validates evidence references and comparison fields against the exact
supplied M3 records. It rejects root/child reference drift, best/played evaluation
drift, impossible root-MultiPV sourcing, and any exact centipawn delta attached to
a non-exact comparison. A complete analysis with no candidate lines is
`unavailable`, not `exact`.

M15 does not modify M14 archives, run an engine, render a UI, round scores into pawn
floats, convert PVs to SAN, invent `inaccuracy/mistake/blunder` labels, invoke an
LLM, generate mentor feedback, or mutate M6/M7/M11.

See the [M15 runbook](../runbooks/m15-evaluation-presentation.md).

## Qualification commands

Focused current product surface:

```bash
python -m pytest tests/test_m11_qualification.py
python -m pytest tests/test_m12_cli.py
python -m pytest tests/test_m13_persistent_tutor_cli.py
python -m pytest tests/test_m14_engine_analysis_cli.py
python -m pytest tests/test_m15_evaluation_presentation.py
```

Engine/comparison contracts:

```bash
python -m pytest tests/test_uci_provider.py tests/test_uci_evidence_contract.py
python -m pytest tests/test_decision_comparison.py
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The final command requires `STOCKFISH_EXECUTABLE`; skips are not an independent
engine pass. CI runs Python 3.11 native tests/lint plus a separate external
Stockfish witness. No standalone static type checker is configured.

## Current claim ceiling

The repository now has a real local CLI, qualified longitudinal-state software,
and a deterministic UI-safe evaluation projection contract, but it does **not**
claim:

- causal cognitive diagnosis or permanent learner traits;
- optimal/effective intervention selection;
- intervention-caused improvement or automatic mastery;
- universal engine-evaluation or move-quality thresholds;
- globally complete exposure history;
- automatic M6 diagnosis generation from engine output;
- automatically generated grounded mentor explanation;
- autonomous M7/M11 mutation from tutor or analysis commands;
- a web UI, authenticated hosted service, or production multi-user persistence;
- empirical tutoring efficacy.

M15 ends at trustworthy deterministic presentation semantics. Grounded mentor
feedback remains the next separate downstream package and is not authorized by M15.