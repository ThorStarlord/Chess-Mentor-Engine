# Version 1.0 Release Candidate Scope

This package is limited to repository-only and hermetic distribution qualification.

It changes only release identity, artifact validation, clean-install CI, rejection tests,
and release documentation. It does not add chess analysis, learner inference, tutoring
behavior, hosted infrastructure, or production integrations.

The package succeeds only when the exact candidate passes the existing source and
Stockfish gates plus the new `release-distribution` job.
