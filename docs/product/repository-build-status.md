# Chess Mentor Engine — Current Build Status

**Status authority:** current implementation and qualification boundary.  
**Current implementation boundary:** M19 — Provenance-Bound Mentor Coaching, PR #51.  
**Merged baseline before M19:** `00bab82dc963bff005c9753b498f1e50a8c513d4` (M18 merge).  

This file is the concise moving authority for repository state. Historical
qualification details remain in feature PRs, ADRs, architecture records, runbooks,
and Git history. Software qualification is not empirical tutoring efficacy.

## Milestone board

```text
M1  - Trustworthy Chess Evidence Substrate       QUALIFIED
M2  - Deterministic Chess Feature Extraction     QUALIFIED
M3  - Engine Evidence                            QUALIFIED
M4  - Diagnostic Position Selection              QUALIFIED
M5  - Player Decision Evidence                   QUALIFIED
M6  - Reasoning Discrepancy                      QUALIFIED
M7  - Learner Hypothesis Ledger / M7Q            QUALIFIED
M8  - Evidence-Aware Tutor Session               QUALIFIED
M9  - Training Intervention Registry             QUALIFIED
M10 - Bounded Outcome / Transfer Evidence        QUALIFIED - MERGED PR #41
M11 - Longitudinal Learner State                 QUALIFIED - MERGED PR #43
M12 - Local Evidence CLI                         QUALIFIED - MERGED PR #44
M13 - Persistent Tutor Session CLI               QUALIFIED - MERGED PR #45
M14 - Engine-Backed Analysis CLI                 QUALIFIED - MERGED PR #46
M15 - Evaluation Presentation Contract           QUALIFIED - MERGED PR #47
M16 - Grounded Mentor Feedback Composer          QUALIFIED - MERGED PR #48
M17 - Analysis-to-Presentation CLI Bridge         QUALIFIED - MERGED PR #49
M18 - Diagnostic Move-Analysis Queue             QUALIFIED - MERGED PR #50
M19 - Provenance-Bound Mentor Coaching           CURRENT CANDIDATE - PR #51
```

Supporting repairs/capabilities remain part of this baseline:

```text
UCI evidence contract repair / provider 0.2      MERGED - PR #39
Durable artifacts + verified M8 replay           MERGED - PR #40
Post-M10 documentation consolidation             MERGED - PR #42
```

## Recent promotion provenance

| Milestone | Qualified/final head | Merged commit | Qualification |
| --- | --- | --- | --- |
| M14 / PR #46 | `c2e1ded12ae3dd40402c67ddb713db7f6c38fdbc` | `6112b3a970c3b2a4b10b58a6cb3b438d332e605e` | run `34411793232`: 554 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M15 / PR #47 | `275bafceb949fc564b80a5f0b09b062514d7602c` | `c93faf74cb1d7b54d05853cd4775a57c725cfc7b` | run `34412807819`: 566 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M16 / PR #48 | `44314e9de8be5c17d7357849568fa2d3816bc387` | `ec48032c5866461b767697dc20df0c8b6b945b3b` | run `34413803156`: 577 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M17 / PR #49 | `c91ffa33a0797e0894f1f2dc519600be39f6afcc` | `4672a2b5dc34cae736be8e260f439afe6acfb1e6` | run `34435288183`: 582 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |
| M18 / PR #50 | `65297abd366bf092a60ed4fa202e2e51bb1950cd` | `00bab82dc963bff005c9753b498f1e50a8c513d4` | run `34436086912`: 589 passed, 8 intentional skips, Ruff PASS, Stockfish 8/8 PASS |

PR #51 and Git history are authoritative for the exact M19 final candidate head,
qualification run, and eventual merge provenance. Any candidate-head change requires
a fresh full CI and independent Stockfish pass before merge.

## Current evidence path

```text
PGN / canonical position
-> deterministic chess context
-> provenance-bound engine evidence
-> objective played-decision comparison / bounded diagnostic selection
-> deterministic evaluation presentation projection
-> frozen participant decision evidence
-> position-local reasoning discrepancy
-> participant-specific hypothesis + contradiction/challenge evidence
-> controlled evidence-aware tutor session
-> deterministic grounded session-local mentor feedback
-> provenance-bound model language rendering
-> explicit training applicability / selected | ineligible | unclear
-> predeclared outcome protocol
-> practice / near / far / real-game outcome evidence
-> append-only longitudinal learner state
```

Every arrow remains an authority boundary. M19 adds a model-authored language layer;
it does not make the model a source of objective chess truth, M6/M7 learner truth,
training authority, or outcome evidence.

## Current product surfaces

### M12-M13 — Local evidence and persistent tutor CLI

The installed `cme` command provides deterministic PGN/position inspection,
participant-scoped artifact reads, and replay-verified append-only M8 tutor
transitions. M13 does not generate explanation text; `cme tutor explain` records
explicitly supplied text and provenance.

See the M12 and M13 runbooks for command-level details.

### M14-M17 — Engine analysis and presentation

M14 adds bounded external-UCI analysis through:

```text
cme analyze <pgn> --ply-index N --engine <uci> ...
```

M17 adds the opt-in `--with-presentation` bridge. The exact in-memory M3 root
analysis, optional played-child analysis, and native M4 comparison are passed to the
qualified M15 projector before optional archival. M15 preserves canonical White
scores, decision-mover projection, bound direction, symbolic mate, partial/failure
states, engine identity, and exact evidence references.

Optional M14 archival still stores only `m14.analysis-package.v1`. A M15 integrity
failure exits before archival.

### M18 — Diagnostic move-analysis queue

M18 adds:

```text
cme diagnose <pgn> --policy <selection-policy.json> --engine <uci> ...
```

The command analyzes one selected game over an explicit inclusive played-ply window,
derives M4C objective signals, applies an explicit versioned M4D `SelectionPolicy`,
and produces the native deterministic `DiagnosticCandidateBatch` plus its complete
auditable source pool.

M18 does not embed universal move-quality thresholds. Failed, partial, bounded, or
incompatible engine evidence remains explicit; the workflow does not invent an exact
score or silently weaken policy to fill a batch. See the
[M18 runbook](../runbooks/m18-diagnostic-analysis-queue.md).

### M16 — Deterministic grounded mentor feedback

M16 remains the deterministic factual grounding ceiling for mentor language:

```text
chess_mentor_engine.feedback.compose_grounded_mentor_feedback
chess_mentor_engine.feedback.record_grounded_mentor_feedback
```

It requires an exact M8 session in `compared` state and exact M3/M4 evidence already
bound into the M6 reasoning context and objective reveal. It rebuilds M15, preserves
every M6 assertion, optionally preserves complete active-current M7 context, and
keeps non-exact evidence non-exact.

M16 may record its deterministic template output through M8 with
`actor_kind=template`. It does not invoke a model.

### M19 — Provenance-bound model coaching

M19 introduces `chess_mentor_engine.coaching` with:

```text
build_model_coaching_request
bind_model_coaching_response
record_model_coaching_response
run_model_coaching
ModelCoachingGeneration
ModelCoachProvider
```

`build_model_coaching_request` first recomputes the exact M16 grounded feedback. The
M19 request is then content-addressed over the current tutor snapshot, exact M16
record, and a versioned instruction ceiling that restricts the model to language
rendering, Socratic reflection, and explanation of existing evidence/uncertainty.

A provider result may contain only request identity/fingerprint echo, prose,
provider/model identity, provider run ID, and generation time. It cannot submit new
M3/M4/M6/M7/M9 structures through the M19 generation contract.

Before recording, M19 revalidates request shape/identity, exact instruction contract,
recomputed M16 grounding, request echo, and chronology. Accepted prose is recorded
through the existing M8 explanation transition with:

```text
actor_kind = model
actor_id = <provider_id>:<model_id>
actor_version = <model_version>
instruction_fingerprint = exact M19 instruction fingerprint
run_id = provider run ID
```

The M19 coaching record deliberately states:

```text
grounding_status = request_bound_not_semantically_verified
claim_scope = session_local_model_rendering
```

This is important: provenance binding proves which evidence and instructions were
supplied to which model run. It does **not** prove that model prose is factually
correct, pedagogically optimal, or effective. Production provider/transport choice
remains deferred. See the
[M19 runbook](../runbooks/m19-provenance-bound-model-coaching.md).

## Qualification commands

Focused current product surface:

```bash
python -m pytest tests/test_m11_qualification.py
python -m pytest tests/test_m12_cli.py
python -m pytest tests/test_m13_persistent_tutor_cli.py
python -m pytest tests/test_m14_engine_analysis_cli.py
python -m pytest tests/test_m15_evaluation_presentation.py
python -m pytest tests/test_m16_grounded_mentor_feedback.py
python -m pytest tests/test_m17_analysis_presentation_bridge.py
python -m pytest tests/test_m18_diagnostic_analysis_queue.py
python -m pytest tests/test_m19_provenance_bound_model_coaching.py
```

Engine/comparison contracts:

```bash
python -m pytest tests/test_uci_provider.py tests/test_uci_evidence_contract.py
python -m pytest tests/test_decision_comparison.py
```

Full merge gate:

```bash
python -m pytest -rs
python -m ruff check .
python -m compileall -q src tests
python -m pytest tests/integration/test_stockfish_uci.py -rs
```

The final command requires `STOCKFISH_EXECUTABLE`; skips are not an independent
engine pass. CI runs Python 3.11 native tests/lint plus a separate external Stockfish
witness. No standalone static type checker is configured.

## Current claim ceiling

The repository now has qualified deterministic chess/evidence contracts, persistent
bounded tutor state, a diagnostic analysis queue, deterministic grounded feedback,
and a provider-neutral model-language boundary with exact request/model provenance.
It still does **not** claim:

- causal cognitive diagnosis or permanent learner traits;
- optimal/effective intervention selection;
- intervention-caused improvement or automatic mastery;
- universal engine-evaluation or move-quality thresholds;
- globally complete exposure history;
- automatic M6 diagnosis generation from engine output;
- automatic M7/M11 mutation from tutor, analysis, or model-coaching calls;
- semantic correctness, safety, or pedagogical quality of arbitrary model prose;
- a production LLM provider, provider transport, retry/rate-limit policy, or secrets
  architecture;
- a web UI, authenticated hosted service, or production multi-user persistence;
- empirical tutoring efficacy.

M16 remains the deterministic grounding ceiling. M19 proves that model-authored
language can be request-bound, provenance-bearing, and isolated from upstream
structured authority; it does not certify the language itself.
