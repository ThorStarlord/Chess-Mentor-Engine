# M22 — End-to-End Evaluation Fidelity Matrix

## Purpose

M22 is a hermetic qualification package for the evaluation path already implemented
by M3/M4, M15, M16, M19, and M20. It does not add a second chess evaluator or a new
source of tutoring authority.

The qualified fidelity path is:

```text
M3 PositionAnalysis
+ M4 DecisionComparison
        ↓
M15 EvaluationPresentation
        ↓
M16 GroundedMentorFeedback
        ↓
M19 provenance-bound model request / model rendering
        ↓
M20 evaluator request / bounded evaluation record
```

M22 asks one narrow question:

> Do evaluation semantics and their uncertainty/authority boundaries remain faithful
> as the same evidence crosses the presentation, deterministic-feedback, model-
> language, and model-output-evaluation layers?

The answer is established only for the deterministic contracts and hermetic cases in
this matrix. It is not an empirical claim about production model quality, UI quality,
or tutoring efficacy.

## Artifacts

```text
tests/fixtures/m22_evaluation_fidelity_matrix.json
tests/test_m22_end_to_end_evaluation_fidelity.py
docs/runbooks/m22-end-to-end-evaluation-fidelity-matrix.md
```

M22 intentionally adds no production runtime module. The existing qualified
producers remain the implementation under test.

## Machine-readable semantic matrix

The fixture declares eight distinct evaluation regimes:

| Case | Fidelity property |
| --- | --- |
| exact White root MultiPV | exact White and decision-mover CP values, exact delta, root-MultiPV provenance |
| bounded Black perspective | White score retained, mover sign inverted, lower/upper bound reversed, no exact delta |
| symbolic terminal mate | winner + plies-to-mate retained, no CP sentinel, terminal relation retained |
| partial root | partial quality remains partial and no exact loss is invented |
| empty complete root | unavailable evidence remains unavailable |
| compatible child reanalysis | child score and compatible analysis regime produce exact mover-relative comparison |
| incompatible child regime | child evidence remains visible but comparison is explicitly incompatible and non-exact |
| failed child | failure code remains explicit and comparison remains unavailable/non-exact |

The fixture contains expected semantic fields, not duplicated engine logic. The test
builds each scenario through the native M3/M4 records and the native M15 projector,
then compares the projected fields with the declared matrix.

## Cross-layer exact-chain fidelity

The exact-chain test uses the existing qualified M8/M16/M19/M20 hermetic fixtures and
verifies all of the following in one lineage:

```text
M4 exact mover-relative delta
== M15 exact comparison delta

SHA256(canonical M15 presentation)
== M16 evaluation_presentation fingerprint

recomputed M16 feedback
== M19 request grounded_feedback

M16 feedback ID/fingerprint
== M19 coaching grounded_feedback_ref

M15 presentation
== M20 evaluator-request evaluation_presentation

M16 feedback
== M20 evaluator-request grounded_feedback

M19 rendered text + model provenance
== M20 evaluator-request model text + provenance

M20 accepted evaluation refs
== exact M16/M19 source refs
```

The current exact fixture carries a 60-centipawn mover-relative difference. M22
verifies that the M15 structured value and M16 deterministic wording agree on that
same value before any model-authored prose is evaluated.

## Model-overclaim isolation

A separate hermetic case supplies model-authored prose claiming an invented exact
325-centipawn loss while the qualified source chain still says 60 centipawns.

The M20 request must retain the true M15/M16 source values unchanged, while the
fixture evaluator rejects the prose on:

```text
objective_chess_consistency
evidence_sufficiency
```

This test is not a claim that arbitrary evaluators will always catch every bad model
statement. It proves that the architecture can retain the source truth independently
of the rendered prose and can record a bounded rejection without rewriting upstream
evidence.

## Rehashed drift rejection

M22 includes rejection tests that deliberately recompute outer content-addressed IDs
after tampering. This distinguishes semantic-source validation from simple checksum
validation.

### M19 grounding drift

The test modifies the nested M16 grounded-feedback content inside an M19 request and
then recomputes the M19 request fingerprint and request ID. M19 must still reject the
request because rebuilding M16 from the exact current sources produces a different
record.

Expected boundary:

```text
rehashed outer M19 request
+ drifted nested M16 grounding
≠ exact recomputed M16 grounding
→ reject
```

### M20 presentation drift

The test changes the M15 exact centipawn delta embedded in an M20 evaluation request,
then recomputes the M20 request fingerprint and request ID. M20 must still reject the
request because rebuilding the evaluator packet from the exact M16/M19/M3/M4 sources
produces the qualified M15 presentation rather than the tampered one.

Expected boundary:

```text
rehashed outer M20 request
+ drifted nested M15 presentation
≠ exact rebuilt evaluator packet
→ reject
```

M22 also retains direct M15 source-reference rejection and M16 analysis-binding
rejection cases.

## Perspective and bound invariants

M15 is the structured evaluation-presentation authority tested by the matrix.
For centipawn evaluations:

```text
canonical engine perspective = White
presentation display perspective = decision mover
```

For a Black decision mover, M22 therefore verifies both:

```text
White: -50 lower-bound CP
Decision mover (Black): +50 upper-bound CP
```

This is a perspective transformation, not a new engine evaluation. The bound must
reverse because negating `x >= -50` produces `-x <= 50`.

Any non-exact comparison regime in the matrix must expose:

```text
exact_centipawn_delta_for_mover = null
```

M22 never fills missing exact values with estimates.

## Mate invariant

Mate remains symbolic across the structured presentation boundary:

```text
kind = mate
winner = black
plies_to_mate = 1
```

The matrix explicitly rejects the architectural pattern of converting mate into an
arbitrary centipawn sentinel. The existing M20 evaluator policy separately includes
`mate_and_bound_preservation` for evaluating model-authored prose.

## Failure and incompatibility invariants

A failed child analysis remains a failed child analysis. Its failure code is retained
and it cannot yield an exact move-loss delta.

An incompatible child analysis remains inspectable as evidence but cannot be treated
as an exact same-regime comparison. M22 verifies both the child analysis payload and
the comparison-level `incompatible` quality.

This distinction matters: evidence availability and comparison compatibility are not
the same property.

## Qualification commands

Focused M22 suite:

```bash
python -m pytest tests/test_m22_end_to_end_evaluation_fidelity.py
```

Full repository gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

Pull-request CI remains the merge authority. Its independent Stockfish job is an
external engine witness for the existing engine boundary; M22 itself performs no
live model/provider calls and requires no production credentials.

## What M22 qualifies

M22 qualifies a bounded repository claim:

> For the declared hermetic evaluation regimes, the current qualified producers
> preserve score perspective, exactness, bounds, mate representation, failure /
> incompatibility state, and exact source binding through the M15/M16/M19/M20
> evaluation path, and fail closed on the covered cross-layer drift cases.

That is a regression and architectural-integrity claim.

## Explicit non-claims

M22 does **not** establish:

- that an arbitrary LLM will produce factually correct coaching prose;
- that an arbitrary model/human evaluator will detect every semantic error;
- a universal chess-engine calibration or universal move-quality threshold;
- causal learner diagnosis or permanent learner traits;
- automatic M6/M7/M9 authority;
- pedagogical optimality or tutoring efficacy;
- UI rendering fidelity in a browser or accessibility correctness;
- production provider credentials, latency, retry, cost, privacy, or availability;
- hosted-service correctness or production QA;
- empirical transfer, mastery, or intervention-caused improvement.

M22 validates fidelity of the repository's existing evidence contracts. It does not
turn those contracts into broader product or scientific claims.
