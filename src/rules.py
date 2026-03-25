from random import Random
from typing import Final, Literal, ReadOnly, TypedDict

from src.core import Pos, Size, adjacent, all_positions, neighbors, swap
from src.board import Board, make_empty_board, fill_empty
from src.match import Match, MatchKind, find_matches
from src.cascade import CascadeResult, run_cascade


class ValidMove(TypedDict):
    tag: ReadOnly[Literal["valid"]]
    cascade: ReadOnly[CascadeResult]
    score: ReadOnly[int]


class InvalidMove(TypedDict):
    tag: ReadOnly[Literal["invalid"]]
    reason: ReadOnly[str]


type MoveResult = ValidMove | InvalidMove

MATCH_SCORES: Final[dict[MatchKind, int]] = {
    "line3": 30,
    "line4": 80,
    "line5": 150,
    "cross": 200,
}


class GameState(TypedDict):
    board: ReadOnly[Board]
    size: ReadOnly[Size]
    score: ReadOnly[int]
    drowsiness: ReadOnly[float]
    rng: ReadOnly[Random]


def make_game_state(
    board: Board,
    size: Size,
    score: int,
    drowsiness: float,
    rng: Random,
) -> GameState:
    return {
        "board": board,
        "size": size,
        "score": score,
        "drowsiness": drowsiness,
        "rng": rng,
    }


def validate_move(
    board: Board,
    size: Size,
    p1: Pos,
    p2: Pos,
    rng: Random,
) -> MoveResult:
    if not adjacent(p1, p2):
        return {"tag": "invalid", "reason": "Only adjacent cells can be swapped."}

    swapped = swap(board, p1, p2)
    matches = find_matches(swapped, size)
    if not matches:
        return {"tag": "invalid", "reason": "Swap does not produce a match."}

    cascade = run_cascade(swapped, size, rng)
    score = score_cascade(cascade)
    return {"tag": "valid", "cascade": cascade, "score": score}


def score_cascade(result: CascadeResult) -> int:
    total = 0
    for phase_idx, phase in enumerate(result["phases"]):
        multiplier = phase_idx + 1
        phase_score = sum(
            MATCH_SCORES[m["kind"]]
            for m in phase["matches"]
        )
        total += phase_score * multiplier
    return total


def match_time_bonus(matches: tuple[Match, ...]) -> float:
    return 0.1 * len(matches)


def tick(state: GameState, elapsed_ms: int) -> GameState:
    decay_rate = 0.001
    new_drowsiness = max(0.0, state["drowsiness"] - decay_rate * elapsed_ms)
    return {**state, "drowsiness": new_drowsiness}


def has_possible_moves(board: Board, size: Size) -> bool:
    for pos in all_positions(size):
        for neighbor in neighbors(pos, size):
            if pos >= neighbor:
                continue
            swapped = swap(board, pos, neighbor)
            if find_matches(swapped, size):
                return True
    return False


def initialize_board(size: Size, rng: Random) -> CascadeResult:
    if size < 3:
        raise ValueError("Board size must be at least 3 to guarantee a possible move.")

    board = make_empty_board(size)
    filled = fill_empty(board, size, rng)
    result = run_cascade(filled, size, rng)

    if has_possible_moves(result["board"], size):
        return result

    return initialize_board(size, rng)
