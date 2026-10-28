# Evidence Rules for Repo Sensemaking

To maintain diagnostic rigor, all claims in a **Repository Sensemaking Brief** must be backed by evidence:

1. **File Citation**: Mention the specific file and line numbers (if possible) where a signal or weakness is found.
2. **Structural Proof**: Cite the directory tree or file organization as proof of shape or missing pieces.
3. **Contrastive Evidence**: Compare what the README says vs. what the `ls` or `view_file` output shows.
4. **Logic Trace**: Follow the execution path of a workflow or skill to identify where boundaries are unenforced.
5. **No Vibe-based Diagnosis**: Avoid saying something "feels" off. State exactly which boundary is unproven or ambiguous.
6. **Taxonomy Verification**: Before flagging a vocabulary-drift or contradiction claim, verify the flagged term against the codebase's actual enums, models, and layer/scope definitions. Multiple legitimate taxonomies can coexist in one repository (e.g. auteur's 5 semantic layers AND its 9 structure-engine diagnostic layers in `src/auteur/structure/state.py:185-193`), and a "contradiction" between them may be a false positive. Cite the code-level definition (enum, `_LAYER_ORDER`, schema) that proves or disproves the drift before writing it into the brief. (See Evidence 0016, Failure 2.)
7. **Collision Dedup Direction**: When two artifacts collide on an ID (ADR number, artifact id, workflow id), determine which side is load-bearing **before** recommending which to renumber: count external references to each candidate, check git history for prior dedup intent, and grep **all** files (including handoffs, archived docs, and code docstrings) for every reference. Keep the load-bearing number on the most-referenced side (usually 0 reference edits); renumber the orphan. Never recommend "renumber one of X/Y" without the reference-count evidence. (See Evidence 0016, Failure 1.)
8. **Test Count Precision**: When a doc or README claims "N tests", compare it against a `pytest --collect-only` test-case count, never against a raw test-file count. Test-file counts and test-case counts are different metrics and comparing them produces false staleness findings. The probe report's `test_collection` now carries both `test_file_count` and a best-effort `test_case_count` for this purpose. (See Evidence 0016.)
9. **Probe Timeout Is Not a Measurement**: When a probe subprocess cannot complete (e.g. `git status --ignored` hitting its timeout cap while enumerating a large ignored set), the metric is unmeasured and must be reported as such — never as a false "clean" value. Auteur's `context_entropy.ce` read `0.0` despite ~10k ignored root JSONs because the git call hit its cap and returned empty; a silent failure that looks like a clean measurement masks exactly the sprawl the probe exists to detect. (See Evidence 0017, finding 1.)
10. **Excerpt Format Matches the Consumer's Validator Generation**: Evidence line references come in two accepted forms (bare numbers vs `Lx`/`Lx-Ly`), and not every validator generation accepts both — a brief that passes the canonical validator can fail a target's vendored validator (and vice versa). Know which generation the target validator runs and emit that format; never assume two consumers agree on citation syntax. (See Evidence 0017, finding 2.)
11. **A Catalog Entry Is Not a Finding**: A probe that catalogs a condition without emitting a finding (e.g. duplicate ADR ids present in `relationships.adr.catalog` while `relationships.adr.findings` is empty) leaves detection to the model's semantic review. Treat empty `findings` as "no known defect flagged", not "no defect": check raw catalog data against known defect classes (duplicate ids, missing/unrecognized statuses) before concluding a negative. (See Evidence 0017, finding 3.)
12. **Guards Must Cover the Artifacts They Claim to Protect**: A validator check that scans only a subset of the surface it claims to guard (auteur's `file:///` check walked `examples/` only, so a stale root `HANDOFF.md` with machine-specific links passed every check) is an unguarded escape hatch. When a brief flags an artifact, verify the guard's scan surface actually includes it before citing the guard as coverage. (See Evidence 0017, finding 4.)
13. **Observation Is Not Inference**: A direct read or deterministic probe establishes only its bounded observation. Keep semantic interpretations such as architectural intent, root cause, product value, or repair success separate and explicitly inferential unless independently ratified.
14. **Material Claims Carry Epistemic Status**: For decision-changing claims, use the shared semantic vocabulary where it improves clarity: `OBSERVED`, `DERIVED`, `INFERRED`, `HYPOTHESIZED`, `RATIFIED`, `CONTRADICTED`, `SUPERSEDED`, or `UNRESOLVED`. These labels describe warrant, not numeric probability.
15. **Currentness Is Part of Warrant**: A material claim about present repository state must inherit the mandatory state-currency boundary or be clearly marked documented/unverified. A correct historical claim is not automatically a current claim.
16. **Absence Requires Completeness**: Zero matches establish bounded absence only when the search/probe contract establishes the searched scope as complete for the claim. Otherwise report `no match observed in searched scope`, not `does not exist`.
17. **Preserve Explicit Limits**: Every consequential conclusion should preserve material blind spots and non-claims: inaccessible surfaces, unmeasured metrics, inherited assumptions, unresolved contradictions, or evidence that would change the conclusion.

Rules 13-17 operationalize the shared Reasoning Model for Phase 9 without changing the `repository_sensemaking_brief` schema. Apply them through the existing evidence, Logic trace, state-currency, representation-sufficiency, and optional extended-analysis surfaces. See [semantic-reasoning-alignment.md](semantic-reasoning-alignment.md).

## Provenance of rules 6-12

Rules 6-8 were added after Evidence 0016 (`experiments/evidence/0016-auteur-remediation-postmortem.md`), a postmortem of the first full brief -> remediation cycle on the external `auteur` repository. Rule 6 fixes a false-positive vocabulary-drift flag (9 structure layers vs 5 semantic layers); Rule 7 fixes a reversed architecture-decision record 013 deduplication in the external Auteur repository that broke 9 load-bearing references and missed a 10th; Rule 8 fixes a file-count-vs-case-count comparison in the HANDOFF staleness finding.

Rules 9-12 were added after Evidence 0017 (`experiments/evidence/0017-auteur-repo-sensemaking-brief/EVIDENCE.md`), the direct-invoked dogfood record of the second auteur brief. Rule 9 fixes a false "clean" `context_entropy.ce` caused by a probe timeout; Rule 10 fixes cross-validator excerpt-format drift (bare numbers vs `Lx`/`Lx-Ly`); Rule 11 fixes the duplicate-ADR condition being cataloged but not flagged; Rule 12 fixes the root-handoff `file:///` escape from a guard that only scanned `examples/`.

Rules 13-17 were added in Phase 9 Pilot A to align repo-sensemaker with the repository-wide semantic architecture. They formalize distinctions that the Skill already used inconsistently in prose and do not create new routing or mutation authority.

## Citation Format: Two Output Modes

Rule 1 (File Citation) supports **two output modes**, optimized for different consumers of the brief.

### Mode 1: Investigative

**When to use:** Default mode when a human is reading the brief directly to decide what to do next.

**What to cite:**
- Specific file paths **with line numbers** (e.g., `src/auth/login.ts:42-58`)
- Exact code snippets showing the problem
- Direct quotes from documentation

**Why:** Investigators need exact locations to quickly verify the problem in their IDE.

### Mode 2: Durable

**When to use:** When the brief will be consumed by downstream skills that validate, transform, or act on the evidence (e.g. `to-prd`, `to-issues`, `workflow-planner`, `sensemaking-docs-reconciler`).

**What to cite:**
- File paths **only, no line numbers** (e.g., `src/auth/login.ts`)
- Behavioral descriptions, not code locations
- All claims must be **grep-verifiable** against the current tree

**Why:** Downstream tools can't maintain line numbers as the codebase evolves. They need claims verifiable by grep, not by sight.

### Choosing your mode

Signal the mode in Section 7 of the [Repository Sensemaking Brief](repo-analysis-template.md):

```markdown
## 7. Evidence

<!-- mode: investigative | durable -->
```

If unsure, default to **investigative** — a downstream skill can transform investigative-mode evidence into durable form, but the reverse (durable -> investigative) is not possible without re-running the analysis, since line numbers are already gone.

### Testing your evidence

- **Investigative mode** is self-evident: open the file at the line number and verify the problem exists.
- **Durable mode** must pass a grep test: take the file path, grep for key terms from the behavioral description, and confirm the results show the problem described. If grep returns nothing, or shows the problem is already fixed, the evidence is stale.

## Related

- [Repository Sensemaking Brief Template](repo-analysis-template.md) — Section 7 (Evidence)
- [Semantic reasoning alignment](semantic-reasoning-alignment.md) — Phase 9 observation/claim/currentness discipline
- [Reasoning Model](../../../docs/semantic-architecture/reasoning-model.md) — repository-wide semantic lifecycle
- [Artifact Contracts: repository_sensemaking_brief](../../workflow-planner/references/artifact-contracts.yaml) — Consumer requirements
