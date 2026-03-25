# Layered Functional Architecture

The game is structured as six layers, each building on the one below.
Every layer adds exactly one concept and hides it behind a clean boundary.

```
Layer 5  session.py    I/O shell (impure)
Layer 4  rules.py      Game mechanics
Layer 3  cascade.py    Cascade step stream
Layer 2  match.py      Pattern detection
Layer 1  board.py      Elements on a grid
Layer 0  core.py       Grid primitives
```

Import rule: a layer may only import from layers below it, never sideways or up.

---

## Layer 0 — `core.py`: Grid Primitives

No game knowledge. Pure math on positions and 2D grids.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `Pos` | `tuple[int, int]` | (row, col) coordinate |
| `Size` | `int` | Board dimension, always > 0 |
| `Grid[T]` | `tuple[tuple[T, ...], ...]` | Immutable square 2D array |

**Key functions**: `pipe`, `compose`, `make_pos`, `make_grid`, `get`, `set_cell`, `swap`, `neighbors`, `adjacent`

**What it makes inexpressible**:
- `make_pos` returns `None` for out-of-bounds coordinates — invalid positions cannot enter the system through the public API.
- `Grid` is a nested tuple — mutation is impossible.
- `set_cell` and `swap` return new grids.

---

## Layer 1 — `board.py`: Elements on a Grid

Knows that cells contain elements. No knowledge of matches, moves, or scores.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `Element` | `TypedDict` with `symbol: str` | A single cell's content |
| `Board` | `Grid[Element]` | The playing field |
| `EMPTY` | `"0"` | Marker for an empty cell |
| `SYMBOLS` | `("A".."F")` | Valid game symbols |

**Key functions**: `make_element`, `is_empty`, `symbol_at`, `apply_gravity`, `fill_empty`

**What it makes inexpressible**:
- `make_element` returns `None` for invalid symbols — no way to construct a bad element through the public API.
- "Empty" is always an explicit `EMPTY` marker, never a null/None cell.
- `apply_gravity` is pure: returns a new board with elements dropped to the bottom of each column.

---

## Layer 2 — `match.py`: Pattern Detection

Knows what a "match" is. No knowledge of moves, scores, or effects.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `MatchKind` | `Literal["line3", "line4", "line5", "cross"]` | Pattern classification |
| `Match` | `TypedDict` with `kind`, `element`, `positions: frozenset[Pos]` | A detected pattern |

The key design decision: a match is a **set of positions**, not a direction + start + length.
This representation naturally handles lines, crosses, T-shapes, and L-shapes —
any connected pattern is just a `frozenset[Pos]`.

**Key functions**: `find_matches`, `find_runs`, `merge_crosses`, `classify_match`

**How cross detection works**:
1. `find_runs` scans all rows and columns for 3+ consecutive same symbols.
2. `merge_crosses` uses union-find to merge runs that share a position and the same element.
3. Merged groups get kind `"cross"`.

```
  B A B C          Horizontal run: {(1,0), (1,1), (1,2)}
  A A A D    ->    Vertical run:   {(0,1), (1,1), (2,1)}
  E A F C          Overlap at (1,1) + same symbol A
  G H I J          -> Cross: {(0,1), (1,0), (1,1), (1,2), (2,1)}
```

**What it makes inexpressible**:
- `make_match` returns `None` for fewer than 3 positions or EMPTY element.
- Matches always carry their element — impossible to have a match where positions disagree on symbol.

---

## Layer 3 — `cascade.py`: Cascade Step Stream

Knows that matches change the board. No knowledge of player moves or scoring.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `CascadePhase` | `TypedDict` with `board_before`, `matches`, `cleared`, `fallen`, `filled` | One complete cascade step with all intermediate boards |
| `CascadeResult` | `TypedDict` with `phases` and final `board` | Full cascade history |

This is the **step stream** that the frontend needs for animation.
Each phase captures every intermediate board state:

```
board_before  ->  matches found
                  cleared   (matched positions set to EMPTY)
                  fallen    (gravity applied)
                  filled    (empty cells filled with random symbols)
```

The cascade loops until no more matches are found. Each iteration produces one `CascadePhase`.

**Key functions**: `clear_matches`, `cascade_step`, `run_cascade`

**What it makes inexpressible**:
- `cascade_step` returns `None` when the board is stable — no empty phase objects.
- Every phase captures the full before/after chain — no information loss between steps.

---

## Layer 4 — `rules.py`: Game Mechanics

Knows what's valid and how to score. No I/O.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `ValidMove` | `TypedDict` with `tag: "valid"`, `cascade`, `score` | Successful move result |
| `InvalidMove` | `TypedDict` with `tag: "invalid"`, `reason` | Failed move with explanation |
| `MoveResult` | `ValidMove \| InvalidMove` | Sum type — move always produces one or the other |
| `GameState` | `TypedDict` with `board`, `size`, `score`, `drowsiness`, `rng` | Complete game snapshot |

**Scoring**: each `MatchKind` has a base score (line3=30, line4=80, line5=150, cross=200),
multiplied by the cascade phase number (phase 1 = 1x, phase 2 = 2x, etc.).

**Key functions**: `validate_move`, `score_cascade`, `has_possible_moves`, `initialize_board`, `tick`

**What it makes inexpressible**:
- `validate_move` returns `InvalidMove` for non-adjacent or non-matching swaps — no silent passthrough.
- Score is computed from cascade phases, not set directly.
- `initialize_board` guarantees: no initial matches + at least one possible move.

---

## Layer 5 — `session.py`: I/O Shell (Impure)

The only layer with side effects. Thin shell over the pure core.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `SwapCmd` | `TypedDict` with `tag: "swap"`, `p1`, `p2` | Player swap command |
| `QuitCmd` | `TypedDict` with `tag: "quit"` | Exit command |
| `Command` | `SwapCmd \| QuitCmd` | Sum type for all commands |

**Key functions**: `parse_command`, `apply_command`, `render_board`, `run_game`

All parsing and validation happens here. Invalid input returns `None` or prints an error.
The game loop is a simple `while True` that reads, parses, applies, and renders.

---

## Design Principles

### Functional core, imperative shell

Layers 0–4 are pure functions: immutable data in, new data out, no side effects.
Side effects (console I/O, RNG creation) live only in layer 5.
RNG is passed as an explicit `Random` parameter, not a module global.

### Make illegal states unrepresentable

Each layer uses smart constructors (`make_pos`, `make_element`, `make_match`) that return
`None` for invalid inputs. Sum types (`ValidMove | InvalidMove`, `SwapCmd | QuitCmd`)
eliminate boolean flags and stringly-typed error handling.

### Pipeline style

Data flows top-to-bottom, one operation per line. `pipe(value, f, g, h)` instead of `h(g(f(value)))`.

### Why TypedDict and not dataclasses/NamedTuple

TypedDict gives us plain dicts with type annotations and `ReadOnly` fields.
No `__init__`, no `__eq__` magic, no inheritance hierarchy.
Construction is just `{"key": value}` — transparent data, no hidden behavior.

The tradeoff: dicts are not hashable, so `frozenset[Match]` is impossible.
We use `tuple[Match, ...]` for match collections instead.
Positions stay as `frozenset[Pos]` since `Pos = tuple[int, int]` is hashable.
