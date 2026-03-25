from conftest import MockRNG, board_from_symbols, symbols_from_board

from src.cascade import cascade_step, clear_matches, run_cascade
from src.match import find_matches


def test_clear_matches_empties_matched_positions() -> None:
    board = board_from_symbols(
        "AAAB",
        "CDEF",
        "GHIJ",
        "KLMN",
    )
    matches = find_matches(board, 4)
    cleared = clear_matches(board, matches)
    assert symbols_from_board(cleared) == (
        "000B",
        "CDEF",
        "GHIJ",
        "KLMN",
    )


def test_cascade_step_returns_none_when_stable() -> None:
    board = board_from_symbols(
        "ABCD",
        "EFAB",
        "CDEF",
        "ABCD",
    )
    rng = MockRNG([])
    assert cascade_step(board, 4, rng) is None  # type: ignore[arg-type]


def test_cascade_step_returns_phase_with_all_boards() -> None:
    board = board_from_symbols(
        "XYZW",
        "PQRS",
        "AAAT",
        "UVWX",
    )
    rng = MockRNG(["D", "E", "F"])
    phase = cascade_step(board, 4, rng)  # type: ignore[arg-type]

    assert phase is not None
    assert symbols_from_board(phase["board_before"]) == (
        "XYZW",
        "PQRS",
        "AAAT",
        "UVWX",
    )
    assert symbols_from_board(phase["cleared"]) == (
        "XYZW",
        "PQRS",
        "000T",
        "UVWX",
    )
    assert symbols_from_board(phase["fallen"]) == (
        "000W",
        "XYZS",
        "PQRT",
        "UVWX",
    )
    assert symbols_from_board(phase["filled"]) == (
        "DEFW",
        "XYZS",
        "PQRT",
        "UVWX",
    )


def test_run_cascade_collects_all_phases() -> None:
    board = board_from_symbols(
        "ABC",
        "DEC",
        "FGC",
    )
    rng = MockRNG(["A", "A", "A", "D", "E", "F"])
    result = run_cascade(board, 3, rng)  # type: ignore[arg-type]

    assert len(result["phases"]) == 2
    assert symbols_from_board(result["board"]) == (
        "ABD",
        "DEE",
        "FGF",
    )


def test_run_cascade_returns_empty_phases_when_stable() -> None:
    board = board_from_symbols(
        "ABCD",
        "EFAB",
        "CDEF",
        "ABCD",
    )
    rng = MockRNG([])
    result = run_cascade(board, 4, rng)  # type: ignore[arg-type]
    assert result["phases"] == ()
    assert result["board"] is board
