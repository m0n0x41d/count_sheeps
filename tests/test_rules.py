from random import Random

from conftest import board_from_symbols

from src.rules import (
    MATCH_SCORES,
    has_possible_moves,
    initialize_board,
    match_time_bonus,
    score_cascade,
    tick,
    validate_move,
    make_game_state,
)
from src.cascade import run_cascade


def test_validate_move_rejects_non_adjacent() -> None:
    board = board_from_symbols(
        "ABC",
        "DEF",
        "GHI",
    )
    rng = Random(42)
    result = validate_move(board, 3, (0, 0), (2, 2), rng)
    assert result["tag"] == "invalid"
    assert "adjacent" in result["reason"]


def test_validate_move_rejects_no_match() -> None:
    board = board_from_symbols(
        "ABC",
        "DEF",
        "GHI",
    )
    rng = Random(42)
    result = validate_move(board, 3, (0, 0), (0, 1), rng)
    assert result["tag"] == "invalid"
    assert "match" in result["reason"].lower()


def test_validate_move_accepts_matching_swap() -> None:
    board = board_from_symbols(
        "ABD",
        "BAA",
        "CDE",
    )
    rng = Random(42)
    # swap (0,0)A ↔ (1,0)B → row 1 becomes AAA
    result = validate_move(board, 3, (0, 0), (1, 0), rng)
    assert result["tag"] == "valid"
    assert result["score"] > 0
    assert result["cascade"]["phases"]


def test_score_cascade_applies_multiplier() -> None:
    board = board_from_symbols(
        "ABC",
        "DEC",
        "FGC",
    )
    from conftest import MockRNG
    rng = MockRNG(["A", "A", "A", "D", "E", "F"])
    result = run_cascade(board, 3, rng)  # type: ignore[arg-type]

    score = score_cascade(result)
    phase_1_score = MATCH_SCORES["line3"] * 1
    phase_2_score = MATCH_SCORES["line3"] * 2
    assert score == phase_1_score + phase_2_score


def test_match_time_bonus() -> None:
    matches = (
        {"kind": "line3", "element": {"symbol": "A"}, "positions": frozenset()},
        {"kind": "line4", "element": {"symbol": "B"}, "positions": frozenset()},
    )
    assert match_time_bonus(matches) == 0.2


def test_tick_decreases_drowsiness() -> None:
    rng = Random(42)
    state = make_game_state(
        board=board_from_symbols("ABC", "DEF", "GHI"),
        size=3,
        score=0,
        drowsiness=1.0,
        rng=rng,
    )
    updated = tick(state, 100)
    assert updated["drowsiness"] == 0.9


def test_tick_clamps_drowsiness_at_zero() -> None:
    rng = Random(42)
    state = make_game_state(
        board=board_from_symbols("ABC", "DEF", "GHI"),
        size=3,
        score=0,
        drowsiness=0.05,
        rng=rng,
    )
    updated = tick(state, 1000)
    assert updated["drowsiness"] == 0.0


def test_has_possible_moves_playable() -> None:
    board = board_from_symbols(
        "ABA",
        "CAE",
        "FGH",
    )
    assert has_possible_moves(board, 3) is True


def test_has_possible_moves_dead() -> None:
    board = board_from_symbols(
        "ABC",
        "DEF",
        "GHI",
    )
    assert has_possible_moves(board, 3) is False


def test_initialize_board_rejects_small_size() -> None:
    import pytest
    with pytest.raises(ValueError):
        initialize_board(2, Random(42))


def test_initialize_board_returns_stable_playable_board() -> None:
    rng = Random(42)
    result = initialize_board(3, rng)

    assert result["phases"] is not None
    from src.match import find_matches
    assert find_matches(result["board"], 3) == ()
    assert has_possible_moves(result["board"], 3) is True
