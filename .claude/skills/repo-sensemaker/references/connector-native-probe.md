# Connector-native exact-SHA probe

This reference defines the deterministic state-currency backend used by `repo-sensemaker` when the authorized target-access surface is a read-only GitHub connector rather than a local checkout.

## Backend identity

`github_connector_exact_sha_v1`

This backend is an alternative probe surface, not a fallback that weakens the requirement to verify current state before synthesis. It exists so a connector-only campaign can satisfy the same evidence-authority principle without creating an unauthorized local checkout.

## Preconditions

Use this backend only when all of the following are true:

- the target repository is accessible through the GitHub connector;
- an exact 40-character target commit SHA is known;
- target access is read-only;
- the execution contract does not authorize a local checkout or local probe execution.

If the exact target SHA cannot be resolved through GitHub, stop. Do not silently read a mutable branch tip instead.

## Required procedure

Before writing Sections 3-9 of the Repository Sensemaking Brief:

1. **Verify target identity.** Resolve the exact target commit through GitHub and confirm that every repository-content observation is pinned to that SHA.
2. **Inspect the exact tree.** Enumerate the repository structure at the exact target SHA and inspect the files needed for the diagnosis, including relevant README/docs, manifests, test configuration, workflow configuration, and the files cited by decision-changing claims.
3. **Pin file evidence.** For every file used as decision-changing evidence, preserve the repository path, GitHub-supplied blob SHA, and the smallest relevant line range. Record blob identities in Section 7's state-currency prose or another schema-compatible evidence string; do **not** add undeclared keys to Section 8's `evidence_excerpts` objects. A default-branch read is not equivalent evidence.
4. **Separate live metadata.** Issues, pull requests, workflow runs, and other GitHub metadata that are not part of the target tree may be queried when relevant, but label them as live metadata observed at query time. Record the stable GitHub resource identity (number/id/URL as available). Do not present live metadata as if it were part of the immutable target snapshot.
5. **Distinguish observation classes.** Treat exact-SHA tree/file/blob observations as verified state of the pinned snapshot; treat live GitHub metadata as verified only at its observation time; treat repository prose as a documented claim until corroborated by one of those observations.
6. **Do not invent local-only measurements.** `verification_gap.vg`, `context_entropy.ce`, `fixtures_coverage.coverage`, and `churn` are local Probe Engine outputs. Under `github_connector_exact_sha_v1`, they are unavailable unless an explicitly authorized deterministic remote adapter computes them. Never approximate, infer, or back-fill those values from prose inspection.
7. **Fail closed on measurement-dependent claims.** If a diagnosis materially depends on a local-only metric that is unavailable on this surface, label that claim unmeasured and either use different exact-SHA evidence or set `escalation_recommended: true`. Do not convert missing measurement into a guessed result.
8. **Declare the backend in the brief.** In Section 7's state-currency discussion, identify `github_connector_exact_sha_v1` and the exact target SHA. Section 8 evidence excerpts must cite files/line ranges actually read at that SHA.

## Determinism boundary

The deterministic part of this backend is the immutable Git object graph reachable from the exact target SHA. Repeating the same connector reads against the same SHA should resolve the same tree/blob identities. Live GitHub metadata is intentionally outside that deterministic snapshot and must remain separately labeled.

This backend therefore does not claim to reproduce local-only filesystem observations such as ignored files, untracked files, local worktree dirtiness, or metrics derived from them. Those facts are **unmeasured on this surface**, not presumed absent.

## Safety constraints

- No local target checkout is required or implied.
- No target mutation is permitted.
- No external provider API is introduced.
- No mutable branch tip may substitute for the exact target SHA.
- No unavailable metric may be fabricated.
- Connector evidence does not silently become canonical Evidence; classification remains controlled by the calling workflow/campaign.

## Relationship to the local Probe Engine

When a local checkout is authorized, `repo-sensemaker` continues to use `python scripts/probe-repo.py --repo-root <target-repo> ...` and may rely on its measured report fields.

When only read-only GitHub connector access is authorized, use this contract instead. The two backends share the same rule: decision-changing current-state claims must be grounded in an actual observation, and anything not observed must remain explicitly unverified or unmeasured.
