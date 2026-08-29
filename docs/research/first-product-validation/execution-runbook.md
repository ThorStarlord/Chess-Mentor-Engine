# First product-validation execution runbook

Status: Operational preparation only. Protocol version 1.0 remains frozen and unexecuted.

This runbook explains how to start Run 1 once real participant material is supplied. It does not authorize recruitment, participant contact, or study execution by itself.

## Required package for one participant

Provide all of the following before analysis begins:

- an anonymous participant ID, such as `P01`;
- rating or rating band and eligibility information;
- a PGN set containing 10-30 recent usable games;
- game dates and time controls where available;
- confirmation that the games may be used for this research exercise;
- optional improvement goal or self-report;
- a proposed game-set ID, such as `P01-GS01`.

Do not include real names, email addresses, usernames, account IDs, or unrelated profile information unless the study explicitly needs them. Use [participant-intake.md](participant-intake.md) and follow [data-handling.md](data-handling.md).

## Start checklist

1. Confirm that the participant meets [participant-criteria.md](participant-criteria.md).
2. Copy the supplied PGN into a controlled, uncommitted working location.
3. Record the participant and game-set metadata in the intake form.
4. Freeze the exact game set before producing either analysis condition.
5. Record the protocol version and current repository revision in the run manifest.
6. Analyze the participant independently using [analysis-template.md](analysis-template.md) and [analyst-guide.md](analyst-guide.md).
7. Produce and freeze Conditions A and B before participant evaluation.
8. Present both reports as Analysis A and Analysis B in randomized order where practical.
9. Record evaluation and reviewer material without changing the frozen reports.
10. Synthesize only after all planned participant material is frozen.

## Run creation

Create `runs/FPV-RUN-001/` only when the first real participant package is accepted. Record the run ID, protocol version, repository revision, participant IDs, game-set IDs, presentation order, review process, deviations, and status in its manifest.

Do not create empty participant directories. Do not commit raw PGNs or identifiable participant material unless an explicit data-handling decision permits it.

## Stop conditions

Stop before analysis if the participant has fewer than 10 usable games, the game set is dominated by excluded time controls, consent or use confirmation is missing, the games are not comparable, or the participant cannot complete the evaluation.

If analysis produces no defensible recurring pattern, record "insufficient evidence". Do not change the protocol or force a diagnosis.

