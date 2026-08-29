# Chess Mentor Engine product discovery

Status: Working product definition

This pass narrows the first product question without pretending that the answers are proven. "Decided" means the current direction is specific enough to guide a validation test. "Working hypothesis" means the claim is strong enough to test but should not yet shape a permanent architecture. "Open question" means the repository does not have enough evidence to choose.

## 1. Product thesis

Chess Mentor Engine should help a player discover the recurring decision problems they cannot see in ordinary game review and choose what to practice next. Its distinguishing output is not an engine evaluation or a list of blunders. It is an evidence-backed, explicitly uncertain explanation of a player's repeated decisions.

The product must keep three questions separate:

```text
What is the best move?
Why is it the best move?
Why did this particular player fail to find it?
```

The first two questions belong primarily to objective chess analysis. The third is the product's main differentiation hypothesis. It may require chess evidence, player history, self-report, and pedagogical judgment, but it must not be presented as engine truth.

**Decided:** The first product definition will focus on recurring decision patterns and the next learning priority, not general chess analysis.

**Working hypothesis:** A persistent record of evidence and previous interventions can produce more useful teaching decisions than isolated post-game feedback.

## 2. Initial design customer

The recommended initial design customer is an online player rated approximately 1400-1800 who plays regularly, has enough games to review, and already uses engine analysis but still lacks a clear answer to "what should I work on next?"

This segment fits the thesis better than a broad all-rating product. These players usually have enough chess knowledge for a diagnosis about calculation, candidate moves, defensive resources, or decision discipline to be meaningful. They also tend to generate repeated decisions rather than only one-off introductory tactical errors. The range is still broad enough to find players with different goals and habits.

| Segment | Fit with the thesis | Current judgment |
| --- | --- | --- |
| Sub-1000 beginners | Many errors are likely to collapse into basic rules, legality, and tactical recognition. Longitudinal diagnosis may be useful later, but the first product could become a beginner course. | Rejected for the first design customer. |
| 1000-1400 developing players | They can produce useful recurring patterns, but simple tactical and chess-knowledge gaps may dominate the signal. The tutor would need to distinguish a process problem from missing fundamentals. | Plausible follow-on segment. |
| 1400-1800 intermediate online players | They are likely to have enough history, engine exposure, and vocabulary for a player-specific decision diagnosis to be understood and challenged. | Recommended initial design customer. |
| 1800-2200 advanced amateurs | Their decisions may support rich diagnoses, but the standard of evidence and explanation will be higher. The segment is smaller and may expect a level of coaching expertise that is expensive to validate. | Defer until the method is credible. |
| All ratings | Maximizes theoretical reach but hides major differences in knowledge, motivation, terminology, and error type. | Rejected for the first product definition. |

**Working hypothesis:** The segment should be tested rather than treated as a permanent rating gate. The important property is not the number itself. It is whether the player has enough recurring decisions, engine exposure, and motivation to evaluate a diagnosis.

## 3. Job To Be Done

When I have accumulated games and know that engine review alone is not giving me a clear training direction, help me find the recurring decision problem holding back my improvement, show me evidence from my own games, and tell me what to practice next.

The job has three parts:

- **Functional job:** Compare a player's decisions across games, identify a recurring pattern worth investigating, and recommend one focused intervention.
- **Emotional job:** Replace vague frustration and the feeling of "I keep doing this but do not know why" with a credible explanation the player can inspect and question.
- **Progress outcome:** Spend training time on a bottleneck that matters in the player's games, then see whether the decision improves in later attempts and games.

This is different from "analyze my chess games." Conventional analysis answers what happened in a position. The proposed tutor must help answer what keeps happening to this player and what to do about it.

**Decided:** The first product job is to make the next training priority understandable and evidence-based.

**Open question:** The relative importance of rating improvement, enjoyment, competitive performance, and general understanding will vary by player. The initial validation should measure the usefulness of the recommended priority before trying to optimize all of these outcomes.

## 4. First-value moment

The smallest credible first-value experience is a review of approximately 10 recent games, producing one cautious recurring-pattern diagnosis with concrete examples and one training recommendation.

The player should be able to say:

> This tutor noticed something about how I make decisions that my normal engine review did not show me, and I know what to try next.

The first experience should contain:

1. PGN import for a recent set of games.
2. Objective analysis of selected decision points.
3. A visible link from each claim to specific positions and moves.
4. A distinction between observed behavior and the explanation proposed for it.
5. One prioritized learning opportunity, not a dashboard of every possible weakness.
6. A way for the player to agree, disagree, or add context.

Five games may reveal a useful clue, but it is a weak basis for a recurring claim. Hundreds of games create cost and delay before the player has received value. Live tutoring and exercises before import test different products and should not be required for first value.

**Decided:** Test first value with a small recent game set, using 10 games as the starting target and allowing an explicit insufficient-evidence result.

**Working hypothesis:** A human or semi-manual analysis can produce the first useful insight before a mature learner model exists. The prototype should test the insight before the repository commits to an automated pipeline.

## 5. Core recurring tutoring loop

The persistent product loop is:

```text
recent games and player goals
        ↓
new objective chess evidence
        ↓
updated observations and competing hypotheses
        ↓
one current learning priority
        ↓
teaching or a focused exercise
        ↓
player attempt and response
        ↓
evidence of performance and transfer in later games
        ↓
revised learner understanding
```

The first meaningful product needs only a narrow version of this loop:

- import games;
- analyze selected decisions;
- form and explain one recurring-pattern hypothesis;
- recommend and record one intervention;
- preserve the evidence for later comparison.

Live play, a full curriculum, broad exercise generation, and a complete mastery system can wait. Persistence matters from the first slice because the product becomes a tutor only when a later analysis can refer to earlier evidence, instruction, and outcomes.

**Decided:** Persistence of evidence, diagnoses, player responses, and later comparison belongs inside the first validated product slice.

## 6. Differentiation

The relevant product categories answer different questions:

| Category | Strong at | Missing for this thesis |
| --- | --- | --- |
| Chess engine analysis | Objective evaluation, best moves, and variations | A persistent explanation of the player's recurring decision process |
| Automated post-game review | Fast detection and labeling of mistakes in one game | Cross-game recurrence and a justified next priority |
| Puzzle trainer | Repeated practice of known puzzle categories | Diagnosis of why this player fails in real decisions and whether practice transfers |
| Opening trainer | Repertoire memory and opening preparation | General decision patterns outside the opening |
| Static course | Structured instruction written for a broad audience | Selection and adaptation based on one player's evidence |
| LLM chess chatbot | Conversation and flexible explanation | Reliable objective chess grounding and longitudinal accountability |
| Human coach | Context, judgment, and adaptation | Cost, availability, and systematic evidence across a large game history |

Engine evaluation, blunder detection, best-move display, and generic tactical puzzles are commoditized inputs or adjacent features. The proposed differentiators are recurrence detection, a longitudinal player reasoning record, explicit competing hypotheses, evidence-backed priorities, intervention selection, and transfer tracking.

**Decided:** Chess Mentor Engine is differentiated by helping a player understand and change a recurring decision pattern through evidence from that player's own games.

## 7. Primary optimization target

**Decided primary target:** decision-process improvement.

The first product should optimize whether a player can recognize and handle the targeted decision situation more effectively after instruction. This target is closer to the product's causal contribution than rating, which is noisy and affected by opponents, time controls, volume, and form. It is more concrete than "understanding" while still allowing understanding to matter.

Secondary outcomes are:

- training efficiency, measured by whether the player can identify a useful next priority and spend less time on generic review;
- chess understanding, measured through the player's explanation and exercise responses;
- rating and game performance as delayed, noisy indicators;
- engagement and enjoyment as retention conditions, not the primary learning target.

**Working hypothesis:** If the product improves decision processes, rating and game performance may improve later, but the first experiment should not claim rating gains from a small sample.

## 8. Meaning of personalization

Personalization has levels:

0. Cosmetic personalization, such as name, rating, and openings.
1. Performance personalization, based on topics where results are weak.
2. Behavioral personalization, based on recurring decisions and process patterns.
3. Pedagogical personalization, where explanation and intervention change based on demonstrated misconceptions and prior learning history.
4. Longitudinal personalization, where the system tracks which interventions worked, whether learning transferred into real games, and how bottlenecks changed.

Levels 0 and 1 are useful context but do not establish the product thesis. Level 2 is the minimum meaningful product promise. A first validated slice should reach toward level 3 by adapting the recommended intervention to the evidence and the player's response. Level 4 is the longer-term reason to persist learner state, not a prerequisite for first value.

**Decided:** The product definition requires behavioral personalization and should test a limited form of pedagogical personalization. Cosmetic personalization is not a differentiator.

## 9. Evidence and epistemic discipline

The product should communicate claims in layers rather than flattening them into a label such as "you do not understand tactics."

```text
Player self-report
        ↓
System observation
        ↓
Diagnostic hypothesis
        ↓
Evidence-supported pattern
        ↓
Confirmed recurring weakness
        ↓
Improvement evidence
        ↓
Demonstrated transfer
```

These are product communication states, not source-code classes. The product must distinguish at least:

- **Fact:** The player lost more than 1.5 evaluation in 7 selected positions after initiating an attack.
- **Observation:** In 6 of those positions, the opponent had a forcing defensive resource that the player did not address.
- **Hypothesis:** The player may be committing before checking forcing replies.
- **Not established:** The player does not understand tactics.

A useful insight needs repeated evidence, concrete examples, an understandable causal hypothesis, explicit uncertainty, an actionable recommendation, and a clear separation between observation and interpretation. It should also mention relevant prior instruction or disagreement when that history exists.

**Decided:** The first product must show evidence and uncertainty alongside any diagnosis. It must be safe to say "insufficient evidence" or "two explanations remain plausible."

## 10. Minimum evidence horizon

The initial evidence horizon is a working range, not a statistical threshold.

- **One game:** enough for position-level feedback and self-reflection, not a recurring player claim.
- **Five games:** enough to generate a lead, but usually too little for a confident pattern unless the evidence is unusually consistent.
- **Ten games:** a credible starting point for a first hypothesis when the games contain relevant decisions and the selection is explained.
- **Twenty to thirty games:** stronger support for recurrence and variation across contexts. This is a reasonable follow-up horizon when the first pass is inconclusive.
- **Fifty or more games:** useful for longitudinal comparison, but not necessary before first value and likely too costly as an onboarding requirement.

The product should explicitly report insufficient evidence when games do not contain comparable decisions, analysis quality is poor, the pattern appears only once, or plausible explanations cannot be separated. More games do not automatically turn a weak observation into a diagnosis.

**Working hypothesis:** Ten recent games can support one initial diagnostic hypothesis for the proposed design customer. Twenty to thirty games may support a stronger recurring-pattern claim.

## 11. Initial product boundary

The first validated slice should include:

### Inputs

- PGN import for approximately 10 recent games;
- basic player context, including rating and time control where available;
- an optional stated improvement goal;
- optional player self-report about a suspected problem.

### Analysis

- deterministic chess analysis of selected decision points;
- extraction of comparable, significant decisions;
- manual or semi-manual grouping of recurring behavior;
- a diagnosis that labels observations, interpretation, uncertainty, and evidence.

### Output

- one prioritized recurring decision pattern or an explicit insufficient-evidence result;
- several concrete examples from the player's games;
- an explanation of why the pattern matters;
- one recommended training intervention;
- a way for the player to respond to the diagnosis.

### Persistence

- save the diagnosis and its supporting evidence;
- save the player's response and the chosen intervention;
- make later comparison possible without pretending to have a complete mastery model.

The slice should defer live play, a complete curriculum engine, a full mastery system, opening repertoire management, social features, rating prediction, a large course library, sophisticated UI, voice tutoring, tournament preparation, and a complete knowledge graph.

## 12. Explicit non-goals

The initial product will not replace Stockfish or another chess engine, become a general chess database, reproduce every feature of Chess.com or Lichess, generate large volumes of generic content, present model-generated chess judgments as objective truth, or implement a full training platform before the tutoring thesis is validated.

## 13. Falsifiable product hypothesis

Given 10-30 recent games from a motivated 1400-1800 online player, Chess Mentor Engine can identify at least one recurring decision pattern that the player recognizes as plausible and finds more actionable for choosing what to practice than a conventional engine mistake summary.

This claim fails if most outputs collapse into generic advice such as "practice tactics," if the evidence cannot support a meaningful pattern, if hypotheses are too speculative for players to trust, if players cannot understand the distinction between evidence and interpretation, or if the recommended intervention is no more useful than existing puzzle categories.

The longer-term thesis also weakens if persistent learner state does not materially improve later tutoring or if exercise success never produces evidence of transfer into real games.

## 14. First validation experiment

The detailed protocol is frozen in [docs/research/first-product-validation](../research/first-product-validation/README.md). It is designed, not run.

**Question:** Can a player-specific recurring-pattern insight guide a better next training decision than conventional engine review?

**Hypothesis:** Players in the proposed segment will prefer and better understand a cautious, evidence-backed diagnosis with one recommendation over a standard list of engine mistakes.

**Participants:** Six to eight online players approximately 1400-1800 who play regularly and already use engine analysis.

**Inputs:** Ten to thirty recent games per player, preferably from a consistent time control, plus rating, optional goal, and optional self-report.

**Process:** A researcher or coach creates a disposable analysis packet. The packet selects comparable decision points, records objective chess observations, groups repeated behavior, writes one or two competing explanations, and chooses one intervention. The player reviews the packet, explains what they believe it means, and chooses what they would practice next. The team does not automate the pipeline during this test.

**Baseline:** A conventional engine review containing move evaluations, blunder labels, and common category summaries.

**Experimental condition:** One evidence-backed recurring-pattern diagnosis with game examples, uncertainty, a player-response prompt, and one recommended intervention.

**Evaluation criteria:**

- Can the player restate the observed pattern without confusing it with the hypothesis?
- Does the player judge the insight as more specific and actionable than the baseline?
- Does the player choose the recommended priority or provide a credible reason to reject it?
- Can the researcher produce the packet without relying on unsupported causal claims?
- Do players report that the diagnosis changes what they would practice next?

**Failure conditions:** The diagnosis is generic, players cannot understand or trust it, the evidence selection is inconsistent, researchers disagree about the interpretation, or players choose existing generic advice as equally useful.

**Limitations:** The sample is small, manual analysis introduces researcher judgment, self-reported usefulness is not proof of learning, and the proposed rating segment may be wrong. The experiment tests whether the product insight is valuable enough to pursue. It does not validate automated chess analysis, mastery measurement, or rating improvement.

## 15. Decisions reached

- Use 1400-1800 regular online players as the initial design customer hypothesis.
- Define the first job as finding a recurring decision problem and choosing what to practice next.
- Test first value with about 10 recent games and permit an insufficient-evidence result.
- Optimize first for decision-process improvement, with understanding and training efficiency as secondary outcomes.
- Treat behavioral personalization as the minimum meaningful level and test a limited form of pedagogical personalization.
- Require evidence, uncertainty, and observation-versus-interpretation separation in the first insight.
- Include persistence of evidence and interventions in the first validated slice.
- Test the insight manually or semi-manually before automating the analysis pipeline.

## 16. Hypotheses still unresolved

- Whether 1400-1800 is the best initial segment compared with 1000-1400.
- Whether players will trust a diagnosis that competes with their own explanation of a move.
- Which decision patterns can be identified reliably from game records.
- How much analysis is needed to distinguish process failure from knowledge, attention, time, or execution failure.
- Whether one intervention is enough to create a useful first experience.
- How to measure decision-process improvement and transfer without overclaiming causality.
- Whether player goals should alter the priority ranking from the first version.
- Which parts of the tutor need a model and which can remain deterministic or human-authored.

## 17. Consequences for future domain modeling

Future domain modeling should start with the evidence chain around a decision, not with a complete taxonomy of chess skills. The first questions are how to represent a player decision, objective analysis evidence, a repeated observation, a competing diagnostic hypothesis, an intervention, a player response, and later transfer evidence.

The model should preserve the difference between a position-level chess error and a player-level pedagogical claim. It should support uncertainty and competing explanations. It should also record provenance so that a player or researcher can inspect why a pattern was proposed and what later evidence changed it.

Terms such as weakness, misconception, mastery, skill, and learner profile remain useful discovery language, but they should not become production objects until the validation experiment and domain modeling establish their boundaries.
