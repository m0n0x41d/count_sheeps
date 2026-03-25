import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.board import Board


def board_from_symbols(*rows: str) -> Board:
    size = len(rows)
    assert all(len(row) == size for row in rows)
    return tuple(
        tuple({"symbol": s} for s in row)
        for row in rows
    )


def symbols_from_board(board: Board) -> tuple[str, ...]:
    return tuple(
        "".join(elem["symbol"] for elem in row)
        for row in board
    )


class MockRNG:
    def __init__(self, values: list[str]) -> None:
        self._iter = iter(values)

    def choice(self, seq: Sequence[Any]) -> Any:
        return next(self._iter)
