# Chess Mentor Engine — Repository Handoff

**Handoff scope:** post-M34 Chess Knowledge Ontology program K0–K7  
**Repository:** `ThorStarlord/Chess-Mentor-Engine`  
**Program start baseline:** `b2256e6dd9fb68fb0b22edcb51f29def9679ccf3`  
**Post-feature baseline:** K7 merge `0ca0dc42ef84a3f9a6c120b1dc0561d00a73603c`  
**Prepared:** 2026-09-11  

This is the latest durable handoff. The numbered milestone implementation remains
qualified through **M34 — Hermetic Reviewed-Coaching Recovery Reconciliation**. On
top of that boundary, the repository now also has a separately named, qualified
**Chess Knowledge Ontology program K0–K7**. The K labels deliberately do not consume
or imply provisional M35+ milestone numbers.

Use [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
as the moving implementation authority, this file as the latest handoff,
[`docs/runbooks/chess-knowledge-ontology-program.md`](docs/runbooks/chess-knowledge-ontology-program.md)
for the K0–K7 restart/qualification path, and
[`docs/runbooks/m32-m34-milestone-runbook.md`](docs/runbooks/m32-m34-milestone-runbook.md)
for the preceding M32–M34 milestone.

## Program outcome

All K0–K7 packages are implemented, qualified on exact final candidate heads, and
merged into `main`.

```text
K0–K2  Ontology authority + registry + tactical/Lichess foundation   MERGED - PR #75
K3     Strategy, evaluation-factor, position-feature, plan vocab     MERGED - PR #76
K4     Provenance-bound chess-knowledge assertions                   MERGED - PR #77
K5     Conservative deterministic concept detectors                  MERGED - PR #78
K6     Authority-preserving M19 coaching sidecar                     MERGED - PR #79
K7     M7C-preserving learner-knowledge projection                   MERGED - PR #80
```

The new semantic path is:

```text
registered concept definition
        |
        v
versioned ontology registry / crosswalk
        |
        v
provenance-bound concept assertion
        |
        +--> conservative deterministic detector evidence
        |
        +--> K6 model-consumable sidecar bound to an unchanged M19 request
        |
        +--> K7 projection onto existing M7C recurrence units
             while preserving the original M7C relation verbatim
```

The governing invariant is:

```text
concept definition != concept assertion != learner inference
```

A concept occurring in a position does not by itself say what a participant noticed,
does not establish a learner weakness, and does not select an intervention.

## Qualified package provenance

| Package | PR | Final head | Merge commit | Successful CI |
| --- | --- | --- | --- | --- |
| K0–K2 | #75 | `5e76400ed0df80ad845c07bfdedec08e3c46af45` | `f52b3773b773883d1ac9f476d563c70433bdeb63` | `34590630613` |
| K3 | #76 | `ecd5bf19517d9e8a657f1c2f1044596bc5e3f88b` | `a0c6dcb01060e84f2b9ac1b517a39873720a4b7a` | `34591111549` |
| K4 | #77 | `2d7537b260007613b81e720be683b531b2f8bc55` | `fd43a0a416aceb33444b7f2b62edf1d2e5767872` | `34591799180` |
| K5 | #78 | `be0cffdbe73c3b37e998ea805f87ae7a80493cf8` | `b417d170b69de271635fb24b666bea2f6f290d2e` | `34592343696` |
| K6 | #79 | `eb3dcc7a06485a40c6a9fdcd9a2429c16a597bdf` | `8653b058e2ed7af598a80c9293bbc51d3e5da2bf` | `34592709220` |
| K7 | #80 | `f4cb0721d9769b067985d253be4659e8ccd888bd` | `0ca0dc42ef84a3f9a6c120b1dc0561d00a73603c` | `34595432067` |

Every final package head passed the repository PR gate: full pytest, Ruff,
`compileall`, and the independent Stockfish integration job. K7's final run collected
865 tests and completed with **857 passed, 8 intentional regular-job Stockfish
skips**, Ruff PASS, compile PASS, and the independent Stockfish witness PASS.

Intermediate style-only failures were not merged. K0–K2 and K4 were amended and
re-qualified on new exact heads before merge.

## K0–K2 — ontology foundation

Delivered:

- ADR 0012 defining `concept definition != concept assertion != learner inference`;
- strict stdlib-only ontology model, loader, registry, validator, and deterministic
  fingerprints;
- stable dotted concept IDs independent of display labels;
- concept kinds, detector-support levels, assertion-authority ceilings,
  relationships, hierarchy, external mappings, and pedagogy metadata;
- fail-closed validation for duplicate IDs, graph cycles, aliases, unknown targets,
  mapping collisions, unexpected JSON fields, and authority drift;
- initial tactical/mating/defensive vocabulary;
- a Lichess puzzle-theme crosswalk that preserves one-to-many ambiguity such as
  broad `pin` rather than collapsing absolute and relative pins.

K0–K2 establish vocabulary and registry infrastructure. They do not assert that a
concept occurs in an arbitrary position and do not mutate learner state.

## K3 — strategic/evaluation/plan vocabulary

Delivered:

- composed ontology fragments with content version `1.1.0`;
- deterministic rule and position-feature vocabulary;
- strategic principles covering opening, pieces, pawn structure, exchanges/space,
  prophylaxis, weaknesses, and endgames;
- qualitative positional-evaluation factors without pretending to decompose engine
  scores arithmetically;
- strategic plan vocabulary distinct from concrete best moves and M9 training
  interventions;
- explicit principle-conflict relationships where heuristic priorities can diverge.

K3 is semantic vocabulary, not a strategic evaluator or move-selection engine.

## K4 — provenance-bound assertions

Delivered:

- bounded subjects for position, move, move sequence, and position comparison;
- exact evidence references and source provenance;
- content-addressed `KnowledgeAssertion` and `KnowledgeAssertionBundle` records;
- exact concept and ontology fingerprint binding;
- distinct authority classes for deterministic facts/patterns, engine-derived claims,
  external taxonomy tags, heuristic assessment, model interpretation, and human
  ratification;
- external Lichess tags preserved as external evidence rather than promoted to CME
  detector results.

K4 lets the repository represent a bounded chess-knowledge claim. It does not make
that claim participant evidence or a learner diagnosis.

## K5 — conservative deterministic detectors

Qualified automatic detection is intentionally narrow.

Position-level support includes:

```text
check / checkmate
absolute pin
bishop pair
open / semi-open file
isolated / doubled / passed pawns
pawn islands
```

Move-transition support includes:

```text
promotion / underpromotion
moved-piece fork
discovered check
double check
```

The move detector replays exact legal board transitions. The position detector
reuses qualified deterministic chess evidence where appropriate, including M2's
absolute-pin feature.

K5 intentionally does **not** automatically detect context-heavy concepts such as
initiative, prophylaxis, relative pins, deflection, overload, fortress, strategic
plans, principle violations, or pedagogical meaning.

## K6 — M19 model-coaching sidecar

Delivered:

- `KnowledgeCoachingContext` projecting exact ontology assertions into a
  model-consumable, content-addressed context;
- fixed anti-promotion instructions that preserve assertion authority;
- `KnowledgeModelBinding` referencing one already-valid M19 request by exact ID and
  fingerprint plus one exact ontology context;
- an opt-in provider wrapper carrying the unchanged `m19_request`, the chess
  knowledge context, and the binding.

K6 does **not** add keys to, refingerprint, or widen the authority of M19. Existing
provider paths remain unchanged unless an application explicitly adopts the sidecar.

## K7 — M7C-preserving learner projection

Delivered:

- `HypothesisKnowledgeProjection` bound to one exact M7C hypothesis assessment and
  one exact ontology fingerprint;
- attachment of position-level knowledge bundles to exact M7C recurrence units by
  game/position identity;
- verbatim preservation of M7C relations:
  `supports`, `contradicts`, `successful_counterexample`, `context_exception`,
  `unclear`, and `mixed`;
- explicit partial coverage through covered/uncovered recurrence-unit IDs;
- descriptive per-concept counts by M7C relation, assertion status, authority,
  source positions, and source games;
- regression evidence that the same chess concept may occur in both supporting and
  contradictory units without reclassifying either.

M7C remains the recurrence authority. K7 does not decide whether a hypothesis is
supported, change recurrence thresholds, create causal learner traits, mutate M7,
or select M9 interventions.

## Current operational boundary

The numbered milestone board remains qualified through M34. K0–K7 are an additional
qualified semantic program layered over those existing contracts.

No K0–K7 package adds a new production CLI command. The ontology program currently
exposes Python API/reference-document surfaces. Existing commands remain the M12–M30
operator set such as `cme`, `cme-candidate-tutor`, `cme-reviewed-coaching`, and
`cme-participant-review`.

The K6 model sidecar is opt-in. It does not cause a provider call by itself. K7 is a
read/projection layer over already-qualified M7C recurrence evidence and does not
perform a learner-state mutation.

## Claim ceiling and remaining external gates

The ontology program adds typed chess semantics and bridges those semantics to model
and learner consumers while preserving upstream authority. It still does **not**
establish:

- causal cognitive diagnosis or permanent learner traits;
- automatic or empirically optimal learner-hypothesis creation;
- automatic M7/M11 mutation from ontology assertions, model calls, or tutoring runs;
- automatic M9 intervention selection or intervention-caused improvement;
- automatic mastery or transfer;
- complete deterministic detection for the ontology vocabulary;
- semantic correctness of heuristic/model/human assertions merely because their
  concept IDs are registered;
- semantic correctness, safety, or pedagogical quality of arbitrary model prose;
- production provider/vendor approval, credentials, retry/backoff, cost/SLO, or
  privacy/security authority;
- external-side-effect idempotency or production recovery correctness;
- production frontend browser/device/a11y/localization/usability quality;
- hosted authentication/authorization, multi-user persistence, observability, or
  deployment readiness;
- empirical tutoring efficacy.

M16 remains the deterministic mentor-grounding ceiling. M19 remains model-language
provenance rather than chess truth. M7C remains recurrence authority. K5 detectors
own only their explicitly qualified mechanical subset.

## Recommended next priorities

These are recommendations, not an automatically approved queue.

1. **Deterministic learner-state read model (REPOSITORY_ONLY).** Use existing
   M7/M9/M10/M11 evidence and optionally K7's typed concept projection to expose what
   is currently supported, contradicted, trained, transferred, or still uncertain
   for one participant without creating new learner authority.
2. **Hypothesis evidence synthesis / contradiction-oriented learner intelligence
   (REPOSITORY_ONLY / HERMETIC_VALIDATION).** Reuse M7C as recurrence authority and
   use ontology concepts as descriptive context rather than building a competing
   recurrence engine.
3. **Teaching-priority and intervention-matching policies
   (REPOSITORY_ONLY / HERMETIC_VALIDATION).** Let the ontology's principles, plans,
   and pedagogy metadata inform explicit future policy contracts, while keeping M9
   selection and efficacy claims separate.
4. **Operator exposure for qualified read/projection artifacts
   (REPOSITORY_ONLY).** Expose useful M32/M33 and/or ontology read surfaces only when
   a concrete consumer needs them rather than expanding infrastructure speculatively.
5. **External adoption and human QA (EXTERNAL_AUTHORITY).** Production frontend,
   provider, privacy/security, usability, retry/idempotency, and empirical teaching
   claims still require their real external witnesses.

## Restart instructions

1. Read this `STATUS.md`.
2. Read `CONTEXT.md`, `docs/product/repository-build-status.md`,
   `docs/architecture/architecture.md`, and
   `docs/runbooks/chess-knowledge-ontology-program.md`.
3. Confirm live `main` and recent commits before relying on hashes in this handoff.
4. Run the focused ontology suites, then the full repository gate and independent
   Stockfish witness.
5. Preserve these boundaries:

```text
concept definition != concept assertion != learner inference
ontology concept presence != M7C hypothesis relation
K7 descriptive projection != recurrence reclassification or learner mutation
K6 ontology sidecar != M19 request identity or M16 factual authority
external taxonomy tag != deterministic CME detector result
registered concept != automatically detectable concept
heuristic principle != engine-evaluation decomposition
strategic plan != best move != M9 training intervention
M16 deterministic grounding != M19 model prose
M20 evaluator acceptance != objective chess truth
M34 resume eligibility != retry authorization or retry execution
```

6. Extend deterministic detection only for concepts whose exact operational semantics
   and near-miss rejection cases can be qualified.
7. Reuse M7C for recurrence/support/contradiction authority; do not create a parallel
   learner-recurrence subsystem inside the ontology.
8. Do not modify M19 request identity to adopt K6; use the qualified sidecar/binding
   boundary.
9. Treat missing K7 coverage as missing ontology evidence, not as concept absence.
10. Begin future product milestones from live `main` and a fresh bounded queue.

## Key references

- `docs/decisions/0012-*` — ontology authority decision
- `docs/chess-knowledge/` — ontology vocabulary, detector, sidecar, and learner
  projection documentation
- `docs/runbooks/chess-knowledge-ontology-program.md`
- `docs/product/repository-build-status.md`
- `docs/product/chess-mentor-engine-repository-build-plan.md`
- `docs/runbooks/m32-m34-milestone-runbook.md`
- PR #75 through PR #80 — K0–K7 implementation program
