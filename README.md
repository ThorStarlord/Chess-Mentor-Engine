# Chess Mentor Engine

Chess Mentor Engine is intended to become a persistent, personalized chess tutor that learns from a player's games and training history. It should identify recurring decision patterns, explain what those patterns may reveal about the player's thinking, and turn that evidence into focused learning opportunities.

Repository description: Persistent AI chess tutor that learns how you think, diagnoses recurring mistakes, and turns game evidence into personalized training.

## Product thesis

Chess engines can answer what is objectively happening in a position. A tutor should also help answer why a particular player missed it and what that player should work on next.

```text
Chess engine:
What is objectively happening in the position?

Chess Mentor Engine:
What does this position reveal about how this player thinks,
and what should they learn next?
```

The working product hypothesis is that recurring mistakes can become an individualized curriculum when engine-grounded chess evidence is combined with a persistent learner model. This is a product hypothesis, not finalized architecture.

One tentative future loop looks like this:

```text
games / positions / goals
        ↓
objective chess evidence
        ↓
player-learning model
        ↓
diagnostic hypotheses
        ↓
learning priorities
        ↓
lesson / exercise
        ↓
student attempt
        ↓
evaluation
        ↓
updated player model
```

## Current repository status

This repository is in the foundation and product-discovery stage. It contains the initial product, domain, architecture, research, and decision notes, plus a minimal importable Python package. It does not contain a chess engine, persistence layer, web application, or tutoring implementation.

## Development principles

- Start with evidence and preserve its provenance.
- Keep objective chess analysis separate from pedagogical interpretation.
- Treat diagnoses and domain concepts as hypotheses until supported.
- Prefer small, testable changes over speculative abstractions.
- Keep learner state inspectable.

## Documentation map

- [Product definition](docs/product/product-definition.md) describes the problem, hypotheses, possible first value, and open questions.
- [Product discovery](docs/product/product-discovery.md) records the current design customer, first-value test, product boundary, and unresolved hypotheses.
- [Product principles](docs/product/product-principles.md) records the initial rules for product thinking.
- [Architecture hypothesis](docs/architecture/architecture.md) sketches possible system boundaries without freezing them.
- [Domain discovery seed](docs/domain/domain-model.md) lists concepts and distinctions that need investigation.
- [Research notes](docs/research/README.md) defines how future experiments should be recorded.
- [First validation experiment](docs/research/first-product-validation/README.md) contains the frozen manual study protocol and evaluation instruments.
- [Decision records](docs/decisions/README.md) explains when to capture a material product or architecture decision.
- [CONTEXT.md](CONTEXT.md) is the short orientation document for contributors and coding agents.

## Getting started

Create a Python 3.11 or newer virtual environment, install the development tools, and install the package in editable mode:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

## Tests and linting

```bash
pytest
ruff check .
```
