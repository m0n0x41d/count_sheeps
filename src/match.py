from typing import Literal, ReadOnly, TypedDict

from src.core import Pos, Size, get
from src.board import Board, Element, EMPTY, symbol_at

type MatchKind = Literal["line3", "line4", "line5", "cross"]


class Match(TypedDict):
    kind: ReadOnly[MatchKind]
    element: ReadOnly[Element]
    positions: ReadOnly[frozenset[Pos]]


def make_match(kind: MatchKind, element: Element, positions: frozenset[Pos]) -> Match | None:
    if len(positions) < 3 or element["symbol"] == EMPTY:
        return None
    return {"kind": kind, "element": element, "positions": positions}


def classify_match(positions: frozenset[Pos]) -> MatchKind:
    count = len(positions)
    if count >= 5:
        return "line5"
    if count == 4:
        return "line4"
    return "line3"


def _run_to_match(board: Board, line: tuple[Pos, ...], start: int, end: int) -> Match | None:
    positions = frozenset(line[start:end])
    element = get(board, line[start])
    kind = classify_match(positions)
    return make_match(kind, element, positions)


def _scan_line(board: Board, line: tuple[Pos, ...]) -> tuple[Match, ...]:
    if len(line) < 3:
        return ()

    segments: list[tuple[int, int]] = []
    start = 0

    for i in range(1, len(line)):
        curr_sym = symbol_at(board, line[i])
        start_sym = symbol_at(board, line[start])

        if curr_sym != start_sym or curr_sym == EMPTY:
            if i - start >= 3 and start_sym != EMPTY:
                segments.append((start, i))
            start = i

    start_sym = symbol_at(board, line[start])
    if len(line) - start >= 3 and start_sym != EMPTY:
        segments.append((start, len(line)))

    return tuple(
        match
        for s, e in segments
        if (match := _run_to_match(board, line, s, e)) is not None
    )


def find_runs(board: Board, size: Size) -> tuple[Match, ...]:
    runs: list[Match] = []

    for row in range(size):
        line = tuple((row, col) for col in range(size))
        runs.extend(_scan_line(board, line))

    for col in range(size):
        line = tuple((row, col) for row in range(size))
        runs.extend(_scan_line(board, line))

    return tuple(runs)


def merge_crosses(runs: tuple[Match, ...]) -> tuple[Match, ...]:
    n = len(runs)
    if n == 0:
        return ()

    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i in range(n):
        for j in range(i + 1, n):
            if (runs[i]["element"]["symbol"] == runs[j]["element"]["symbol"]
                    and runs[i]["positions"] & runs[j]["positions"]):
                union(i, j)

    groups: dict[int, list[int]] = {}
    for i in range(n):
        root = find(i)
        groups.setdefault(root, []).append(i)

    result: list[Match] = []
    for members in groups.values():
        if len(members) == 1:
            result.append(runs[members[0]])
        else:
            all_positions = frozenset().union(*(runs[i]["positions"] for i in members))
            element = runs[members[0]]["element"]
            result.append({"kind": "cross", "element": element, "positions": all_positions})

    return tuple(result)


def find_matches(board: Board, size: Size) -> tuple[Match, ...]:
    runs = find_runs(board, size)
    return merge_crosses(runs)
