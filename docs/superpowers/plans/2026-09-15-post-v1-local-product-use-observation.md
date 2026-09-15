# Post-V1 Local Product-Use Observation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the qualified V1 local tutor easier to exercise through the M8 baseline-freeze boundary and persist descriptive product-use observations without claiming learner improvement, tutor efficacy, or mastery.

**Architecture:** Preserve all existing M18/M44/M42/M45/M23/M8/M46 authority owners. Add an append-only observation package backed by `LocalArtifactStore`, a guided baseline consumer that calls existing M8 transitions, and a deterministic participant-scoped usage report. The guided consumer stops before executing an M46 proposal.

**Tech Stack:** Python 3.11+, standard library, existing SQLite artifact store, pytest, Ruff, compileall, Stockfish CI.

**Spec:** `docs/product/post-v1-local-product-use-observation.md`

## Global Constraints

- `objective chess truth != participant evidence != learner inference`.
- M45 priority remains proposal-only and never implies consent.
- M46 remains proposal-only and is not executed by the new guided baseline surface.
- Observations are descriptive product-use evidence only.
- `learning_effect = tutor_efficacy = mastery = not_established`.
- No new runtime dependency, hosted service, browser UI, M47, or K8.
- Existing V1 commands remain supported.

---

### Task 1: Reconcile post-V1 authority and release identity

**Files:** `CONTEXT.md`, `STATUS.md`, `docs/architecture/architecture.md`, `docs/product/repository-build-status.md`, `pyproject.toml`, `.github/workflows/ci.yml`, `tools/release_qualification.py`, authority/release tests.

- [ ] Add failing tests proving stale pending-V1 claims are gone and post-V1 development does not ship under the exact `1.0.0` identity.
- [ ] Observe RED on the candidate PR.
- [ ] Reconcile authority docs and set development version `1.1.0.dev0`.
- [ ] Make release CI derive the expected version from `pyproject.toml` rather than hard-code `1.0.0`.
- [ ] Run focused tests and full repository gates.

### Task 2: Add descriptive interaction observations

**Files:** `src/chess_mentor_engine/observation/{__init__,model,persistence}.py`, `tests/test_post_v1_product_use_observation.py`.

- [ ] Write failing model/persistence tests.
- [ ] Observe RED.
- [ ] Implement immutable content-addressed observation records with exact M8 dependency.
- [ ] Enforce participant scope, timezone timestamps, bounded event types, unique metadata keys, and claim ceilings.
- [ ] Run focused tests.

### Task 3: Add guided baseline capture

**Files:** `src/chess_mentor_engine/local_tutor_review.py`, `src/chess_mentor_engine/local_tutor_review_cli.py`, `src/chess_mentor_engine/local_tutor_entry.py`, guided tests.

- [ ] Write failing end-to-end tests using a real M8 fixture and real `LocalArtifactStore`.
- [ ] Observe RED.
- [ ] Implement position presentation, protocol prompt rendering, raw participant response capture, freeze, exact snapshot persistence, and product-use observations.
- [ ] On EOF/interrupt after session start, preserve M8 history and record descriptive abandonment only.
- [ ] Add `cme-local-tutor review`; preserve `start` and `next`.
- [ ] Generate the post-freeze M46 proposal for operator inspection but do not execute or render its prompt as participant tutoring.
- [ ] Run focused and regression tests.

### Task 4: Add deterministic product-use report

**Files:** `src/chess_mentor_engine/observation/report.py`, `src/chess_mentor_engine/local_tutor_entry.py`, `tests/test_post_v1_product_use_report.py`.

- [ ] Write failing report tests.
- [ ] Observe RED.
- [ ] Aggregate only participant-scoped counts, action distributions, and explicit self-report metadata.
- [ ] Add `cme-local-tutor report`.
- [ ] Keep learning effect, tutor efficacy, and mastery explicitly not established.

### Task 5: Runbook and qualification

**Files:** `docs/runbooks/post-v1-local-product-use-observation.md`, README/status docs.

- [ ] Document the guided baseline workflow and external real-use boundary.
- [ ] Run `python -m pytest -rs`.
- [ ] Run `python -m ruff check .`.
- [ ] Run `python -m compileall -q src tests tools`.
- [ ] Require the independent Stockfish CI job and release-distribution job to pass on the exact PR head.

### Task 6: Stop at the evidence boundary

Do not claim the tutor is validated. Do not automatically implement the next intelligence feature. Real learner sessions and feedback are external evidence; once they exist, reconcile again and choose one bounded next objective.
