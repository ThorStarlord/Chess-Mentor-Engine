# 0001 — Chess rules provider boundary

**Status:** Accepted for the next bounded deterministic-chess milestone  
**Date:** 2026-09-08

## Context

M1 introduced a private Standard-chess replay core behind provider-neutral public
contracts (`CanonicalGame`, `CanonicalPosition`, provenance, and
`PositionContextPacket`). Before expanding the deterministic chess surface, we
needed to decide whether to replace that private core with the mature `chess`
(python-chess) package.

The maintained `chess` package is published under GPL-3.0-or-later, while Chess
Mentor Engine is currently MIT-licensed. This record does not make a general legal
compatibility determination. It records that we do not want to introduce a
copyleft runtime dependency silently or incidentally while the repository's
licensing strategy remains MIT.

A temporary spike in PR #1 installed `chess==1.11.2` only as a development oracle.
The spike compared the current private core against the oracle across:

- five canonical PGN replay cases, including annotations, custom FEN, en passant,
  and promotion;
- six representative legal-move sets, including the standard start, the research
  context position, en passant, castling, promotion, and check;
- the existing M1 qualification suite.

The spike CI result was 24/24 tests passing and Ruff passing.

## Decision

1. **Do not add `chess` as a production runtime dependency in this milestone.**
2. **Keep the public chess-evidence contracts provider-neutral.** The private rules
   implementation remains replaceable and must not leak into the domain API.
3. **Retain the current private Standard-chess core for the next bounded
   deterministic-feature milestone**, while keeping its scope narrow and testing
   every newly exposed fact.
4. **Use the mature library only as an isolated verification oracle when useful**
   (for example, in temporary spikes or non-shipping CI checks), not as an implicit
   runtime architecture decision.
5. Revisit the provider choice before materially expanding beyond the bounded
   deterministic surface, or earlier if a suitable permissively licensed provider
   is selected or the repository's licensing strategy changes explicitly.

## Consequences

### Positive

- M1/M2 public contracts remain independent of a third-party chess library.
- The MIT runtime dependency surface stays unchanged.
- We can cross-check our deterministic outputs against a mature implementation.
- A later provider substitution can remain contained behind the existing boundary.

### Costs and risks

- We continue to own correctness risk in the private rules core.
- Every new deterministic chess feature requires strong fixture and oracle testing.
- We must resist expanding the private core into engine evaluation or subjective
  chess interpretation.

## Revisit triggers

Reopen this decision if any of the following becomes true:

- the private rules surface grows substantially beyond the bounded feature layer;
- oracle comparisons reveal a rules divergence;
- a mature permissively licensed rules provider is selected;
- the project makes an explicit licensing decision that permits a different runtime
  dependency strategy;
- maintenance cost of the private core becomes disproportionate to product value.

## Evidence

- M1 CI on `main`: 13/13 tests passed and Ruff passed.
- Provider spike: PR #1, 24/24 tests passed and Ruff passed.
- The provider spike is exploratory evidence and is not intended for merge as a
  production dependency change.
