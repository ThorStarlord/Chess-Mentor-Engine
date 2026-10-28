# Discovery methodology

Adapted from `lucasgaravelli/pm-skills-claude-code/.claude/commands/discovery.md` at commit `21cbb2903d740d10fc65c667aea97d3ee8657349` (MIT, Flowgrammers 2026).

Start with problem framing. Prefer a JTBD-compatible sentence such as `When [context], the user needs [job] so that [outcome]`.

Generate root-cause hypotheses rather than feature proposals. For each, record supporting and contradictory evidence, uncertainty/risk, affected outcome, the cheapest credible way to learn more, observable success/refutation criteria, and which decision changes under each result.

Sequence learning so the highest-consequence or cheapest-to-disambiguate uncertainty is addressed first. A calendar is optional; causal and decision ordering matters more than inventing a fixed schedule. Do not default to interviews: choose the evidence source appropriate to the uncertainty, including repository inspection, analytics, interviews, surveys, session evidence, experiments, or owner decision.
