# FPV-PILOT-002 Result

## Status

Outcome: Mixed.

This is an exploratory, participant-specific result from one participant. Five fresh positions received spontaneous pre-engine responses, and one previously exposed position was retained for C1/C2 context analysis only. No cross-participant validation or production conclusion follows.

## Participant evidence

P01's five responses are preserved verbatim in [participant-response.md](participants/P01/decision-reconstruction/participant-response.md). The evidence was frozen before the engine/context reveal. P01 recognized a concrete tactical idea in P002-02 and P002-04, reported a positional feature without a concrete plan in P002-03 and P002-05, and reported no satisfactory move in P002-01.

## Evidence completeness

All five fresh positions received responses. The responses did not provide every structured questionnaire field. Missing candidate sets, replies, continuations, confidence, reasoning categories, and original-game recollections are recorded as `NOT PROVIDED`; none were inferred or re-solicited. This limits causal and psychological interpretation.

## Position-by-position findings

### P002-01

- P01 noticed: No satisfactory move, in the recorded words: “I do not see any good moves”.
- Engine/context established: `28...Rxc2` produced a large deterioration from `-57` to `-609`; `28...Qf5` was the top candidate at the recorded depth.
- C3 added: The response establishes only that no satisfactory candidate was reported.
- Still unresolved: Whether P01 considered moves privately, why none was satisfactory, and whether the original-game decision used the same reasoning.

### P002-02

- P01 noticed: A pawn move `e5` creating a fork of bishop and knight.
- Engine/context established: `11.e5` was the engine-preferred move; the played `11.Bxd6` reduced White's advantage.
- C3 added: It directly shows that P01 reported the decisive tactical feature before reveal.
- Still unresolved: The candidate set, expected reply, calculation depth, and confidence.

### P002-03

- P01 noticed: Central tension and lack of a reported development plan.
- Engine/context established: The engine favored a dynamic kingside move, especially `10.g5`; `10.a3` gave up the small White edge at the recorded depth.
- C3 added: It separates reported feature recognition from the absence of a reported concrete candidate.
- Still unresolved: Whether P01 considered `g5`, saw a tactical issue, or chose `a3` for a specific reason.

### P002-04

- P01 noticed: A hanging knight and a rook capture.
- Engine/context established: `15.Rxe3` was the top engine move and preserved the large advantage.
- C3 added: It confirms successful recognition of the immediate tactical requirement.
- Still unresolved: The expected defensive reply and whether the tactic was calculated beyond the capture.

### P002-05

- P01 noticed: A missing g-pawn as a kingside target and uncertainty about implementation.
- Engine/context established: The structural target was real, but `17.f5` was the top candidate; `17.g4` worsened the evaluation.
- C3 added: It shows that a genuine strategic observation did not, in the recorded response, become a concrete move sequence.
- Still unresolved: Black's defensive resources as understood by P01 and the participant's candidate set.

## C1 findings

Annotation-level evidence established move quality, evaluation movement, and engine-preferred candidates. It supports objective statements such as “the played move was substantially worse at this search depth” or “the played move matched the top candidate.” It does not establish what P01 saw, considered, or intended.

## C2 findings

The Position Context Packet made the board geometry, material, side to move, and tactical/strategic features inspectable. It materially supported explanations of the fork in P002-02, the hanging knight in P002-04, the tactical urgency in P002-01, and the distinction between a kingside target and the immediate `f5` break in P002-05. Board context alone did not reveal why P01 selected a move or failed to select one.

FEN, ASCII board, piece map, and side to move were complementary rather than interchangeable for rapid inspection. Material was useful as orientation but was less decisive than legal geometry and dynamic threats. The full combination of candidates, evaluations, and PVs was more useful than PVs alone, but still required human/model reconstruction.

## C3 findings

Player Decision Evidence materially narrowed the interpretation in the five fresh positions:

- P002-02 and P002-04 provide direct evidence of successful recognition of the important tactical feature.
- P002-03 and P002-05 provide evidence of feature recognition without a recorded concrete implementation.
- P002-01 provides evidence only of no satisfactory move being reported.

C3 did not establish unique psychological causes. Sparse responses leave candidate-generation, verification, confidence, and original-game-recollection variables unresolved.

## Incremental information value

The information path was:

`C1` established objective move quality → `C2` explained the board mechanism and made the objective evidence more intelligible → `C3` connected that evidence to what P01 explicitly reported noticing.

C2 improved chess explanation but did not explain player choice. C3 added participant-grounded discrepancy information, especially by distinguishing tactical recognition from strategic implementation uncertainty. Its value was real but limited by response sparsity.

## Success/control comparison

The fresh set contains two successful tactical recognitions and three responses that did not report a matching concrete solution. This is consistent with a possible tactical-versus-strategic response difference, but five positions and incomplete structured fields are insufficient to establish a stable learner pattern. The controls demonstrate that selected positions can contain correct player reasoning; not every selected position is a failure case.

## Pilot 001 diagnosis re-evaluation

The Pilot 001 candidate diagnosis concerning under-verification of opponent resources remains unresolved, not confirmed. P002-02 and P002-04 show correct tactical recognition, while P002-01 and P002-05 leave verification details unreported. The direct evidence neither supports a general diagnosis nor rules it out.

## H1 result

Partially supported at exploratory level. Board context materially improved explanation of why several moves were good or bad relative to annotation-level evidence alone. This is one participant and one small position set.

## H2 result

Supported. Board context improved chess explanation but did not determine why P01 selected a move or reported no satisfactory move.

## H3 result

Partially supported. Direct Player Decision Evidence narrowed competing explanations by showing reported recognition or non-recognition of features, but sparse evidence prevented unique learner-level attribution.

## H4 result

Not supported as the overall description of this pilot, but not rejected generally. The added evidence produced meaningful incremental information in this exploratory run; whether that value justifies production complexity remains unestablished.

## Position Context Packet assessment

The packet addressed the original missing-context problem sufficiently for this small comparison. ASCII board and piece map reduced reconstruction burden; FEN preserved deterministic provenance; material aided orientation. Candidate moves and short PVs helped explain dynamic alternatives, but the packet did not automatically expose motifs such as attacked/defended relationships, pins, overloads, or forcing-move inventories.

## Remaining information gaps

- Exact candidate moves considered by P01.
- Expected opponent replies and continuations.
- Confidence and explicit reasoning category.
- Whether current reasoning matched the original game decision.
- Deterministic attacked/defended and forcing-move information that might reduce PV reconstruction.

These are evidence gaps exposed by the pilot, not production requirements.

## What was demonstrated

For one participant, authentic sparse reasoning could be frozen before reveal and compared against objective chess evidence. The comparison distinguished at least some successful tactical recognition from strategic feature recognition without a reported concrete implementation.

## What was suggested but not established

The findings suggest that direct player evidence can improve diagnostic specificity beyond board context alone, and that tactical and strategic responses may differ. Neither suggestion is validated across participants or tasks.

## What remains unknown

Whether the observed differences generalize, whether richer prompting would improve evidence without contamination, and whether the packet's added information justifies implementation complexity remain unknown.

## Product implications

Evidence-backed: preserve participant reasoning separately from engine evidence; treat missing fields as missing; make board state and provenance explicit when explaining chess evidence.

Hypothesis: deterministic attackers/defenders and forcing-move summaries may reduce reconstruction burden. This requires a separate experiment and is not a production-domain decision.

## Research implications

Future pilots should retain the freeze-before-reveal sequence, include controls, and predefine how sparse evidence is coded without prompting. A larger sample is required before testing the tactical-versus-strategic pattern or revisiting the Pilot 001 diagnosis.

## Claim ceiling

Exploratory and participant-specific. No claims of rating improvement, transfer, mastery, automated reliability, validated learner modeling, or production architecture are established.

## Recommended next experiment

Run a preregistered multi-participant replication with the same freeze/reveal separation, balanced tactical and strategic controls, and a separately tested deterministic context augmentation.
