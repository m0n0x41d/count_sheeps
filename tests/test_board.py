from conftest import MockRNG, board_from_symbols, symbols_from_board

from src.board import (
    EMPTY,
    apply_gravity,
    empty_positions,
    fill_empty,
    is_empty,
    make_element,
    make_empty_board,
    symbol_at,
)


def test_make_element_valid_symbol() -> None:
    elem = make_element("A")
    assert elem is not None
    assert elem["symbol"] == "A"


def test_make_element_empty() -> None:
    elem = make_element(EMPTY)
    assert elem is not None
    assert elem["symbol"] == EMPTY


def test_make_element_invalid_returns_none() -> None:
    assert make_element("Z") is None
    assert make_element("AB") is None
    assert make_element("") is None


def test_is_empty() -> None:
    assert is_empty({"symbol": EMPTY}) is True
    assert is_empty({"symbol": "A"}) is False


def test_make_empty_board() -> None:
    board = make_empty_board(3)
    assert symbols_from_board(board) == ("000", "000", "000")


def test_symbol_at() -> None:
    board = board_from_symbols("AB", "CD")
    assert symbol_at(board, (0, 0)) == "A"
    assert symbol_at(board, (1, 1)) == "D"


def test_empty_positions() -> None:
    board = board_from_symbols(
        "A0B",
        "00C",
        "DEF",
    )
    result = empty_positions(board, 3)
    assert result == frozenset({(0, 1), (1, 0), (1, 1)})


def test_apply_gravity_drops_elements_down() -> None:
    board = board_from_symbols(
        "A00",
        "0B0",
        "00C",
    )
    result = apply_gravity(board, 3)
    assert symbols_from_board(result) == (
        "000",
        "000",
        "ABC",
    )


def test_apply_gravity_preserves_order() -> None:
    board = board_from_symbols(
        "A0",
        "B0",
    )
    result = apply_gravity(board, 2)
    assert symbols_from_board(result) == ("A0", "B0")


def test_apply_gravity_column_with_gaps() -> None:
    board = board_from_symbols(
        "A00",
        "000",
        "B00",
    )
    result = apply_gravity(board, 3)
    assert symbols_from_board(result) == (
        "000",
        "A00",
        "B00",
    )


def test_fill_empty_replaces_only_empty_cells() -> None:
    board = board_from_symbols(
        "0A0",
        "BC0",
        "DEF",
    )
    rng = MockRNG(["X", "Y", "Z"])
    result = fill_empty(board, 3, rng)  # type: ignore[arg-type]
    assert symbols_from_board(result) == (
        "XAY",
        "BCZ",
        "DEF",
    )
