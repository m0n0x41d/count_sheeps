import json
import sys
from random import Random

# Pyodide runs Python 3.12 — ReadOnly was added in 3.13.
# Patch typing before importing src modules so `from typing import ReadOnly` works.
if sys.version_info < (3, 13):
    import typing

    class _ReadOnlyShim:
        def __getitem__(self, item: object) -> object:
            return item

    typing.ReadOnly = _ReadOnlyShim()  # type: ignore[attr-defined]

from src.board import Board
from src.cascade import CascadePhase
from src.match import Match
from src.rules import (
    GameState,
    has_possible_moves,
    initialize_board,
    make_game_state,
    match_time_bonus,
    validate_move,
)

_state: GameState | None = None


def _serialize_board(board: Board) -> list[list[str]]:
    return [
        [elem["symbol"] for elem in row]
        for row in board
    ]


def _serialize_positions(positions: frozenset[tuple[int, int]]) -> list[list[int]]:
    return sorted([list(p) for p in positions])


def _serialize_match(match: Match) -> dict:
    return {
        "kind": match["kind"],
        "symbol": match["element"]["symbol"],
        "positions": _serialize_positions(match["positions"]),
    }


def _serialize_phase(phase: CascadePhase) -> dict:
    return {
        "board_before": _serialize_board(phase["board_before"]),
        "matches": [_serialize_match(m) for m in phase["matches"]],
        "cleared": _serialize_board(phase["cleared"]),
        "fallen": _serialize_board(phase["fallen"]),
        "filled": _serialize_board(phase["filled"]),
    }


def _serialize_state(state: GameState) -> dict:
    return {
        "board": _serialize_board(state["board"]),
        "size": state["size"],
        "score": state["score"],
        "drowsiness": state["drowsiness"],
    }


def init_game(size: int) -> str:
    global _state
    rng = Random()
    result = initialize_board(size, rng)
    _state = make_game_state(
        board=result["board"],
        size=size,
        score=0,
        drowsiness=1.0,
        rng=rng,
    )
    return json.dumps(_serialize_state(_state))


def try_move(r1: int, c1: int, r2: int, c2: int) -> str:
    global _state
    assert _state is not None

    result = validate_move(
        _state["board"], _state["size"],
        (r1, c1), (r2, c2),
        _state["rng"],
    )

    if result["tag"] == "invalid":
        return json.dumps({"tag": "invalid", "reason": result["reason"]})

    all_matches = tuple(
        m for phase in result["cascade"]["phases"]
        for m in phase["matches"]
    )
    bonus = match_time_bonus(all_matches)
    new_drowsiness = min(1.0, _state["drowsiness"] + bonus)

    _state = make_game_state(
        board=result["cascade"]["board"],
        size=_state["size"],
        score=_state["score"] + result["score"],
        drowsiness=new_drowsiness,
        rng=_state["rng"],
    )

    return json.dumps({
        "tag": "valid",
        "score": result["score"],
        "phases": [_serialize_phase(p) for p in result["cascade"]["phases"]],
        "state": _serialize_state(_state),
        "has_possible_moves": has_possible_moves(_state["board"], _state["size"]),
    })


def get_state() -> str:
    assert _state is not None
    return json.dumps(_serialize_state(_state))
