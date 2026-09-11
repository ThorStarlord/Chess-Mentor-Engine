# Chess Knowledge Ontology K0–K7 — Runbook

**Program:** post-M34 Chess Knowledge Ontology  
**Qualified packages:** K0–K7  
**Implementation PRs:** #75–#80  
**Post-feature baseline:** `0ca0dc42ef84a3f9a6c120b1dc0561d00a73603c`

This runbook is the consolidated restart and qualification path for the qualified
Chess Knowledge Ontology program. It complements, rather than replaces, the M1–M34
runbooks.

## 1. Authority model

Preserve this invariant before changing any ontology code:

```text
concept definition != concept assertion != learner inference
```

And these derived boundaries:

```text
registered concept != automatically detectable concept
external taxonomy tag != deterministic CME detector result
ontology concept presence != M7C hypothesis relation
K7 projection != recurrence reclassification or learner mutation
K6 sidecar != M19 request identity or M16 deterministic authority
heuristic principle != engine-evaluation decomposition
strategic plan != best move != M9 training intervention
```

The ontology may make chess semantics more explicit. It may not silently inherit
participant, learner, tutoring, engine, model, evaluator, or pedagogical authority.

## 2. Package map

| Package | PR | Purpose |
| --- | --- | --- |
| K0 | #75 | Ratify ontology authority boundaries in ADR 0012. |
| K1 | #75 | Strict versioned registry, graph validation, stable IDs, and fingerprints. |
| K2 | #75 | Tactical vocabulary and Lichess puzzle-theme crosswalk. |
| K3 | #76 | Rule/position features, strategic principles, qualitative evaluation factors, candidate plans, and pedagogy metadata. |
| K4 | #77 | Provenance-bound assertions and bundles over exact chess subjects. |
| K5 | #78 | Conservative deterministic position/move detectors for the mechanically qualified subset. |
| K6 | #79 | Model-consumable ontology context and exact sidecar binding to an unchanged M19 request. |
| K7 | #80 | Descriptive ontology projection over already-classified M7C recurrence units. |

## 3. Public Python entry points

The public ontology surface is exported from:

```python
from chess_mentor_engine.chess_knowledge import ...
```

### Registry / vocabulary

```python
from chess_mentor_engine.chess_knowledge import OntologyRegistry

registry = OntologyRegistry.load_default()
concept = registry.get("position.open_file")
concept_fp = registry.concept_fingerprint("position.open_file")
ontology_fp = registry.fingerprint
```

Use the registry for concept identity and semantics. Do not infer that a registered
concept is present in a position or has a deterministic detector.

### Provenance-bound assertions

Core entry points:

```python
from chess_mentor_engine.chess_knowledge import (
    KnowledgeEvidenceRef,
    KnowledgeProvenance,
    KnowledgeQualifier,
    KnowledgeSubject,
    build_assertion_bundle,
    build_knowledge_assertion,
    validate_assertion_bundle,
    validate_knowledge_assertion,
)
```

A knowledge assertion must carry an exact subject, concept/ontology identity,
assertion status, authority class, evidence refs, provenance, claim scope, and
created-at timestamp.

Deterministic assertion authority is binary (`present` / `absent`). External tags,
engine-derived claims, model interpretations, and human ratifications remain distinct
classes.

### Deterministic detectors

Detector modules live under:

```text
chess_mentor_engine.chess_knowledge.detectors
```

The qualified K5 subset includes position-local detection for:

```text
rule.check
rule.checkmate
tactic.absolute_pin
position.bishop_pair
position.open_file
position.semi_open_file
position.isolated_pawn
position.doubled_pawns
position.passed_pawn
position.pawn_island
```

and move-transition detection for:

```text
tactic.promotion
tactic.underpromotion
tactic.fork
tactic.discovered_check
tactic.double_check
```

The detector boundary is intentionally incomplete. Do not add a heuristic concept to
a deterministic detector merely because a human can recognize it informally.

### K6 model-consumer sidecar

Core entry points:

```python
from chess_mentor_engine.chess_knowledge import (
    bind_knowledge_context_to_model_request,
    build_knowledge_augmented_provider_payload,
    build_knowledge_coaching_context,
    validate_knowledge_coaching_context,
    validate_knowledge_model_binding,
)
```

Safe sequence:

```text
exact K4 assertion bundle
-> build_knowledge_coaching_context
-> already-valid exact M19 request
-> bind_knowledge_context_to_model_request
-> optional build_knowledge_augmented_provider_payload
```

The wrapper payload contains the original `m19_request` unchanged. Do not insert CKO
fields directly into the M19 request or recalculate M19 identity under a new shape.

Existing reviewed-coaching/provider paths are not automatically changed by K6.
Applications must explicitly opt into the sidecar.

### K7 M7C learner projection

Core entry points:

```python
from chess_mentor_engine.chess_knowledge import (
    build_hypothesis_knowledge_projection,
    validate_hypothesis_knowledge_projection,
)
```

Safe sequence:

```text
exact existing M7C HypothesisAssessment
+
zero or more exact position-level K4 assertion bundles
-> HypothesisKnowledgeProjection
```

K7 matches assertion bundles to M7C recurrence units by exact game/position identity.
For every covered unit it preserves the original M7C relation verbatim:

```text
supports
contradicts
successful_counterexample
context_exception
unclear
mixed
```

Partial coverage is valid and explicit. `uncovered_recurrence_unit_ids` means no
ontology bundle was supplied for those units; it does **not** mean the concepts are
absent.

## 4. External taxonomy crosswalks

Lichess puzzle-theme mappings are compatibility metadata, not internal detector
authority.

Important example:

```text
lichess pin
-> tactic.absolute_pin
-> tactic.relative_pin
```

The broad external tag remains ambiguous when the source taxonomy does not specify
the internal subtype. Do not collapse one-to-many mappings to manufacture precision.

If an external source adds or changes tags, treat unmapped/drifting vocabulary as a
crosswalk-maintenance problem. Do not silently invent an internal meaning.

## 5. Focused qualification

Run the ontology suites:

```bash
python -m pytest \
  tests/test_chess_knowledge_ontology.py \
  tests/test_chess_knowledge_assertions.py \
  tests/test_chess_knowledge_detectors.py \
  tests/test_chess_knowledge_projection.py \
  tests/test_chess_knowledge_learner_projection.py -rs
```

Run the principal authority-boundary regressions:

```bash
python -m pytest \
  tests/test_hypothesis_recurrence_assessment.py \
  tests/test_hypothesis_recurrence_provenance.py \
  tests/test_m16_grounded_mentor_feedback.py \
  tests/test_m19_provenance_bound_model_coaching.py -rs
```

For detector changes, include near-miss/rejection fixtures. Positive examples alone
are insufficient because the main risk is authority expansion through over-detection.

## 6. Full merge gate

Every K package was merged only after its exact final PR head passed the repository
gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

Independent engine witness:

```bash
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

A skipped Stockfish suite in the regular job is not an independent-engine pass.
Pull-request CI remains the merge authority.

K7's final qualification run `34595432067` collected 865 tests and reported:

```text
857 passed
8 intentional regular-job Stockfish skips
Ruff PASS
compileall PASS
independent Stockfish job PASS
```

## 7. Negative/rejection expectations

Ontology changes should fail closed on at least the relevant cases below.

### Registry / graph

Reject:

- duplicate concept IDs;
- ambiguous aliases where exact lookup would become unstable;
- unsupported schema versions;
- unexpected JSON keys;
- unknown parent/relationship targets;
- hierarchy cycles;
- incompatible detection-support / assertion-authority combinations;
- ambiguous exact external mappings that claim false one-to-one identity.

### Assertions

Reject:

- concept or ontology fingerprint drift;
- subject-shape ambiguity;
- deterministic uncertainty labels under deterministic authority;
- detector authority drift;
- model/external/human provenance under incompatible assertion classes;
- mixed-subject bundles;
- rehashed identity drift.

### Detectors

Reject or refrain from claiming:

- illegal move transitions;
- tactical labels not established by exact board mechanics;
- context-heavy strategic concepts under deterministic authority;
- inferred learner meaning from position facts.

### K6

Reject:

- invalid/tampered M19 request identity;
- ontology-context drift;
- assertion-bundle drift;
- model-binding ID/fingerprint drift.

Never solve a K6 validation failure by modifying the original M19 request shape.

### K7

Reject:

- tampered M7C assessment identity;
- assertion bundles outside the assessment's recurrence-unit subjects;
- duplicate position bundles for one recurrence subject;
- move/move-sequence bundles in the position-level learner projection;
- ontology or assertion-bundle drift;
- relation drift between projection and M7C source unit;
- projection identity drift.

## 8. Safe extension workflow

### Add vocabulary only

1. Decide whether the concept is a rule fact, tactical motif, position feature,
   principle, evaluation factor, plan, or another already-supported kind.
2. Give it a stable semantic ID independent of display wording.
3. Define its claim ceiling and detector support truthfully.
4. Add parent/relationship/external mappings only when semantics justify them.
5. Add positive graph/load tests and relevant rejection tests.
6. Do not add a detector merely to make the concept appear more complete.

### Add deterministic detector support

1. Write an operational definition in board/move terms.
2. Identify near misses that a naive implementation would misclassify.
3. Prefer exact chess-core/M2 evidence over heuristic score thresholds.
4. Emit precise qualifiers needed to recover why the assertion was made.
5. Bind detector identity/version/fingerprint through provenance.
6. Prove deterministic rebuild identity.
7. Run full qualification.

### Add a model consumer

1. Keep deterministic evidence/ontology assertions authoritative only within their
   original scope.
2. Project context separately from M19 request identity unless a future ratified
   M19 schema version explicitly changes that contract.
3. Include anti-promotion instructions.
4. Treat model output as model interpretation/language, not a new deterministic
   fact source.

### Add a learner consumer

1. Start from existing M7/M7C learner authority.
2. Attach ontology evidence descriptively.
3. Preserve support, contradiction, counterexample, and context-exception evidence.
4. Do not derive a learner weakness from ontology presence alone.
5. Any future policy that mutates M7/M11 or selects M9 must receive its own explicit,
   versioned authority contract and qualification.

## 9. Restart checklist

Before continuing ontology or ontology-enabled learner-intelligence work:

1. confirm live `main`;
2. read `STATUS.md` and `docs/product/repository-build-status.md`;
3. read ADR 0012 and relevant files under `docs/chess-knowledge/`;
4. run focused ontology tests;
5. run M7C/M19 regressions if touching K6/K7 boundaries;
6. run the full gate and independent Stockfish witness before merge;
7. verify that the proposed change does not duplicate existing M7C recurrence
   authority;
8. verify that a registered-but-undetected concept remains explicitly so unless the
   detector contract is truly qualified;
9. verify that any K6 adoption leaves the exact M19 request identity unchanged;
10. verify that missing K7 coverage is not interpreted as negative concept evidence.

## 10. Current non-goals

The K0–K7 program does not establish:

- complete chess ontology coverage;
- complete automatic concept detection;
- an engine evaluation decomposition;
- an automatic strategic best-move planner;
- participant perception from board semantics;
- a causal learner model;
- automatic M7/M11 mutation;
- automatic M9 intervention selection;
- mastery or intervention efficacy;
- arbitrary model prose truth/safety;
- production provider/front-end/privacy/security/retry authority.

Use the ontology as a typed semantic substrate for future learner/tutor capabilities,
not as a shortcut around the repository's evidence ladder.
