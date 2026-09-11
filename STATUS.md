# Chess Mentor Engine — Repository Handoff

**Prepared:** 2026-09-11  
**Contiguous numbered baseline:** M1–M34 qualified  
**Qualified semantic program:** Chess Knowledge Ontology K0–K7  
**Qualified post-M34 learner-intelligence packages:** M36, M39, M40, M41, M43, M44  
**Post-feature baseline:** `c8d28c235e2c2141ea96028835f360034051ea92`

This is the current restart handoff for `ThorStarlord/Chess-Mentor-Engine`.
Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
as the moving implementation authority and
[`docs/runbooks/m41-m44-tutor-decision-loop.md`](docs/runbooks/m41-m44-tutor-decision-loop.md)
for the latest focused restart/qualification path.

## Current outcome

The tutor-decision-loop Phase 1 milestone is complete:

```text
M43  Contradiction / Control Evidence Acquisition   MERGED - PR #86
M41  Ontology-Aware Intervention Matching           MERGED - PR #87
M44  Learner Progress Reference Surface              MERGED - PR #88
```

The numbering remains intentionally non-contiguous. **M35, M37, M38, and M42 are not
implied to be implemented.** Later-numbered qualified packages do not reserve or
complete missing labels.

The strongest currently qualified learner-facing chain is:

```text
M7 / M7C learner hypothesis + recurrence/contradiction authority
+ M9 intervention-selection authority
+ M10 bounded practice/transfer evidence
+ M11 longitudinal learner state
+ optional K7 typed chess-knowledge context
        |
        v
M36 deterministic current learner-state read model
        |
        v
M39 exact hypothesis evidence synthesis
        |
        v
M40 ranked next-action proposal
        |
        +-- challenge / control / collect evidence --> M43 candidate acquisition
        |
        +-- teach concept --------------------------> M41 intervention candidates
        |
        `--------------------------------------------> M44 reference presentation
```

M44 can present M36/M39/M40 plus optional exact M43/M41 consumer artifacts without
creating new learner, recurrence, pedagogical-selection, transfer, or execution
authority.

## M43 — Contradiction / Control Evidence Acquisition

**PR:** #86  
**Final head:** `70728729905f69beed2f608ec02ddd94c1e9cfbf`  
**Merge commit:** `a9552ee745d2bce862f2e94eb5ca9320870defbf`  
**CI run:** `34608614837`

M43 adds a transparent, content-addressed evidence-acquisition policy and plan for
these M40 actions:

```text
CHALLENGE_HYPOTHESIS
PRESENT_CONTROL
COLLECT_NEW_EVIDENCE
```

It can preserve already-classified M7C contradiction/counterexample/context-exception
units for presentation and can rank additional exact-current participant-local M7B
links as **potential** review/reassessment candidates.

Important distinction:

```text
M43 candidate != M7C relation
potential contradiction != contradiction established
successful case != mastery
ranked first != objectively best evidence
```

M43 records:

```text
decision_authority = candidate_only
m7c_effect = not_established
mastery = not_established
```

The default policy deduplicates current-synthesis positions, excludes contaminated
additional evidence, prefers new games/positions within equal candidate kinds, and
keeps missing K7 coverage explicit rather than interpreting it as negative concept
evidence.

Final qualification:

```text
896 passed
8 intentional regular-job Stockfish skips
Ruff PASS
compileall PASS
independent Stockfish job PASS
```

## M41 — Ontology-Aware Intervention Matching

**PR:** #87  
**Final head:** `a1fd0cfb6455a68ac5ea10390e7840009a3c0be3`  
**Merge commit:** `8aefe1183ce2623e50b3f732fc7de26164f4a014`  
**CI run:** `34610142609`

M41 gives an exact M40 `TEACH_CONCEPT` proposal a deterministic bridge toward the
existing M9 intervention registry.

It adds exact, content-addressed `InterventionSemanticProfile` sidecars that can state:

```text
target concepts
reinforced concepts
contraindicated concepts
training modes
```

Profiles bind an exact M9 intervention version and exact ontology fingerprint while
preserving content provenance. M41 deliberately does not infer semantics by parsing
intervention prose.

Candidate statuses are:

```text
eligible_candidate
possible_candidate
insufficient_information
ineligible
```

Multiple eligible candidates remain multiple candidates. M41 does not choose one.
Ontology prerequisites are exposed as `unverified_prerequisites`; they are not learner
deficiency or mastery claims.

M41 records:

```text
selection_authority = not_exercised
efficacy = not_established
mastery = not_established
```

**Product-pulled ontology result:** K0–K7 was sufficient for M41 v1. No ontology
schema/data expansion and no generic K8 were required.

Final qualification:

```text
904 passed
8 intentional regular-job Stockfish skips
Ruff PASS
compileall PASS
independent Stockfish job PASS
```

## M44 — Learner Progress Reference Surface

**PR:** #88  
**Final head:** `cdbf50c9af3154f940b0c575893a1ae51309e612`  
**Merge commit:** `c8d28c235e2c2141ea96028835f360034051ea92`  
**CI run:** `34611475360`

M44 adds:

```text
m44.learner-progress-view.v1
m44.learner-progress-reference-surface.v1
```

The presentation model composes exact M36/M39/M40 sources plus optional exact M43 and
M41 sources. It preserves M40 priority ordering and can display:

- current hypothesis, lifecycle, and M7C status;
- M39 evidence counts, source game/position units, gaps, and change conditions;
- ontology concept names/types and instructional recognition questions;
- M9 current intervention state and selected intervention refs;
- M10 practice/near/far/real-game evidence states;
- M40 next action, reasons, and blocking uncertainty;
- M43 challenge/control candidates and gaps when supplied;
- M41 intervention candidates/prerequisites/gaps when supplied.

The renderer is static escaped HTML, loads no scripts/network assets, validates the
exact M44 view before rendering, and is independently content-addressed.

M44 is **local reference presentation only**. It does not establish production
browser/device/accessibility/usability quality.

The first M44 candidate passed all functional tests and Stockfish but Ruff rejected
line length. The final amendment split presentation-model logic from HTML rendering,
which strengthened the architecture while preserving the public API, then the entire
exact head was requalified.

Final qualification:

```text
912 passed
8 intentional regular-job Stockfish skips
Ruff PASS
compileall PASS
independent Stockfish job PASS
```

**Product-pulled ontology result:** M44 also required no ontology expansion.

## Durable authority boundaries

Preserve all of these:

```text
concept definition != concept assertion != learner inference
K7 ontology projection != M7C recurrence classification
M36 read model != learner-state mutation authority
M39 synthesis != M7C recurrence authority
M40 proposal != execution authority
M43 evidence candidate != M7C contradiction/refutation
M41 intervention candidate != M9 applicability mapping
M41 rank != M9 selection
M44 rendering != learner inference
M40 transfer-test proposal != M10 transfer evidence
successful evidence case != mastery
transparent heuristic policy != empirically optimal pedagogy
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective chess truth
```

## Product-pulled ontology rule

Do **not** open a generic K8 merely to expand vocabulary, detectors, relationships, or
pedagogy metadata.

Use this sequence instead:

```text
concrete learner/tutor consumer needs semantic distinction X
-> prove K0-K7 cannot represent X safely
-> add the minimum ontology extension
-> add ontology rejection tests
-> consume it in the requesting feature
-> qualify ontology + consumer together
```

M41 and M44 both demonstrated that existing K0–K7 semantics can already support new
product capabilities without ontology churn.

## Current operational boundary

M36/M39/M40/M41/M43/M44 are deterministic Python APIs/reference surfaces. M44 does not
add a production web frontend or a new public CLI. Existing M12–M30 operator commands
remain the established CLI surface.

No package in this milestone:

- uses production credentials;
- calls paid/live external model services;
- deploys infrastructure;
- creates a hosted product;
- establishes empirical tutoring effectiveness;
- grants automatic learner-state mutation or action execution authority.

## Recommended next priorities

These are recommendations, not automatic implementation authority.

1. **M42 — Transfer / Retest Planning** (`REPOSITORY_ONLY / HERMETIC_VALIDATION`)
   - consume M40 `RUN_NEAR_TRANSFER_TEST` / `RUN_FAR_TRANSFER_TEST` proposals;
   - create bounded provenance-complete test plans;
   - keep planning separate from actual M10 outcome evidence;
   - do not infer mastery from scheduling or completion.
2. **M45 — Batch Games -> Mentor Queue** (`REPOSITORY_ONLY / HERMETIC_VALIDATION`)
   - rank a bounded set of recent participant games/positions by learner relevance,
     contradiction value, transfer value, uncertainty, and novelty rather than raw
     centipawn loss alone;
   - reuse M7C/M39/M40/K7 rather than building a second learner model.
3. **M46 — Adaptive Socratic Tutor** (`REPOSITORY_ONLY / HERMETIC_VALIDATION` first)
   - use current learner evidence, ontology recognition cues, and explicit pedagogical
     actions to choose bounded question/hint/reveal steps;
   - keep model language downstream of deterministic evidence and preserve pre-reveal
     measurement boundaries.
4. **M35/M37 only when pulled by a concrete consumer blocker.** Do not increase CLI or
   compatibility infrastructure merely to fill missing milestone numbers.

## External/human authority still pending

The repository still cannot mechanically establish:

- real participant usefulness or approval;
- accessibility/device/browser quality of a production frontend;
- empirically effective/optimal tutoring policy;
- intervention-caused learning or mastery;
- production privacy/security/compliance posture;
- hosted auth/multi-tenancy readiness;
- production provider retry/cost/secrets operations.

Those remain explicit external/human gates rather than claims to simulate locally.
