# Repository Sensemaking Brief

## 1. Repository goal
What this repo appears to be trying to accomplish.

## 2. Current shape
Main folders, files, skills, workflows, examples, and references.

## 3. Strong signals
What is already working or conceptually strong.

## 4. Missing pieces
What is absent, incomplete, or implied but not implemented.

## 5. Improvement opportunities
Useful refinements that are not urgent blockers.

## 6. Weakest boundary
The most ambiguous, unproven, unsafe, or unenforced part of the repo.

**You MUST classify the boundary using one of the recognized weakness types** (see
[Weakness Types](weakness-types.md)): `Vocabulary Drift`, `Contract Mismatch`,
`Ghost Features`, `Safety Gaps`, `Implicit Dependencies`, `Zero Validation`, or
`Orphaned Examples`. State it explicitly on its own line:

`**Weakness type:** <one of the recognized types>`

Example: `**Weakness type:** Zero Validation`

**This weakness-type enum is a completely different vocabulary from the
fog-type classification in Section 6.5 below.** Do not answer this question
with a fog-type value (e.g. `architecture_fog`) -- only the seven weakness
types listed above are valid here.

---

## 6.5. Problem classification (fog type)
Classify the primary type of uncertainty or problem:
- **product_fog**: Vague user needs, unclear feature requirements, undocumented workflows
- **ui_fog**: Navigation complexity, screen design issues, interaction patterns unclear
- **docs_fog**: Missing documentation, unclear specifications, knowledge gaps
- **architecture_fog**: Code structure problems, design issues, unclear boundaries (default if unclear)

This classification is diagnostic metadata. It does not determine an implementation workflow. The active agent selects the warranted responsibility; a workflow recommendation is optional and must be independently supported.

## 7. Evidence
File-level evidence supporting the diagnosis (cites specific files and line ranges,
e.g. `scripts/validate-brief.py:46`).

**Output mode:** choose and signal the citation mode per [evidence-rules.md](evidence-rules.md)
("Citation Format: Two Output Modes"):

```markdown
<!-- mode: investigative | durable -->
```

- **investigative** (default, human readers): file paths **with line numbers**, e.g. `src/auth/login.ts:42-58`.
- **durable** (downstream skills that validate/transform evidence): file paths **only, no line numbers**, grep-verifiable claims.

If unsure, default to `investigative` -- a downstream skill can transform
investigative evidence into durable form, but the reverse is not possible
without re-running the analysis.

**This section's own prose must contain at least one literal file-path
citation** (e.g. `scripts/validate-brief.py:46`), even though Section 8
(evidence excerpts) and Section 13 (machine-readable `evidence:` list) also
carry structured citations. The validator checks Section 7's prose
independently -- citations that appear only in Sections 8/13 do not satisfy
this requirement.

Minimal valid example:

> `scripts/validate-brief.py:259` shows the Evidence-section check runs
> independently of the evidence_excerpts block in Section 8, which is why a
> citation must also appear here in Section 7's own prose.

**Logic trace (required):** Show the diagnostic reasoning that connects the cited
evidence to the weakest boundary — i.e., the chain from observed signals to your
conclusion. Begin this paragraph with the literal words "Logic trace:".

**State currency and claim provenance (required):** Keep observed evidence,
documented claims, inference, and owner-supplied judgment/context
distinguishable. Decision-changing current-state claims must explicitly
distinguish verified current state from merely documented state: when verified,
cite the probe used (e.g. git history, working-tree state, test runs, recent
reviews); when not verified, clearly identify the claim as documented but not
independently verified. Never treat documented state as automatically current.

## 8. Evidence excerpts
Each excerpt's `lines` field is a single line or a range. Use either the `Lx` /
`Lx-Ly` form (e.g. `L18`, `L25-L30`) or bare numbers (e.g. `18`, `25-30`) — both
are accepted. Every excerpt must include all four fields: `file`, `lines`,
`quote`, `supports_claim`.

`file` and `lines` are what matter — give the exact path and the smallest
line range that contains the cited text. Do not invent a path or a range you
have not actually read. **Do not hand-transcribe the `quote` text yourself:**
the runtime overwrites `quote` with the exact verbatim text it reads from
`file`/`lines` before validation runs (issue #89) — the model is no longer
the verbatim-copy boundary, because hand-transcription has been observed to
silently mangle Unicode punctuation (e.g. em dashes), drop leading
indentation, and alter Markdown formatting (bold/backticks). Write a short
placeholder for `quote` (e.g. `"see file/lines"`) rather than retyping the
source text.

**When you must supply a real `quote` yourself** (any invocation without the
runtime's quote-extractor pass — standalone/conversational use), a multi-line
span MUST be a YAML **literal block scalar** (`quote: |`) so newlines are
preserved. A folded (`>`) or plain multi-line scalar collapses newlines to
single spaces and will fail grounding against multi-line source. When in doubt,
quote a single physical source line.

**Local Probe Engine citations.** Cite a measured probe value with the exact
logical name `file: probe-report.yaml` and a real `lines:` location in that
report. On an external-repository run the report sits outside the target
checkout (the runtime-owned `expected_probe_report_path`); the brief validator
must be given that exact path via `--probe-report` for the citation to resolve
(`validate-and-report.py` and the workflow runtime pass it automatically).
That logical name binds to the one authorized report only — no other path may
resolve outside `--target-repo`.

```yaml
evidence_excerpts:
  - file: path/to/file.ext
    lines: L10-L15
    quote: "see file/lines"
    supports_claim: "..."
  - file: probe-report.yaml            # resolves to --probe-report on external runs
    lines: L24
    quote: "  vg: 0.0"
    supports_claim: "mechanical health is not the weak boundary"
```

## 9. Why this boundary matters
What breaks if this remains weak.

## 10. Candidate next steps
2–5 possible next moves.

## 11. Recommended next step
The smallest concrete action with highest leverage.

If the recommended step depends on a current-state claim, cite the probe that
verified it, or state explicitly that the claim is documented but not
independently verified.

## 12. Recommended workflow
Optionally name one workflow candidate from the official `workflow-registry.yaml`
only when the evidence supports that bounded workflow as a current execution
vehicle. Product or architecture fog does **not** imply a default workflow. If
a workflow is named, it must actually be available as an execution vehicle from
the analysed target (the target vendors `workflow-planner` and the workflow's skills, e.g. a
`skills/workflow-planner/` dir / `skills/VENDORED.yaml` / `sensemaking-config.yaml`,
or the workflow runs within the Sensemaking toolchain against the target).
"Exists in the toolchain registry" is not "available in the target repository".
If a registry workflow fits conceptually but is not available in the target, name
it here as a pointer, say plainly it is not vendored/available in the target, and
set `recommended_workflow_id: null` with `escalation_recommended: true` in
Section 13. Do not invent workflow IDs.

## 13. Machine-readable handoff

```yaml
artifact_id: repository_sensemaking_brief
schema_version: 1
source_intent_ref: artifacts/01-orchestration-run/00-user-intent.md
user_implied_fog_type: product_fog | ui_fog | docs_fog | architecture_fog | unknown
primary_fog_type: product_fog | ui_fog | docs_fog | architecture_fog
diagnosis_conflict: true | false
escalation_recommended: true | false
evidence:
  - "path/to/file.ext (lines L10-L15): short citation supporting the diagnosis"
  - "path/to/other_file.ext: short citation supporting the diagnosis"
recommended_workflow_id: # MUST match an ID in workflow-registry.yaml AND be available from the target (else null + escalation; see Section 12)
recommended_execution_mode: plan_only | guided_execution
weakest_boundary:
weakness_type: # one of the 7 registered types in weakness-types.md, or "Other"
weakness_type_explanation: null # required non-empty string ONLY when weakness_type is "Other"; otherwise null
required_inputs:
  - user_intent
  - repository_state
created_at: "2026-05-19T16:00:00Z"
immutable: true
outcome: ACTION_REQUIRED | NO_REPOSITORY_CHANGE_WARRANTED # optional; omit for a normal action brief, set NO_REPOSITORY_CHANGE_WARRANTED for a first-class terminal success
representation_sufficiency: # optional; producer-authored task-relative MODEL_WARRANT input (Ruling 2 / directive #23); NOT a repository fact
  status: sufficient | insufficient_bounded | inconclusive
  rationale: >- # required non-empty for insufficient_bounded; names the specific consequential gap
  needed_representation: >- # required non-empty for insufficient_bounded; the bounded representation that resolves the reasoning gap; null for sufficient/inconclusive
```

`representation_sufficiency` is the producer's semantic judgment about whether the
current evidence environment is **sufficient for the current consequential
reasoning problem** (MODEL_WARRANT input). It is never inferred from evidence-line
count or citation presence. `status: sufficient` grounds `NO`; `status:
insufficient_bounded` (with a non-empty `rationale` naming a consequential gap and
a non-empty `needed_representation`) grounds `PARTIAL`; `inconclusive`/absent/
malformed stays UNKNOWN. Absence of evidence is never treated as insufficiency.

**No-change / workflow mutual exclusion (directive #29)**: `outcome:
NO_REPOSITORY_CHANGE_WARRANTED` is affirmative-only and MUST NOT be combined with a
non-null `recommended_workflow_id` (a NO_CHANGE terminal never routes a workflow; the
validator rejects the combination as `NO_CHANGE_WORKFLOW_CONFLICT`). NORMAL ACTION
briefs require a valid `recommended_workflow_id` (a real `workflow-registry.yaml` id).
A missing/null `recommended_workflow_id` alone NEVER implies NO_CHANGE.

`user_implied_fog_type` records the fog type the **user's stated intent** implies —
an input characterization, not the diagnosis. Use `unknown` when the intent is
fog-neutral (implies no particular fog type); it is a legal value for this field
only. `primary_fog_type` (the diagnosis) is always one of the four canonical fog
types and is never `unknown`.

`weakness_type` is required metadata but non-blocking (D2): a missing or
unrecognized value is a validator warning, not an error, and never
invalidates the brief. It must match the `**Weakness type:**` line stated in
Section 6's prose. If none of the 7 registered types fit, use `Other` and
give a non-empty `weakness_type_explanation` — omitting the explanation for
`Other` is also a non-blocking warning, but it must be resolved before a
human grants final approval.

All required fields (Stage 1 intent-aware fields, standard routing fields, and
top-level fields required by `artifact-contracts.yaml`) MUST appear in that
**single** fenced yaml block above. Do not split them across multiple yaml
blocks — only the first yaml fence immediately following this heading is
parsed by `validate-brief.py`.

`evidence` is a required field: a list of short file-level citation strings
(the machine-readable counterpart to the prose in Section 7 / the excerpts in
Section 8). It is distinct from `evidence_excerpts` (structured excerpt
objects) — both are expected, under their own names.

### Complete Example
```yaml
artifact_id: repository_sensemaking_brief
schema_version: 1
source_intent_ref: artifacts/01-orchestration-run/00-user-intent.md
user_implied_fog_type: product_fog
primary_fog_type: product_fog
diagnosis_conflict: false
escalation_recommended: true
evidence:
  - "README.md (lines 5-12): feature requirements are vague, no user context"
  - "docs/ARCHITECTURE.md: does not exist"
recommended_workflow_id: null  # product fog has no default workflow; active agent selects the responsibility directly
recommended_execution_mode: plan_only
weakest_boundary: Zero Validation
weakness_type: Zero Validation  # must be one of the 7 weakness types (weakness-types.md) or "Other", NOT a fog-type value
weakness_type_explanation: null
required_inputs:
  - user_intent
  - repository_state
created_at: "2026-05-19T16:00:00Z"
immutable: true
```

## 14. Ready-to-copy prompt
Prompt for `workflow-planner` or another downstream skill.

## 15. Extended analysis

**Optional. Non-blocking.** Ratified as ordinary optional contract fields —
see [ADR 0024](../../../docs/adr/0024-extended-analysis-field-classification.md)
and [docs/candidate/architecture-decision.md](../../../docs/candidate/architecture-decision.md)
for the classification and rationale. Leave this section absent entirely if
you have nothing to add here — `validate-brief.py` never requires it, and
Sections 1-14 above remain the complete, valid brief on their own.

If you do have something to add, use a single `extended_analysis:` YAML
mapping with any subset of these fields (all optional, independently):

```yaml
extended_analysis:
  schema_version: 1
  domain:
    # List, not a single value -- unlike primary_fog_type (Section 13),
    # which is forced to pick one. Reuses the same canonical fog-type
    # vocabulary base names (product, ui, architecture, docs, integration).
    # List EVERY fog dimension genuinely implicated, not just the primary
    # one. A downstream reader outside one of these domains should treat
    # it as an explicit disclosure trigger ("this is out of my lens"),
    # never silently ignore it.
    - product
    - architecture
  consequential_boundary:
    description: >
      What actually matters for what happens next -- may be narrower or
      broader than Section 6's weakest_boundary. Section 15 is
      deliberately allowed to name a boundary Section 6 doesn't --
      co-occurrence in the same brief is not a claim that they're the
      same boundary. A downstream reader deciding whether a proposal
      "covers" this weakness must check what THIS field itself
      describes, not assume it's Section 6's weakest_boundary restated.
    rationale: >
      Why this boundary, specifically, is the one worth acting on.
    is_demonstrated_weakness: true | false
    # true only if this is independently, currently demonstrated (not a
    # suspicion or a plausible-sounding pattern). Do NOT use a
    # weakness_type value of "none" for a legitimate-but-unresolved
    # choice -- set this to false and leave Section 13's weakness_type
    # absent instead; weakness_type's own taxonomy (Section 6) is
    # untouched by this field.
  uncertainty:
    source: repository_evidence | empirical | owner_intent | external_environment
    # The discriminant between repository_evidence and empirical is NOT
    # the question's subject matter or tense ("is X true", "has X
    # happened") -- it's whether the answer already exists somewhere
    # inspectable (repository_evidence: files, logs, traces, run
    # history, git history -- already generated, just needs to be
    # looked up/searched) or whether answering it requires generating a
    # NEW observation (empirical: running something, executing a probe,
    # triggering an experiment that hasn't happened yet). "Has this ever
    # failed in production" is repository_evidence if run logs already
    # exist to search; it's empirical if nothing has ever been run and
    # the only way to find out is to run it. Either way: empirical
    # uncertainty is never resolved by asking the owner to guess.
    # Identify the evidence need and apply Experiment Economy before
    # recommending an evidence-producing action. A probe is a candidate,
    # not an automatic consequence of empirical uncertainty; an experiment
    # requires experiment warrant (see Boundary Rule 2).
    question: >
      The specific unresolved question, independent of source -- every
      source can have one, not only owner_intent.
  owner_intent_state:
    known: >
      What's already been established about owner intent from prior
      context, stated plainly (not padded to look more complete than it
      is).
    status: sufficient | thin | blocking_unknown
    # What's actually unresolved lives in uncertainty.question above --
    # do not restate it here as a second, separately-maintained note;
    # the two can silently drift apart.
```

None of these fields drive automated routing (`workflow-runtime.py` does
not read them) — they exist for a human, or a downstream skill reading
the brief directly, to use at their own discretion. See
`skills/repo-sensemaker/SKILL.md`'s Interact section for how these fields
are meant to be used in conversational (non-runtime) invocation.
