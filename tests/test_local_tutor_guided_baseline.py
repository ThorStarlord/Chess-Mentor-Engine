import importlib.util

from test_reasoning_discrepancy_facts import (
    T1,
    T2,
    T3,
    T4,
    T5,
    T6,
    T7,
    T8,
    _a1_prompt,
    _a2_prompt,
    _protocol,
    _upstream,
)

from chess_mentor_engine.chess import build_position_context
from chess_mentor_engine.storage import (
    LocalArtifactStore,
    load_tutor_session,
    save_tutor_session,
)
from chess_mentor_engine.tutoring import start_tutor_session


def _api():
    spec = importlib.util.find_spec("chess_mentor_engine.local_tutor_review")
    assert spec is not None
    from chess_mentor_engine.local_tutor_review import run_guided_baseline_capture

    return run_guided_baseline_capture


def _fixture(tmp_path):
    upstream = _upstream()
    store = LocalArtifactStore(tmp_path / "mentor.sqlite3")
    session = start_tutor_session(
        context=upstream.player_context,
        capture_protocol=_protocol(),
        created_at=T1,
    )
    ref = save_tutor_session(
        store,
        session,
        prompts=(_a1_prompt(), _a2_prompt()),
    )
    packet = build_position_context(upstream.game, upstream.position)
    return store, ref, packet


def test_guided_baseline_reaches_frozen_without_objective_reveal(tmp_path) -> None:
    run = _api()
    store, ref, packet = _fixture(tmp_path)
    answers = iter(("I would play e4.", "I considered e4 and ...e5."))
    times = iter((T2, T3, T4, T5, T6, T7, T8))
    output = []

    result = run(
        store=store,
        participant_id="P01",
        initial_session_ref=ref,
        position_context=packet,
        input_fn=lambda _: next(answers),
        output_fn=output.append,
        now_fn=lambda: next(times),
    )

    recovered = load_tutor_session(
        store,
        result.final_session_ref,
        participant_id="P01",
    )
    assert result.baseline_frozen is True
    assert recovered.session.state == "frozen"
    assert recovered.session.capture_session.objective_reveal is None
    assert len(result.observation_refs) == 8
    assert any("What do you think" in line for line in output)


def test_guided_baseline_eof_preserves_checkpoint_and_records_abandonment(
    tmp_path,
) -> None:
    run = _api()
    store, ref, packet = _fixture(tmp_path)
    times = iter((T2, T3, T4))

    def stop(_: str) -> str:
        raise EOFError

    result = run(
        store=store,
        participant_id="P01",
        initial_session_ref=ref,
        position_context=packet,
        input_fn=stop,
        output_fn=lambda _: None,
        now_fn=lambda: next(times),
    )

    recovered = load_tutor_session(
        store,
        result.final_session_ref,
        participant_id="P01",
    )
    assert result.baseline_frozen is False
    assert result.abandoned is True
    assert recovered.session.state == "capturing"
    assert result.observation_refs[-1].kind == "post-v1.interaction-observation.v1"
