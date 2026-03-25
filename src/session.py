from random import Random
from typing import Literal, ReadOnly, TypedDict

from src.core import Pos, Size, make_pos
from src.board import Board
from src.rules import (
    GameState,
    make_game_state,
    match_time_bonus,
    validate_move,
    initialize_board,
)


type Command = SwapCmd | QuitCmd


class SwapCmd(TypedDict):
    tag: ReadOnly[Literal["swap"]]
    p1: ReadOnly[Pos]
    p2: ReadOnly[Pos]


class QuitCmd(TypedDict):
    tag: ReadOnly[Literal["quit"]]


def parse_command(raw: str, size: Size) -> Command | None:
    raw = raw.strip()
    if raw == "q":
        return {"tag": "quit"}

    parts = raw.split()
    if len(parts) != 4:
        return None

    try:
        coords = [int(p) for p in parts]
    except ValueError:
        return None

    p1 = make_pos(coords[0], coords[1], size)
    p2 = make_pos(coords[2], coords[3], size)
    if p1 is None or p2 is None:
        return None

    return {"tag": "swap", "p1": p1, "p2": p2}


def apply_command(state: GameState, cmd: Command) -> GameState | None:
    if cmd["tag"] == "quit":
        return None

    result = validate_move(
        state["board"], state["size"],
        cmd["p1"], cmd["p2"],
        state["rng"],
    )

    if result["tag"] == "invalid":
        print(result["reason"])
        return state

    all_matches = tuple(
        m for phase in result["cascade"]["phases"]
        for m in phase["matches"]
    )
    bonus = match_time_bonus(all_matches)
    new_drowsiness = min(1.0, state["drowsiness"] + bonus)

    return make_game_state(
        board=result["cascade"]["board"],
        size=state["size"],
        score=state["score"] + result["score"],
        drowsiness=new_drowsiness,
        rng=state["rng"],
    )


def render_board(board: Board, size: Size) -> str:
    header = "  " + " ".join(str(i) for i in range(size))
    rows = [
        f"{row} " + " ".join(board[row][col]["symbol"] for col in range(size))
        for row in range(size)
    ]
    return "\n".join([header] + rows)


def read_input() -> str:
    print(">")
    return input()


def run_game(size: Size) -> None:
    rng = Random()
    result = initialize_board(size, rng)
    state = make_game_state(
        board=result["board"],
        size=size,
        score=0,
        drowsiness=1.0,
        rng=rng,
    )

    while True:
        print(render_board(state["board"], state["size"]))
        raw = read_input()
        cmd = parse_command(raw, state["size"])
        if cmd is None:
            print("Expected move format: row col row1 col1")
            continue

        new_state = apply_command(state, cmd)
        if new_state is None:
            break
        state = new_state
