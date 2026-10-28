# Strategic repository analysis — 2026-10-28

**Artifact:** `strategic_repository_analysis` (agent-authored, provisional)
**Target:** `thorstarlord/chess-mentor-engine` at `16c38160db3793947f3e6d24f6c4bdd89cbd63fd`
**Method:** `using-sensemaking` first engagement (Steward BOOTSTRAP, then possibility exploration)
**Authority:** This is evidence. It is not a product decision, a roadmap entry or an implementation authorization. Under the `CONTEXT.md` documentation-governance rule it is exploratory context, not repository authority.

## 1. What the repository is

Chess Mentor Engine (CME) is a pure-Python (≥3.11, zero runtime dependencies), local, CLI-first engine for building a persistent, participant-specific chess learner model. Its main design commitment is a strict separation of authority layers:

```text
objective chess evidence (M1-M4, M14-M18)
  -> participant evidence frozen before reveal (M5/M8)
  -> position-local discrepancy (M6) -> learner hypothesis + recurrence (M7/M7C)
  -> intervention selection (M9) -> outcome/transfer evidence (M10) -> longitudinal state (M11)
  -> read/synthesize/propose layers with no mutation authority (K0-K7, M36-M46)
  -> V1 local composition (cme-local-tutor) -> post-V1 descriptive product-use observation
```

Scale: about 43k lines of source and more than 90 test modules (974 tests passed on the PR #98 head). It has 12 accepted ADRs and 9 installed CLIs. It ships its own chess rules core (ADR 0001), takes Stockfish as a supplied UCI executable, uses SQLite content-addressed artifacts with replay verification, and defines a model-coaching provider Protocol but ships no concrete provider.

Governing intent: `README.md`, `STATUS.md`, `CONTEXT.md` and `docs/product/repository-build-status.md` agree. V1 is repository-ready and the post-V1 observation package is integrated. **The next evidence must come from real repeated local use**, and no further repository package is justified solely by architectural possibility. Efficacy, learning effect and mastery stay `not_established`.

External evidence on record: FPV-PILOT-001 found that the analysis was "not helpful" because it lacked board context. FPV-PILOT-002 found that board context helped explanation and that frozen pre-reveal reasoning narrowed the interpretation. Both pilots had N=1 and were exploratory. PILOT-003 and PILOT-004 are designed and frozen but not executed; PILOT-004 B01 is awaiting P01's responses.

Durable records: `.sensemaking/knowledge/domain.json`, `architecture.json` and `possibilities.json`.

## 2. Decisive finding

The governing next step ("collect repeated local use") depends on a path that, as observed in source and in a probe of the installed commands, a real learner cannot complete from their own games:

- `cme-local-tutor start` requires `--learner-progress-json` (a strict-codec M44 `LearnerProgressView`), `--protocol-json` and `--prompts-json` (`src/chess_mentor_engine/local_tutor_cli.py`).
- None of the nine installed commands emits an M44 view, a capture protocol or prompt definitions. `build_learner_progress_view` exists only as a Python API (`learner_intelligence/progress_model.py`).
- The guided-review tests construct M8 sessions programmatically from synthetic fixtures and never go through `start` on a real PGN (`tests/test_local_tutor_guided_baseline.py`).
- Inferred, not run: a first-time learner has no M7 hypotheses, so cold-start M44/M45 inputs may be empty or fail closed.
- Even when the path succeeds, `review` stops at baseline freeze, so the participant gets no chess feedback from that command. A low `would_review_again` score could then measure that boundary rather than product value.

The finding is consistent with the empty observation record: there is no recorded post-V1 use. The repository has qualified each layer, but the evidence-collection loop it is waiting on cannot start without operator-level Python work.

## 3. Possibility landscape

| Possibility | Fit with governing intent | Notes |
| --- | --- | --- |
| `poss:cold-start-local-session`: PGN plus engine to a consented, frozen baseline in one command | **High**. It is a precondition for the evidence the owner asked for | It reuses `cme diagnose`, M45 and M23/M8, and would need a defined cold-start M44 view (or a bypass) plus default protocol and prompts. Change surface is new composition only |
| `poss:closed-loop-review-payoff`: continue past freeze into reveal with board context and a deterministic grounded explanation | High | The M8 reveal/compare/explain transitions already exist. Pilot 001's negative result was exactly about the missing payoff and context |
| `poss:execute-frozen-pilots`: run PILOT-004 B01 with P01 | High, and cheapest | Needs no code, but participant time is an external dependency. It also does not exercise the software path |
| `poss:deterministic-tactical-context`: attacked/defended and forcing-move summaries | Medium | Pilot 002 hypothesis. K detectors may already partly cover it (not assessed) |
| `poss:concrete-model-provider` | Medium | Introduces vendor, privacy and provider-policy questions the repository explicitly defers |
| `poss:game-import` (Lichess/Chess.com) | Medium | Removes PGN friction. A network dependency departs from the zero-dependency local posture |
| `poss:surface-consolidation`: one learner-facing workflow over nine CLIs | Medium | Simplification counterfactual. Could be combined with cold-start |
| `poss:browser-or-hosted`, `poss:new-learner-intelligence-layer` | Low | Explicitly deferred by governing decision |

Counterfactual considered: *stop building and only run studies* (manual pilots as in 001/002). This yields evidence about the thesis but not about the software. The governing post-V1 decision specifically asks for evidence from using the product, so this does not replace a working local path.

Areas not assessed: K0-K7 detector depth and quality; M19-M34 reviewed-coaching internals; correctness of the M41-M46 policies; CI workflow details; whether a cold-start M44 view is constructible (it was not executed); performance with real engines (no Stockfish in this environment).

## 4. Disposition

**OWNER_DECISION**, with a recommendation.

Recommendation: authorize one bounded objective, a **cold-start local session**. That means a single installed command that takes a learner's PGN and a supplied engine to a consented, frozen M8 baseline using default protocol and prompts, with no hand-built structural JSON. Optionally, the same objective could continue through the existing M8 reveal path with board context, so each session returns something to the learner. It would reuse existing authority owners, add no new learner-intelligence authority, and keep the current claim ceiling.

Why it beats the alternatives: it is the smallest change that makes the owner's own evidence-first decision executable. Every other credible direction either depends on that use evidence (consolidation, provider, tactical context) or is explicitly deferred (UI, hosted, new layers). Running PILOT-004 is complementary, not a substitute.

Why this is an owner decision and not an agent build: `STATUS.md` reserves "authorize one bounded next objective" for after real observations are reconciled. Whether this onboarding gap counts as the "demonstrated bottleneck" (it was shown by a source probe, not by learner use) is the owner's call.

What would change this recommendation:

- an existing operator path that produces M44, protocol and prompt JSON, which this analysis missed;
- owner intent that local use is operator-mediated by design, so hand-built inputs are acceptable;
- PILOT-004 results that redirect product scope.
