# M28 — Coach Review Local Reference Surface

M28 adds a deliberately thin, repository-only HTML reference surface over the
qualified M25 coach-review read model.

It exists to make engine evidence, participant authority, deterministic mentor
feedback, model language, and evaluator judgment inspectable in one local browser
surface without turning presentation code into a new evidence or semantic authority.

## Boundary

M28 is a reference renderer, not a production UI.

```text
strict local M25 input bundle
        ↓
M25 build_coach_review_read_model_from_bundle
        ↓
qualified authority-separated M25 read model
        ↓
M28 deterministic semantic HTML renderer
        ↓
new local .html/.htm file
```

The installed command is:

```bash
cme-coach-review-reference path/to/m25-bundle.json \
  --output path/to/coach-review-reference.html
```

The output path must be new. M28 refuses to overwrite an existing file.

The command performs no network request, engine execution, model/evaluator call,
browser automation, credential lookup, deployment, or persistence mutation beyond
creating the requested local HTML file and any missing parent directory.

## What the surface preserves

The top-level section order is exactly the M25 order:

```text
objective_evidence
 diagnostic_selection
participant_authority
tutor_state
deterministic_grounding
model_coaching
model_evaluation
```

The first line above is intentionally the M25 `objective_evidence` section; the
leading space before `diagnostic_selection` is only Markdown formatting and has no
schema meaning.

The generated HTML exposes the seven sections with explicit authority-source labels:

- M15 objective evidence;
- M18 diagnostic selection;
- M21 participant authorization;
- M8 workflow state;
- M16 deterministic feedback;
- M19 model language;
- M20 bounded model-output assessment.

Missing optional downstream sections are rendered as explicitly not present rather
than synthesized.

### Objective evaluation fidelity

M28 renders both canonical engine and decision-mover score perspectives already
provided by M15. It does not recalculate scores.

For centipawn evaluations it preserves:

- White-perspective centipawns and bound;
- decision-mover side, centipawns, and bound;
- exact-vs-lower-vs-upper bound labels.

For mate evaluations it preserves:

- symbolic winner;
- plies to mate;
- White and decision-mover favorability;
- bound semantics.

For non-exact comparisons M28 renders the exact mover delta as unavailable rather
than inventing a centipawn value.

Root/child partial, bounded, incompatible, unavailable, and failure states remain
literal. Failure code/message and evidence fingerprints remain visible.

### Authority separation

M19 rendered language appears only inside the model-coaching section and is labeled
as request-bound, not objective truth.

M20 qualification and `truth_status` appear only inside the model-evaluation
section. The surface repeats that M20 is a bounded assessment and does not establish
objective chess truth.

Each present M25 section also includes an expandable exact canonical source record.
This is for local inspection and diffing; it does not promote presentation output to
source authority.

## Accessibility-oriented semantic structure

M28 uses browser-native semantic HTML only. There is no JavaScript and no external
CSS or asset dependency.

The stable structure includes:

```text
html[lang=en]
header
aside  — claim boundary
main   — M25 review sections
  section + h2 for each M25 authority layer
  h3 subsections for analyses/evaluations/feedback
  table + caption for score, candidate, signal, judgment, and fingerprint data
footer — source fingerprints
```

Tables use column headers with `scope="col"`. Sections use `aria-labelledby` and the
page includes a skip link to the main review.

This is structural qualification only. It is not a claim of production browser,
screen-reader, device, localization, visual-design, or usability correctness.

## Determinism and identity

M28 validates the content-addressed identity of a direct M25 read model before
rendering. The CLI takes the stronger path: it starts from the strict M25 input bundle
and invokes the qualified M25 builder before M28 runs.

The surface identity is content-addressed from:

```text
m28 schema version
M25 read-model id
M25 read-model fingerprint
SHA-256 of exact generated HTML
M28 claim scope
```

Repeated rendering of the same M25 source produces identical HTML, surface id, and
fingerprint.

## Qualification

Focused M28 qualification:

```bash
python -m pytest tests/test_m28_coach_review_reference_surface.py -rs
```

Principal presentation/fidelity regression:

```bash
python -m pytest \
  tests/test_m15_evaluation_presentation.py \
  tests/test_m22_end_to_end_evaluation_fidelity.py \
  tests/test_m25_coach_review_read_model.py \
  tests/test_m26_persistent_reviewed_coaching.py \
  tests/test_m27_reviewed_coaching_execution_ledger.py \
  tests/test_m28_coach_review_reference_surface.py -rs
```

Full merge gate remains:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
```

The repository CI also runs the independent Stockfish integration witness on the
candidate head.

## Negative/rejection coverage

M28 qualification includes rejection for:

- malformed strict M25 bundles;
- rehashed M20 truth-status promotion;
- direct M25 read-model mutation without matching identity;
- unsafe output extensions;
- missing input files;
- existing output paths (no overwrite);
- model content containing HTML/script-like text, which must be escaped and remain
  inert text.

The M22 matrix is replayed through M28 so exact, bounded, mate, partial, empty,
compatible child, incompatible child, and failed-child regimes remain visible without
presentation reinterpretation.

## Claim ceiling

A passing M28 surface establishes only deterministic local reference rendering over
qualified M25 data plus the tested semantic HTML structure.

It does **not** establish:

- production UI usability or visual correctness;
- browser/device/screen-reader compatibility outside bounded structural tests;
- localization correctness;
- correct external disclosure or consent UX;
- model semantic correctness, safety, or pedagogical quality;
- evaluator truth or completeness;
- production provider/credential/transport readiness;
- tutoring efficacy or causal learning impact;
- hosted authentication, multi-user isolation, deployment, or operational readiness.

M15 remains the evaluation-presentation authority, M16 the deterministic feedback
ceiling, M19 model provenance rather than truth, M20 bounded evaluation rather than
objective truth, M25 the read-model authority separator, M26 the persisted local
orchestration seam, and M27 the mechanical execution-ledger/fidelity verifier.
