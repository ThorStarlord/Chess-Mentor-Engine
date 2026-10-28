# coding-agent-native-campaign — run an approved agent-native campaign

Run an approved `coding_agent_native` campaign: the human approves in the
conversation, the coding agent performs every repository operation, a
Markdown file (`approval.md`) records the decision, and no external model
provider API is involved. On connector-native surfaces that cannot expose a
truthful platform conversation pointer, one agent-authored GitHub issue
comment may be created after approval solely as a durable audit locator.

## The one-word approval contract

> A standalone `approve` from the human authorizes the one and only
> campaign most recently presented in the active conversation, provided
> its digest has not changed. The coding agent records the complete
> authorization in `approval.md`.

`approve` is the human decision. `approval.md` is the agent-generated
receipt containing the precise meaning of that decision. The file is
**not** independent proof of human identity — the conversation is the
source of authority — but the runtime validates the receipt against the
exact campaign envelope before every step.

### The agent MUST refuse to record an approval when

- more than one campaign is pending;
- the campaign changed after it was presented;
- no campaign was presented;
- the policy digest cannot be resolved;
- `approve` appears inside a quotation, example, or hypothetical
  question (the word alone, standalone, is the decision);
- the campaign has already expired.

In those cases respond: `Approval is ambiguous: there are multiple or no
pending campaigns.` and execute nothing.

## When to use

The campaign policy declares:

```yaml
execution_mode: "coding_agent_native"
execution_surface: "current_coding_agent"
external_provider_api_prohibited: true
allowed_models: []
```

The human has replied with a standalone `approve` to the presented
envelope in THIS conversation.

**Approval and the execution window are separate gates.** The human's
`approve` may be given any time after the final envelope is presented and
before it expires. `approved_at` records the actual approval time: it may
precede `validity_window.not_before`, must not be in the future, and must
not exceed `validity_window.not_after`. The receipt is recorded
immediately. Execution is mechanically gated by the window: `prepare`
refuses until `validity_window.not_before`, and the agent executes
automatically inside the approved envelope once the window opens.

## Hard rules

- NEVER call an external model/provider API; the policy prohibits it and
  the envelope authorizes no external model.
- NEVER fabricate an approval: only a standalone `approve` from the
  human, for the exact presented envelope, may be recorded.
- NEVER fabricate a platform session/message identifier merely to satisfy
  the receipt schema.
- NEVER describe an agent-authored GitHub audit comment as human-authored
  consent or independent identity proof.
- NEVER modify the target checkout (read-only analysis).
- NEVER hide, retry, or repair an attempt: failed, validation-failed, and
  interrupted attempts are recorded and reported identically.
- Every result is `EXPLORATORY_NOT_CANONICAL_EVIDENCE`.
- Stop at the campaign's window end; the bookkeeping commands re-check
  the clock and re-validate the receipt before every step.

## Protocol

1. **Present the full envelope** in the conversation: campaign id,
   `policy_digest`, `maximum_attempts`, `concurrency`,
   `automatic_merge: prohibited`, `external_provider_api_prohibited:
   true`, classification, and the validity window. Confirm there is
   exactly one pending campaign and its digest is unchanged.
2. **The human replies with a standalone `approve`.** Nothing else
   counts (a reaction, a merge, silence, or `approve` inside a question
   or quote does not).
3. **Create a truthful audit locator and write `approval.md`** in the
   campaign package directory. Use exactly one reference form:

   - **Legacy conversation pointer:** only when the active execution surface
     actually exposes a concrete truthful `<session-id>#<message-id>`. Omit
     `reference_kind`; never infer or fabricate this value.
   - **Connector-native GitHub audit event:** when real platform conversation
     IDs are unavailable but the approved execution surface can write GitHub,
     add one top-level comment to the campaign tracking issue *after* the
     standalone `approve`. The comment must identify itself as an
     **agent-recorded conversation approval event**, transcribe the exact
     campaign id, exact presented policy digest, `approval_text: approve`, and
     approval timestamp, and explicitly say that it is an agent-authored
     durable audit locator rather than independent human-authored consent.
     Use the exact GitHub permalink returned for that comment with
     `reference_kind: agent_recorded_github_issue_comment`.

   Connector-native receipt shape:

   ```markdown
   ---
   approval_schema_version: "1"
   status: "approved"
   campaign_id: "EXP-0000-EXAMPLE"
   policy_digest: "<PRESENTED_DIGEST>"
   approval_source: "active_human_conversation"
   approval_text: "approve"
   approved_at: "<now, RFC3339>"
   maximum_attempts: 3
   concurrency: 1
   automatic_merge: "prohibited"
   external_provider_api_prohibited: true
   classification: "EXPLORATORY_NOT_CANONICAL_EVIDENCE"
   reference_kind: "agent_recorded_github_issue_comment"
   reference: "https://github.com/<owner>/<repo>/issues/<issue-number>#issuecomment-<comment-id>"
   ---

   The human approved the single pending campaign presented in the
   active conversation. The GitHub reference identifies an agent-recorded
   audit event; it is not independent proof of human identity.
   ```

   The frontmatter must be written with the exact values presented; the
   runtime validates every binding (campaign id, digest, limits, merge
   rule, external-provider prohibition, classification, window) before
   any step. `approved_at` is the actual approval timestamp (today, even
   if the execution window has not opened yet): it may be earlier than
   `validity_window.not_before`, must never be in the future, and must
   not exceed `validity_window.not_after`.

   For connector-native references, the verifier accepts only a concrete
   `https://github.com/<owner>/<repo>/issues/<positive-number>#issuecomment-<positive-id>`
   permalink with the explicit `reference_kind` above. A GitHub URL without
   that discriminator, a placeholder, other host, PR URL, missing comment
   fragment, zero id, or unknown reference kind fails closed. The verifier
   does not fetch the comment and does not treat it as identity proof.

4. **Validate the receipt immediately, window-independently:**

   ```bash
   python scripts/execution_infra/agent_native_campaign.py validate-approval \
       --package-dir experiments/campaigns/EXP-0002-stage1-auteur-coding-agent-pilot
   ```

   Expected: `APPROVAL_VALID <campaign_id> <policy_digest>
   window_independent=true reference=<audit-reference>`. The command
   verifies the receipt against the exact envelope WITHOUT requiring the
   execution window to be open and performs no reservation or invocation.
   The campaign is now `APPROVED_NOT_STARTED`; execution is scheduled for
   the valid window.

5. **Before the window opens, `prepare` refuses by design:**

   ```text
   REFUSED: ... validity window has not opened
   ```

   That refusal is the mechanical execution gate, not an error: no
   reservation, no ledger event, no attempt directory is created.
   Starting at `validity_window.not_before`, execute the attempts
   automatically inside the approved envelope (`prepare` / perform /
   `finalize`, exactly three serialized attempts, no hidden retries).
   Stop at the window end; the bookkeeping commands re-check the clock
   and re-validate the receipt before every step.

   ```bash
   python scripts/execution_infra/agent_native_campaign.py prepare \
       --package-dir experiments/campaigns/EXP-0002-stage1-auteur-coding-agent-pilot \
       --campaign-root <campaign-root> \
       --framework-checkout <pinned-framework-checkout> \
       --target-checkout-root <target-checkout-root> \
       --allowed-approver ThorStarlord
   ```

5. Read the frozen instructions at the printed `INSTRUCTIONS` path; they
   embed the pinned `repo-sensemaker/SKILL.md`, the read-only target
   checkout at the approved SHA, and the delivery path.
6. Perform `repo-sensemaker` yourself against the target checkout and
   write the Repository Sensemaking Brief to the delivery path.
7. `finalize` the attempt (re-validates the receipt + window, preserves
   raw output + artifact, validates, records the terminal state):

   ```bash
   python scripts/execution_infra/agent_native_campaign.py finalize \
       --package-dir experiments/campaigns/EXP-0002-stage1-auteur-coding-agent-pilot \
       --campaign-root <campaign-root> \
       --framework-checkout <pinned-framework-checkout> \
       --target-checkout-root <target-checkout-root> \
       --attempt-id <attempt-id> \
       --artifact <delivery-path> \
       --allowed-approver ThorStarlord
   ```

8. Repeat for the remaining slots (the ledger decides; the commands
   refuse when the budget is exhausted or an attempt is still active).
9. Render the complete report, commit every attempt directory + ledger +
   report on an isolated results branch, open ONE results PR with the
   nothing-omitted statement, and stop at
   `EXP_0002_RESULTS_PR_READY_FOR_INDEPENDENT_AUDIT` for the human's
   review. Never push to `main`; never merge the PR yourself.

## If anything refuses

A `REFUSED: ...` message means a precondition failed (receipt missing or
superseded, reference invalid, window closed, budget exhausted, injection
detected, drift). Record it and stop; never bypass the refusal by editing
the policy, receipt, or ledger files.
