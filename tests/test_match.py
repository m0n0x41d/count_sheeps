from conftest import board_from_symbols

from src.match import (
    classify_match,
    find_matches,
    find_runs,
    make_match,
    merge_crosses,
)


def test_make_match_valid() -> None:
    m = make_match("line3", {"symbol": "A"}, frozenset({(0, 0), (0, 1), (0, 2)}))
    assert m is not None
    assert m["kind"] == "line3"
    assert m["element"]["symbol"] == "A"
    assert len(m["positions"]) == 3


def test_make_match_rejects_too_few_positions() -> None:
    assert make_match("line3", {"symbol": "A"}, frozenset({(0, 0), (0, 1)})) is None


def test_make_match_rejects_empty_element() -> None:
    assert make_match("line3", {"symbol": "0"}, frozenset({(0, 0), (0, 1), (0, 2)})) is None


def test_classify_match_by_count() -> None:
    assert classify_match(frozenset({(0, 0), (0, 1), (0, 2)})) == "line3"
    assert classify_match(frozenset({(0, 0), (0, 1), (0, 2), (0, 3)})) == "line4"
    assert classify_match(frozenset({(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)})) == "line5"


def test_find_runs_horizontal() -> None:
    board = board_from_symbols(
        "AAAB",
        "CDEF",
        "GHIJ",
        "KLMN",
    )
    runs = find_runs(board, 4)
    assert len(runs) == 1
    assert runs[0]["kind"] == "line3"
    assert runs[0]["element"]["symbol"] == "A"
    assert runs[0]["positions"] == frozenset({(0, 0), (0, 1), (0, 2)})


def test_find_runs_vertical() -> None:
    board = board_from_symbols(
        "ABCD",
        "AEFC",
        "AGHC",
        "BIJC",
    )
    runs = find_runs(board, 4)
    assert len(runs) == 2

    symbols = {r["element"]["symbol"] for r in runs}
    assert symbols == {"A", "C"}


def test_find_runs_ignores_empty_cells() -> None:
    board = board_from_symbols(
        "0AA",
        "BC0",
        "DEF",
    )
    runs = find_runs(board, 3)
    assert len(runs) == 0


def test_find_runs_horizontal_and_vertical() -> None:
    board = board_from_symbols(
        "AAAX",
        "BCDX",
        "EFGX",
        "HIJX",
    )
    runs = find_runs(board, 4)
    assert len(runs) == 2

    kinds = {(r["element"]["symbol"], r["kind"]) for r in runs}
    assert ("A", "line3") in kinds
    assert ("X", "line4") in kinds


def test_merge_crosses_detects_cross_pattern() -> None:
    board = board_from_symbols(
        "BABC",
        "AAAD",
        "EAFC",
        "GHIJ",
    )
    runs = find_runs(board, 4)
    merged = merge_crosses(runs)

    crosses = [m for m in merged if m["kind"] == "cross"]
    assert len(crosses) == 1
    assert crosses[0]["element"]["symbol"] == "A"
    assert (1, 0) in crosses[0]["positions"]
    assert (1, 1) in crosses[0]["positions"]
    assert (1, 2) in crosses[0]["positions"]
    assert (0, 1) in crosses[0]["positions"]
    assert (2, 1) in crosses[0]["positions"]


def test_merge_crosses_keeps_independent_runs() -> None:
    board = board_from_symbols(
        "AAAB",
        "CDEF",
        "GHIJ",
        "BBBK",
    )
    runs = find_runs(board, 4)
    merged = merge_crosses(runs)
    assert len(merged) == 2
    assert all(m["kind"] == "line3" for m in merged)


def test_find_matches_end_to_end() -> None:
    board = board_from_symbols(
        "BABC",
        "AAAD",
        "EAFC",
        "GHIJ",
    )
    matches = find_matches(board, 4)
    crosses = [m for m in matches if m["kind"] == "cross"]
    assert len(crosses) == 1


def test_find_matches_no_matches_on_clean_board() -> None:
    board = board_from_symbols(
        "ABCD",
        "EFAB",
        "CDEF",
        "ABCD",
    )
    assert find_matches(board, 4) == ()


def test_find_matches_line4() -> None:
    board = board_from_symbols(
        "AAAA",
        "BCDE",
        "FGHI",
        "JKLM",
    )
    matches = find_matches(board, 4)
    assert len(matches) == 1
    assert matches[0]["kind"] == "line4"


def test_find_matches_line5() -> None:
    board = board_from_symbols(
        "AAAAAB",
        "BCDEFG",
        "HIJKLM",
        "NOPQRS",
        "TUVWXY",
        "ZABCDE",
    )
    matches = find_matches(board, 6)
    assert len(matches) == 1
    assert matches[0]["kind"] == "line5"
