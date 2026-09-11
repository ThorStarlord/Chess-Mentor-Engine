# M32 — Persisted Review Delivery Fidelity Contract

M32 is a repository-only consumer contract over the already-qualified M25/M28/M30 review chain. It does not add chess facts, reinterpret engine scores, invoke a model, execute a provider call, advance tutor state, or claim production UI/pedagogical quality.

## Purpose

M15/M22 already qualify evaluation semantics and M28 already renders them into a deterministic local HTML reference surface. M30 adds participant-scoped persisted navigation and exact source fingerprints. M32 closes the remaining machine-consumer gap: a downstream UI or tool can consume one versioned object without reverse-engineering score semantics from HTML or collapsing authority layers.

The principal API is:

```python
from chess_mentor_engine.review_delivery import (
    build_persisted_review_delivery_bundle,
    validate_persisted_review_delivery_bundle,
    validate_review_delivery_bundle,
)
```

`build_persisted_review_delivery_bundle(...)` starts from one exact participant-scoped M30 package, re-runs the M30/M29/M28 validation path, and emits a deterministic `m32.persisted-review-delivery-fidelity.v1` bundle.

## Contract

The bundle contains:

- exact M30/M26/M25/M27 source references;
- M30, M25, and M28 source fingerprints;
- the exact M25 section order and content;
- an explicit authority label per M25 section;
- a deterministic evaluation index derived only from exact M15 objective evidence;
- White-versus-decision-mover score semantics, mate representation, bound semantics, evidence quality, comparison state, and child-analysis status without score reinterpretation;
- an authority boundary that explicitly denies model-language promotion, evaluator-truth promotion, external execution, tutor-state mutation, production-UI claims, and pedagogical-quality claims.

The exact section authority mapping is:

```text
objective_evidence       -> M15 objective chess evidence
diagnostic_selection     -> M18 diagnostic selection evidence
participant_authority    -> M21 participant authorization
tutor_state              -> M8 workflow state
deterministic_grounding  -> M16 deterministic grounded feedback
model_coaching           -> M19 request-bound model language
model_evaluation         -> M20 bounded assessment, not objective truth
```

## Fail-closed fidelity checks

M32 rejects, including when the detached object has been correctly rehashed:

- White/decision-mover perspective drift;
- incorrect sign or lower/upper bound inversion;
- numericization of symbolic mate evidence;
- non-exact comparisons that expose an exact centipawn delta;
- reordered or duplicate MultiPV ranks;
- M25 source-fingerprint drift;
- forged authority labels or authority boundaries;
- detached bundle identity/fingerprint drift;
- participant-scope drift;
- source-reference swaps when checked against the persisted store.

`validate_review_delivery_bundle(...)` checks a detached bundle's schema, authority, semantics, source-fingerprint envelope, and content address. `validate_persisted_review_delivery_bundle(...)` additionally rebuilds the bundle from the exact referenced M30 package and requires byte-for-byte data equality at the canonical JSON level.

## Qualification

Focused M32 suite:

```bash
python -m pytest tests/test_m32_persisted_review_delivery_fidelity.py -rs
```

Relevant regression chain:

```bash
python -m pytest \
  tests/test_m15_evaluation_presentation.py \
  tests/test_m22_end_to_end_evaluation_fidelity.py \
  tests/test_m25_coach_review_read_model.py \
  tests/test_m28_coach_review_reference_surface.py \
  tests/test_m29_persisted_review_reference_bridge.py \
  tests/test_m30_participant_review_package_navigation.py \
  tests/test_m32_persisted_review_delivery_fidelity.py -rs
```

Native repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

The existing independent Stockfish witness remains relevant to upstream engine truth:

```bash
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

A skipped Stockfish suite is not an independent-engine pass. M32 itself requires no production credentials or live external service.

## Deferred external authority

M32 does not establish real browser/device correctness, accessibility conformance, localization, interaction quality, hosted authentication, production provider behavior, production privacy/security approval, semantic correctness of arbitrary model prose, evaluator completeness, or empirical tutoring efficacy. Those remain explicit external/human gates.
