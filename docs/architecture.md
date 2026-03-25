# Layered Functional Architecture

The game is structured as five pure layers plus a thin I/O shell.
Each layer adds exactly one concept and hides it behind a clean boundary.

```
Shell    api.ts          Stateful API for the frontend (only impure module)
Layer 4  rules.ts        Game mechanics
Layer 3  cascade.ts      Cascade step stream
Layer 2  match.ts        Pattern detection
Layer 1  board.ts        Elements on a grid
Layer 0  core.ts         Grid primitives
         rng.ts          Seedable PRNG
```

Import rule: a layer may only import from layers below it, never sideways or up.

All core modules live in `web/src/core/`. The frontend shell (`api.ts`, `controller.ts`,
`renderer.ts`, `animator.ts`) lives in `web/src/`.

---

## Layer 0 — `core.ts`: Grid Primitives

No game knowledge. Pure math on positions and 2D grids.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `Pos` | `readonly [number, number]` | (row, col) coordinate |
| `Size` | `number` | Board dimension, always > 0 |
| `Grid<T>` | `ReadonlyArray<ReadonlyArray<T>>` | Immutable square 2D array |

**Key functions**: `pipe`, `compose`, `makePos`, `makeGrid`, `get`, `setCell`, `swap`, `neighbors`, `adjacent`

**Utilities**: `posKey(pos)` encodes a `Pos` as `"row,col"` string for use as `Set`/`Map` keys.
`parsePos(key)` reverses the encoding.

**What it makes inexpressible**:
- `makePos` returns `null` for out-of-bounds coordinates — invalid positions cannot enter the system through the public API.
- `Grid` is `ReadonlyArray<ReadonlyArray<T>>` — mutation is a type error.
- `setCell` and `swap` return new grids.

---

## `rng.ts`: Seedable PRNG

Provides a seedable pseudo-random number generator (mulberry32).

| Name | Definition | Purpose |
|------|-----------|---------|
| `RNG` | `{ choice<T>(items: readonly T[]): T }` | Opaque RNG with a single method |

`createRNG(seed?)` returns an `RNG` instance. Internal state is encapsulated —
the only observable behavior is the sequence of `choice()` results.

RNG is always passed as an explicit parameter, never a module global.

---

## Layer 1 — `board.ts`: Elements on a Grid

Knows that cells contain elements. No knowledge of matches, moves, or scores.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `Element` | `{ readonly symbol: string }` | A single cell's content |
| `Board` | `Grid<Element>` | The playing field |
| `EMPTY` | `"0"` | Marker for an empty cell |
| `SYMBOLS` | `["A".."F"]` | Valid game symbols |

**Key functions**: `makeElement`, `isEmpty`, `symbolAt`, `applyGravity`, `fillEmpty`

**What it makes inexpressible**:
- `makeElement` returns `null` for invalid symbols — no way to construct a bad element through the public API.
- "Empty" is always an explicit `EMPTY` marker, never a null/undefined cell.
- `applyGravity` is pure: returns a new board with elements dropped to the bottom of each column.

---

## Layer 2 — `match.ts`: Pattern Detection

Knows what a "match" is. No knowledge of moves, scores, or effects.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `MatchKind` | `"line3" \| "line4" \| "line5" \| "cross"` | Pattern classification |
| `Match` | `{ kind, element, positions: ReadonlySet<string> }` | A detected pattern |

The key design decision: a match is a **set of position keys**, not a direction + start + length.
This representation naturally handles lines, crosses, T-shapes, and L-shapes —
any connected pattern is just a `ReadonlySet<string>` of `posKey`-encoded positions.

**Key functions**: `findMatches`, `findRuns`, `mergeCrosses`, `classifyMatch`

**How cross detection works**:
1. `findRuns` scans all rows and columns for 3+ consecutive same symbols.
2. `mergeCrosses` uses union-find to merge runs that share a position and the same element.
3. Merged groups get kind `"cross"`.

```
  B A B C          Horizontal run: {(1,0), (1,1), (1,2)}
  A A A D    ->    Vertical run:   {(0,1), (1,1), (2,1)}
  E A F C          Overlap at (1,1) + same symbol A
  G H I J          -> Cross: {(0,1), (1,0), (1,1), (1,2), (2,1)}
```

**What it makes inexpressible**:
- `makeMatch` returns `null` for fewer than 3 positions or EMPTY element.
- Matches always carry their element — impossible to have a match where positions disagree on symbol.

---

## Layer 3 — `cascade.ts`: Cascade Step Stream

Knows that matches change the board. No knowledge of player moves or scoring.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `CascadePhase` | `{ board_before, matches, cleared, fallen, filled }` | One complete cascade step with all intermediate boards |
| `CascadeResult` | `{ phases, board }` | Full cascade history |

This is the **step stream** that the frontend needs for animation.
Each phase captures every intermediate board state:

```
board_before  ->  matches found
                  cleared   (matched positions set to EMPTY)
                  fallen    (gravity applied)
                  filled    (empty cells filled with random symbols)
```

The cascade loops until no more matches are found. Each iteration produces one `CascadePhase`.

**Key functions**: `clearMatches`, `cascadeStep`, `runCascade`

**What it makes inexpressible**:
- `cascadeStep` returns `null` when the board is stable — no empty phase objects.
- Every phase captures the full before/after chain — no information loss between steps.

---

## Layer 4 — `rules.ts`: Game Mechanics

Knows what's valid and how to score. No I/O.

**Types**

| Name | Definition | Purpose |
|------|-----------|---------|
| `ValidMove` | `{ tag: "valid", cascade, score }` | Successful move result |
| `InvalidMove` | `{ tag: "invalid", reason }` | Failed move with explanation |
| `MoveResult` | `ValidMove \| InvalidMove` | Discriminated union — move always produces one or the other |
| `GameState` | `{ board, size, score, drowsiness, rng }` | Complete game snapshot |

**Scoring**: each `MatchKind` has a base score (line3=30, line4=80, line5=150, cross=200),
multiplied by the cascade phase number (phase 1 = 1x, phase 2 = 2x, etc.).

**Key functions**: `validateMove`, `scoreCascade`, `hasPossibleMoves`, `initializeBoard`, `tick`

**What it makes inexpressible**:
- `validateMove` returns `InvalidMove` for non-adjacent or non-matching swaps — no silent passthrough.
- Score is computed from cascade phases, not set directly.
- `initializeBoard` guarantees: no initial matches + at least one possible move.

---

## Shell — `api.ts`: Stateful API

The only module with mutable state. Thin bridge between the pure core and the frontend.

Holds a `GameState` and exposes three functions:
- `initGame(size)` — creates a new game, returns serialized state
- `tryMove(r1, c1, r2, c2)` — attempts a swap, returns `MoveResult` with cascade phases
- `getState()` — returns current state

Converts core types (typed `Element` objects, `ReadonlySet` positions) to frontend types
(plain `string[][]` boards, `[number, number][]` positions) at the serialization boundary.

---

## Frontend

The frontend is a thin animation layer over the pure core:

```
controller.ts   User input state machine (idle -> selected -> animating -> game_over)
renderer.ts     DOM construction and visual updates
animator.ts     Cascade phase animation with configurable timing
symbols.ts      Symbol-to-emoji mapping (A=sheep, B=cow, C=moon, D=star, E=cloud, F=sleep)
types.ts        Frontend type definitions (serialized forms of core types)
```

---

## Design Principles

### Functional core, imperative shell

Layers 0–4 are pure functions: immutable data in, new data out, no side effects.
Side effects (DOM manipulation, RNG creation) live only in `api.ts` and the frontend shell.
RNG is passed as an explicit parameter, not a module global.

### Make illegal states unrepresentable

Each layer uses smart constructors (`makePos`, `makeElement`, `makeMatch`) that return
`null` for invalid inputs. Discriminated unions (`ValidMove | InvalidMove`)
eliminate boolean flags and stringly-typed error handling.

### Pipeline style

Data flows top-to-bottom, one operation per line. `pipe(value, f, g, h)` instead of `h(g(f(value)))`.

### Why plain objects and not classes

Plain objects with `readonly` fields. No `constructor`, no `this`, no inheritance.
Construction is just `{ key: value }` — transparent data, no hidden behavior.

The tradeoff: objects are not hashable in JS, so match positions use `Set<string>` with
`posKey`-encoded position strings instead of `Set<Pos>`.
