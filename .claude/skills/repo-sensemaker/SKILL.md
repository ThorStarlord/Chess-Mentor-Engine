---
name: repo-sensemaker
description: analyze a repository diagnostically to produce a repository sensemaking brief. use when the user asks what a repo is for, what is missing or contradictory, what the weakest consequential boundary is, or what evidence should shape a bounded next step. for high-level questions about multiple coherent repository evolution or construction paths, use strategic-repository-analysis instead.
---

# repo-sensemaker

Analyzes a repository and produces a **Repository Sensemaking Brief**. This skill is diagnostic, focusing on understanding the user intent, codebase structure, and fragility to find the "weakest boundary."

## Diagnostic boundary vs. strategic repository analysis

This Skill answers primarily:

```text
What is this repository?
What is strong / weak / missing / contradictory?
What is the weakest consequential boundary?
What evidence supports that diagnosis?
```

When the user's real question is instead:

```text
What could this repository become?
What coherent ways could it be constructed from here?
How do those repository-evolution paths differ?
Which strategic direction / inquiry is warranted?
```

the first-class Level-3 capability is
`../strategic-repository-analysis/SKILL.md`.

A current Repository Sensemaking Brief can supply diagnostic evidence to that
analysis, but do not force a new Brief when the strategic analyst can establish
current repository state directly from the authorized evidence surface.

```text
diagnosis != strategic evolution synthesis
candidate next step != construction path
weakest boundary != automatically selected strategic direction
```

## Ground the repository without documentation theater

Start with the question that could change the **next useful product or
engineering decision**. Read the target's current intent, non-goals,
domain invariants, relevant code, tests, and owner decisions. An existing
`.sensemaking/` pack is a convenient index, **not** a replacement for its
cited sources and not an additional permission layer.

When the responsibility is to build, recall or correct a persistent
repository ontology/architecture model, use
`../repository-semantic-steward/SKILL.md`. The diagnostic Brief may provide
evidence but is not a durable architecture memory. Do not require a complete
semantic model for routine diagnostics.

If the existing sources already answer the question, **act or diagnose**
without rewriting them. Do not make creation of a complete pack a prerequisite
for proposing a local repair or executing an authorized responsibility.

When a genuinely missing or stale **non-derivable** fact would otherwise
cause repeated misinterpretation, wrong construction, or owner escalation,
create or refresh only the affected entries in `templates/grounding-pack/`'s
format:

1. Reuse `CONTEXT.md`, `CLAUDE.md`, `AGENTS.md`, ADRs, and product
   decisions by linking rather than copying; keep the existing word budgets.
2. Ground non-obvious terms, invariants, and traps in **current** code,
   tests, authority documents, or actual observations. Every factual line
   needs exactly one primary tag: `[policy: path]`, `[code: path]`,
   `[test: path]`, `[owner: date]`, `[delegated: date]`, or
   `[hypothesis]`. Check what the cited source **says**, not just its path.
3. Keep inferred intent as `[hypothesis]` and explicit open questions.
   Never fabricate owner approval. An unsupported hypothesis cannot alone
   justify an irreversible product decision.
4. Preserve the reasoning behind meaningful past choices; avoid class
   catalogs, module maps, restated function signatures, and empty templates.
5. When implementation invalidates a pack line, update the affected line in
   the **same change**. Record only information worth retrieving later.
   Report unresolved gaps without blocking unrelated authorized work.

The value is **better grounded decisions and useful code**, not pack volume,
schema compliance, or a perfect representation before action.

## Two responsibilities, one skill

This skill has two responsibilities. They stay conceptually separate (see [docs/candidate/architecture-decision.md](../../docs/candidate/architecture-decision.md), Decision 1) but live in one file, not two, because one of them is structurally incapable of running outside conversation:

- **Diagnose** (below, through "Runtime-owned artifact skeleton") — produces the brief. Runs identically whether invoked by a human or by `workflow-runtime.py`'s automated per-step execution. This is the whole of what this skill did before this section existed.
- **Interact** (final section of this file) — reads the brief and decides whether to ask one clarifying question before recommending. **Only runs in direct conversational invocation.** The automated runtime path has no chat channel mid-run — its deliverable is the artifact, full stop — so this responsibility cannot execute there even in principle. Giving it a separate, independently-routable Skill file would misrepresent when it can run at all; keeping it as a clearly-labeled section of the same file keeps that constraint visible where an implementer will actually see it.

If you are invoked through `workflow-runtime.py` (see "Execution Protocol" below), stop after producing and recording the artifact — the Interact section does not apply to you this run.

## Stage 1: Intent-Aware Analysis (New)

When analyzing a repository, **always compare** what the user intends with what the codebase signals:

1. **Extract User Intent**: From the user's problem statement or prior context, identify what fog type they *implied*:
   - Implied product_fog? ("We need better user onboarding")
   - Implied ui_fog? ("Dashboard UX redesign")
   - Implied docs_fog? ("API docs are confusing")
   - Implied architecture_fog? ("System is slow")

2. **Diagnose Codebase**: Analyze the code structure to determine what fog type the *actual problems* require:
   - **product_fog signals**: Feature flags, user data, analytics tracking, roadmap docs, unclear user needs
   - **ui_fog signals**: See [UI Fog Signals Registry](references/ui-fog-signals.md) for checkable indicators:
     - Missing user flow documentation or interaction specs
     - Frontend components scattered without clear boundaries
     - Routing logic complex and undocumented
     - Design system fragmented or absent
     - Low test coverage for UI interactions
   - **docs_fog signals**: README, ADR files, architecture docs, runbooks missing or outdated
   - **architecture_fog signals**: Module boundaries unclear, circular dependencies, performance issues, coupling, state management scattered

3. **Detect Conflicts**: If user intent (implied fog) ≠ codebase diagnosis (actual fog), flag it:
   - Example: User wants "UI redesign" but code shows "state management is broken" → conflict
   - This is when escalation to full-fog is recommended

4. **Emit Stage 1 Fields** (decision-support metadata for the Brief handoff —
   `primary_fog_type` is required and the remaining fields below are recommended
   machine fields per `artifact-contracts.yaml`; none grants automatic-routing
   authority):
   - `source_intent_ref`: Reference to 00-user-intent.md
   - `user_implied_fog_type`: What the user's problem statement suggests — one of
     the four fog types, or `unknown` when the intent is fog-neutral (implies no
     particular fog type). `unknown` is legal for this field only.
   - `primary_fog_type`: What the codebase actually signals (always one of the
     four fog types; never `unknown`)
   - `diagnosis_conflict`: Boolean (user_implied != primary?)
   - `escalation_recommended`: Boolean (true if high uncertainty or conflict)

## UI Fog Classification Guide (NEW)

When evaluating whether a repository has **UI Fog**, follow the [UI Fog Signals Registry](references/ui-fog-signals.md):

1. **Check for frontend code**: Does the codebase contain React/Vue/Angular/HTML/CSS?
   - If no → Not ui_fog; evaluate other fog types
   - If yes → Continue to step 2

2. **Evaluate Tier 1 signals** (high-confidence UI fog indicators):
   - Missing UI flow documentation?
   - Frontend components scattered without clear boundaries?
   - Routing logic complex and undocumented?
   - Design system fragmented or absent?
   - Count how many Tier 1 signals are present (0-4)

3. **Evaluate Tier 2 signals** (moderate confidence):
   - Low test coverage for UI interactions?
   - Accessibility not addressed?
   - Responsive design undocumented?
   - Screen count vs. documentation mismatch?

4. **Make the call**:
   - 2+ Tier 1 signals → STRONG CONFIDENCE: Classify as `ui_fog`
   - 1 Tier 1 + 2+ Tier 2 signals → MEDIUM CONFIDENCE: Classify as `ui_fog`
   - Only Tier 3 signals or missing frontend → NOT ui_fog; evaluate architecture_fog or product_fog

5. **Break ties with user intent**: If diagnosis is uncertain and user's problem statement mentions screens, flows, navigation, or design → use intent as tiebreaker to classify as `ui_fog`.

**Important**: Avoid vibe-based diagnosis. Every ui_fog classification must cite specific signals from the UI Fog Signals Registry.

---

## Standard Workflow
1. **Analyze**: Inspect README, core files, folder structure, and existing documentation.
2. **Signal Detection**: Identify what is working well (Strong Signals).
3. **Gap Analysis**: Identify what is absent or incomplete (Missing Pieces).
4. **Evidence Gathering**: Cite specific file paths and code snippets to back up signals and gaps. Each evidence excerpt's `lines` field is a single line or range — `Lx`/`Lx-Ly` or bare numbers both work (e.g. `L18` or `18`). Include a **Logic trace** (begin the paragraph with the literal words "Logic trace:") that walks from the cited evidence to the weakest-boundary conclusion. **State-currency verification:** documented state is not automatically verified current state — before treating any tracker, roadmap, TODO, review, milestone, or branch-status claim as current, verify it with the cheapest repository probe (current branches, commits, working-tree state, tests, runtime artifacts, recent reviews), or clearly identify the claim as documented but not independently verified. Never convert "documented X" into "X is currently true" without verification, and do not treat unfinished documentation as proof that work remains unfinished.
5. **Boundary Stress Test**: Find the "Weakest Boundary" (e.g., mismatch between README and code, unsafe workflows, missing validation) and **classify it with one of the recognized [Weakness Types](references/weakness-types.md)** — `Vocabulary Drift`, `Contract Mismatch`, `Ghost Features`, `Safety Gaps`, `Implicit Dependencies`, `Zero Validation`, or `Orphaned Examples` — stated explicitly as `**Weakness type:** <type>` in Section 6's prose, AND recorded in the structured `weakness_type` field in Section 13's machine-readable YAML (the two must agree). If none of the 7 types fit, use `Other` and give a non-empty `weakness_type_explanation` in Section 13 — an unrecognized value or a missing explanation for `Other` is a non-blocking validator warning, not a rejection, but it must be resolved before a human grants final approval.
6. **Intent Comparison** (Stage 1): Compare user intent with diagnosis. Detect conflicts. Recommend escalation if needed.
7. **Problem Classification**: Classify the primary fog type based on the weakest boundary.
   Use [UI Fog Signals Registry](references/ui-fog-signals.md) to evaluate `ui_fog` signals systematically:
   - **product_fog**: Unclear user needs, missing feature specs, undocumented workflows → needs discovery/research
   - **ui_fog**: Screen/flow design problems (use UI Fog Signals Registry for checkable indicators):
     - Missing or unclear user flows/screen specs
     - Components scattered without reusability boundaries
     - Routing logic complex and undocumented
     - Design system inconsistent or absent
     - → needs UI diagnostic workflow: ui-brief → ui-flow → ui-screen-spec
   - **docs_fog**: Missing documentation, unclear specifications, knowledge silos → needs documentation architecture
   - **architecture_fog**: Code structure problems, unclear boundaries, module coupling, state management scattered → needs spec-driven refactoring (default)
8. **Synthesis**: Produce a Repository Sensemaking Brief with fog type classification, intent alignment, candidate next steps, and recommended workflows. Keep observed evidence, documented claims, inference, and owner-supplied judgment/context distinguishable in the synthesis. Decision-changing current-state claims must explicitly distinguish verified current state from merely documented state: cite the probe used when verified, and clearly identify unverified documented claims as documented but not independently verified. If you have grounds for it, optionally fill in Section 15 (Extended analysis) — see [Repo Analysis Template](references/repo-analysis-template.md#15-extended-analysis). It is optional and non-blocking (ADR 0024); leave it out entirely if you have nothing to add.

## State-currency probe (mandatory before synthesis)

A state-currency probe is mandatory before writing Sections 3–9. The probe backend is selected by the **authorized target-access surface**; do not widen that surface merely to satisfy a preferred probe implementation.

### Backend selection

- **Local checkout authorized:** use the local Probe Engine described below.
- **Read-only GitHub connector + exact target SHA authorized:** use `github_connector_exact_sha_v1` as defined in [Connector-native exact-SHA probe](references/connector-native-probe.md).

**No third implicit probe path exists.** Do not skip state-currency verification because the local backend is unavailable, and do not create an unauthorized local checkout when the connector-native backend is the authorized surface.

### Local Probe Engine

When a local target checkout is authorized, deterministic probes replace *derived* evidence (text inspection) with *measured* current-state evidence. Run:

```powershell
python scripts/probe-repo.py --repo-root <target-repo> [--output <path>/probe-report.yaml]
```

When the runtime has allocated an `expected_probe_report_path` (a runtime-owned,
session-scoped, same-episode destination for the local Probe Engine), you MUST
write the report there — always passing it as the probe's `--output` — and read
that exact file before synthesis. Do not probe-report to an arbitrary path, glob
for a report, select the newest report, or scan the target for a plausible one.
The runtime and the MODEL_WARRANT seam consume that exact report, and the brief
validator is given that exact path as `--probe-report` so a `file: probe-report.yaml`
citation in Section 8 resolves to it (see item 3 below). There is one probe-report
authority — that exact path — never a discovered or heuristically chosen file.

Then:

1. **Read `probe-report.yaml`.** Its values are verified current state, measured on the checked-out tree — prefer them over any documented claim (state-currency verification, per Standard Workflow item 4).
2. **Surface the measured numbers in your prose.** The report's `verification_gap.vg`, `context_entropy.ce`, `fixtures_coverage.coverage`, and `churn` fields feed directly into the missing-pieces, weakest-boundary, and evidence sections. A `vg > 0` with declared-but-unenforced checks is a `Contract Mismatch` signal; `vg == 1.0` means every declared check is unenforced (or CI is absent). `ce >= 5` triggers a hygiene warning about untracked/ignored artifact sprawl. A non-empty `missing_fixtures` list signals validator orphans (Zero Validation or Orphaned Examples candidates).
3. **Cite the local probe in Section 8.** Every excerpt that rests on a measured value must reference the probe that produced it (e.g. `probe-report.yaml:verification_gap.vg`), plus the usual `file:lines`. In an `evidence_excerpts` object, cite it as the exact logical name `file: probe-report.yaml` (with `lines:` a real line/range in the report). On an **external-repository run** the report legitimately lives outside the target checkout (the runtime-owned `expected_probe_report_path`, which must stay out of the target tree). For its citation to resolve, the validator must be given that exact path: `validate-brief.py --target-repo <target> --probe-report <expected_probe_report_path>` (the workflow runtime and `validate-and-report.py` pass it automatically). The `probe-report.yaml` logical name then binds to that one authorized file; no other path may resolve outside `--target-repo`, and a supplied-but-missing `--probe-report` fails closed (`PROBE_REPORT_NOT_FOUND`). If a multi-line span is quoted, use a YAML **literal block scalar** (`quote: |`) so newlines are preserved for grounding — a folded (`>`) or plain multi-line scalar collapses newlines to spaces and will not ground.
4. **Probe failure fallback.** If the local probe exits nonzero or the target is not a git repository (`is_git_repo: false`), the probe still reports directory-level facts; any claim you cannot measure must be labeled "documented but not independently verified" (per Standard Workflow item 4 and Section 8). Never treat local-probe failure as permission to fabricate measurements.
5. **Relationship findings are evidence candidates, not diagnoses.** The report's `relationships` section (version drift + ADR integrity, plus the discovered doc surface) lists mechanically-established disagreements with file:line provenance. Treat each finding as a candidate requiring semantic review: the probe cannot decide which source has authority, which claim is historical, or whether a disagreement matters — you can. A repository with zero relationship findings is a valid correct-negative result. Where a relationship finding sharpens a boundary (e.g. a version conflict, a stale ADR-status claim, a doc that references a missing ADR), cite it in Section 8 like any measured value (`probe-report.yaml:relationships.version.findings`).

### Representation-sufficiency assessment (MODEL_WARRANT input)

Before finalizing Section 13, make one explicit task-relative judgment about the
evidence environment: is it **sufficient for the current consequential reasoning
problem** (not merely "present")? Emit it in Section 13 as
`representation_sufficiency`:

```yaml
representation_sufficiency:
  status: sufficient | insufficient_bounded | inconclusive
  rationale: name the specific consequential gap, or why it suffices / why undetermined
  needed_representation: null | the bounded additional representation that resolves the gap
```

- `sufficient` — you can affirm the native evidence environment answers the current
  consequential question with acceptable diligence and traceability. (Grounds NO.)
- `insufficient_bounded` — you can affirm BOTH that a specific evidence/relationship/
  context gap exists AND that the gap is **consequential to the current goal**, and
  that a **bounded additional representation** resolves that reasoning gap. A
  mechanically detected gap (e.g. "relationship X not assembled") is repository
  evidence, not by itself a consequential insufficiency verdict: you must make and
  explain the consequentiality-and-boundedness judgment. (Grounds PARTIAL.)
- `inconclusive` — you cannot affirm sufficiency or bounded insufficiency (Grounds
  INCONCLUSIVE). Absence of evidence is never treated as insufficiency.

Do not infer sufficiency or insufficiency from evidence-line counts, missing files,
or citation presence. Do not invent a gap or a bounded remedy to force PARTIAL.

### Connector-native exact-SHA probe

When the execution contract authorizes only read-only GitHub connector access, follow [references/connector-native-probe.md](references/connector-native-probe.md) before synthesis. In this mode:

1. verify the exact target commit through GitHub and pin **every repository-content read** to that SHA;
2. record the GitHub-supplied blob SHA and line range for every file that supports a decision-changing claim;
3. separate immutable exact-SHA repository evidence from live GitHub metadata observed at query time;
4. treat local-only metrics (`verification_gap.vg`, `context_entropy.ce`, `fixtures_coverage.coverage`, `churn`) as **unmeasured on this surface** unless an explicitly authorized deterministic remote adapter produced them — never approximate them from prose inspection;
5. state `github_connector_exact_sha_v1 @ <target-sha>` in Section 7's state-currency discussion and use only evidence actually read at that exact SHA in Section 8.

The connector-native backend is not a weaker documentary fallback: exact Git tree/blob identity is measured evidence for the pinned snapshot. What the authorized surface cannot measure remains explicitly unmeasured rather than silently inferred.

## Output Format
Every response must follow the [Repository Sensemaking Brief](references/repo-analysis-template.md) structure.

## Boundary Rules
1. **No Implementation**: Do not execute workflows or implement changes. The output of this skill is a diagnostic artifact.
2. **Experiment responsibility boundary**: This diagnostic Skill may identify empirical uncertainty and missing evidence, but it does not manufacture an experimentation responsibility. Apply `../using-sensemaking/references/experiment-economy-v1.md` before recommending a probe/experiment when empirical evidence is material.

   ```text
   uncertainty != experiment
   missing evidence != experiment required
   diagnostic recommendation != experimentation responsibility
   ```

   Prefer an evidence need or candidate evidence source until experiment warrant exists.
3. **Registry grounding AND target availability**: A non-null `recommended_workflow_id` MUST satisfy *both* checks. (a) **Exists in the toolchain**: it is a live id in `skills/workflow-planner/references/workflow-registry.yaml` — do not invent or "hallucinate" workflow IDs from semantic context. (b) **Available from the analysed target**: the recommended workflow is actually an execution vehicle reachable from the target's context — i.e. the target repository is Sensemaking-configured and vendors `workflow-planner` plus the workflow's constituent skills (check for `skills/workflow-planner/`, a `skills/VENDORED.yaml`, `sensemaking-config.yaml`, or an equivalent marker), or the workflow is being run within the Sensemaking toolchain itself against the target. A workflow that exists in the registry but is **not** available from the target is a **no-match**, not a recommendation: do not silently collapse "exists in the Sensemaking toolchain" into "available in the target repository". In the no-match case (whether because nothing matches semantically, or because the match is not available from the target), set `escalation_recommended: true` and emit `recommended_workflow_id: null` (valid no-match state per ADR 0014); if the toolchain workflow is still a useful conceptual pointer, name it in the Section 11/12 prose and state plainly that it is a Sensemaking-toolchain workflow **not vendored/available in the analysed target repository**. Do not fabricate a closest structural match, and never imply target-local availability you have not verified.
4. **Clarification policy**: Ask no questions when repository evidence is sufficient. When unresolved owner intent would materially change the recommendation, ask a neutral, high-information clarification that gathers intent rather than advocating one option. Resolve empirical uncertainty through probes rather than asking the owner to guess. This policy applies regardless of execution mode, but *how* it's carried out differs: in conversational invocation, apply it directly — see "Interact" below, which is this policy's full worked-out procedure (uncertainty classification, the neutral-clarification discipline, the one-question default). In automated runtime execution there is no owner to ask (see Execution Protocol step 8) — the equivalent signal is `escalation_recommended: true`, optionally sharpened by Section 15's `uncertainty`/`owner_intent_state` fields, which is what a later conversational consumer (a human, or this skill re-invoked conversationally) uses to actually ask.

## References
- [Canonical Vocabulary Registry](../../docs/canonical-vocabulary.yaml) — Authoritative fog type definitions and routing field enums
- [Repo Analysis Template](references/repo-analysis-template.md)
- [Weakness Types](references/weakness-types.md)
- [Evidence Rules](references/evidence-rules.md)
- [UI Fog Signals Registry](references/ui-fog-signals.md)
- [Connector-native exact-SHA probe](references/connector-native-probe.md)
- [Architecture decision record](../../docs/candidate/architecture-decision.md) — why Diagnose/Interact are one skill, not two

## Execution Protocol

When executing as part of a workflow run:

1. Read the provided run_id, step_id, input artifacts, and expected artifact_id.
2. Call `scripts/run-ledger.py start-step`.
3. The runtime already resolved the output path and passed it as `expected_output_path` in context — use that path verbatim. Never call `scripts/create-artifact.py` (or otherwise recompute a path) during a runtime-invoked run; that path-recomputation is what caused a prior run to overwrite a tracked framework artifact (see ADR 0010, issue #40).
4. Produce the artifact at that exact path.
5. Call `scripts/validate-and-record.py`.
6. Only report completion if validation passes.
7. Never mark the next step complete yourself.
8. Stop here. Do not proceed to the Interact section below — there is no owner to ask in this execution path.

## Runtime-owned artifact skeleton (issue #55)

When this skill is invoked through the runtime's model executor,
`expected_output_path` already contains a **runtime-generated skeleton** by
the time you read it — see `scripts/brief_skeleton.py`. This exists because
prompt guidance alone was proven insufficient to guarantee the artifact's
deterministic grammar (PR #54: the model omitted the YAML fence entirely).

**Do not recreate the envelope.** These are already filled in by the runtime
and must not be re-authored or reordered:
- `artifact_id`, `schema_version`, `source_intent_ref`, `created_at`, `immutable`
- The heading structure and the single `## 13. Machine-readable handoff` YAML fence
- `<!-- MODEL_SECTION:<name>:BEGIN/END -->` marker comments — do not delete them

**Your job is only to fill in:**
- The prose between each `MODEL_SECTION` marker pair (repository goal, current
  shape, strong signals, missing pieces, improvement opportunities, weakest
  boundary prose, evidence prose, why-it-matters, candidate next steps,
  recommended next step, ready-to-copy prompt).
- The `evidence_excerpts` YAML block under Section 8.
- The placeholder YAML fields in Section 13: `user_implied_fog_type`,
  `primary_fog_type`, `diagnosis_conflict`, `escalation_recommended`,
  `evidence`, `recommended_workflow_id`, `recommended_execution_mode`,
  `weakest_boundary`.
- Optionally, Section 15's `extended_analysis:` block (see `references/repo-analysis-template.md`'s Section 15; ratified per ADR 0024). Leave it out
  entirely if you have nothing grounded to add; it is never required.

**Workflow IDs vs. skill IDs**: `recommended_workflow_id` must be an id from
`workflow-registry.yaml` (e.g. `architecture-implementation-workflow`), never
a skill id (e.g. `docs-aligner`). If uncertain which workflow applies, prefer
escalation (`escalation_recommended: true`) and the truthful no-match value
(`recommended_workflow_id: null`) over guessing — the runtime will
preserve your value verbatim, valid or not, and the validator (not the
runtime) is what rejects an invalid one.

**No-change / workflow mutual exclusion (directive #29)**: these are mutually
exclusive — never emit a routable workflow on a no-change brief.
- NORMAL ACTION brief -> emit a valid `recommended_workflow_id` (a real
  `workflow-registry.yaml` id).
- `outcome: NO_REPOSITORY_CHANGE_WARRANTED` -> omit `recommended_workflow_id`
  entirely or emit `recommended_workflow_id: null`. NEVER emit a routable
  workflow id on a NO_CHANGE brief (a NO_CHANGE terminal must not route a
  workflow; the validator rejects the combination as
  `NO_CHANGE_WORKFLOW_CONFLICT`).
- A missing/null `recommended_workflow_id` alone NEVER means NO_CHANGE.
  `NO_REPOSITORY_CHANGE_WARRANTED` is affirmative-only: it requires the
  explicit `outcome` field set to that exact value. Do not infer it from an
  absent workflow.

**Evidence-authority hierarchy and grammar** (unchanged from prior guidance,
still your responsibility): cite specific files and line ranges you actually
read (`Lx`/`Lx-Ly` or bare numbers both work, e.g. `L18` or `18`); never cite
a file you have not opened; state-currency probe evidence (`probe-report.yaml`
for the local backend, or exact-SHA Git tree/blob observations for
`github_connector_exact_sha_v1`) sits above direct code/config; prefer probes
over code/config over comments over external docs when they conflict; include
a **Logic trace** paragraph (beginning literally with "Logic trace:") connecting
evidence to your weakest-boundary conclusion.

The runtime writes a **tool-call trace** (`tool-call-trace.jsonl` in the
session artifact directory) recording every tool call you make during this
invocation — this is for debugging failed runs, not something you need to
produce yourself.

---

## Interact: conversational-invocation-only interaction procedure

**Applies only when you are talking directly with a user (or another agent) in conversation, not when invoked as an automated workflow step (see "Execution Protocol" above, step 8).** If you're not sure which mode you're in: if you were given a `run_id`/`step_id`/`expected_output_path`, you're in the automated path — stop after producing the artifact. Otherwise, continue below.

This section is the conversational-mode procedure for **Boundary Rule 4's clarification policy** — the policy itself is stated once, above, and applies in both execution modes; what follows is how to actually carry it out when a chat channel exists. Don't let this section's wording drift from Boundary Rule 3's — if you're revising one, revise both.

This skill's job, in this mode: given real (or agent-selected) owner uncertainty, produce a useful recommendation with the least owner burden possible, while never inventing an owner preference it doesn't have. This procedure is evidenced by a real-use validation experiment (see `docs/prototypes/real-use-experiment-2026-08-09/` on `prototype/repo-sensemaker-vnext`, PR #164) that ran it twice under genuine context isolation and found it independently avoided a real design failure mode (bundling an evidence-resolved fact with an evidence-supported-but-unauthorized recommendation) both times — see [docs/candidate/architecture-decision.md](../../docs/candidate/architecture-decision.md) for why the underlying *behavior* is treated as evidenced even though the packaging it originally shipped in (a separate Skill) was not. Independently, canonical `main`'s Boundary Rule 4 (PR #165, merged without knowledge of this branch) codifies the same "ask only if evidence-insufficient and decision-changing, resolve empirical uncertainty via probes" policy at the Diagnose level — real, if indirect, corroboration that this behavior is worth having, from a source that never saw #164's evidence.

### Interaction workflow

```text
recover known owner intent (conversation/prior context)
        |
        v
run Diagnose (above) -- produce the Repository Sensemaking Brief,
        |               optionally with Section 15 filled in
        v
read the brief you just produced
        |
        v
does Section 15's extended_analysis block exist and have an
owner_intent_state?
        |
   +----+----+
   no        yes
   |          |
   |          v
   |    inspect owner_intent_state.status
   |          |
   |   +------+-------------------+
   |   |                          |
   | sufficient / thin      blocking_unknown
   |   |                          |
   |   |                          v
   |   |                    ask the owner what's needed
   |   |                    to proceed at all (a hard
   |   |                    stop, not the "one neutral
   |   |                    question" refinement below)
   |   v
   |  inspect uncertainty.source
   |          |
   |   repository_evidence -> re-run Diagnose with a narrower
   |                          investigation focus (not a new
   |                          owner question)
   |   empirical            -> identify the decision-changing evidence
   |                          need and apply Experiment Economy before
   |                          recommending any evidence-producing action.
   |                          Prefer existing evidence, inspection,
   |                          verification, owner/external clarification,
   |                          a tiny probe, or cheap reversible construction
   |                          when sufficient. A bounded probe is only a
   |                          candidate after that comparison; an experiment
   |                          requires separate experiment warrant. Do not
   |                          run it here -- Boundary Rule #1 (No
   |                          implementation) still applies. If the selected
   |                          evidence-producing action would itself need
   |                          separate authorization, say so; do not assume
   |                          "bounded" means "pre-authorized."
   |   owner_intent         -> would a different answer materially
   |                          change the recommendation?
   |                             no  -> proceed, note the residual
   |                                    uncertainty as non-decision-
   |                                    changing
   |                             yes -> ask ONE neutral, high-
   |                                    information question (see
   |                                    below), then proceed
   |   external_environment -> note what would need inspecting
   |                          outside this repository; do not guess
   v
synthesize and recommend, keeping these separate (do not bundle them
into one "ready to act on" recommendation, even when both are true):
  - a repository-evidence-resolved fact/fix (ready regardless of any
    open owner question)
  - an evidence-supported-but-not-owner-authorized recommendation
    (present it as a recommendation for the owner to ratify, not as
    already decided)
```

**"One question" is a working constraint, not a hard-coded rule.** If investigation genuinely produces two independent decision-changing owner-intent uncertainties, that is itself a finding worth reporting plainly rather than silently forcing both into one question or silently dropping the second — but the default is one question.

### `repository_evidence` vs. `empirical`

The discriminant is not the question's subject matter or tense ("is X true," "has X happened") — it's whether the answer already exists somewhere inspectable, or has to be newly generated:

- **`repository_evidence`**: the answer exists already, in something you can look up or search — files, git history, run logs, session artifact directories, `tool-call-trace.jsonl` records, CI history. You haven't looked yet, but looking is enough.
- **`empirical`**: nothing that already exists can answer it. Answering requires making something happen that hasn't happened yet — running a script, executing a probe, triggering an experiment.

"Has this ever caused a real failure in production" is `repository_evidence` if run logs/traces already exist to search. It's `empirical` if nothing has ever been run and the only way to find out is to run it. Get this wrong in either direction and the downstream behavior is still safe (neither branch asks the owner to guess), but get it right and the *type* of next step you recommend — search vs. probe — is the correct one, not just a defensible one.

### Neutral clarification

A clarification question that labels one option as "what the repository evidence supports" is leading, even when unintentional. Concretely, when constructing the question:

- Do not name a preferred option in the option labels.
- Do not use language that implies one answer is more evidenced than another when the uncertainty is genuinely about *owner preference*, not evidence — if it were an evidence question, it wouldn't have reached this step (`uncertainty.source` would have been `repository_evidence` or `empirical`, handled above without asking).
- State the decision each option leads to, not just the option's label — the owner is choosing a consequence, not a taxonomy term.

### Recover known intent

Before producing the brief, extract whatever the owner has already established from the conversation or prior context (this is the same extraction Stage 1 already does for `user_implied_fog_type` — apply it here as the interaction procedure's first step too, not a separate mechanism). **Do not pad thin intent to look more complete than it is** — a Section 15 `owner_intent_state.known` that overstates what's actually established defeats the field's own purpose.

### What this procedure does not do

- Does not treat this procedure as running during automated workflow execution — see the mode check above.
- Does not ask more than one clarifying question without explicitly noting why the default was insufficient.
- Does not present Section 15's fields or this interaction procedure as experimental in the final output to the user — they are ratified (ADR 0024); represent them as such, without hedging.

## Declared architecture rules (optional)

When the target has architecture records (`schema_version: 2`), compare the
diagnosis with its declared rules and cite them by claim id, for example
`rule:stable-core-no-lab-imports`. A rule that does not cover the
diagnosed path is `NOT_ASSESSED`, not evidence of absence. Declared rules are
claims to verify against code, not verified facts.
