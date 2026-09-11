# Chess Mentor Engine

Chess Mentor Engine is a persistent chess-learning system that keeps objective
chess evidence, chess-knowledge semantics, participant evidence, learner inference,
tutoring, model-authored language, model-output evaluation, review mechanics, and
pedagogy in separate provenance-bearing layers.

> **Current implementation authority:**
> [`docs/product/repository-build-status.md`](docs/product/repository-build-status.md)
>  
> **Latest repository handoff:** [`STATUS.md`](STATUS.md)  
> **Contributor orientation:** [`CONTEXT.md`](CONTEXT.md)  
> **Architecture map:**
> [`docs/architecture/architecture.md`](docs/architecture/architecture.md)

**Current qualified boundary:** numbered milestones M1–M34 plus the post-M34 Chess
Knowledge Ontology program K0–K7. The K labels are a separate qualified package
namespace and do not consume provisional M35+ roadmap labels.

Repository description: Persistent AI chess tutor that learns how you think,
diagnoses recurring mistakes, and turns game evidence into personalized training.

## Product thesis

Chess software is already strong at answering whether a move is objectively good
or bad. Chess Mentor Engine is aimed at the harder longitudinal problem:

```text
What is objectively happening on the board?
Which chess concepts describe that evidence, and under what authority?
What did this player actually notice, consider, and expect?
What recurring explanation is currently supported strongly enough to affect teaching?
What should the player practice next?
Did that learning transfer into later play?
```

The repository therefore treats chess evidence, concept semantics, participant
evidence, learner inference, model language, evaluator judgment, and pedagogy as
different authorities. A registered concept is not automatically present in a
position; concept presence is not automatically a learner weakness; and a convincing
model explanation is not promoted into chess truth.

## Current bounded product path

The qualified product path remains:

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound UCI engine analysis
-> objective played-move comparison / bounded diagnostic selection
-> M15 deterministic evaluation presentation
-> M18 diagnostic candidate batch
-> explicit participant candidate selection + separate capture consent
-> M23 cme-candidate-tutor
-> M21 authorization / launch
-> exact M5 PlayerDecisionContext
-> persisted replay-verifiable M8 state=selected
-> M13 tutor capture / freeze / reveal / compare workflow
-> position-local M6 discrepancy + optional bounded M7 context
-> replay-verified persisted M8 state=compared
-> M26 reviewed-coaching operator
   -> M16 deterministic grounded feedback
   -> optional M19 request / M24 provider execution / M19 coaching
   -> optional M20 request / M24 evaluator execution / M20 bounded evaluation
   -> M25 authority-separated coach-review read model
   -> atomic append-only M26 run lineage
-> M27 mechanical reviewed-coaching execution ledger
-> M29 persisted review -> M28 deterministic reference surface
-> M30 participant-scoped review package / navigation / export
-> M32 machine-readable persisted review delivery bundle
-> M33 deterministic M16 mentor-feedback trace
-> optional M31 synthetic-canary/manual-retry preflight
-> optional M34 hermetic multi-attempt recovery reconciliation
-> explicit M9 training applicability / selection
-> M10 outcome / transfer evidence
-> append-only M11 longitudinal learner state
```

The Chess Knowledge Ontology is a cross-cutting semantic layer over that path:

```text
canonical chess subject
-> K0–K3 registered concept definition
-> optional K4 provenance-bound assertion
-> optional K5 deterministic detector for the qualified mechanical subset

exact K4 assertion bundle
   +--> K6 model-consumable ontology sidecar bound to an unchanged M19 request
   +--> K7 learner-knowledge projection + existing M7C recurrence assessment
        -> original M7C relation preserved verbatim
```

Not every application must invoke every optional layer. Every arrow remains an
authority boundary.

## Capability map

| Packages | Qualified capability |
| --- | --- |
| M1–M4 | Canonical games/positions, deterministic chess context/features, normalized engine evidence, played-decision comparison, and explicit diagnostic selection. |
| M5–M7 | Frozen participant evidence, position-local reasoning discrepancy, participant-specific learner hypotheses, recurrence, challenge, and contradiction evidence. |
| M8–M11 | Evidence-aware tutor state, explicit intervention selection, bounded practice/transfer outcome evidence, and append-only longitudinal learner state. |
| M12–M18 | Evidence/artifact CLI, persistent tutor CLI, engine-backed analysis, deterministic presentation/feedback, analysis-presentation bridge, and diagnostic queue. |
| M19–M22 | Provenance-bound model coaching, bounded model-output evaluation, participant-authorized candidate launch, and hermetic cross-layer fidelity qualification. |
| M23–M27 | Diagnostic-to-persistent-tutor operator, provider/evaluator execution conformance, coach-review read model, persistent reviewed coaching, and mechanical execution ledger. |
| M28–M31 | Deterministic local review surface, persisted-review bridge, participant-scoped navigation/export, and hermetic privacy/manual-retry preflight. |
| M32–M34 | Machine-consumer review-delivery fidelity, deterministic mentor-feedback traceability, and hermetic reviewed-coaching recovery reconciliation. |
| K0–K3 | Versioned Chess Knowledge Ontology authority, strict registry/validation, tactical/Lichess crosswalk, position features, principles, evaluation factors, plans, and pedagogy metadata. |
| K4–K5 | Provenance-bound knowledge assertions plus a deliberately conservative deterministic detector subset. |
| K6–K7 | Authority-preserving ontology projection for model consumers and M7C-preserving learner-knowledge projection. |

See the moving
[`repository-build-status.md`](docs/product/repository-build-status.md) for exact PR,
qualification, and current-boundary details.

## Core authority rules

```text
objective chess truth != chess concept definition != participant self-report
concept definition != concept assertion != learner inference
registered concept != automatically detectable concept
ontology concept presence != M7C hypothesis relation
K7 descriptive projection != recurrence reclassification or learner mutation
K6 ontology sidecar != M19 request identity or M16 factual authority
external taxonomy tag != deterministic CME detector result
heuristic principle != engine-evaluation decomposition
strategic plan != best move != M9 training intervention
local discrepancy != recurrence != causal learner trait
supported recurrence != automatic training eligibility
selected intervention != effective intervention
practice completion != successful performance != transfer != mastery
engine analysis != evaluation presentation != deterministic mentor feedback
M16 deterministic grounding != M19 model-authored language
request provenance != semantic correctness of model prose
M20 evaluator acceptance != objective chess truth
participant candidate selection != capture consent
M27 mechanically_verified != semantic truth or pedagogical quality
M30 participant scoping != authentication
M32 consumer fidelity != production UI correctness
M33 deterministic traceability != model or pedagogical truth
M34 resume eligibility != retry authorization or retry execution
```

## Chess Knowledge Ontology

The ontology program is documented under [`docs/chess-knowledge/`](docs/chess-knowledge/)
and consolidated in the
[`K0–K7 runbook`](docs/runbooks/chess-knowledge-ontology-program.md).

Key properties:

- stable dotted concept IDs and deterministic ontology/concept fingerprints;
- strict graph, mapping, alias, schema, and authority validation;
- tactical vocabulary plus a Lichess puzzle-theme crosswalk;
- separate position features, strategic principles, qualitative evaluation factors,
  candidate plans, and pedagogy metadata;
- bounded, provenance-bearing assertions over exact chess subjects;
- deterministic automatic detection only for the explicitly qualified mechanical
  subset;
- an opt-in K6 sidecar that augments model-provider context without changing M19;
- a K7 projection that adds typed chess context to existing M7C recurrence evidence
  without deciding recurrence itself.

K0–K7 introduce no new production CLI command and make no production provider,
frontend, learner-causality, intervention-efficacy, or mastery claim.

## Install

Use Python 3.11 or newer:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
cme --help
```

Stockfish or another UCI engine is an explicitly supplied external executable; no
engine binary is bundled with the package.

## Installed operator commands

The package currently installs:

```text
cme
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

The principal `cme` command exposes:

```text
cme games inspect
cme position packet
cme analyze
cme diagnose
cme artifacts list/show/verify
cme tutor ...
```

M31–M34 and K0–K7 are primarily Python API / hermetic qualification surfaces. They
do not add production CLI commands.

### Inspect deterministic game and position evidence

```bash
cme games inspect games.pgn
cme games inspect games.pgn --full
cme position packet games.pgn --game-index 0 --ply-index 12
```

`position packet` remains engine-free.

### Run bounded engine analysis

```bash
cme analyze games.pgn \
  --game-index 0 \
  --ply-index 12 \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3 \
  --timeout-ms 10000 \
  --with-presentation
```

M14/M17 run the canonical position through the qualified M3/M4 engine evidence
contracts and optionally project the exact in-memory records through M15. Partial,
bounded, mate, terminal, incompatible, and failed states remain explicit rather
than being coerced into fake centipawn precision.

### Build a diagnostic analysis queue

```bash
cme diagnose games.pgn \
  --game-index 0 \
  --start-ply 0 \
  --end-ply 30 \
  --policy ./selection-policy.json \
  --engine /path/to/stockfish \
  --depth 14 \
  --multipv 3
```

The M18 output retains the complete auditable source pool plus the deterministic
candidate/control batch, exclusions, quotas, policy/source fingerprints, and
shortfalls. The repository does not define universal `inaccuracy`, `mistake`, or
`blunder` thresholds.

### Inspect verified local artifacts

```bash
cme artifacts list --db ./mentor.sqlite3 --participant P01
cme artifacts show --db ./mentor.sqlite3 --participant P01 --kind KIND ARTIFACT_ID
cme artifacts verify --db ./mentor.sqlite3 --participant P01
```

Participant scoping is an integrity boundary, not authentication. Protect the local
plaintext database.

### Run persistent tutor checkpoints

```text
cme tutor start
cme tutor status
cme tutor present-position
cme tutor present-stage
cme tutor respond
cme tutor freeze
cme tutor reveal
cme tutor compare
cme tutor attach-hypothesis
cme tutor explain
cme tutor complete
```

Every mutation replay-verifies the exact prior checkpoint, applies one native M8
transition, and writes an append-only successor checkpoint.

### Reviewed-coaching and review surfaces

Use the installed dedicated commands for the post-M23 operator path:

```text
cme-candidate-tutor
cme-coach-review
cme-reviewed-coaching
cme-reviewed-coaching-ledger
cme-coach-review-reference
cme-persisted-coach-review-reference
cme-participant-review
```

The reviewed-coaching commands do not select a production model/evaluator provider
for the application. Network execution occurs only through explicitly supplied
M24-compatible application adapters.

See the runbooks under [`docs/runbooks/`](docs/runbooks/) for exact operator/API
contracts and qualification commands.
