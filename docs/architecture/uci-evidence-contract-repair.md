# UCI evidence contract repair - provider 0.2

## Scope

This repair implements Feature 1 of the post-M9 execution queue. It preserves the
accepted [M3 contract](../decisions/0002-engine-evidence-contract.md) and the
[engine-evidence architecture](engine-evidence.md). It does not implement durable
storage, tutor-comparison fingerprint repair, M10, or any learner-state change.

## White-perspective score bounds

UCI centipawn and mate scores describe the engine's root-side evaluation. M3 stores
both score types from a fixed White perspective. Converting a Black-root score to
White reverses its evaluation ordering, so `lower` becomes `upper`, `upper` becomes
`lower`, and `exact` remains `exact`.

For example, a Black-root `score cp 22 lowerbound` means a White-perspective
centipawn value of -22 with an **upper** bound, not a lower bound. This reversal
applies to negative and zero centipawn values as well.

Mate remains a separate `winner + plies_to_mate` record. Its winner and distance
conversion are unchanged: positive UCI mate N means the root side wins in 2*N-1
plies; negative N means the other side wins in 2*abs(N) plies. Its bound describes
White-perspective evaluation ordering, not an inequality on the numeric
`plies_to_mate` field. Black-root mate bounds therefore reverse too. No mate score
is converted to a centipawn sentinel, and no bound becomes an exact score.

## Explicit MultiPV rank validation

An absent `multipv` field retains the rank-1 default. An explicitly supplied zero,
negative, non-integer, or missing rank value is invalid engine output. It must not
be replaced by rank 1 through truthiness-based defaulting. A parsing error in the
normal search path returns `INVALID_ENGINE_OUTPUT`, including when valid scored
lines were received before the malformed line.

## Provenance and compatibility

`UCI_PROVIDER_VERSION` changes from `0.1` to `0.2`. Provider version already
participates in request identity and the normalized result record, so repaired
runs have new request/result fingerprints even when an exact White score itself
is unchanged. Existing records and frozen research fixtures are not rewritten or
silently relabeled. Obtain new evidence through the repaired provider when
corrected normalized results are needed. M4's existing analysis-regime checks and
conservative handling of bound-limited evidence remain unchanged.

## Regression coverage and verification

`tests/test_uci_evidence_contract.py` reuses the existing fake-engine fixture from
`tests/test_uci_provider.py`. It covers both root sides; positive, zero, and
negative centipawn scores; exact/lower/upper bounds; both mate winners and sign
conventions; contradictory bound flags; absent and explicit ranks; invalid ranks
before and after valid evidence; complete provider output; fingerprint
self-consistency; and material provider-version identity.

Run the focused and full gates with:

```bash
pytest tests/test_uci_provider.py tests/test_uci_evidence_contract.py
pytest
ruff check .
python -m compileall -q src tests
pytest tests/integration/test_stockfish_uci.py
```

The final command requires an external Stockfish executable exposed through
`STOCKFISH_EXECUTABLE`. The existing independent CI integration job installs that
witness. Fake-engine checks establish protocol normalization and rejection
behavior; they are not evidence of improved engine playing strength or learning.
