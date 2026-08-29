# First product-validation experiment protocol

Status: Frozen for the first run. Not executed.

Protocol version: 1.0

## Research question

Does an evidence-backed recurring decision-pattern diagnosis better answer "what is repeatedly holding back my chess decisions, and what should I work on next?" than a competent conventional game review?

The study separately evaluates usefulness, actionability, explanatory power, trust, novelty, specificity, evidence quality, and diagnostic plausibility. It is not a general satisfaction test.

## Product claim being tested

Given a meaningful sample of a player's recent games, Chess Mentor Engine can identify at least one recurring decision-making pattern that the player finds more actionable and explanatory for choosing what to practice than conventional engine-centered game review.

The claim must be able to fail. A fluent report, participant enthusiasm, or analyst confidence does not establish the claim by itself.

## Participants

Plan for 6-8 participants. The intended design customer is a regular online player approximately rated 1400-1800 in rapid or classical-strength games.

Include participants who:

- actively play online chess;
- want to improve;
- can provide 10-30 recent games;
- have enough serious games for comparable decisions to appear;
- understand ordinary chess analysis terms;
- already use, or have used, engine analysis.

Exclude a participant from the primary comparison if their available set is dominated by bullet games, contains too little history, or includes known anomalies that materially invalidate deliberate decision analysis. Record the reason. Do not over-screen for a statistically uniform sample.

This is a product-discovery sample, not a representative population.

## Experimental unit and evidence horizon

The primary unit is one participant plus one frozen game set. The same underlying games must feed both comparison conditions. Freeze the game set before either report is written.

Use approximately 10 games as the minimum exploratory sample and prefer 20-30 when available. These are practical discovery ranges, not statistically justified thresholds.

Use these qualitative evidence states:

- **Insufficient evidence:** fewer than two coherent supporting instances, poor comparability, or unresolved explanations that prevent a responsible pattern claim.
- **Candidate pattern:** at least two potentially related instances, but important alternative explanations or evidence gaps remain.
- **Supported pattern:** at least three comparable instances, concrete examples, a coherent relationship, and an actionable intervention, with no simpler explanation that currently accounts for the evidence better.
- **Strongly supported pattern:** repeated comparable evidence across contexts, meaningful contradictory evidence reviewed, and a pattern that a second reviewer can understand and substantially reproduce.

The analyst may return insufficient evidence. They must not invent a diagnosis to complete a report.

## Comparison conditions

### Condition A, conventional review baseline

Condition A approximates a competent conventional post-game analysis experience. It may include significant engine mistakes, best-move alternatives, tactical or strategic themes, conventional recurring categories, and generic practice recommendations.

It must not be deliberately weak. It should answer where the player lost evaluation, what chess concepts appear relevant, and what conventional training advice follows. It should avoid the distinctive longitudinal cognitive framing of Condition B.

### Condition B, recurring-pattern diagnostic

Condition B attempts to identify at most one high-priority recurring decision pattern. It must separate these layers:

1. **Objective evidence:** what occurred in the games.
2. **Behavioral pattern:** what observable decision tendency may recur.
3. **Diagnostic hypothesis:** what possible explanation may account for the pattern.
4. **Training intervention:** what bounded behavior the player should practice next.

The report must label uncertainty and include supporting positions. It must include at least one serious competing explanation where relevant and summarize important contradictory evidence.

## Analyst procedure

1. Assign an anonymous participant ID and game-set ID.
2. Freeze the participant's game set, metadata, and analysis settings.
3. Identify meaningful decision points without selecting only positions that fit a hoped-for diagnosis.
4. Record objective chess evidence for each selected point.
5. Group superficially similar errors and record why each point belongs in a group.
6. Search for repeated decision-process patterns, while considering simpler explanations such as time pressure, missing chess knowledge, or execution failure.
7. Record candidate and rejected patterns, including reasons for rejection.
8. Actively search for contradictory examples.
9. Select at most one primary diagnostic hypothesis, or report insufficient evidence.
10. Record the evidence state, competing explanations, and a bounded intervention.
11. Produce Condition A and Condition B using the same frozen game evidence.
12. Freeze both outputs before participant evaluation.
13. Prepare blinded copies labeled only Analysis A and Analysis B.

Do not use centipawn loss as a direct proxy for pedagogical importance. Do not use hindsight to claim that a move reveals a stable cognitive cause. Record engine output as chess evidence, not learner psychology.

## Epistemic rules

Every Condition B report must distinguish:

```text
fact
observation
pattern
hypothesis
intervention
```

Use calibrated language such as "suggests," "appears consistent with," "working hypothesis," and "insufficient evidence." Repeated correlation is not a proven cognitive cause.

## Blinding and presentation

Present reports as Analysis A and Analysis B. Randomize presentation order across participants when practical. Do not reveal which report represents the recurring-pattern product hypothesis until comparison responses are recorded.

Participant blinding is partial. Participants may infer the purpose from the report style, and analysts cannot be blind to the condition they write. Record any failure of presentation blinding. The fixed game set and frozen outputs provide the main control against unequal source evidence and post-response changes.

## Participant evaluation

After reading both reports, participants complete the questionnaire in [participant-evaluation.md](participant-evaluation.md). Ask separately about explanatory value, actionability, trust, novelty, specificity, and usefulness. Do not reduce responses to one weighted composite score.

The key outcome question is:

> If you had only one of these analyses to decide how to spend your next three hours of chess practice, which would you choose and why?

## Researcher evaluation

At least one analyst or reviewer assesses Condition B for factual accuracy, genuine recurrence, evidence quality, calibration, consideration of contradictory evidence, logical connection between diagnosis and intervention, and meaningful individualization. If feasible, a second reviewer independently assesses a subset of reports.

Participant preference and reviewer quality are separate findings. A liked diagnosis can be weakly supported, and a well-supported diagnosis can fail to be useful.

## Outcome categories

### Strong support

Recurring diagnoses are evidence-backed, meaningfully individualized, trusted, more actionable than baseline, and repeatedly preferred for choosing what to practice.

### Partial support

The approach shows value but has a clear limitation, such as useful observations with speculative explanations, a good diagnosis with a weak intervention, value only with 20-30 games, or participant value with poor reviewer agreement.

### No support

Reports mostly restate engine analysis, give generic advice, depend on storytelling, cannot be reproduced, are not trusted, or do not meaningfully outperform conventional review.

### Harmful failure mode

The report produces confident, psychologically persuasive diagnoses that weak evidence does not justify. This outcome receives special attention even if participants like the reports.

## Predefined failure conditions

The product claim is weakened if any of these recur:

- Condition B collapses into generic advice.
- Independent analysts derive incompatible diagnoses from the same evidence.
- Diagnoses rely heavily on subjective storytelling.
- Participants cannot see how evidence supports the diagnosis.
- Participants prefer conventional review when deciding what to practice.
- Reports are no more specific than rating-level advice.
- Recommendations do not follow logically from the observed pattern.
- 10-30 games frequently provide insufficient evidence for a useful recurrence claim.
- Confidence language systematically exceeds evidential support.

Do not revise these conditions after seeing results without recording a protocol deviation.

## Limitations

The sample is small and selected for discovery. Manual analysis introduces researcher judgment. Participant ratings test perceived value, not learning or transfer. The study cannot establish rating improvement, causal psychological explanations, automated-analysis reliability, or a complete learner model.

Transfer is a later question. A future study would need to follow diagnosis, bounded intervention, practice performance, and behavior in later comparable games. Understanding or liking an intervention does not prove that it worked.

## Protocol-change policy

The first run uses this frozen protocol. If a change becomes necessary, preserve the previous protocol, record the change and reason, and state whether data collected before and after the change remain comparable. Never silently edit methodology in response to early results.

