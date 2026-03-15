import random
from typing import Final, ReadOnly, TypedDict

EMPTY: Final[str] = "0"
SYMBOLS: Final[tuple[str, ...]] = ("A", "B", "C", "D", "E", "F")
RNG = random.Random()


class Element(TypedDict):
    symbol: ReadOnly[str]


def make_element(symbol: str) -> Element:
    if len(symbol) != 1:
        raise ValueError("Element symbol must be exactly one character long.")
    return {"symbol": symbol}


type BoardCells = tuple[tuple[Element, ...], ...]


class Board(TypedDict):
    size: ReadOnly[int]
    cells: ReadOnly[BoardCells]


class BoardState(TypedDict):
    board: ReadOnly[Board]
    score: ReadOnly[int]


def make_board(size: int, cells: BoardCells) -> Board:
    return {
        "size": size,
        "cells": cells,
    }


def make_board_state(board: Board, score: int = 0) -> BoardState:
    return {
        "board": board,
        "score": score,
    }


def generate_random_cells(size: int = 8) -> BoardCells:
    return tuple(
        tuple(make_element(RNG.choice(SYMBOLS)) for _ in range(size))
        for _ in range(size)
    )


def initialize_game(cells: BoardCells, score: int = 0) -> BoardState:
    size = len(cells)
    board = make_board(size, cells)
    return make_board_state(board, score)


def draw(board: Board) -> None:
    size = board["size"]
    print("  " + " ".join(str(i) for i in range(size)))
    for row in range(size):
        print(
            f"{row} "
            + " ".join(board["cells"][row][col]["symbol"] for col in range(size))
        )
    print()


def clone_board(board: Board) -> Board:
    size = board["size"]
    cells = tuple(
        tuple(board["cells"][row][col] for col in range(size)) for row in range(size)
    )
    return make_board(size, cells)


def read_move(board_state: BoardState) -> BoardState:
    print(">")
    input_line = input()
    if input_line == "q":
        raise SystemExit(0)

    board = clone_board(board_state["board"])
    coords = input_line.split()
    x = int(coords[1])
    y = int(coords[0])
    x1 = int(coords[3])
    y1 = int(coords[2])

    cells = [list(row) for row in board["cells"]]
    element = cells[x][y]
    cells[x][y] = cells[x1][y1]
    cells[x1][y1] = element

    new_board = make_board(
        board["size"],
        tuple(tuple(row) for row in cells),
    )
    return make_board_state(new_board, board_state["score"])


def main() -> None:
    # until save/load is not implemented.
    random_cells = generate_random_cells()
    board_state = initialize_game(cells=random_cells, score=0)
    while True:
        draw(board_state["board"])
        board_state = read_move(board_state)


if __name__ == "__main__":
    main()
