# .sensemaking — agent knowledge layer

Reusable, source-grounded understanding of Chess Mentor Engine for later
agent sessions. **This is not repository authority.** Under the documentation
governance in `CONTEXT.md`, accepted decisions, qualified state and runbooks
live in `docs/`, `CONTEXT.md` and `STATUS.md`; nothing here is a roadmap,
backlog or approved decision.

| Path | What it holds |
| --- | --- |
| `knowledge/domain.json` | Goals, non-goals, domain concepts, invariants, governance constraints |
| `knowledge/architecture.json` | Layers, components (with owned paths), capabilities, ADR 0001-0012 decisions, architecture rules |
| `knowledge/observations-and-possibilities.json` | Observed findings at a pinned commit, retained product possibilities (`poss:`), shared premises (`hyp:`) |
| `analyses/strategic_repository_analysis.md` | First strategic analysis (`SRA-2026-10-28-cme-bootstrap`): frontier, paths, recommendation |
| `receipts/` | Per-session receipts: what each session did, where it stopped, what stays open |

## Status of these records

- Built at `afbdf775356483f08a5ea979b34dbb36cbafb2f3` by session
  `2026-10-28-repository-bootstrap`.
- All records carry `review_status: unvalidated_draft`. The Sensemaking CLI
  (`knowledge-proposal-check`) could not be installed in that session, so the
  records were only checked for JSON shape, unique ids, resolvable file
  references and relation targets.
- Before relying on an `observed` claim, re-check its cited file at the current
  revision; observations are pinned to the commit above.

## Fast orientation for a new session

1. Read `CONTEXT.md` (authority graph and contracts) and `STATUS.md`.
2. Read the analysis summary (sections 2, 4 and 9) for what is operable vs
   library-only.
3. Key distinctions that are easy to miss:
   - the learner layers M6-M46 are mostly Python APIs; persisted kinds are
     analysis, diagnostic queues, tutor sessions, prompts, observations and
     review ledgers;
   - M40/M44 refuse a learner with no active M7 hypothesis, so
     `cme-local-tutor start|next` need prior learner state; baseline capture
     for a new learner goes through `cme-candidate-tutor` and
     `cme-local-tutor review`;
   - no LLM provider ships; M19 is a protocol.
