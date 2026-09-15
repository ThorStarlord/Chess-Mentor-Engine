# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Integrated main authority:** `VERSION_1_REPOSITORY_READY`.  
**V1 implementation baseline:** `8e3abf063b2af7d09a46495f5e35c85c86d58f01`.  
**Historical V1 release identity:** `chess-mentor-engine==1.0.0`.  
**Post-V1 development identity:** `chess-mentor-engine==1.1.0.dev0`.  
**Active development candidate:** PR #98 — local product-use observation.  
**Contiguous numbered milestone boundary:** M34.  
**Qualified semantic program:** K0-K7.  
**Qualified learner-intelligence packages:** M36, M39, M40, M41, M42, M43, M44, M45, M46.

`STATUS.md` is the restart handoff. Software qualification is not production approval or empirical tutoring efficacy.

## Integrated V1 capability map

```text
M1-M4    canonical chess evidence, deterministic features, engine evidence,
         played-decision comparison and diagnostic selection
M5-M7    participant evidence, reasoning discrepancy, learner hypothesis and
         M7C recurrence/contradiction authority
M8-M11   controlled tutoring, intervention selection, bounded outcome/transfer
         evidence, append-only longitudinal learner state
M12-M18  local/operator tooling, persistence, engine-backed analysis,
         presentation, deterministic mentor grounding, diagnostic queues
M19-M22  model-language provenance, bounded evaluator judgment, candidate launch,
         cross-layer evaluation fidelity
M23-M30  persistent reviewed-coaching runtime, verification, local review,
         participant-scoped navigation/export
M31-M34  privacy/retry preflight, consumer fidelity, deterministic traceability,
         hermetic recovery reconciliation
K0-K7    typed chess semantic ontology, assertions, conservative detectors,
         sidecar context and M7C-preserving learner projection
M36      deterministic current learner-state read model
M39      deterministic current hypothesis evidence synthesis
M40      transparent teaching-priority / next-session proposal policy
M43      contradiction/control evidence-acquisition candidate planning
M41      ontology-aware intervention candidate matching before M9 selection
M42      bounded near/far transfer and retest planning before M10 outcomes
M44      deterministic learner-progress presentation + local reference HTML
M45      participant-scoped bounded mentor queue over diagnostic candidates
M46      adaptive Socratic tutor-action proposal over the exact M8 lifecycle
V1       local composition + repository-authority reconciliation + qualified
         1.0.0 wheel/sdist clean-install distribution contract
```

M35, M37, and M38 remain unimplemented labels. K8 and M47 are not active programs by default. Their absence does not make Version 1.0 incomplete.

## Historical V1 provenance

| Package | PR | Final head | Merge commit | Qualification |
| --- | --- | --- | --- | --- |
| Local tutor vertical slice | #94 | `9867105509e0f243a7823066d626abe1cad40148` | `2fd14c32e81d19222cc3e2f332337c00f8086f5f` | source + independent Stockfish PASS |
| Authority reconciliation | #95 | `f12758c52de3e13468774d13c324510d48e6d7d7` | `c41fda2f1c3c2002a4c960270b38ef3cce1ad144` | exact candidate gates PASS |
| Release/distribution | #96 | `4b5512a1b5d67ad0df43000898b5d371701d832c` | `8e3abf063b2af7d09a46495f5e35c85c86d58f01` | run `34673791962` PASS; post-merge `34673834249` PASS |

The V1 release candidate source suite reported 957 passed and 8 intentional regular-job Stockfish skips, followed by Ruff and compileall PASS. The independent Stockfish job remains the real-engine witness.

## Active post-V1 candidate boundary

PR #98 adds a downstream observation/consumer layer without acquiring upstream authority.

```text
exact selected M8 checkpoint
        |
        v
guided baseline capture
        |
        v
exact M8 baseline freeze
        |
        +------------------------------+
        |                              |
        v                              v
immutable product-use observation   explicit participant self-report
        |                              |
        +--------------+---------------+
                       |
                       v
          deterministic participant-scoped report
```

The layer's executable claim ceiling is:

```text
claim_scope = descriptive_local_product_use_only
learning_effect = not_established
tutor_efficacy = not_established
mastery = not_established
```

### Observation contract

Artifact kind:

```text
post-v1.interaction-observation.v1
```

Observations are immutable, content-addressed, participant-scoped, timezone-stamped, and depend on an exact M8 session artifact through the existing `LocalArtifactStore` dependency graph.

The bounded event namespace includes review/position/prompt/response/freeze/proposal/abandonment/completion/feedback events. Supporting an event type does not imply every event is automatically produced by every consumer.

### Guided consumer contract

`cme-local-tutor review` consumes an existing exact selected M8 checkpoint plus an exact structural `PositionContextPacket`. It calls existing M8 transitions for position presentation, protocol-bound prompt presentation, participant response capture, and response freeze.

It stops when the M8 checkpoint is `frozen`.

It does not reveal objective evidence, attach an M6 comparison, attach M7 context, generate an explanation, complete the session, or execute M46. The returned payload explicitly reports `m46_execution = not_performed` and points to the existing `cme-local-tutor next` authority for proposal inspection.

### Self-report contract

`cme-local-tutor feedback` records bounded participant self-report:

```text
review_relevance     1..5
workflow_clarity     1..5
would_review_again   1..5
note                 optional participant-authored text
```

This is descriptive self-report, not learner-state or efficacy evidence.

### Report contract

`cme-local-tutor report` aggregates only the exact participant's observation records and returns event counts, explicit action counts when present, and feedback metadata. Its claim scope is `descriptive_local_product_use_summary_only`, with learning effect, tutor efficacy, and mastery still `not_established`.

## Current operational surfaces

Installed commands remain:

```text
cme
cme-local-tutor
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

Principal local workflow commands now include:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
cme-local-tutor start|next|review|feedback|report
```

## Version identity and distribution

`1.0.0` remains the historical V1 release identity. Active post-V1 development uses `1.1.0.dev0`.

The `release-distribution` CI job derives its expected artifact identity from `pyproject.toml`, validates wheel/sdist metadata, entry points and package data, clean-installs the exact built wheel with `--no-index --no-deps`, and smokes the installed command surfaces.

Changing the development identity does not itself approve, publish, or promise a future `1.1.0` release.

## Qualification commands

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests tools
STOCKFISH_EXECUTABLE=/path/to/stockfish \
  python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The exact PR candidate also requires:

```text
test-and-lint          PASS
release-distribution   PASS
stockfish-integration  PASS
```

## Claim ceiling

The repository can mechanically establish deterministic local composition, provenance/identity checks, authority preservation, exact M8 baseline orchestration, immutable descriptive observation persistence, participant isolation, deterministic usage aggregation, and distributable-artifact integrity.

It still does **not** establish:

- causal cognitive diagnosis or permanent learner traits;
- real-participant usefulness;
- tutoring efficacy;
- mastery or intervention-caused improvement;
- empirically optimal tutoring policies;
- production browser/device/accessibility/usability quality;
- production provider/vendor, privacy/security, auth, hosted persistence, or deployment;
- successful public artifact publication.

## Core boundaries

```text
objective chess truth != participant evidence != learner inference
K7 projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/refutation
M41 intervention candidate != M9 selection
M42 plan != M10 outcome evidence
M44 rendering != learner inference
M45 mentor priority != learner diagnosis / implicit consent
M46 proposal != M8 execution / exposure authority
post-V1 observation != learner inference / tutoring efficacy / mastery
participant self-report != objective efficacy evidence
successful evidence case != mastery
repository release qualification != hosted-product approval
```

## Next boundary

Version 1.0 is already repository-ready. PR #98 is a post-V1 candidate, not a missing V1 package.

After the repository candidate is integrated, the next meaningful evidence must come from actual local use. Do not automatically promote M35/M37/M38/K8/M47, a browser interface, hosted infrastructure, or policy expansion. Reconcile the resulting observations first and select one bounded next objective only if the evidence warrants it.
