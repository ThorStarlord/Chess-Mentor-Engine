# RECONCILE / AUDIT — Living memory from engineering evidence

## Trigger

Consequential new evidence about product intent, accepted design, important implementation, tests, migration, failure analysis or incidents. A corrected test assumption or a task blocked by an overlooked architectural alternative can justify a durable lesson **without changing product code**. Minor edits and unsurprising confirmations with no reusable consequence use NO_MODEL_CHANGE.

## Procedure

1. Pin the prior indexed revision and current Git HEAD. **Continue in the active checkout and context**, including while it is dirty. Inspect changed code and existing knowledge through `knowledge-query --repo .`; the workspace metadata says whether the index is historical or local changes are unindexed. `--operation workspace-impact --repo .` lists the reviewed indexed records whose cited source files changed since the indexed revision (committed or not), separating an edited record definition from changed evidence; treat the list as re-inspection candidates, and changed code that no record cites as a possible coverage gap, not as unaffected knowledge. Those uncited paths are listed in `workspace_impact.uncited_changed_paths` (bounded; `uncited_changed_path_total` is the pre-limit count); inspect them directly when they bear on the task. A dirty checkout is never a committed source revision.
2. Do not create a clean-room development session just to proceed. After an ordinary code/knowledge commit, at the naturally clean current HEAD, compare source fingerprints with `semantic knowledge-audit --indexed-ref OLD_SHA --current-ref HEAD_SHA`. Review its additive `authored_record_audit` for changed shared JSON packs: individual authored fields may be unchanged despite container drift, or absent from their previous pack path (not proof of deletion). The record-level comparison avoids another indexed snapshot but does not assess semantic validity, changed supporting code, external sources or dirty overlay bytes. Source drift does not automatically invalidate historical decisions.
3. If both snapshots are indexed, use `knowledge-query --operation changes --base-ref OLD --target-ref NEW` to inspect recorded set differences. Read its additive `change_classification` details for supported Git-reviewed records: distinguish individually authored-field changes, source-container drift, independently cited evidence changes and provenance-only fingerprint noise while preserving raw delta IDs. A NOT_ASSESSED result or missing cited path is not a clean bill of health. These mechanical facets do **not** prove the historical claim has changed meaning or remains applicable. `knowledge-audit` remains a separate conservative byte-drift check; do not require this query for trivial work.
4. If relevant receipts exist, read pending and repeated misses with `python scripts/summarize-receipts.py --repo .` when the optional framework script is available; otherwise inspect the relevant receipt YAML directly. Did any RECALL in this or an earlier session return NOT ASSESSED for something a task needed? A miss recurring across sessions is evidence for a source-linked ADD, not proof and not a quota. Without receipts, task output is not automatically available for cross-session aggregation.
5. Follow changed evidence **and consequential newly understood evidence** to claims/relations, verify original affected code and tests, and check documented product/architecture authority. Do not assume only changed source files can teach something worth retaining.
6. Choose a disposition per consequential affected claim:
   - **CONFIRM:** current evidence supports the existing interpretation.
   - **REVISE:** correct an unsupported or mistaken interpretation.
   - **SUPERSEDE:** retain historical context and record the replacement.
   - **ADD:** introduce a meaningful new concept, relationship, decision or lesson.
   - **CONTEST:** preserve contradictory sources as unresolved.
   - **NO_MODEL_CHANGE:** no durable change is justified.

   Distinguish *no existing claim was falsified* from *nothing reusable was learned*. Before selecting NO_MODEL_CHANGE after a repaired test, incorrect blocker inference or architecture rediscovery, ask whether a future agent would plausibly repeat the mistake without one source-linked invariant, decision link or lesson. Use **ADD** only if the distinction is stable, decision-relevant, source-supported and not already represented. A successful no-change run is not a quota failure.
7. Edit only the relevant reviewed Git-authored knowledge files and source documents. If a record's interpretation is disputed, never silently change its historical assertion to disguise the conflict.
8. In the active dirty checkout run `semantic knowledge-proposal-check --repo . --proposal .sensemaking/knowledge/NAME.json --json` to preflight reviewed draft records when warranted. For ordinary development, select verification proportional to the intended claim. **Under the owner's current construction-only direction, do not add, run, or wait for unit or synthetic evidence tests**; report `NOT_RUN`, preserve existing hosted CI and its protections, and do not make tested/release-qualified claims from untested work. Commit source and knowledge in the normal feature-branch workflow. No fresh-context handoff is required after every commit.
9. At the resulting **naturally clean committed SHA**, rebuild the index outside the repo, check currentness and preserve older snapshots. Exact committed indexing requires clean bytes; dirty-worktree querying and feature construction do not.
10. Report affected domains, corrections, remains-unknown evidence, tests actually run, and where future agents should look for the reasoning. If a [query receipt](query-receipt.md) is used, finalize it with each disposition, including NO_MODEL_CHANGE.

## Memory hygiene

- Separate lexical imports and path containment from semantic dependencies.
- Avoid endless duplicate incident lessons and obsolete active claims.
- Reuse stable identifiers for the same entity through versions, but use distinct identifiers for genuinely different concepts.
- When a re-inspection candidate is a `poss:` possibility record, check its realization and `revisit_when` against the change. REVISE by appending to `disposition_history` or updating `realization` with its new basis; never rewrite an earlier disposition. A satisfied `revisit_when` is a question for the agent, not a selection.
- When construction realizes, changes or abandons an option an `architectural_synthesis` compared, re-inspect its `arch:` and `conseq:` records. Compare what was observed with each prediction and append an assessment (CONFIRM, REVISE or CONTEST; status `invalidated` when observation refutes it), citing the observed evidence as an `observation` claim. Never rewrite the original prediction or the immutable synthesis. Append to the option's preference history when the preference changes, and retain a genuinely new possibility as a `poss:` record. One confirmed prediction does not prove its mechanism.
- After building an option, anchor its reasoning to the code, or `context-for` on the implementing files returns none of it: a `component` with `owned_paths` for those files, `decided_by` the governing `decision`, which `references` the compared `arch:` options; `references` from the component to decisive observations and lessons; and a path-scoped `architecture_rule` for an invariant that must survive later edits (for example "stays derived").
- Distinguish a historical decision that was valid then from an error in the original interpretation.
- Never infer a successful verification because a test file exists or a PR mentions a green check.
- Use explicit source-revision identities for third-party issues/PRs when evidence matters.
- If concurrent work changes the same authored pack, reconcile Git conflicts through source inspection rather than overwriting another agent's knowledge.

AUDIT returns currentness/coverage findings without mutating the record; reconciliation is a separate meaning judgment.
- **Architecture drift:** run `knowledge-check-rules` at the new clean HEAD. Changed files that no component covers are coverage candidates. A finding is evidence for review, never a verdict; a rule changes only through the same disposition vocabulary as any other claim.
