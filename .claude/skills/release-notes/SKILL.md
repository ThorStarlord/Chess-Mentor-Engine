---
name: release-notes
description: Turn supplied release, implementation, fix, performance, known-issue, and planned-work evidence into benefit-oriented release communication for a named audience while preserving what is actually shipped, beta, planned, unknown, or merely expected. Use for a communication responsibility and produce feature_announcement. Do not claim a feature shipped, a bug is fixed, performance improved, a date is committed, or customer value was realized without evidence; drafting never publishes or sends the announcement.
---

# Release notes

Satisfy a `communication` responsibility by producing `feature_announcement`.

## Inputs

Require the intended audience and evidence describing the release/update. Prefer release artifacts, merged/deployed change evidence, test/measurement results, product context, known issues, and approved future commitments when available. A PRD or ticket alone does not establish that work shipped.

## Procedure

1. Read [references/contract.md](references/contract.md).
2. Bind the release/update scope, audience, as-of boundary, and source evidence.
3. Classify each communicated item as shipped, beta, planned, or unknown from evidence rather than from intent documents.
4. Translate implementation facts into user-relevant benefits only when the benefit is supported or clearly framed as expected/proposed.
5. Separate features, fixes, performance changes, known issues, and coming-soon items when useful.
6. Require evidence for shipped/beta availability, bug-fix completion, and observed performance claims.
7. Preserve planned work as planned; future dates or commitments require explicit authority if represented as ratified.
8. Draft calls to action and help/feedback guidance without sending, publishing, scheduling, or modifying external systems.
9. Stop when the message is accurate for the bounded audience and remaining uncertainty would not change it, or when required evidence/authority is unavailable.
10. Return `feature_announcement` and control.

## Boundary

`ticket closed != feature deployed`, `PRD says feature != feature shipped`, `expected benefit != observed benefit`, `draft != published announcement`, and `coming soon != committed date`.
