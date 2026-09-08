# M4Q — Full Diagnostic Position Selection Qualification

## Status

**M4 — Diagnostic Position Selection is qualified. M4Q is complete. M5 Player Decision Evidence is authorized next but has not started.**

This record closes the qualification gate frozen by ADR 0003 and
`docs/architecture/diagnostic-position-selection.md`. M4Q added qualification assets
only; it did not add production selection features, learner inference, or pedagogy.

## Qualified boundary

The complete qualified objective selection path is:

```text
CanonicalGame / CanonicalPosition
+ PositionContextPacket
+ PositionFeaturePacket
+ PositionAnalysis
        |
        v
DecisionComparison
        |
        v
SelectionSignal[]
        |
        v
SelectionPolicy
        |
        v
SelectionDecision / DiagnosticCandidate
        |
        v
DiagnosticCandidateBatch
```

M4 chooses bounded places to gather evidence. It does not explain why a player made a
move and does not rank pedagogical value.

## Frozen M4Q corpus

M4Q freezes `tests/fixtures/m4q_selection_corpus.json` and executes it through the
actual M1→M4D implementation surface in `tests/test_m4_qualification.py`.

The corpus contains every category required by the frozen M4A contract:

1. obvious large exact-centipawn loss;
2. quiet engine-preferred move;
3. side-to-move in check / defensive decision;
4. multiple close engine candidates;
5. clearly separated top candidate;
6. forced mate missed;
7. forced mate allowed;
8. correct rank-1 played move;
9. correct quiet/control decision;
10. custom-FEN decision;
11. promotion decision;
12. prior research board-context position:
   `r2qr1k1/1b3ppp/2p5/ppb4Q/3p4/6PP/PPP3BK/R1B2R2 b - - 0 22`.

The research fixture is used only as immutable board context for qualification. M4Q
does not rewrite any Pilot 001–004 selection evidence or participant exposure state.

## Whole-surface qualification assertions

The M4Q suite proves more than category presence.

### Provenance and reconstructability

For eligible positions, the suite verifies that:

- the candidate and selection decision retain the exact policy identity;
- the complete policy configuration is bound by a policy fingerprint;
- each matched policy rule cites an exact eligibility signal;
- each eligibility signal retains reconstructable evidence references;
- exclusions retain explicit reasons instead of disappearing from the batch.

### Deterministic replay

The balanced qualification policy constructs the same batch when the source result
order is reversed. Stable source-pool provenance and candidate identities are retained.

### Successful controls

The balanced policy deliberately samples objectively successful decisions as controls
and satisfies its control floor without treating a control as contradiction of a
learner hypothesis.

### Policy-version sensitivity

Changing only the selection-policy version preserves upstream `DecisionComparison`
and `SelectionSignal` identities while changing policy-derived decision/batch identity.
This proves that policy evolution does not rewrite prior objective evidence.

### Visible shortfalls

A second deliberately unsatisfiable policy exercises:

- requested-size shortfall;
- control shortfall;
- quota shortfall;
- deterministic per-game caps;
- explicit exclusion reasons.

The batch is never silently padded with positions that failed eligibility or a batch
constraint.

### Non-centipawn and incomplete evidence

Additional M4Q assertions prove that:

- terminal checkmate can flow through symbolic mate evidence into a policy candidate;
- partial analysis does not become exact severity;
- bound-limited analysis does not become exact severity;
- analysis failure remains incomparable;
- engine-evidence inversion remains explicit and can be policy-excluded;
- incompatible child reanalysis never becomes a quantitative move-loss value.

### Claim ceiling

Qualification outputs are checked against the frozen M4 boundary. They do not emit
learner-psychology or pedagogical labels such as tunnel vision, weak strategy, learner
weakness, or best teaching opportunity.

## Superseded M4Q attempt

The first M4Q candidate exposed a useful fixture-policy interaction: three fixtures
intended to demonstrate successful controls also satisfied the versioned close-choice
candidate threshold. M4D correctly gives candidate rules precedence, so the batch
reported a control shortfall.

The production policy logic and qualification gate were not weakened. Instead, the
control fixtures were corrected so their rank-1 separation lies outside the
close-choice threshold. The replacement exact head requalified from scratch.

## Exact qualification evidence

### Exact qualified M4Q candidate

```text
24e0d98e1453671190c3cd34deabd9bdd6d82cb2
```

The candidate changes only:

```text
tests/fixtures/m4q_selection_corpus.json
tests/test_m4_qualification.py
```

No production implementation file changed in M4Q.

### Exact-head CI

GitHub Actions run:

```text
34217205717
```

Result:

```text
106 passed
8 intentionally skipped external-engine tests in the normal suite
Ruff PASS
external Stockfish integration PASS
```

### Qualification merge

```text
ca7e79e748ea6d52ee7122bf4d49a7a0e2123d3c
```

The merge is tree-identical to the exact qualified M4Q candidate: comparing the two
commits produced zero changed files.

### Post-merge CI

GitHub Actions run on the exact merge commit:

```text
34217319671
```

Result:

```text
test-and-lint PASS
external Stockfish integration PASS
```

## Qualification verdict

> **M4 — DIAGNOSTIC POSITION SELECTION: QUALIFIED**

The qualified claim is exactly the M4A claim ceiling:

> Chess Mentor Engine can derive transparent, provenance-rich objective decision
> comparisons and use versioned deterministic policies to select bounded candidate
> sets containing both potentially informative decisions and successful controls.

## Claims still prohibited

M4 qualification does **not** establish:

- why the player made a move;
- that a selected position demonstrates a stable learner weakness;
- that a selected position is the best teaching opportunity;
- that centipawn loss measures cognitive severity;
- recurrence of a reasoning pattern;
- that an intervention is warranted;
- that learning, transfer, or mastery occurred.

Those claims require later player-evidence, learning-inference, and pedagogy layers.

## Next authorized boundary

M4Q closes the objective selection milestone.

The only next milestone authorized by the current build sequence is:

> **M5 — Player Decision Evidence.**

M5 is authorized, but it has **not started**. A new M5 contract/design gate should be
reviewed before production implementation, especially because M5 crosses from
objective chess evidence into direct evidence about what the player actually thought.

## Governing principle

> Diagnostic selection is not diagnosis. M4 is qualified to choose where to gather
> evidence; it is not qualified to decide what is wrong with the learner.
