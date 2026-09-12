# Version 1.0 Post-Milestone Handoff Runbook

## Purpose

This runbook is the restart path after completion of the bounded Chess Mentor Engine
Version 1.0 repository milestone. It records the integration candidate, exact CI evidence,
known failure history, commands needed to reproduce repository qualification, and the
claim ceiling future engineers must preserve.

## Authority snapshot

```text
milestone state:          INTEGRATED / CURRENT-MAIN AUTHORITY
repository:               ThorStarlord/Chess-Mentor-Engine
V1 implementation merge: 8e3abf063b2af7d09a46495f5e35c85c86d58f01
release identity:         chess-mentor-engine==1.0.0
repository state:         VERSION_1_REPOSITORY_READY
```

Version 1.0 closed three packages:

```text
[x] Package 1 — V1 Local Tutor Vertical Slice
[x] Package 2 — Architecture / Authority Reconciliation
[x] Package 3 — Release Candidate / Distribution Qualification
```

## Implementation PR #96

The final implementation package was:

```text
PR:                      #96 — V1: qualify release distributions
branch:                  work/v1-release-distribution
final head:              4b5512a1b5d67ad0df43000898b5d371701d832c
merged:                  yes
V1 implementation merge: 8e3abf063b2af7d09a46495f5e35c85c86d58f01
PR CI run:               34673791962 — success
post-merge CI run:       34673834249 — success
```

PR #96 added:

- package/runtime release identity `1.0.0`;
- deterministic wheel/sdist artifact validation;
- rejection tests for wrong release identity, missing console scripts, and missing
  required package data;
- independent `release-distribution` CI;
- fresh-environment wheel installation with `--no-index --no-deps`;
- installed CLI and package-data smoke tests;
- preserved full pytest/Ruff/compileall and independent Stockfish gates.

## CI failure triage history

An earlier PR #96 candidate at
`80a85b316ef6accaf02043e102020ff41a1002d4` produced failed CI run `34663723350`.

Observed jobs:

```text
stockfish-integration  PASS
release-distribution   PASS
test-and-lint          FAIL
```

The failure occurred only in the source-suite step. Nine V1 release-distribution tests
failed because:

```text
from tools import release_qualification
ModuleNotFoundError: No module named 'tools'
```

The failing workflow invoked bare `pytest`, while the repository's documented full gate
used `python -m pytest -rs` and the independent release job successfully invoked
`python -m tools.release_qualification` from the same checkout.

**Classification:** `IMPLEMENTATION_FAILURE`.

It was a repository CI/test-invocation defect relevant to the implementation candidate;
it was not obsolete CI, an API-key failure, or an external-service outage. Commit
`4b5512a1b5d67ad0df43000898b5d371701d832c` changed the source-suite invocation to the
canonical module form. The exact corrected head then passed all three jobs and merged.

During the post-milestone audit, the connected GitHub App could not read the classic
`main` branch-protection endpoint. The repository-level ruleset list was empty. Treat
required-check configuration as an integration-platform concern to re-check if merge
policy changes; do not infer branch-protection state from this runbook. The V1
integration itself is unambiguous because PR #96 is merged and both its final candidate
and integrated implementation commit have green CI evidence.

## Development setup

Use Python 3.11 or newer:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Useful installed surfaces:

```bash
cme --help
cme-local-tutor --help
cme-candidate-tutor --help
cme-coach-review --help
cme-reviewed-coaching --help
cme-reviewed-coaching-ledger --help
cme-coach-review-reference --help
cme-persisted-coach-review-reference --help
cme-participant-review --help
```

The principal `cme` workflow includes:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
```

## V1 local tutor

Start a bounded review only after explicit selection and capture consent:

```bash
cme-local-tutor start game.pgn \
  --diagnostic-json diagnostic.json \
  --learner-progress-json learner-progress.json \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --protocol-json capture-protocol.json \
  --prompts-json prompts.json \
  --selection-decision selected \
  --capture-consent granted \
  --recorded-at 2026-09-12T10:00:00-03:00 \
  --created-at 2026-09-12T10:01:00-03:00 \
  --create-db
```

Continue from the exact persisted session artifact:

```bash
cme-local-tutor next \
  --diagnostic-json diagnostic.json \
  --learner-progress-json learner-progress.json \
  --db ./mentor.sqlite3 \
  --participant P01 \
  --created-at 2026-09-12T10:10:00-03:00 \
  '<current-session-artifact-id>'
```

See `v1-local-tutor-vertical-slice.md` for the exact artifact/authority contract.

## Focused repository tests

```bash
python -m pytest tests/test_v1_local_tutor_workflow.py -rs
python -m pytest tests/test_v1_local_tutor_authority_edges.py -rs
python -m pytest tests/test_v1_release_distribution.py -rs
python -m pytest tests/test_package.py -rs
```

The release-distribution tests include positive contract qualification plus rejection of
wrong versions, missing promised console scripts, and missing wheel/sdist package data.

## Full source and engine qualification

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests tools
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

Regular source-suite Stockfish skips are expected when `STOCKFISH_EXECUTABLE` is absent;
they do not replace the independent real-engine witness.

## Build and validate the 1.0.0 distribution

Install only the build tooling required by the release witness:

```bash
python -m pip install "build>=1.2,<2" "setuptools>=68"
```

Build wheel and source distribution:

```bash
rm -rf dist
python -m build --no-isolation --wheel --sdist --outdir dist
```

Expected artifacts:

```text
dist/chess_mentor_engine-1.0.0-py3-none-any.whl
dist/chess_mentor_engine-1.0.0.tar.gz
```

Validate the static release contract:

```bash
python -m tools.release_qualification \
  --wheel dist/chess_mentor_engine-1.0.0-py3-none-any.whl \
  --sdist dist/chess_mentor_engine-1.0.0.tar.gz \
  --expected-version 1.0.0
```

The validator fails closed when release identity drifts, promised console scripts are
missing or remapped, or required wheel/sdist package data is absent.

## Clean-install witness

Create a fresh environment and install only the built wheel without resolving project
dependencies from an index:

```bash
rm -rf .release-venv
python -m venv .release-venv
.release-venv/bin/python -m pip install \
  --no-index \
  --no-deps \
  dist/chess_mentor_engine-1.0.0-py3-none-any.whl
```

Smoke the installed commands:

```bash
for command in \
  cme \
  cme-candidate-tutor \
  cme-coach-review \
  cme-reviewed-coaching \
  cme-reviewed-coaching-ledger \
  cme-coach-review-reference \
  cme-persisted-coach-review-reference \
  cme-participant-review \
  cme-local-tutor
do
  ".release-venv/bin/${command}" --help >/dev/null
done
```

Verify installed metadata/package data:

```bash
.release-venv/bin/python - <<'PY'
import json
from importlib.metadata import version
from importlib.resources import files

assert version("chess-mentor-engine") == "1.0.0"
package_root = files("chess_mentor_engine")
assert package_root.joinpath("py.typed").is_file()
data_root = package_root.joinpath("chess_knowledge", "data")
for filename in ("ontology.v1.json", "strategy.v1.json"):
    payload = json.loads(data_root.joinpath(filename).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
PY
```

## V1 claim ceiling

Repository-qualified Version 1.0 means:

```text
source tests qualified
+ deterministic rejection tests qualified
+ wheel/sdist contract qualified
+ clean wheel install qualified
+ installed entry points/package data qualified
+ independent Stockfish integration qualified
```

It does **not** mean:

```text
published to PyPI or another registry
release/tagging policy approved
hosted deployment exists
production credentials/secrets are validated
production auth/privacy/security/compliance is approved
browser/device/accessibility usability is approved
real participants found the tutor useful
tutoring policy is empirically optimal
intervention-caused learning or mastery is established
```

## Restart procedure for the next milestone

1. Read `STATUS.md` and `docs/product/repository-build-status.md`.
2. Confirm live `main` still contains the recorded V1 implementation baseline; if later
   work has landed, reconcile that newer repository reality rather than resetting to the
   baseline SHA.
3. Re-run the relevant qualification gate for any code area you intend to modify.
4. Ask what concrete post-V1 problem is now being solved: release operations, hosted
   productization, real-user validation, or a demonstrated product capability gap.
5. Identify the authority owner and claim ceiling before designing a new package.
6. Do not auto-create M35, M37, M38, K8, M47, provider abstraction, or infrastructure
   work solely because the label or idea exists.

The next milestone should be pulled by demonstrated product need, not by unused milestone
numbers.
