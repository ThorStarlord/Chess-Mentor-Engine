# FPV-PILOT-001 result

## Status

Pilot result recorded from one real participant. Structured questionnaire completion is incomplete, the independent reviewer assessment is pending, and the pilot is not a validation of the product thesis across the target segment.

Outcome category: **Mixed**

## Participant feedback

P01 said the analysis was not helpful and identified missing board context as the main problem. The complete qualitative record is in [participant-feedback.md](participants/P01/evaluation/participant-feedback.md).

P01's feedback is a negative usefulness finding. It does not supply numeric ratings for the frozen questionnaire dimensions and must not be represented as a completed A/B preference.

## What the pilot demonstrated

- The supplied PGN contained objective move-evaluation annotations that could support a traceable candidate pattern.
- A candidate pattern could be described across human Standard, AI Standard, and AI From Position strata without pooling them into one count.
- The dataset's heterogeneity materially limited claims about ordinary competitive human rapid play.
- A participant can reject the usefulness of a diagnosis because the report does not make the underlying position understandable.
- Engine verdicts, move labels, and principal variations are not automatically pedagogically usable context.

## What the pilot failed to demonstrate

- It did not demonstrate that the candidate recurring pattern is a proven weakness or cognitive cause.
- It did not demonstrate that the diagnosis generalizes across P01's human games, all positions, or the 1400-1800 segment.
- It did not demonstrate that the recommended intervention is useful or effective.
- It did not demonstrate clean blinded preference because P01 saw recognizable diagnostic content before evaluation.
- It did not demonstrate rating improvement, learning transfer, automated diagnosis reliability, or a validated learner model.

## Evidence-representation limitation

The pilot moved from engine annotations and selected alternatives to a learner-level diagnosis without supplying enough explicit board-state context for P01 to understand or judge the explanation. The participant's response suggests that the evidence interface, not only the diagnosis wording, was under-specified.

## Board-context limitation

P01 could not adequately judge the recurring-pattern analysis from engine verdicts and selected move annotations alone because the reports did not reconstruct enough of the underlying board context. A principal variation describes a dynamic continuation, but it does not guarantee that the reader can see the spatial relationships that make the move important.

This is a product-relevant negative result, not a formatting preference.

## Cognitive-inference limitation

Even complete board context would not establish why P01 chose a move. The same objective error could reflect failure to see a reply, incorrect evaluation of a seen reply, attention, time pressure, position-specific knowledge, or one-off execution. Pilot 001 did not collect pre-engine player reasoning, so it could not distinguish these explanations.

## Blinding limitation

The pre-evaluation exposure was recorded as D-001. P01's later feedback remains useful for usefulness, explanatory value, actionability, trust, novelty, specificity, evidence credibility, and qualitative criticism. It cannot support a clean blinded-condition preference claim.

## Pilot hypothesis result

The pilot generated a traceable candidate pattern, but P01 did not find the resulting analysis helpful because the evidence presentation lacked sufficient board context. The most defensible result is **Mixed**. The pilot shows a possible product signal while failing to establish that the current evidence representation can deliver useful tutoring diagnosis.

## Claim ceiling

The result is participant-specific and exploratory. It does not establish that a recurring-player diagnosis is useful in general, that the candidate pattern is real outside this dataset, or that richer context will solve the problem. It does not validate a production architecture.

## Operational lessons

- Do not expose diagnostic summaries before participant evaluation.
- Preserve the full board state in any future position-level evidence packet.
- Collect player reasoning before revealing engine conclusions where practical.
- Keep objective chess evidence, player decision evidence, and learner-level hypotheses separate.
- Stratify human, AI, Standard, and From Position evidence.

## Product implications

A candidate research concept is a **Position Context Packet** that gives a reasoning system or participant an explicit board representation alongside engine evidence. This is not a production domain object or architecture decision.

## Consequences for next research

Pilot 002 should compare annotation-only evidence with explicit board context and with board context plus pre-engine player decision evidence. It should test whether each added evidence level improves explanation, diagnosis defensibility, and actionability.

