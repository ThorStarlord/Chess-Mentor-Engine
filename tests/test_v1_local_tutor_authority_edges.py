"""Authority-edge rejection tests for the V1 local tutor consumer."""

from __future__ import annotations

from dataclasses import replace

import pytest
from test_m45_batch_mentor_queue import _challenge_view, _rehash_view
from test_reasoning_discrepancy_facts import _upstream
from test_v1_local_tutor_workflow import CREATED_AT, _selected_session, _source_refs

from chess_mentor_engine.learner_intelligence import (
    build_default_mentor_queue_policy,
)
from chess_mentor_engine.local_tutor import (
    LocalTutorWorkflowError,
    build_local_tutor_workflow,
)
from chess_mentor_engine.tutoring import build_default_adaptive_tutor_policy


def test_v1_objective_only_queue_item_requires_explicit_hypothesis_context() -> None:
    upstream = _upstream()
    view = _challenge_view(
        upstream.candidate.game_id,
        upstream.candidate.position_id,
    )
    hypothesis = view.hypotheses[0]
    objective_only_view = _rehash_view(
        view,
        (
            replace(
                hypothesis,
                acquisition_ref=None,
                acquisition_intent=None,
                acquisition_candidates=(),
            ),
        ),
    )

    preview = build_local_tutor_workflow(
        participant_id="P01",
        diagnostic_batch=upstream.batch,
        batch_source_refs=_source_refs(),
        learner_progress_view=objective_only_view,
        queue_policy=build_default_mentor_queue_policy(
            requested_size=1,
            maximum_per_game=1,
        ),
        adaptive_tutor_policy=build_default_adaptive_tutor_policy(),
        created_at=CREATED_AT,
    )
    assert preview.active_item.hypothesis_ids == ()
    assert preview.active_item.dimensions.learner_relevance == 0

    with pytest.raises(
        LocalTutorWorkflowError,
        match="no learner-hypothesis link",
    ):
        build_local_tutor_workflow(
            participant_id="P01",
            diagnostic_batch=upstream.batch,
            batch_source_refs=_source_refs(),
            learner_progress_view=objective_only_view,
            queue_policy=build_default_mentor_queue_policy(
                requested_size=1,
                maximum_per_game=1,
            ),
            adaptive_tutor_policy=build_default_adaptive_tutor_policy(),
            created_at=CREATED_AT,
            tutor_session=_selected_session(),
        )
