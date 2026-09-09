from __future__ import annotations

import hashlib
import json
from pathlib import Path

from test_hypothesis_recurrence_assessment import (
    _actor,
    _assess,
    _make_hypothesis,
    _make_link,
    _policy,
    _retag_link,
    _review,
    _support_units,
)

from chess_mentor_engine.learning import (
    build_hypothesis_ledger_snapshot,
    create_learner_hypothesis,
    record_hypothesis_lifecycle_event,
    record_hypothesis_revision,
)

Q_CORPUS = Path(__file__).parent / "fixtures" / "m7q_learner_hypothesis_corpus.json"
Q_TIME = "2026-09-09T10:00:00+00:00"


def _load_corpus() -> dict[str, object]:
    return json.loads(Q_CORPUS.read_text(encoding="utf-8"))


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def test_m7q_corpus_freezes_complete_m7a_claim_surface() -> None:
    corpus = _load_corpus()
    required = set(corpus["required_cases"])
    assert required == {
        "one_support_is_isolated",
        "same_position_does_not_double_count",
        "independence_rule_blocks_recurrence_inflation",
        "multiple_independent_supports_are_candidate_recurrence",
        "policy_qualified_support_is_supported_recurrence",
        "contradiction_is_retained",
        "successful_counterexample_is_retained",
        "m4_control_is_not_automatic_counterevidence",
        "no_supported_discrepancy_is_not_automatic_counterevidence",
        "context_exception_is_scope_evidence",
        "unclear_evidence_does_not_manufacture_support",
        "stage_incompatibility_is_explicit",
        "measurement_condition_is_preserved_and_policy_gated",
        "m6_policy_family_compatibility_is_explicit",
        "competing_explanation_review_is_required",
        "revision_preserves_prior_assessment_history",
        "retirement_preserves_history",
        "supersession_preserves_both_lineages",
        "deterministic_replay_and_fingerprint_identity",
        "no_training_or_pedagogy_claims",
        "research_artifact_preservation",
    }


def test_m7q_recurrence_requires_distinct_qualified_evidence_units() -> None:
    hypothesis, revision = _make_hypothesis()

    one = _support_units(hypothesis, revision, 1)[0]
    isolated = _assess(hypothesis, revision, _policy(), (one,))
    assert isolated.status == "isolated"
    assert isolated.evidence_summary.independent_support_count == 1

    duplicate = _retag_link(one, "supports", "m7q-duplicate-mapping")
    repeated = _assess(hypothesis, revision, _policy(), (one, duplicate))
    assert repeated.status == "isolated"
    assert len(repeated.recurrence_units) == 1

    same_game = tuple(
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=index,
            relation="supports",
            game_id="same-game",
        )
        for index in (2, 3)
    )
    non_independent = _assess(
        hypothesis,
        revision,
        _policy(),
        same_game,
    )
    assert non_independent.status == "insufficient"
    assert non_independent.evidence_summary.support_unit_count == 2
    assert non_independent.evidence_summary.independent_support_count == 1


def test_m7q_candidate_and_supported_recurrence_are_policy_bound() -> None:
    hypothesis, revision = _make_hypothesis()
    policy = _policy()

    candidate = _assess(
        hypothesis,
        revision,
        policy,
        _support_units(hypothesis, revision, 2),
    )
    assert candidate.status == "candidate_recurrence"
    assert candidate.evidence_summary.independent_support_count == 2

    supported = _assess(
        hypothesis,
        revision,
        policy,
        _support_units(hypothesis, revision, 3),
    )
    assert supported.status == "supported_recurrence"
    assert supported.contradiction_review.state == "completed"
    assert supported.counterexample_review.state == "completed"
    assert supported.competing_explanation_review.state == "completed"


def test_m7q_challenge_evidence_coexists_with_support() -> None:
    hypothesis, revision = _make_hypothesis()
    supports = list(_support_units(hypothesis, revision, 3))

    contradiction = _make_link(
        hypothesis=hypothesis,
        revision=revision,
        index=4,
        relation="contradicts",
        game_id="g4",
    )
    contradicted = _assess(
        hypothesis,
        revision,
        _policy(),
        tuple(supports + [contradiction]),
    )
    assert contradicted.status == "contradicted"
    assert contradicted.evidence_summary.independent_support_count == 3
    assert contradicted.evidence_summary.contradiction_unit_count == 1

    counterexample = _make_link(
        hypothesis=hypothesis,
        revision=revision,
        index=5,
        relation="successful_counterexample",
        game_id="g5",
        status="no_supported_discrepancy",
        with_assertion=False,
    )
    retained = _assess(
        hypothesis,
        revision,
        _policy(),
        tuple(supports + [counterexample]),
    )
    assert retained.evidence_summary.successful_counterexample_unit_count == 1
    assert len(retained.successful_counterexample_link_refs) == 1


def test_m7q_controls_and_no_discrepancy_are_not_automatic_counterevidence() -> None:
    hypothesis, revision = _make_hypothesis()

    no_links = _assess(hypothesis, revision, _policy(), ())
    assert no_links.status == "insufficient"
    assert no_links.evidence_summary.contradiction_unit_count == 0
    assert no_links.evidence_summary.successful_counterexample_unit_count == 0

    explicit_unclear = _make_link(
        hypothesis=hypothesis,
        revision=revision,
        index=1,
        relation="unclear",
        game_id="g1",
        status="no_supported_discrepancy",
        with_assertion=False,
    )
    unclear = _assess(
        hypothesis,
        revision,
        _policy(),
        (explicit_unclear,),
    )
    assert unclear.evidence_summary.successful_counterexample_unit_count == 0
    assert unclear.evidence_summary.unclear_unit_count == 1

    explicit_counterexample = _retag_link(
        explicit_unclear,
        "successful_counterexample",
        "m7q-explicit-counterexample-mapping",
    )
    counter = _assess(
        hypothesis,
        revision,
        _policy(),
        (explicit_counterexample,),
    )
    assert counter.evidence_summary.successful_counterexample_unit_count == 1


def test_m7q_exception_and_unclear_evidence_do_not_manufacture_support() -> None:
    hypothesis, revision = _make_hypothesis()
    supports = list(_support_units(hypothesis, revision, 3))

    exception = _make_link(
        hypothesis=hypothesis,
        revision=revision,
        index=4,
        relation="context_exception",
        game_id="g4",
    )
    scoped = _assess(
        hypothesis,
        revision,
        _policy(),
        tuple(supports + [exception]),
    )
    assert scoped.status == "candidate_recurrence"
    assert scoped.evidence_summary.context_exception_unit_count == 1
    assert "context_exception_present" in scoped.status_reasons

    unclear_link = _make_link(
        hypothesis=hypothesis,
        revision=revision,
        index=5,
        relation="unclear",
        game_id="g5",
    )
    unclear = _assess(
        hypothesis,
        revision,
        _policy(),
        tuple(supports + [unclear_link]),
    )
    assert unclear.status == "candidate_recurrence"
    assert unclear.evidence_summary.unclear_unit_count == 1
    assert "unclear_evidence_present" in unclear.status_reasons


def test_m7q_stage_measurement_and_m6_policy_compatibility_are_explicit() -> None:
    hypothesis, revision = _make_hypothesis()

    stage_units = (
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=1,
            relation="supports",
            game_id="g1",
            stage_ids=("stage-a1",),
        ),
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=2,
            relation="supports",
            game_id="g2",
            stage_ids=("stage-a2",),
        ),
    )
    stage_blocked = _assess(hypothesis, revision, _policy(), stage_units)
    assert stage_blocked.status == "insufficient"
    assert stage_blocked.evidence_summary.eligible_link_count == 0

    stage_allowed = _assess(
        hypothesis,
        revision,
        _policy(
            stage_compatibility_rule="declared_stage_ids",
            allowed_stage_ids=("stage-a1", "stage-a2"),
        ),
        stage_units,
    )
    assert stage_allowed.status == "candidate_recurrence"

    contaminated = _make_link(
        hypothesis=hypothesis,
        revision=revision,
        index=3,
        relation="supports",
        game_id="g3",
        condition="contaminated",
    )
    measurement_blocked = _assess(
        hypothesis,
        revision,
        _policy(),
        (contaminated,),
    )
    assert measurement_blocked.status == "insufficient"
    reasons = measurement_blocked.evidence_summary.exclusion_reasons[0][1]
    assert "measurement_condition_not_allowed:contaminated" in reasons

    policy_units = (
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=4,
            relation="supports",
            game_id="g4",
            policy_fingerprint="policy-a",
        ),
        _make_link(
            hypothesis=hypothesis,
            revision=revision,
            index=5,
            relation="supports",
            game_id="g5",
            policy_fingerprint="policy-b",
        ),
    )
    policy_blocked = _assess(hypothesis, revision, _policy(), policy_units)
    assert policy_blocked.status == "insufficient"
    assert policy_blocked.evidence_summary.eligible_link_count == 0

    compatible = tuple(
        sorted(
            {
                policy_units[0][1].assessment_policy_ref.fingerprint,
                policy_units[1][1].assessment_policy_ref.fingerprint,
            }
        )
    )
    policy_allowed = _assess(
        hypothesis,
        revision,
        _policy(
            m6_policy_compatibility_rule="declared_policy_fingerprints",
            compatible_m6_policy_fingerprints=compatible,
        ),
        policy_units,
    )
    assert policy_allowed.status == "candidate_recurrence"


def test_m7q_competing_explanation_review_is_a_support_gate() -> None:
    hypothesis, revision = _make_hypothesis()
    result = _assess(
        hypothesis,
        revision,
        _policy(),
        _support_units(hypothesis, revision, 3),
        review=_review(revision, completed=False),
    )
    assert result.status == "candidate_recurrence"
    assert "competing_explanation_review_incomplete" in result.status_reasons


def test_m7q_revision_preserves_prior_assessment_without_relabeling_it() -> None:
    hypothesis, revision_one = _make_hypothesis()
    assessment_one = _assess(
        hypothesis,
        revision_one,
        _policy(),
        _support_units(hypothesis, revision_one, 3),
    )
    revision_two = record_hypothesis_revision(
        hypothesis=hypothesis,
        existing_revisions=(revision_one,),
        statement="The pattern is bounded to forcing-check reply positions.",
        scope_definition="forcing-check reply positions",
        revision_reason="M7Q context exception narrows the descriptive scope",
        author_provenance=_actor("m7q-reviser"),
        created_at="2026-09-09T09:00:00+00:00",
    )

    snapshot = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(hypothesis,),
        revisions=(revision_two, revision_one),
        assessments=(assessment_one,),
        lifecycle_events=(),
        created_at=Q_TIME,
    )
    entry = snapshot.entries[0]
    assert entry.current_revision_ref.revision_id == revision_two.revision_id
    assert entry.latest_assessment_ref is None
    assert assessment_one.hypothesis_revision_ref.revision_id == revision_one.revision_id


def test_m7q_retirement_preserves_assessment_and_authority_is_separate() -> None:
    hypothesis, revision = _make_hypothesis()
    assessment = _assess(
        hypothesis,
        revision,
        _policy(),
        _support_units(hypothesis, revision, 3),
    )
    event = record_hypothesis_lifecycle_event(
        hypothesis=hypothesis,
        existing_events=(),
        kind="retired",
        reason="M7Q later evidence makes this lineage unsuitable for current use.",
        author_provenance=_actor("m7q-owner"),
        created_at="2026-09-09T09:00:00+00:00",
    )
    snapshot = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(hypothesis,),
        revisions=(revision,),
        assessments=(assessment,),
        lifecycle_events=(event,),
        created_at=Q_TIME,
    )
    entry = snapshot.entries[0]
    assert entry.authority_lifecycle_state == "retired"
    assert entry.latest_assessment_ref is not None
    assert entry.latest_assessment_ref.status == "supported_recurrence"


def test_m7q_supersession_preserves_both_lineages() -> None:
    original, original_revision = _make_hypothesis()
    replacement, replacement_revision = create_learner_hypothesis(
        participant_id="P01",
        statement="A distinct replacement descriptive pattern.",
        scope_definition="replacement context",
        origin_provenance=_actor("m7q-replacement-author"),
        created_at="2026-09-09T08:00:00+00:00",
    )
    event = record_hypothesis_lifecycle_event(
        hypothesis=original,
        existing_events=(),
        kind="superseded",
        reason="A distinct lineage better matches the retained evidence.",
        author_provenance=_actor("m7q-owner"),
        superseding_hypothesis=replacement,
        created_at="2026-09-09T09:00:00+00:00",
    )
    snapshot = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(replacement, original),
        revisions=(replacement_revision, original_revision),
        assessments=(),
        lifecycle_events=(event,),
        created_at=Q_TIME,
    )
    states = {
        entry.hypothesis_ref.hypothesis_id: entry.authority_lifecycle_state
        for entry in snapshot.entries
    }
    assert states[original.hypothesis_id] == "superseded"
    assert states[replacement.hypothesis_id] == "active"


def test_m7q_full_replay_is_deterministic_and_has_no_pedagogy_claim() -> None:
    hypothesis, revision = _make_hypothesis()
    policy = _policy()
    units = _support_units(hypothesis, revision, 3)

    first = _assess(hypothesis, revision, policy, units)
    second = _assess(hypothesis, revision, policy, tuple(reversed(units)))
    assert first == second
    assert first.fingerprint == second.fingerprint

    snapshot_one = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(hypothesis,),
        revisions=(revision,),
        assessments=(first,),
        lifecycle_events=(),
        created_at=Q_TIME,
    )
    snapshot_two = build_hypothesis_ledger_snapshot(
        participant_id="P01",
        hypotheses=(hypothesis,),
        revisions=(revision,),
        assessments=(second,),
        lifecycle_events=(),
        created_at=Q_TIME,
    )
    assert snapshot_one == snapshot_two
    assert snapshot_one.fingerprint == snapshot_two.fingerprint

    serialized = json.dumps(first.to_dict(), sort_keys=True).lower()
    assert "training_eligible" not in serialized
    assert "intervention" not in serialized
    assert "pedagogy" not in serialized
    assert first.status == "supported_recurrence"


def test_m7q_historical_pilot_artifacts_remain_byte_identical() -> None:
    corpus = _load_corpus()
    expected = corpus["research_artifact_git_blob_shas"]
    assert isinstance(expected, dict)

    repo_root = Path(__file__).resolve().parents[1]
    actual = {
        relative_path: _git_blob_sha(repo_root / relative_path)
        for relative_path in expected
    }
    assert actual == expected
