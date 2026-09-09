# Chess Mentor Engine - Current Build Status

**Status authority:** current implementation and qualification status  
**Updated for:** bounded M10 outcome/transfer evidence  
**Implementation base:** `078fa663feb83b21b57fcab7a0f8d7a66f7d9286`

This is the concise current authority. Detailed milestone contracts and historical
qualification provenance remain in the architecture/decision records and Git
history. An implementation claim is not a claim of empirical tutoring efficacy.

## Current milestone board

```text
M1 - Trustworthy Chess Evidence Substrate       QUALIFIED
M2 - Deterministic Chess Feature Extraction     QUALIFIED
M3 - Engine Evidence                            QUALIFIED
M4 - Diagnostic Position Selection              QUALIFIED
M5 - Player Decision Evidence                   QUALIFIED
M6 - Reasoning Discrepancy                       QUALIFIED
M7 - Learner Hypothesis Ledger / M7Q             QUALIFIED
M8 - Evidence-Aware Tutor Session                QUALIFIED
M9 - Training Intervention Registry              QUALIFIED
UCI evidence contract repair (provider 0.2)      MERGED - PR #39
Local artifacts / verified M8 recovery           MERGED - PR #40
M10 - Bounded Outcome / Transfer Evidence        IMPLEMENTED - CI QUALIFICATION PENDING
M11 - Longitudinal Learner State                 NOT STARTED
M12+ - CLI/UI/richer LLM productization          NOT STARTED
```

M10 implements the bounded evidence contract in ADR 0009. It does not establish
mastery, causal effectiveness, empirical learner improvement, or M11. Its final
qualification requires the complete regression/lint and external Stockfish gates.

## Evidence path and authority boundaries

```text
PGN / canonical position
-> objective chess + provenance-bound engine evidence
-> decision comparison / diagnostic selection
-> frozen player decision evidence
-> position-local reasoning discrepancy
-> participant-specific recurring descriptive hypothesis
-> controlled evidence-aware tutoring
-> explicit hypothesis/intervention applicability
-> selected / ineligible / unclear
-> predeclared outcome protocol for the exact selected intervention
-> frozen attempts / documented practice / authored scoring evidence
-> separate practice, near, far and real-game evidence assessments
```

Downstream results do not rewrite or strengthen upstream semantic authority.

## M7 - Learner Hypothesis Ledger

M7 is qualified under ADR 0006. It supplies stable participant-specific lineages,
append-only revisions/lifecycle, exact M6 evidence mappings, versioned recurrence,
one participant-position per unit, support/contradiction/counterexample/context
exception relations, explicit challenge review and rebuildable snapshots.

Statuses remain `insufficient`, `isolated`, `candidate_recurrence`,
`supported_recurrence`, `contradicted`, and `unclear`. Supported recurrence is not
a causal cognitive mechanism, permanent trait, universal weakness score, or
automatic training eligibility.

Historical qualification: PR #35, corpus head
`334f9c769e50046078d5508ecce4fac9d52cd70a`, merged
`5db3a518afdec38ee052ec3c5dbb453a03c8a739`; 307 passed, 8 intentional
external-engine skips, 13 focused M7Q tests, Ruff and Stockfish passed.
See [M7 qualification](../architecture/m7-qualification.md).

## M8 - Evidence-Aware Tutor Session

M8 is qualified under ADR 0007. It enforces exact position presentation,
minimal-response/optional-probe capture, complete pre-reveal freezes, objective
reveal, exact final-capture M6 comparison, complete active M7 context when attached,
authored explanation provenance and immutable event/snapshot histories.

Historical qualification: PR #36, head
`055325360b14e955b2e94c5c4fcdfd739ba8c430`, merged
`84edce598b55176bbded422fc88cc8f8101d5575`; 320 passed, 8 intentional
skips, 13 focused M8 tests, Ruff, Stockfish and post-merge CI passed.
See [M8 architecture](../architecture/evidence-aware-tutor-session.md).

PR #40 adds SQLite-backed immutable artifacts and verified fresh-process M8
recovery. Typed recovery covers M8, its embedded records and required prompts;
additional archival closure must be declared explicitly. It is local plaintext,
not an authenticated hosted service. See
[durability scope](../architecture/durable-artifacts-and-replay.md).

## M9 - Training Intervention Registry

M9 is qualified under ADR 0008. Versioned exercises/interventions, a registry,
explicit participant-specific applicability mappings and a deterministic policy
produce `selected`, `ineligible`, or `unclear`. Current active supported recurrence
is necessary but not sufficient. Multiple applicable mappings remain unclear;
there is no opaque free-text ranking or efficacy inference.

Historical qualification: PR #37, head
`f5e671b56fd977818aaa33b4e4e5fd7bb967316b`, merged
`5d880ef878154e3b20195044314346054214eb1b`; 336 passed, 8 intentional
skips, 16 focused M9 tests, Ruff, Stockfish and post-merge CI passed.
See [M9 architecture](../architecture/training-intervention-registry.md).

## M10 - Bounded outcome and transfer evidence

The new `evaluation` package implements exact selected-M9 binding, an authored
versioned criterion/rubric/context policy, frozen attempts, documented practice
completion, scored observations and immutable ledger snapshots. Assessment keeps
practice, near transfer, far transfer and real-game evidence independent.

Freshness is conditional on declared exposure scope and the supplied complete
known history. The implementation rejects promotion from nonselected M9 results,
exercise/rubric/version mismatches and invalid chronology. It excludes exposed,
unknown, assisted, early-feedback, premature or reused-position evidence from
transfer support. Repetition and multiple coders do not inflate independent
counts; disagreement, failures, missing scores and unscorable evidence remain
visible. Real-game independence uses game IDs rather than relabeled sessions.

Each dimension reports `insufficient`, `supported`, `not_supported`, `mixed`, or
`unclear`, with counts and included/excluded evidence references. `Supported` is
conditional evidence under the declared criterion, not proof of caused learning.
`mastery` and `causal_effect` remain `not_established`, even when all dimensions
are supported. M10 does not automatically revise M7 or implement M11.

See [ADR 0009](../decisions/0009-outcome-transfer-evidence-contract.md),
[M10 architecture](../architecture/outcome-transfer-evidence.md), and
[the M10 runbook](../runbooks/m10-outcome-transfer-evidence.md).

## Qualification commands

```bash
pytest tests/test_outcome_evidence.py tests/test_m10_qualification.py
pytest
ruff check .
python -m compileall -q src tests
pytest tests/integration/test_stockfish_uci.py
```

Stockfish is external and configured with `STOCKFISH_EXECUTABLE`. The M7-M9
operational protocol remains in [its runbook](../runbooks/m7-m9-milestone-runbook.md).

## Current claim ceiling

The implemented software preserves evidence identity and provenance, bounded
hypotheses, conservative training selection, verified local M8 recovery, and
separate protocol-bound outcome evidence. M10's synthetic corpus qualifies code
behavior; it is not a new participant trial.

The repository does not claim causal cognitive diagnosis, permanent learner
traits, optimal/effective intervention selection, intervention-caused improvement,
automatic mastery, validated universal thresholds, globally complete exposure
history, a qualified longitudinal learner-state model, or an end-user CLI/UI.
Generic M10 JSON can be archived with the existing store; typed M10 recovery and
automatic schema migration remain outside this feature.

## Next boundary

The three-feature queue ends with this bounded M10 implementation. M11 remains
unstarted and requires separate authorization. Neither this status update nor a
supported outcome assessment authorizes autonomous learner-state changes.
