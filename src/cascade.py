from random import Random
from typing import ReadOnly, TypedDict

from src.core import Size
from src.board import Board, EMPTY, apply_gravity, fill_empty
from src.match import Match, find_matches


class CascadePhase(TypedDict):
    board_before: ReadOnly[Board]
    matches: ReadOnly[tuple[Match, ...]]
    cleared: ReadOnly[Board]
    fallen: ReadOnly[Board]
    filled: ReadOnly[Board]


class CascadeResult(TypedDict):
    phases: ReadOnly[tuple[CascadePhase, ...]]
    board: ReadOnly[Board]


def clear_matches(board: Board, matches: tuple[Match, ...]) -> Board:
    positions_to_clear = frozenset().union(*(m["positions"] for m in matches))
    return tuple(
        tuple(
            {"symbol": EMPTY} if (r, c) in positions_to_clear else elem
            for c, elem in enumerate(row_data)
        )
        for r, row_data in enumerate(board)
    )


def cascade_step(board: Board, size: Size, rng: Random) -> CascadePhase | None:
    matches = find_matches(board, size)
    if not matches:
        return None

    cleared = clear_matches(board, matches)
    fallen = apply_gravity(cleared, size)
    filled = fill_empty(fallen, size, rng)

    return {
        "board_before": board,
        "matches": matches,
        "cleared": cleared,
        "fallen": fallen,
        "filled": filled,
    }


def run_cascade(board: Board, size: Size, rng: Random) -> CascadeResult:
    phases: list[CascadePhase] = []
    current = board

    while (phase := cascade_step(current, size, rng)) is not None:
        phases.append(phase)
        current = phase["filled"]

    return {
        "phases": tuple(phases),
        "board": current,
    }
