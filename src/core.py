from collections.abc import Callable
from typing import Any

type Pos = tuple[int, int]
type Size = int
type Grid[T] = tuple[tuple[T, ...], ...]


def pipe(value: object, *fns: Callable[[Any], Any]) -> Any:
    for fn in fns:
        value = fn(value)
    return value


def compose(*fns: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def composed(value: Any) -> Any:
        for fn in fns:
            value = fn(value)
        return value
    return composed


def make_pos(row: int, col: int, size: Size) -> Pos | None:
    if 0 <= row < size and 0 <= col < size:
        return (row, col)
    return None


def make_grid[T](size: Size, fill: Callable[[int, int], T]) -> Grid[T]:
    return tuple(
        tuple(fill(row, col) for col in range(size))
        for row in range(size)
    )


def get[T](grid: Grid[T], pos: Pos) -> T:
    return grid[pos[0]][pos[1]]


def set_cell[T](grid: Grid[T], pos: Pos, value: T) -> Grid[T]:
    row_idx, col_idx = pos
    old_row = grid[row_idx]
    new_row = old_row[:col_idx] + (value,) + old_row[col_idx + 1:]
    return grid[:row_idx] + (new_row,) + grid[row_idx + 1:]


def swap[T](grid: Grid[T], p1: Pos, p2: Pos) -> Grid[T]:
    v1 = get(grid, p1)
    v2 = get(grid, p2)
    after_first = set_cell(grid, p1, v2)
    return set_cell(after_first, p2, v1)


def all_positions(size: Size) -> tuple[Pos, ...]:
    return tuple(
        (row, col)
        for row in range(size)
        for col in range(size)
    )


def row_positions(row: int, size: Size) -> tuple[Pos, ...]:
    return tuple((row, col) for col in range(size))


def col_positions(col: int, size: Size) -> tuple[Pos, ...]:
    return tuple((row, col) for row in range(size))


def neighbors(pos: Pos, size: Size) -> tuple[Pos, ...]:
    row, col = pos
    candidates = ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1))
    return tuple(
        (r, c) for r, c in candidates
        if 0 <= r < size and 0 <= c < size
    )


def adjacent(p1: Pos, p2: Pos) -> bool:
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1
