# Post-M10 milestone runbook: engine evidence, recovery, and outcomes

**Scope:** operating the three features merged in PRs #39, #40, and #41.  
**Implementation baseline:** `f8adde83400fb77ecf2a1e3cb9a5ead820136ab6`.  
**Status:** documentation consolidation; no new runtime feature or M11 authorization.

Use [current build status](../product/repository-build-status.md) for qualification
and claim status. Detailed contracts remain in their ADRs and feature records.
There is no end-user `cme` command: these capabilities are Python APIs. The shell
commands below install the package and run development/qualification tools.

## 1. Setup and platform boundary

Run from the repository root. Match CI with Python 3.11; the package declares
Python 3.11 or newer. For a POSIX shell:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -c "import chess_mentor_engine.analysis; import chess_mentor_engine.storage; import chess_mentor_engine.evaluation"
```

On Windows, an installed Python 3.11 interpreter can be used without changing
PowerShell execution policy:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest tests/test_outcome_evidence.py tests/test_m10_qualification.py
```

Substitute `.\.venv\Scripts\python.exe` for `python` in the commands below when
not activating the environment. These are interpreter/setup instructions, not a
Windows qualification claim: the recorded complete suites ran on Ubuntu/Python
3.11, and the fake UCI engines are subprocess test fixtures. Use the CI platform
when reproducing the recorded qualification.

## 2. Feature 1 - corrected UCI evidence

Configure an external Stockfish executable; the repository does not bundle one.
On the Ubuntu CI platform, the existing workflow installs it with:

```bash
sudo apt-get update
sudo apt-get install -y stockfish
STOCKFISH_PATH="$(command -v stockfish || true)"
if [ -z "$STOCKFISH_PATH" ] && [ -x /usr/games/stockfish ]; then
    STOCKFISH_PATH=/usr/games/stockfish
fi
test -n "$STOCKFISH_PATH"
test -x "$STOCKFISH_PATH"
export STOCKFISH_EXECUTABLE="$STOCKFISH_PATH"
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

For another installation, set `STOCKFISH_EXECUTABLE` to its actual executable.
In PowerShell the assignment is `$env:STOCKFISH_EXECUTABLE = 'C:\path\stockfish.exe'`;
replace that example path. The environment variable configures the tests and the
example below; application code passes the executable explicitly to the provider.
Do not treat an integration run with eight skips as an external-engine pass.

Minimal API example after installation and executable configuration:

```python
import os

from chess_mentor_engine.analysis import (
    AnalysisFailure,
    AnalysisLimit,
    AnalysisRequest,
    UciAnalysisProvider,
)
from chess_mentor_engine.chess import canonical_json, ingest_pgn

game = ingest_pgn('[Event "Runbook example"]\n[Result "*"]\n\n1. e4 *').games[0]
provider = UciAnalysisProvider(
    os.environ["STOCKFISH_EXECUTABLE"],
    engine_options=(("Threads", "1"), ("Hash", "16")),
)
request = AnalysisRequest(
    multipv=2,
    search_limit=AnalysisLimit("depth", 8),
    supervisor_timeout_ms=10_000,
)
outcome = provider.analyze(game.positions[0], request)
if isinstance(outcome, AnalysisFailure):
    raise RuntimeError(f"{outcome.code}: {outcome.message}")
print(canonical_json(outcome.to_dict()))
```

Inspect `status`, score `bound`, termination, provider/engine identity, and exact
request/result fingerprints. `partial` is not `complete`, and a bound is not an
exact score. Provider `0.2` reverses lower/upper bounds for Black-root evaluations
normalized into White ordering, including symbolic mate evaluations. It rejects
explicit invalid MultiPV ranks instead of defaulting them to rank 1.

Keep historical provider `0.1` evidence unchanged. Generate new evidence with the
repaired provider when needed, and retain the changed provenance and identities.
Do not relabel an old artifact or mix incompatible analysis regimes. See the
[repair and compatibility note](../architecture/uci-evidence-contract-repair.md).

## 3. Feature 2 - save and recover M8 sessions

Start with a session produced through the public M8 functions and the exact
`PromptDefinition` objects for every planned stage, including unpresented stages.
The [M7-M9 runbook](m7-m9-milestone-runbook.md) describes that upstream workflow.
The following example assumes real `session` and `planned_prompts` values:

```python
import json

from chess_mentor_engine.storage import (
    ArtifactRef,
    LocalArtifactStore,
    load_tutor_session,
    save_tutor_session,
)

store = LocalArtifactStore("local-data/evidence.sqlite3")
participant_id = session.capture_session.context.participant_id
ref = save_tutor_session(store, session, prompts=planned_prompts)
saved_reference_json = json.dumps(ref.to_dict())

# Preserve this JSON in the application's own checkpoint/locator.
# A later process supplies that locator and the expected participant identity.
recovered = load_tutor_session(
    store,
    ArtifactRef(**json.loads(saved_reference_json)),
    participant_id=participant_id,
)
assert recovered.session == session
session, planned_prompts = recovered.session, recovered.prompts
```

This short example performs a round trip in one process; the recovery tests also
exercise a fresh process. The locator's durable publication is the caller's
responsibility. `store.list_refs(participant_id=participant_id,
kind="m8.tutor-session.v1")` can discover snapshots, but returns identity order,
not a newest/canonical-state decision. Choose the intended checkpoint explicitly.

Continue using the existing M8 present/capture/freeze/reveal functions. A later
save appends a new snapshot; identical saves are idempotent, and different content
under an immutable identity conflicts. Recovery checks storage integrity and
replays the public transitions, so it cannot bypass required freezes or reveal
ordering. Comparison assertions now hash in the same canonical order in which
they serialize; meaningful move and event sequences remain ordered.

For archival closure, save upstream objects separately and pass their exact
`ArtifactRef` values as `dependencies=`. The generic store validates declared
transitive dependencies; it does not discover or certify every external M1-M7
reference. Native evidence fingerprints and storage-envelope digests are distinct.

| Failure | Required operator response |
| --- | --- |
| `MissingDependencyError` | Restore the exact referenced input; do not substitute a newer record. |
| `ArtifactConflictError` | Reconcile identity/content differences; do not overwrite history. |
| `IntegrityError` or replay mismatch | Preserve/quarantine the original and investigate; do not continue with a partial session. |
| `UnsupportedSchemaError` | Use an explicitly compatible reader or separately reviewed migration; no automatic downgrade. |
| Other `StorageError` | Inspect the failure and retry/reconcile using exact identities; an exception does not prove a successful write. |

Keep the database and locators private. Storage is plaintext, participant scoping
is not authentication, and checksums are not signatures. Use a consistent SQLite
backup or copy only with writers stopped, then verify recovery from the backup.
Never silently repair a historical mismatched comparison fingerprint. Preserve
such an original for audit and regenerate a corrected lineage explicitly.
See the [storage runbook](durable-artifacts-and-replay.md) for detailed operation.

## 4. Feature 3 - operate M10 without overstating outcomes

M10 is not automatically invoked by completing a tutor session. Supply an exact
M9 `selected` decision and its matching intervention/exercises. An `ineligible` or
`unclear` decision cannot be promoted into an evaluation plan.

The operator must perform these steps in order:

1. Predeclare an `OutcomePolicy`: criterion, exact scoring-rubric reference,
   near/far/game context definitions, independent-position/session minima, and
   post-practice delay. Retain the authored rationale and provenance. Call
   `define_evaluation_plan` with the actual M9 objects, then `OutcomeLedger(plan)`.
2. Use `reference_outcome_position` for the M1 position. Construct and append
   `EvaluationAttempt` records with raw evidence, source references, exact exercise
   binding, occurrence key, completion fields, and truthful start/freeze/record
   times. Capture exposure and assistance explicitly; unknown is not unexposed.
3. Call `record_practice_completion` for the exact completed practice block.
   Completion documents participation, not successful performance or adequate
   dosage. Collect transfer evidence strictly after the anchor and required delay.
4. Call `record_outcome_observation` for rubric-bound scores with source and actor
   provenance. Keep failures, missing scores, uncertainty, and contrary judgments.
   Supply the complete known ledger to `assess_outcome_evidence`, with the exact
   completion reference and assessment timestamp.

The plan must exist before attempts, including original real-game decisions later
imported. Real-game evidence requires the matching game source. Do not backdate a
plan, claim an incomplete history is complete, or label familiar positions fresh.
An `unexposed` declaration requires the inspected history/attestation references;
software cannot authenticate that account or discover all outside exposure.

Practice, near transfer, far transfer, and real-game evidence are independent
results: `insufficient`, `supported`, `not_supported`, `mixed`, or `unclear`.
Review included/excluded evidence and independence counts, not just the label.
Repeated positions, clock-only changes, relabeled sessions, and extra agreeing
coders must not be used to inflate transfer support. `supported` is conditional
criterion evidence; `mastery` and `causal_effect` remain `not_established`.

Generic M10 JSON archival is available via the existing store. This is not typed
M10 recovery or automatic schema migration. No result automatically revises M7,
creates M11 learner state, or authorizes another feature. See the
[M10 operating runbook](m10-outcome-transfer-evidence.md) for exact capture/scoring
requirements and the ledger/assessment archival example.

## 5. Validation matrix

Run from the repository root with the installed environment. These commands map
to the existing tests; they are not new application CLI commands.

| Scope | Command |
| --- | --- |
| Feature 1 protocol and repair | `python -m pytest tests/test_uci_provider.py tests/test_uci_evidence_contract.py` |
| Feature 2 storage and recovery | `python -m pytest tests/test_artifact_store.py tests/test_tutor_storage.py` |
| Feature 3 outcome contract and integration | `python -m pytest tests/test_outcome_evidence.py tests/test_m10_qualification.py` |
| Existing M7-M9 boundaries | `python -m pytest tests/test_m7_qualification.py tests/test_m8_qualification.py tests/test_m9_qualification.py` |
| Full regression | `python -m pytest -rs` |
| Lint | `python -m ruff check .` |
| Syntax compilation | `python -m compileall -q src tests` |
| External Stockfish | `python -m pytest tests/integration/test_stockfish_uci.py -rs` |

The post-Feature-3 implementation qualification recorded **514 passed and eight
intentional external-engine skips** without Stockfish configured. The separate
configured Stockfish job recorded **eight passed, no skips**. All **178 newly
added cases** passed across the three features (53 UCI, 49 storage/recovery,
76 M10); the Feature 1 command additionally includes the existing provider tests.
These are dated baseline results, not permanent test-count requirements.

The existing CI workflow runs pytest and Ruff on Python 3.11 and separately runs
the Ubuntu Stockfish witness for PRs into `main` and pushes to `main`. The syntax
and import smoke commands here are supplemental; the workflow has no standalone
static type-checking gate. TypeScript compilation does not apply to this Python
repository. Passing compilation/imports, lint, or tests must not be reported as
passing a Python static type checker.

## 6. Human handoff and stop boundary

Before a real run, retain exact source/policy/engine identities, configure the
external executable, protect participant data, and select the intended checkpoint.
During collection, freeze before revealing objective evidence; record actual
exposure/assistance and deviations rather than concealing them. Scorers must use
the declared rubric and preserve disagreement. Afterward, archive the complete
known evidence, inspect exclusions, and verify recovery rather than merely copying
files. Research protocols and frozen pilot artifacts remain unchanged.

This milestone closes only the three-feature queue. Software qualification is not
an empirical intervention study. M11, an end-user CLI/UI, typed M10 recovery, and
broader product validation remain separate work requiring explicit authorization.
