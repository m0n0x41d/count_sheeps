# Functional Match-3

A Match-3 puzzle game built as an exercise in data-first functional programming with Python 3.13.

The goal is to explore how far functional patterns — immutable data, sum types, pure functions,
pipeline composition — can carry game logic without reaching for OOP.

## Quick start

```bash
task run          # play in the console
task test         # run the test suite
```

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

## How to play

The board displays symbols A–F on an 8x8 grid. Enter moves as `row col row1 col1`
to swap two adjacent cells. If the swap creates a line of 3+ matching symbols,
those cells are cleared, tiles drop via gravity, and empty spaces are refilled.
Cascades (chain reactions) score extra. Type `q` to quit.

## Project structure

```
src/
  core.py       # Layer 0: Grid primitives (Pos, Grid, pipe)
  board.py      # Layer 1: Elements, gravity, fill
  match.py      # Layer 2: Pattern detection (lines + crosses)
  cascade.py    # Layer 3: Cascade step stream for animation
  rules.py      # Layer 4: Validation, scoring, game state
  session.py    # Layer 5: Console I/O shell (only impure layer)
tests/
  test_core.py, test_board.py, test_match.py, test_cascade.py, test_rules.py
docs/
  architecture.md
```

Each layer imports only from layers below it. Pure logic in layers 0–4, side effects only in layer 5.

## Documentation

- [Architecture](docs/architecture.md) — layered design, types, what each layer makes inexpressible
