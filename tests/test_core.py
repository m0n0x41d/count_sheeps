from src.core import (
    adjacent,
    all_positions,
    col_positions,
    compose,
    get,
    make_grid,
    make_pos,
    neighbors,
    pipe,
    row_positions,
    set_cell,
    swap,
)


def test_pipe_chains_functions_left_to_right() -> None:
    result = pipe(1, lambda x: x + 1, lambda x: x * 3)
    assert result == 6


def test_pipe_with_no_functions_returns_value() -> None:
    assert pipe(42) == 42


def test_compose_returns_callable_chain() -> None:
    add_then_mul = compose(lambda x: x + 1, lambda x: x * 3)
    assert add_then_mul(1) == 6


def test_make_pos_valid() -> None:
    assert make_pos(0, 0, 3) == (0, 0)
    assert make_pos(2, 2, 3) == (2, 2)


def test_make_pos_out_of_bounds() -> None:
    assert make_pos(-1, 0, 3) is None
    assert make_pos(0, 3, 3) is None
    assert make_pos(3, 0, 3) is None


def test_make_grid_fills_with_callable() -> None:
    grid = make_grid(2, lambda r, c: r * 10 + c)
    assert grid == ((0, 1), (10, 11))


def test_get_returns_cell_value() -> None:
    grid = ((1, 2), (3, 4))
    assert get(grid, (0, 0)) == 1
    assert get(grid, (1, 1)) == 4


def test_set_cell_returns_new_grid() -> None:
    grid = ((1, 2), (3, 4))
    new_grid = set_cell(grid, (0, 1), 99)
    assert new_grid == ((1, 99), (3, 4))
    assert grid == ((1, 2), (3, 4))


def test_swap_exchanges_two_cells() -> None:
    grid = ((1, 2), (3, 4))
    swapped = swap(grid, (0, 0), (1, 1))
    assert swapped == ((4, 2), (3, 1))


def test_all_positions_returns_all_coords() -> None:
    positions = all_positions(2)
    assert positions == ((0, 0), (0, 1), (1, 0), (1, 1))


def test_row_positions() -> None:
    assert row_positions(1, 3) == ((1, 0), (1, 1), (1, 2))


def test_col_positions() -> None:
    assert col_positions(1, 3) == ((0, 1), (1, 1), (2, 1))


def test_neighbors_center() -> None:
    result = neighbors((1, 1), 3)
    assert set(result) == {(0, 1), (2, 1), (1, 0), (1, 2)}


def test_neighbors_corner() -> None:
    result = neighbors((0, 0), 3)
    assert set(result) == {(1, 0), (0, 1)}


def test_adjacent_true() -> None:
    assert adjacent((0, 0), (0, 1)) is True
    assert adjacent((0, 0), (1, 0)) is True


def test_adjacent_false() -> None:
    assert adjacent((0, 0), (1, 1)) is False
    assert adjacent((0, 0), (0, 2)) is False
    assert adjacent((0, 0), (0, 0)) is False
