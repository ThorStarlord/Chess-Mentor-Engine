# Semantic Query Receipt (`semantic_query_receipt`)

**Status:** contract reference for `repository-semantic-steward` (proposed ADR 0032)  
**Validator:** `scripts/validate-receipt.py` (also routed by `sensemaking-skills validate --artifact <file>`)  
**Reader:** `scripts/summarize-receipts.py` (optional framework tool)

## 1. Why the Steward writes a receipt

A query result can be regenerated only by someone who knows the query was
asked. The most decision-relevant Steward output is often **negative**: a
RECALL that returned `NOT ASSESSED` for something the task needed, after which
the agent reconstructed the answer from source. If that miss is not recorded,
the next session neither knows the question was asked nor that the model was
blind there, and a pattern of blindness across sessions can never be detected.

The query receipt records **what was asked, at which revision, what came back,
what was missing, and what happened to the miss**. It does not record query
payloads, claim text or reasoning; those are reproducible from the pinned refs
or belong in reviewed knowledge.

```text
query receipt     != reviewed knowledge (it is never indexed as knowledge)
query receipt     != proof the retrieved claims are true
recorded miss     != knowledge gap fixed (only RECONCILE ADD + review does that)
NO_MODEL_CHANGE   = valid, and recorded so it is visible
```

## 2. When to write it

When a session receipt is available, Steward invocations that run
`orient`, `build`, a `knowledge-query` operation, `knowledge-audit` or
`knowledge-proposal-check` write or update **one** companion query receipt per
session, beside the session receipt:

```text
<target-repo>/.sensemaking/receipts/<session_ref>.query.yaml
```

`session_ref` is the same value as the session's `sensemaking_session_receipt`.
Open it `in_progress` when those operations begin, append queries as they run,
and finalize it when the Steward responsibility ends (`state: final`,
`immutable: true`). If several modes run in one session (for example RECALL,
then RECONCILE), list them all in `modes`. Persistence follows the same rule as
the session receipt (`skills/using-sensemaking/references/session-receipt-v1.md`,
section 3). Commit and push require their respective authority; a local commit
does not prove the receipt has left the host. If it is neither committed nor
uploaded, record `working_tree_only` and disclose that it will not survive the
checkout.
Record earlier operations and results only as supported by available evidence;
disclose omissions rather than inventing them. `using-sensemaking` calls for a
session receipt in every session. If the host or authority prevents writing it,
report the limitation. Report decision-relevant gaps affecting the current
result in task output; when a query receipt is used, record qualifying misses
there too. Task output alone is not automatically counted by the receipt
summarizer across sessions. Consider durable knowledge changes separately under
existing review and authority rules.

## 3. Recording a miss (the required part)

Any query with `decision_relevant: true` and outcome `MISS` or `NOT_ASSESSED`
must have a `misses` entry referencing it (`RECEIPT_MISS_NOT_RECORDED`
otherwise). The entry states:

- `needed_for`: what the task needed that the model could not supply;
- `kind`: `NOT_ASSESSED` (the query contract reports the area as unmodeled) or
  `NO_MATCH_IN_SCOPE` (a literal search returned nothing; absence is not
  established);
- `resolved_by`: how the agent got the answer instead (for example
  `source inspection: CLAUDE.md:83-90`), or `null` if it never did;
- `follow_up`: `ADD_PROPOSED` (a reviewed-knowledge draft exists),
  `ADDED` (merged into `.sensemaking/knowledge/`), `NO_MODEL_CHANGE`
  (deliberately not modeled), or `DEFERRED`;
- `proposal_ref`: required for `ADD_PROPOSED` / `ADDED`; a repository-relative
  path to the draft or the knowledge file.

`PARTIAL` outcomes may also carry misses. A miss may not reference a `HIT` or
`NOT_APPLICABLE` query (`RECEIPT_MISS_QUERY_OUTCOME`).

## 4. Schema (all fields required unless marked nullable)

```yaml
artifact_id: semantic_query_receipt
schema_version: 1
session_ref: 2026-10-23-example            # same as the session receipt
state: in_progress | final
created_at: "2026-10-23T06:00:00Z"
updated_at: "2026-10-23T06:20:00Z"
target_repository: owner/repo
modes: [RECALL]                            # non-empty subset of RECALL, AUDIT, RECONCILE, BOOTSTRAP
decision: <=300 chars                      # the engineering decision the queries served
cli_identity:
  sensemaking_source_ref: <sha/version> | null
  invocation_prefix: <=200 chars           # e.g. "sensemaking-skills" or a pinned uv tool prefix
  version_output: <=120 chars | null
index:
  indexed_ref: <40-hex> | null             # null when no index existed
  current_head: <40-hex>
  worktree_clean: true | false
  uncommitted_changes_not_indexed: true | false
queries:                                   # >=1 required in RECALL mode
  - id: QY-1
    operation: orient | build | snapshot | search | explain | why | impact | workspace-impact | changes | contradictions | history | rules-for | term | orientation-summary | context-for | audit | proposal-check
    terms: ["literal phrase"]              # <=8, <=80 chars each; [] when not a search
    subject: <claim id, repository-relative path (rules-for, context-for), or term> | null
    expect_kinds: [alternative, architecture_rule] # only explain/why; v1/v2 kinds
    target_ref: <40-hex> | null
    result:
      hit_count: 0
      claim_ids: []                        # ids only, never claim text
      truncated: false
      not_assessed_kinds: []               # from bounded_coverage, when reported
    outcome: HIT | PARTIAL | MISS | NOT_ASSESSED | NOT_APPLICABLE
    decision_relevant: true | false
source_checks:                             # original sources opened to verify retrieved claims
  - claim_id: <id>
    sources: [<path:lines>]
    result: SUPPORTED | CONTRADICTED | STALE | NOT_CHECKED
misses:
  - id: M-1
    query_ref: QY-1
    needed_for: <=300 chars
    kind: NOT_ASSESSED | NO_MATCH_IN_SCOPE
    resolved_by: <=300 chars | null
    follow_up: ADD_PROPOSED | ADDED | NO_MODEL_CHANGE | DEFERRED
    proposal_ref: <repo-relative path> | null
reconcile:                                 # >=1 required in RECONCILE mode
  - claim_id: <id> | null                  # null only for NO_MODEL_CHANGE
    disposition: CONFIRM | REVISE | SUPERSEDE | ADD | CONTEST | NO_MODEL_CHANGE
    applied: true | false                  # false when only proposed (no knowledge_edit authority)
    proposal_ref: <repo-relative path> | null
    proposal_check: SEMANTIC_KNOWLEDGE_PROPOSAL_VALID | INVALID | NOT_RUN
persistence: pending | committed | working_tree_only | host_uploaded
action_authorized: false                   # must be false
semantic_truth_established: false          # must be false
immutable: false | true                    # true exactly when state is final
```

Field notes:

- `outcome: HIT` means the query answered what was asked, including a
  complete empty answer (for example `workspace-impact` on a clean HEAD).
  `PARTIAL` means some of what was needed came back, for example claims
  returned while an `--expect-kind` was NOT ASSESSED. Use `NOT_APPLICABLE` for
  `orient`, `build` and `proposal-check`, which retrieve nothing.
- `rules-for`, `term` and `orientation-summary` are existing architecture
  query operations. For `rules-for`, `subject` is one repository-relative file
  path (not a glob); for `term`, it is the literal term. `snapshot` and
  `orientation-summary` do not require a subject.
- `context-for` takes one repository-relative file path as `subject` or 2..8
  distinct paths via repeated CLI `--path` flags (not both). For a batch,
  record one `context-for` query receipt entry **per path** using that path
  as `subject`; batch union results do not establish cross-file authority.
  Set
  `result.claim_ids` to the IDs in the returned `claims` and `hit_count` to
  their count, and preserve `truncated`. For `context-for`, also inspect
  `context.envelope_reference_coverage`: the global claim/relation envelope
  may omit records referenced by individual context categories. Record a
  decision-relevant omission as `PARTIAL` or `NOT_ASSESSED` rather than a
  complete `HIT`; query receipts do not invent missing claim payloads. A path whose `ownership.coverage_status`
  is `NOT_ASSESSED` is never `outcome: HIT`: use `NOT_ASSESSED` or `PARTIAL`
  according to the `knowledge_gaps` that matter to the decision.
- For `rules-for` and `term`, set `result.claim_ids` to the IDs in the query
  envelope's returned `claims`, and `hit_count` to their count. Preserve the
  `truncated` indication; do not turn `coverage_status: NOT_ASSESSED` into
  `outcome: HIT` just because an isolated rule or neighbor was retrieved.
  Use `NOT_ASSESSED` or `PARTIAL` according to the decision's actual coverage,
  and record a miss when the outcome is decision-relevant.
- `snapshot` and `orientation-summary` return index-level summaries, not a
  bounded list of claim hits. Record `hit_count: 0`, `claim_ids: []` and
  `outcome: NOT_APPLICABLE` for them. For `orientation-summary`, mark
  `truncated: true` if `lines_omitted` is positive.
- `expect_kinds` accepts version-1 and version-2 claim kinds for `explain` and
  `why`, with the same one-hop coverage and NOT ASSESSED limits as before.
- `reconcile[].applied` says whether the disposition's change was written to
  `.sensemaking/knowledge/`. It is always `false` for `CONFIRM` and
  `NO_MODEL_CHANGE`, and `false` for a proposal that was drafted but not
  merged.

Do not record the SQLite database path: it is outside the checkout and
disposable by design. The pins (`indexed_ref`, `current_head`,
`cli_identity`) are what make a query reproducible.

## 5. How misses feed RECONCILE

When available, `scripts/summarize-receipts.py` lists misses recorded as
`ADD_PROPOSED` or `DEFERRED` in their original receipts and any subject or
term missed in **two or more sessions**. Those statuses are historical: the
reader does not reconcile later resolutions. Its JSON `pending_misses` field
retains its existing name and has the same historical meaning, disclosed in
`pending_misses_note`. During RECONCILE (`references/reconciliation.md`),
inspect relevant later receipts and current knowledge before treating a miss
as unresolved. A repeated miss is evidence that a source-linked ADD may be
warranted. It is not by itself proof, and not a quota.

## 6. Validate

When the optional validator is available:

```bash
python scripts/validate-receipt.py .sensemaking/receipts/<session_ref>.query.yaml --target-repo .
```
