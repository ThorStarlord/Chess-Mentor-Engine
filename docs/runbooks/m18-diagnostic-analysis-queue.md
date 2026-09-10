# M18 — Diagnostic Move-Analysis Queue

## Purpose

M18 exposes the already-qualified M3/M4 diagnostic-selection path through one
bounded local CLI workflow. It answers a narrow operational question:

> Given one canonical game, an explicit played-ply window, one engine-analysis
> request, and one versioned M4 `SelectionPolicy`, which decisions enter the
> deterministic diagnostic candidate/control batch?

M18 does not define universal move-quality thresholds. Policy thresholds remain
explicit caller configuration and retain the exact M4 policy fingerprint.

## Command

```bash
cme diagnose games.pgn \
  --game-index 0 \
  --start-ply 0 \
  --end-ply 30 \
  --policy ./selection-policy.json \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --timeout-ms 10000
```

`--start-ply` and `--end-ply` are inclusive zero-based **played-ply** indexes.
`--start-ply` defaults to `0`; when `--end-ply` is omitted, the workflow stops at
the final played move in the selected game. The command rejects an empty game,
out-of-range endpoints, and a reversed range before analysis begins.

The analysis limit follows the existing M14 contract and accepts exactly one of:

```text
--depth N
--nodes N
--movetime-ms N
```

`--engine-option NAME=VALUE` is repeatable. `MultiPV` remains controlled only by
`--multipv`.

## Selection policy JSON

The command requires an explicit JSON object matching the qualified M4
`SelectionPolicy` fields. Example:

```json
{
  "policy_id": "diagnostic-review-v1",
  "version": "1",
  "requested_size": 8,
  "candidate_min_cp_delta": 80,
  "control_max_cp_delta": 0,
  "close_choice_max_cp": 15,
  "candidate_mate_relations": [
    "forced_mate_allowed",
    "forced_mate_missed"
  ],
  "include_rank1_controls": true,
  "excluded_signal_kinds": [
    "ENGINE_EVIDENCE_INVERSION"
  ],
  "minimum_controls": 2,
  "maximum_per_game": null,
  "quotas": [
    {
      "signal_kind": "MATE_RELATION",
      "minimum": 0,
      "maximum": 2
    }
  ]
}
```

Only known `SelectionPolicy` and quota fields are accepted. Unknown fields and
unknown signal kinds fail closed. The values above are an **example policy**, not a
claim that 80 centipawns or any other threshold universally defines a human error
category or pedagogical priority.

## Execution path

For every played ply in the selected window, M18 executes:

```text
CanonicalPosition
-> M3 UCI root analysis
-> optional exact canonical child reanalysis
-> M4B played-decision comparison
-> M2 PositionFeaturePacket
-> M4C objective SelectionSignal[]
-> M4D SelectionPolicy decision
```

After every source decision has been evaluated, the exact policy results are passed
to `build_diagnostic_candidate_batch`.

M18 does not reimplement candidate ranking or quota logic. The existing qualified
M4D implementation remains authoritative for deterministic source order, controls,
quota minimums/maximums, per-game caps, exclusions, shortfalls, source-pool
fingerprints, and batch identity.

## Output contract

The top-level schema is:

```text
m18.diagnostic-analysis-queue.v1
```

The response contains:

```text
source
analysis_request
selection_policy
policy_fingerprint
analysis_summary
source_pool[]
batch
```

Each `source_pool` entry retains the exact root engine outcome, optional played-child
outcome, M4 decision comparison, objective selection signals, and complete M4D
selection decision. The final `batch` is the native `DiagnosticCandidateBatch`
serialization.

This deliberately exposes both selected and non-selected decisions. Consumers can
inspect why a position was excluded instead of treating the final candidate list as
an opaque model judgment.

## Partial, failed, bounded, and incompatible evidence

M18 preserves upstream evidence semantics rather than manufacturing precision:

- root `AnalysisFailure` becomes an auditable incomparable M4 decision;
- partial root analysis remains `partial_evidence`;
- incompatible root/child regimes remain `incompatible_analysis_regime`;
- bound-limited evidence does not become an exact centipawn loss;
- policy exclusions and batch shortfalls remain explicit.

These evidence states may therefore produce an M4D `excluded` decision and a batch
shortfall. M18 never pads the batch by weakening the policy.

Malformed provenance relationships, signal/comparison drift, policy identity drift,
or policy-fingerprint drift fail the command instead of emitting a partially trusted
queue.

## Side effects and authority boundary

M18 is read/compute-only with respect to learner and tutor state. It does **not**:

- archive queue output or mutate the artifact database;
- invoke the M15 presentation projection for every queue item;
- generate M5 participant evidence or M6/M7 learner judgments;
- start or mutate M8 tutor sessions;
- select M9 interventions or mutate M11 longitudinal state;
- invoke an LLM or generate free-form coaching;
- render a web UI or claim empirical tutoring efficacy.

A later workflow may consume selected candidates, but that is outside M18.

## Qualification

Focused M18 qualification:

```bash
python -m pytest tests/test_m18_diagnostic_analysis_queue.py
```

Full repository merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The final Stockfish command requires `STOCKFISH_EXECUTABLE`. A skipped integration
suite is not an independent external-engine pass. Pull-request CI runs the native
suite/Ruff gate plus a separate Stockfish witness.

The focused M18 suite covers deterministic candidate/control batching, inclusive
ply-window bounds, partial root evidence, incompatible child reanalysis, explicit
engine failure, invalid policy/range rejection, and policy-fingerprint drift at the
batch boundary.
