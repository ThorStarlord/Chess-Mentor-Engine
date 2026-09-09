from __future__ import annotations

import pytest

from chess_mentor_engine.learning import (
    HypothesisActorProvenance,
    LearnerHypothesisError,
    create_learner_hypothesis,
    record_hypothesis_evidence_link,
    record_hypothesis_revision,
)


def _actor() -> HypothesisActorProvenance:
    return HypothesisActorProvenance(
        actor_kind="human",
        actor_id="analyst",
        actor_version="v1",
        rubric_or_instruction_fingerprint="rubric-v1",
        run_id="run-1",
    )


def test_later_revision_link_requires_exact_revision_history() -> None:
    hypothesis, revision_one = create_learner_hypothesis(
        participant_id="P01",
        statement="Initial descriptive pattern.",
        scope_definition="initial scope",
        origin_provenance=_actor(),
        created_at="2026-09-09T03:00:00+00:00",
    )
    revision_two = record_hypothesis_revision(
        hypothesis=hypothesis,
        existing_revisions=(revision_one,),
        statement="Narrower descriptive pattern.",
        scope_definition="narrower scope",
        revision_reason="scope refinement",
        author_provenance=_actor(),
        created_at="2026-09-09T04:00:00+00:00",
    )

    with pytest.raises(LearnerHypothesisError, match="revision numbers"):
        record_hypothesis_evidence_link(
            hypothesis=hypothesis,
            revision=revision_two,
            reasoning_context=None,  # type: ignore[arg-type]
            assessment=None,  # type: ignore[arg-type]
            assertions=(),
            relation="supports",
            basis_kind="deterministic_mapping",
            mapping_provenance=None,  # type: ignore[arg-type]
            created_at="2026-09-09T05:00:00+00:00",
        )
