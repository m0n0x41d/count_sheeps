from random import Random
from typing import Final, ReadOnly, TypedDict

from src.core import Grid, Pos, Size, get, make_grid, all_positions

EMPTY: Final[str] = "0"
SYMBOLS: Final[tuple[str, ...]] = ("A", "B", "C", "D", "E", "F")


class Element(TypedDict):
    symbol: ReadOnly[str]


type Board = Grid[Element]


def make_element(symbol: str) -> Element | None:
    if symbol != EMPTY and symbol not in SYMBOLS:
        return None
    return {"symbol": symbol}


def make_empty_board(size: Size) -> Board:
    return make_grid(size, lambda _r, _c: {"symbol": EMPTY})


def is_empty(elem: Element) -> bool:
    return elem["symbol"] == EMPTY


def symbol_at(board: Board, pos: Pos) -> str:
    return get(board, pos)["symbol"]


def empty_positions(board: Board, size: Size) -> frozenset[Pos]:
    return frozenset(
        pos for pos in all_positions(size)
        if is_empty(get(board, pos))
    )


def _drop_column(board: Board, col: int, size: Size) -> tuple[Element, ...]:
    non_empty = tuple(
        get(board, (row, col))
        for row in range(size)
        if not is_empty(get(board, (row, col)))
    )
    pad = size - len(non_empty)
    empties = tuple({"symbol": EMPTY} for _ in range(pad))
    return empties + non_empty


def apply_gravity(board: Board, size: Size) -> Board:
    columns = tuple(
        _drop_column(board, col, size)
        for col in range(size)
    )
    return tuple(
        tuple(columns[col][row] for col in range(size))
        for row in range(size)
    )


def fill_empty(board: Board, size: Size, rng: Random) -> Board:
    return tuple(
        tuple(
            elem if not is_empty(elem) else {"symbol": rng.choice(SYMBOLS)}
            for elem in row
        )
        for row in board
    )
