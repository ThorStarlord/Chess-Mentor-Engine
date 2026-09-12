# V1 Release Distribution Qualification

## Purpose

This runbook defines the repository-only / hermetic release boundary for Chess Mentor
Engine Version 1.0. It qualifies the artifacts users would actually install without
making any claim about hosted deployment, production operations, or tutoring efficacy.

The release identity is:

```text
project = chess-mentor-engine
version = 1.0.0
```

A commit is repository-qualified for Version 1.0 only when the normal repository gate
and the `release-distribution` CI job both pass on that candidate.

## Artifact contract

Build both artifacts from the repository root:

```bash
python -m pip install "build>=1.2,<2" "setuptools>=68"
python -m build --no-isolation --wheel --sdist --outdir dist
```

Expected artifacts:

```text
dist/chess_mentor_engine-1.0.0-py3-none-any.whl
dist/chess_mentor_engine-1.0.0.tar.gz
```

Validate their static contract:

```bash
python -m tools.release_qualification \
  --wheel dist/chess_mentor_engine-1.0.0-py3-none-any.whl \
  --sdist dist/chess_mentor_engine-1.0.0.tar.gz \
  --expected-version 1.0.0
```

The validator fails closed if release identity drifts, a promised console script is
missing or remapped, or required package data is absent from the wheel or sdist.

## Clean-install witness

Create a fresh virtual environment and install only the built wheel. Do not install the
project from the working tree and do not resolve project dependencies from an index:

```bash
python -m venv .release-venv
.release-venv/bin/python -m pip install \
  --no-index \
  --no-deps \
  dist/chess_mentor_engine-1.0.0-py3-none-any.whl
```

The clean environment must report package version `1.0.0`, expose every promised
console entry point, include `py.typed`, and include parseable ontology/strategy JSON
package data.

Promised console commands:

```text
cme
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
cme-local-tutor
```

CI smokes each installed command with `--help`; it does not invoke production providers,
credentials, deployments, or destructive operations.

## Rejection tests

Focused hermetic rejection coverage:

```bash
python -m pytest tests/test_v1_release_distribution.py -rs
python -m pytest tests/test_package.py -rs
```

The suite includes wrong-version rejection, missing-entry-point rejection, missing
wheel package-data rejection, and missing-sdist package-data rejection.

## Full qualification gate

A Version 1.0 repository candidate must preserve all existing gates:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests tools
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

GitHub CI adds the independent `release-distribution` witness that builds wheel/sdist,
validates their contents, installs the wheel into a fresh environment, and smokes the
installed surfaces.

## Claim ceiling

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
hosted deployment exists
production credentials/secrets are validated
production auth/privacy/security/compliance is approved
browser/device/accessibility usability is approved
real participants found the tutor useful
tutoring policy is empirically optimal
intervention-caused learning or mastery is established
```

Those remain external-authority or post-V1 productization concerns.
