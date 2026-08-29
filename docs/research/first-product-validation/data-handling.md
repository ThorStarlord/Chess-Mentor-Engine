# Research data handling

Status: Operational preparation only. No participant data is currently stored in this repository.

This guide applies to the first manual validation run. It protects participant privacy without changing the chess positions or game histories used for analysis.

## Minimize data

Use only what the protocol needs:

- anonymous participant ID;
- rating or eligibility band;
- game PGN and required provenance;
- dates and time controls where relevant;
- optional goal or self-report;
- analysis, evaluation, and reviewer records.

Do not commit real names, emails, platform usernames, account IDs, contact details, or unrelated profile data.

## Separate identity from research records

Keep any identity-to-participant-ID mapping outside the repository and outside committed research artifacts. The research record should use IDs such as `P01` and game sets such as `P01-GS01`.

## Preserve chess evidence

Anonymization may remove identifying headers, but it must not alter moves, board positions, game results, or other evidence needed for analysis. Record which headers were removed in the participant's intake or game-set record.

For each material claim, preserve enough provenance to recover the position, including participant ID, game ID, move number, side to move, relevant move or sequence, and objective analysis evidence. Record engine name, version, settings, and limits when known. Do not invent missing settings.

## Storage and commit rules

Store raw PGNs and any identifiable source material in a controlled, uncommitted working location. Commit only anonymized research artifacts that are necessary for reproducibility and allowed by the participant-use confirmation.

Do not create participant directories until a real participant package is accepted. Do not retain unused personal data in analysis notes.

## Corrections and deletion

If an identifying detail appears in a research artifact, remove it from the artifact and record the correction without copying the detail into the correction log. If a participant withdraws permission, stop using their material and follow the applicable local data-retention requirements before removing research copies.

