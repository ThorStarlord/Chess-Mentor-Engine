# Strategic Repository Analysis — Chess Mentor Engine

> Exploratory Sensemaking artifact. Not repository authority under the
> documentation governance in `CONTEXT.md`: it records no accepted decision and
> authorizes no work. `strategic analysis != implementation authorization`.

## 1. Governing Intent and Scope

- **Owner request (2026-10-28):** understand the product, how it is built and what
  it could become; build reusable source-grounded knowledge; explore possibilities;
  recommend warranted directions; do not change product implementation.
- **Repository-owned authority:** `CONTEXT.md` (authority graph, governance, current
  post-V1 decision), `STATUS.md`, `docs/product/repository-build-status.md`,
  `docs/product/product-discovery.md`, `docs/product/product-definition.md`,
  ADRs 0001-0012.
- **Governing post-V1 decision:** the next evidence is actual repeated local use;
  identify the dominant demonstrated bottleneck before authorizing one bounded
  next objective; do not auto-build M35/M37/M38/K8/M47, new learner-intelligence
  subsystems, browser UI or hosted product (`CONTEXT.md`, "Current post-V1 decision").
- **Source identity:** `thorstarlord/chess-mentor-engine` @
  `afbdf775356483f08a5ea979b34dbb36cbafb2f3` (branch `claude-skills-v2`; the only
  change over the post-V1 baseline is the `.claude/skills` addition).
- **Authority:** analysis only. No implementation authority was granted.

### 1A. Goal fitness

| | |
| --- | --- |
| Stated objective (repository) | Repository qualification (V1 + post-V1 package) — complete |
| Objective role | milestone / evidence state |
| Governing intent | A player gets an evidence-backed recurring-decision diagnosis from ~10 of their games and a next practice priority, with persistent learner state (`product-discovery.md` §4, §5, §11) |
| Goal fit | **partial** |

Counterexample: every qualification gate passes (observed locally: 974 passed,
8 skipped) while no end user can reach the first-value moment, because the
operable path needs fixture-built inputs (see §2). Milestone satisfied != product
objective satisfied.

## 1B. Strategic Continuity

`NEW`. No prior Sensemaking analysis exists in this repository.

## 2. Current System Model

**What it is.** A local, stdlib-only Python package (≈44k source lines, ≈28k test
lines, 9 console entry points) that treats chess tutoring as a chain of
authority-separated, content-addressed evidence layers:

```text
PGN -> canonical positions (private rules core) -> UCI engine evidence
-> diagnostic selection (M4/M18) -> participant baseline capture under an
exposure lifecycle (M5/M8) -> position-local discrepancy (M6)
-> learner hypotheses + recurrence (M7/M7C) -> intervention selection (M9)
-> outcome/transfer evidence (M10) -> longitudinal state (M11)
-> read/explain/propose layers (M36-M46) -> local composition (cme-local-tutor)
-> descriptive product-use observation (post-V1)
```

plus a parallel deterministic feedback / optional model-prose / evaluator /
review-ledger chain (M15-M34) and a 41-concept chess ontology (K0-K7).

**What makes it distinctive.** The epistemic discipline is the product's real
asset: "objective truth != self-report != inference", freeze-before-reveal,
proposal != execution, explicit claim ceilings, fail-closed tamper checks. Few
chess tools model *why this player* rather than *what the best move is*.

**How it was built.** 332 commits concentrated in 2026-09-10..15, milestone by
milestone, each with ADR/runbook/qualification ceremony. Breadth of contracts
grew much faster than user-facing operability.

**Where reality is.**

1. *Operability.* `cme-local-tutor start|next` require an M44
   `LearnerProgressView` JSON, a capture-protocol JSON and prompts JSON
   (`src/chess_mentor_engine/local_tutor_cli.py:281-323`,
   `local_tutor_entry.py`); `cme diagnose` requires a `SelectionPolicy` JSON and
   handles one game (`diagnostic_cli.py:386-402`). No installed command produces
   the M44 view, protocol or prompts; the CLI tests build them from other tests'
   fixtures (`tests/test_v1_local_tutor_workflow.py:181-199`).
   A cold-start route for *baseline capture* does exist: `cme-candidate-tutor`
   starts an M8 session from an M18 queue and candidate id with no M44 view, and
   `cme-local-tutor review` needs only the session and a position packet. It still
   needs hand-authored policy, protocol and prompts JSON.
1b. *Cold-start wall.* An M44 view cannot be built for a learner with no active
   M7 hypothesis: `build_next_session_plan` raises "M40 requires at least one
   active learner hypothesis" (`learner_intelligence/next_session.py:543`), and
   `build_learner_progress_view` requires a `NextSessionPlan`. So M40-M46 (and
   therefore `cme-local-tutor start|next`) are unreachable until an M7
   hypothesis exists, and no installed command creates one from captured
   sessions (M7 enters M8 only via `cme tutor attach-hypothesis --bundle-json`).
2. *Persistence.* The store persists analysis, diagnostic queues, authorizations,
   tutor sessions, prompts, observations and review ledgers. No store writer exists
   for M6/M7/M9/M10/M11/M36-M44 artifacts; M11 is "a Python API, not an end-user
   command" (`docs/runbooks/m11-longitudinal-learner-state.md:5`). The persistent
   learner loop is a library capability, not an operable product loop.
3. *Language.* M19 `ModelCoachProvider` is a protocol with no shipped provider
   (`coaching/model.py:95-99`).
4. *External evidence.* One participant, two Mixed pilots; Pilot 003 blocked;
   Pilot 004 Batch 1 frozen and awaiting P01 responses; the 6-8 participant study
   not run (`docs/research/first-product-validation/...`).

## 3. Capability and Limitation Map

| Capability | State | Evidence | Strategic relevance |
| --- | --- | --- | --- |
| `objective-chess-evidence` | ESTABLISHED | `chess/`, `analysis/uci.py`, Stockfish CI job | Foundation; ADR 0001/0002 |
| `authority-separated-contracts` | ESTABLISHED | `CONTEXT.md`, 974 tests | Core differentiator and main maintenance cost |
| `single-game-diagnosis` | PARTIAL | `diagnostic_cli.py:386-402` | First-value needs ~10 games |
| `guided-baseline-review` | ESTABLISHED | `local_tutor_review_cli.py` | Usable once a session exists |
| `cold-start-local-setup` | PARTIAL | baseline route via `cme-candidate-tutor` + `review`; policy/protocol/prompts JSON hand-authored; `local_tutor_cli.py:281-323` | Blocks the governed next evidence |
| `session-to-hypothesis-bridge` | MISSING | `next_session.py:543`; no store writer or command for M6/M7 | Gates every M40-M46 surface for a real learner |
| `persistent-learner-loop` | PARTIAL | library: `learner_intelligence/`, `longitudinal/`; no store writer | Core product thesis not operable |
| `learner-model-library` | ESTABLISHED | `learner_intelligence/progress_model.py:659` | Large unexploited leverage |
| `model-rendered-language` | MISSING | `coaching/model.py:95` | Deferred; not needed for first evidence |
| `visual-board-surface` | DEFERRED | `CONTEXT.md` non-goal; Pilot 001 result | Pulled only by evidence |
| `real-user-usefulness` | CLAIMED_UNVERIFIED (explicitly not claimed) | `STATUS.md`, pilot results | The thesis-level unknown |
| `hosted-product` | OUT_OF_SCOPE | `STATUS.md` | External authority |

## 4. Strategic Frontier

**Possibility coverage.** Considered: all eight layers in the authority graph;
user outcomes from `product-discovery.md` (first value, persistence, transfer);
the research program; composition opportunities (learner library × store × local
CLI; ontology × Lichess puzzle themes; review surfaces × coach use);
counterfactual identities (coach tool, research instrument, stop/thesis review);
engineering alternatives (python-chess, consolidating 9 entry points).
Not examined in depth: internals of M7C recurrence math, M45/M46 policy quality,
ontology detector precision, the M25-M34 review chain, chess-rules correctness.
None of these could plausibly overturn the frontier: they are downstream of a
loop no user can yet run.

- **FRONTIER-1 — Operability gap.** The owner-selected evidence source (repeated
  local use) cannot start for a new learner without hand-built structural JSON.
  Consequence: the evidence loop the governance depends on produces no evidence;
  the "dominant bottleneck" is unobservable because use never begins.
- **FRONTIER-2 — Open persistent loop / cold-start wall.** Sessions do not feed
  M6/M7/M11 state in the store, and M40/M44 refuse a learner with no active
  hypothesis, so the "persistent tutor" thesis (`goal:persistent-learner-model`)
  cannot be experienced even by the owner. Consequence: the largest body of code
  (learner intelligence) has no runtime consumer path for a real learner.
- **FRONTIER-3 — Thesis evidence.** Usefulness rests on one participant and
  mixed results; P01's main negative finding was missing board context.
  Consequence: further architecture risks optimizing an unvalidated thesis.

## 5. Candidate Construction Paths

### PATH-1 — Operable local loop on existing authority

- **Future state:** a learner runs one setup command over their PGN(s) and engine
  path, gets a first guided review with shipped defaults and a cold-start learner
  view; later, completed sessions update persisted learner state and the next
  review is ranked from it.
- **Why plausible:** every builder already exists and is qualified
  (`build_learner_progress_view`, default mentor-queue/adaptive policies, M5
  protocol types); the work is composition and persistence, not new inference.
  It is exactly the "setup" bottleneck class `CONTEXT.md` anticipated, and the
  README's own example note reads "setup still feels technical".
- **Frontier grounding:** FRONTIER-1, FRONTIER-2.
- **Builds on:** `guided-baseline-review`, `learner-model-library`,
  `objective-chess-evidence`. **Requires:** `cold-start-local-setup`,
  `persistent-learner-loop`.
- **Path transitions:** `PATH-1/T1` operable baseline capture (shipped default
  policy/protocol/prompts, documented `cme diagnose` -> `cme-candidate-tutor` ->
  `review` -> `feedback`/`report` route, optionally multi-game diagnose);
  `PATH-1/T2` session-to-hypothesis bridge: persist M6 discrepancies from compared
  sessions and an owner-sanctioned way to create/revise M7 hypotheses, then
  persist M11 and re-derive M36->M44 from the store; `PATH-1/T3` repeated use and
  observation reports through `start|next`.
- **Dependencies:** an explicit owner decision on who may create M7 hypotheses
  from session evidence (automatic M7C vs operator-confirmed) before T2.
- **Unlocks:** real local-use evidence; a demonstrable persistent tutor; a
  platform for PATH-3 or a UI later.
- **Risks:** default policy/prompts become de facto pedagogy; T2 touches M7
  authority; ceremony cost per package.
- **Reversibility:** high for T1 (additive command, defaults are data); medium for
  T2 (new persisted kinds).
- **Evidence gaps:** whether the owner already has a private harness; whether
  the T1 route works end-to-end with a real engine (not run here: no Stockfish).
- **Assumptions:** ASSUMPTION-1, ASSUMPTION-2.
- **Reassessment triggers:** owner shows a private operator harness; T1 route
  fails end-to-end with a real engine.

### PATH-2 — Evidence first, repository frozen

- **Future state:** no new code until Pilot 004 Batch 1 (already frozen) and a
  multi-participant replication return; the next package is chosen from them.
- **Why plausible:** governance explicitly prefers evidence; the B01 package is
  ready and costs only participant time.
- **Frontier grounding:** FRONTIER-3. **Builds on:** research protocol docs.
- **Risks:** manual packets do not exercise the product, so they cannot reveal
  product bottlenecks; recruitment of unexposed participants is already blocking
  Pilot 003.
- **Reversibility:** total. **Reassessment trigger:** new participants available.

### PATH-3 — Model-rendered, coach-mediated experience

- **Future state:** a concrete M19 provider renders grounded explanations and
  Socratic prompts, optionally for a human coach preparing student packets.
- **Why plausible:** the language-only authority rule and evaluator seam already
  exist; Pilot results show explanation/context quality drives perceived value.
- **Frontier grounding:** FRONTIER-3 (indirectly). **Requires:**
  `model-rendered-language`, owner decision on segment and on network/secrets.
- **Risks:** adds runtime dependency and external authority before the loop is
  operable; contradicts the current post-V1 non-goal posture.
- **Reversibility:** medium. **Reassessment trigger:** local use shows language,
  not setup or diagnosis, is the bottleneck.

## 6. Qualitative Path Comparison

- **PATH-1** — highest mission relevance and blocking power (it is the
  precondition for the owner's own chosen evidence); evidence is sufficient
  (repository-observable); error is cheap and reversible at T1; deferral cost is
  high because every week without an operable loop yields no product evidence.
  Authority: needs owner go-ahead for implementation.
- **PATH-2** — necessary but not sufficient: it tests the thesis with manual
  packets, not the product, and it is recruitment-blocked. It runs in parallel at
  near-zero repository cost and does not compete with PATH-1/T1.
- **PATH-3** — attractive but premature: optimizes presentation of a loop no
  one can run; higher consequence of error; contradicts current governance.

Risk of commission for PATH-1/T1 is small (an additive command with data
defaults). Risk of omission is that the repository keeps qualifying layers while
the product never meets a user.

## 7. Decision-Changing Uncertainty

- **Statement:** whether the owner already operates the loop via a private
  script/harness (which would make setup a non-bottleneck), and whether the owner
  intends the next participant evidence to come from the CLI or from manual
  research packets.
- **Could change:** PATH-1 vs PATH-2 priority.
- **Inquiry warranted:** yes, one owner question; no experiment needed.
- **Source:** owner_intent.

## 7A. Decision Assumptions

- **ASSUMPTION-1:** setup/operability is the dominant bottleneck to repeated
  local use. Evidence: `local_tutor_cli.py:281-323`,
  `tests/test_v1_local_tutor_workflow.py:181-199`. Trigger: owner demonstrates an
  existing harness or a completed observation report from real use.
- **ASSUMPTION-2 (CONTRADICTED in this session):** a cold-start learner view
  (no hypotheses) can be represented by existing M36/M40/M44 contracts. Probe:
  `learner_intelligence/next_session.py:543` rejects it. Consequence: T1 uses the
  M44-free `cme-candidate-tutor` route; the learner loop needs T2.
- **ASSUMPTION-3:** `cme-candidate-tutor` -> `cme-local-tutor review` is a
  complete cold-start baseline route given default JSON inputs. Evidence:
  `candidate_tutor_cli.py` help, `local_tutor_review_cli.py:147-158`. Trigger:
  an end-to-end run with a real engine fails.

## 8. Strategic Synthesis

The repository's contract depth is far ahead of its operable surface. The owner's
own governance says the next step is evidence from repeated local use, yet that
use cannot begin without hand-built inputs, and even when begun it hits a
cold-start wall: no command turns captured sessions into the M7 hypothesis that
every M40-M46 surface (including `cme-local-tutor start|next`) requires. The warranted move is therefore not another inference
layer, a UI, or an LLM, but the smallest composition that lets a real learner run
the already-qualified loop on their own games. Running the frozen Pilot 004 Batch
1 in parallel is free and should not wait on code.

## 9. Warranted Direction

**`BUILD`** — selected path `PATH-1`, transition `PATH-1/T1`, conditional on owner
implementation authority and the §7 owner question.

- **Candidate responsibility:** make baseline capture operable for a new learner:
  ship default selection policy, capture protocol and prompts as package data and
  a documented/tested route `cme diagnose` -> `cme-candidate-tutor` ->
  `cme-local-tutor review` -> `feedback`/`report` that needs only a PGN and an
  engine path.
- **Smallest warranted intervention:** an end-to-end test (Stockfish-gated, like
  the existing integration job) that runs that route from shipped defaults; then
  the defaults themselves. T2 (session-to-hypothesis bridge) waits for the owner's
  M7-creation decision.
- **Parallel, non-repository:** collect P01's Pilot 004 Batch 1 responses.

## 10. Authority and Claim Boundaries

- No implementation, merge, release or tracker authority is established here.
- `BUILD` nominates a responsibility; the owner decides.
- Claim ceiling: repository-inspection evidence plus one local test run. Nothing
  here establishes real-user usefulness, tutoring efficacy or the correctness of
  internal M7C/M45/M46 policies (not assessed).

## 11. Evidence

- `CONTEXT.md` — "Current post-V1 decision"; "Documentation governance".
- `STATUS.md` — integration provenance, restart instruction.
- `docs/product/product-discovery.md` — §4 first value, §11 boundary, §13 falsifiable hypothesis.
- `src/chess_mentor_engine/local_tutor_cli.py:281-323` — required structural inputs.
- `src/chess_mentor_engine/diagnostic_cli.py:386-402` — single game, policy JSON.
- `tests/test_v1_local_tutor_workflow.py:181-199` — inputs built from test fixtures.
- `src/chess_mentor_engine/storage/store.py:161-164` — single artifact table.
- `docs/runbooks/m11-longitudinal-learner-state.md:5` — M11 is a Python API.
- `src/chess_mentor_engine/coaching/model.py:95-99` — provider protocol only.
- `docs/research/first-product-validation/pilots/FPV-PILOT-001/result.md`, `FPV-PILOT-002/result.md`, `FPV-PILOT-004/batches/B01/README.md`.

## 12. Machine-Readable Summary

```yaml
schema_version: 2
artifact_id: strategic_repository_analysis
analysis_ref: "SRA-2026-10-28-cme-bootstrap"
continuity:
  prior_analysis_ref: null
  disposition: NEW
  prior_selected_path_id: null
  reason: "No prior analysis is being continued."
target_repository: thorstarlord/chess-mentor-engine
target_source_identity: "afbdf775356483f08a5ea979b34dbb36cbafb2f3"
governing_intent: "Evidence-backed recurring-decision diagnosis and next practice priority with persistent learner state; post-V1 next evidence must come from repeated local use."
governing_authority_refs:
  - CONTEXT.md
  - STATUS.md
  - docs/product/product-discovery.md
  - docs/product/repository-build-status.md
capability_states:
  - capability_id: objective-chess-evidence
    state: ESTABLISHED
    evidence_refs: [src/chess_mentor_engine/analysis/uci.py, .github/workflows/ci.yml]
  - capability_id: guided-baseline-review
    state: ESTABLISHED
    evidence_refs: [src/chess_mentor_engine/local_tutor_review_cli.py]
  - capability_id: learner-model-library
    state: ESTABLISHED
    evidence_refs: [src/chess_mentor_engine/learner_intelligence/progress_model.py]
  - capability_id: single-game-diagnosis
    state: PARTIAL
    evidence_refs: [src/chess_mentor_engine/diagnostic_cli.py]
  - capability_id: cold-start-local-setup
    state: PARTIAL
    evidence_refs: [src/chess_mentor_engine/local_tutor_cli.py, src/chess_mentor_engine/candidate_tutor_cli.py, tests/test_v1_local_tutor_workflow.py]
  - capability_id: session-to-hypothesis-bridge
    state: MISSING
    evidence_refs: [src/chess_mentor_engine/learner_intelligence/next_session.py, src/chess_mentor_engine/tutor_cli.py]
  - capability_id: persistent-learner-loop
    state: PARTIAL
    evidence_refs: [src/chess_mentor_engine/storage/store.py, docs/runbooks/m11-longitudinal-learner-state.md]
  - capability_id: model-rendered-language
    state: MISSING
    evidence_refs: [src/chess_mentor_engine/coaching/model.py]
  - capability_id: visual-board-surface
    state: DEFERRED
    evidence_refs: [CONTEXT.md]
  - capability_id: real-user-usefulness
    state: CLAIMED_UNVERIFIED
    evidence_refs: [STATUS.md, docs/research/first-product-validation/pilots/FPV-PILOT-002/result.md]
strategic_frontier:
  - frontier_id: FRONTIER-1
    statement: "The governed next evidence (repeated local use) cannot start for a new learner without fixture-built structural JSON."
    evidence_refs: [src/chess_mentor_engine/local_tutor_cli.py, tests/test_v1_local_tutor_workflow.py]
    affected_capability_ids: [cold-start-local-setup, guided-baseline-review]
    strategic_consequence: "Without it the owner's chosen evidence loop yields no evidence and no bottleneck can be demonstrated."
  - frontier_id: FRONTIER-2
    statement: "Sessions do not feed persisted learner state; the persistent tutor thesis is library-only."
    evidence_refs: [src/chess_mentor_engine/storage/store.py, docs/runbooks/m11-longitudinal-learner-state.md]
    affected_capability_ids: [persistent-learner-loop, learner-model-library, session-to-hypothesis-bridge]
    strategic_consequence: "Determines whether the largest code body ever reaches a user."
  - frontier_id: FRONTIER-3
    statement: "Thesis usefulness rests on one participant with mixed results."
    evidence_refs: [docs/research/first-product-validation/pilots/FPV-PILOT-001/result.md, docs/research/first-product-validation/pilots/FPV-PILOT-002/result.md]
    affected_capability_ids: [real-user-usefulness]
    strategic_consequence: "Could reopen the product thesis itself."
construction_paths:
  - path_id: PATH-1
    name: "Operable local loop on existing authority"
    future_state: "A learner runs setup on their PGN(s) and engine, reviews with shipped defaults, and later sessions update persisted learner state."
    frontier_refs: [FRONTIER-1, FRONTIER-2]
    why_plausible: "All builders exist and are qualified; the gap is composition and persistence, the setup bottleneck class governance anticipated."
    builds_on_capability_ids: [guided-baseline-review, learner-model-library, objective-chess-evidence]
    required_capability_ids: [cold-start-local-setup, session-to-hypothesis-bridge, persistent-learner-loop]
    construction_sequence:
      - "Ship default policy/protocol/prompts; test diagnose -> candidate-tutor -> review route end-to-end"
      - "Owner decides M7 creation authority; persist M6/M7/M11 and re-derive M36-M44 from the store"
      - "Repeated use through start/next with observation reports"
    path_transitions:
      - transition_ref: PATH-1/T1
        transition: "cold-start-local-setup PARTIAL -> ESTABLISHED"
      - transition_ref: PATH-1/T2a
        transition: "session-to-hypothesis-bridge MISSING -> ESTABLISHED"
      - transition_ref: PATH-1/T2
        transition: "persistent-learner-loop PARTIAL -> ESTABLISHED"
      - transition_ref: PATH-1/T3
        transition: "real local-use observation reports exist"
    possibility_refs: [poss:operable-cold-start-loop, poss:closed-persistent-learner-loop]
    dependencies: ["Owner decision on who may create M7 hypotheses from session evidence (before T2)"]
    unlocks: ["Real local-use evidence", "Demonstrable persistent tutor", "Grounded later UI/LLM decisions"]
    risks: ["Defaults become de facto pedagogy", "T2 touches M7 authority"]
    reversibility: "High for T1 (additive, data defaults); medium for T2 (new persisted kinds)."
    evidence_gaps: ["Whether the owner has a private harness", "End-to-end route not run with a real engine in this session"]
    assumptions: [ASSUMPTION-1, ASSUMPTION-3]
    reassessment_triggers: ["Owner shows an existing operator harness", "End-to-end route fails with a real engine"]
  - path_id: PATH-2
    name: "Evidence first, repository frozen"
    future_state: "No code until Pilot 004 B01 and a multi-participant replication return."
    frontier_refs: [FRONTIER-3]
    why_plausible: "Governance prefers evidence; B01 is frozen and ready."
    builds_on_capability_ids: [objective-chess-evidence]
    required_capability_ids: [real-user-usefulness]
    construction_sequence: ["Collect P01 B01 responses", "Recruit unexposed participants", "Run frozen protocol"]
    dependencies: ["Participant availability"]
    unlocks: ["Thesis-level evidence"]
    risks: ["Manual packets do not exercise the product", "Recruitment already blocking Pilot 003"]
    reversibility: "Total."
    evidence_gaps: ["Participant pool"]
    assumptions: []
    reassessment_triggers: ["New unexposed participants become available"]
  - path_id: PATH-3
    name: "Model-rendered, coach-mediated experience"
    future_state: "A concrete M19 provider renders grounded explanations/Socratic prompts, optionally for coaches."
    frontier_refs: [FRONTIER-3]
    why_plausible: "Language-only authority rule and evaluator seam exist; pilots show explanation quality drives value."
    builds_on_capability_ids: [learner-model-library]
    required_capability_ids: [model-rendered-language]
    construction_sequence: ["Owner decides segment and network/secrets posture", "Implement provider under M20/M24 conformance"]
    possibility_refs: [poss:model-rendered-socratic-tutor, poss:coach-mediated-product]
    dependencies: ["Owner decision", "Operable loop"]
    unlocks: ["Richer tutoring language"]
    risks: ["Premature before loop is operable", "Contradicts current post-V1 non-goals"]
    reversibility: "Medium."
    evidence_gaps: ["Whether language is a bottleneck at all"]
    assumptions: []
    reassessment_triggers: ["Local use shows language is the dominant bottleneck"]
path_comparison:
  - path_id: PATH-1
    lenses:
      mission_relevance: "Highest: precondition for the owner's chosen evidence."
      decision_value: "High: makes the bottleneck observable."
      blocking_power: "Blocks FRONTIER-1 and FRONTIER-2."
      evidence_sufficiency: "Repository-observable."
      consequence_of_error: "Low at T1."
      deferral_cost: "High: no product evidence accrues meanwhile."
      reversibility: "High at T1."
      authority_availability: "Needs owner implementation authority."
      dependency: "T2 needs an M7 authority decision."
  - path_id: PATH-2
    lenses:
      mission_relevance: "High for the thesis, low for product bottlenecks."
      decision_value: "High if participants exist."
      blocking_power: "Does not unblock FRONTIER-1/2."
      evidence_sufficiency: "Recruitment-limited."
      consequence_of_error: "Low."
      deferral_cost: "Moderate."
      reversibility: "Total."
      authority_availability: "Owner/participants."
      dependency: "Participant availability."
  - path_id: PATH-3
    lenses:
      mission_relevance: "Medium."
      decision_value: "Low until loop operable."
      blocking_power: "None currently."
      evidence_sufficiency: "Weak."
      consequence_of_error: "Medium."
      deferral_cost: "Low."
      reversibility: "Medium."
      authority_availability: "Owner decision plus external secrets."
      dependency: "PATH-1."
decision_changing_uncertainty:
  statement: "Whether the owner already runs the loop through a private harness, and whether next participant evidence should come from the CLI or manual packets."
  could_change: "PATH-1 vs PATH-2 priority"
  inquiry_warranted: true
  evidence_needed: "One owner answer."
  source: owner_intent
decision_assumptions:
  - assumption_id: ASSUMPTION-1
    statement: "Setup/operability is the dominant bottleneck to repeated local use."
    evidence_refs: [src/chess_mentor_engine/local_tutor_cli.py, tests/test_v1_local_tutor_workflow.py]
    reassessment_triggers: ["Owner demonstrates an existing harness or a real observation report"]
  - assumption_id: ASSUMPTION-2
    statement: "CONTRADICTED: a zero-hypothesis learner view is not representable (M40 rejects it)."
    evidence_refs: [src/chess_mentor_engine/learner_intelligence/next_session.py]
    reassessment_triggers: ["M40 contract changes to admit a cold-start action"]
  - assumption_id: ASSUMPTION-3
    statement: "candidate-tutor -> review is a complete cold-start baseline route given default inputs."
    evidence_refs: [src/chess_mentor_engine/candidate_tutor_cli.py, src/chess_mentor_engine/local_tutor_review_cli.py]
    reassessment_triggers: ["End-to-end run with a real engine fails"]
strategic_disposition: BUILD
selected_path_id: PATH-1
candidate_repository_responsibility: "Operable cold-start baseline capture: shipped default policy/protocol/prompts and a tested diagnose -> candidate-tutor -> review -> feedback/report route from a PGN and engine path."
candidate_path_transition_ref: PATH-1/T1
smallest_warranted_intervention: "A Stockfish-gated end-to-end test of that route from shipped defaults, then the defaults."
implementation_authority_established_by_artifact: false
semantic_truth_established: false
created_at: "2026-10-28T23:59:00Z"
immutable: true
```
