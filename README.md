# Count Sheep

A Match-3 puzzle game built as an exercise in data-first functional programming with TypeScript.

The goal is to explore how far functional patterns — immutable data, discriminated unions, pure functions,
pipeline composition — can carry game logic without reaching for OOP.

**[Play online](https://ivanzakutnii.com/count_sheeps/)**

## Quick start

```bash
cd web
npm install
npm run dev       # dev server with hot reload
npm run build     # production build
```

## How to play

The board displays emoji symbols on an 8x8 grid. Tap two adjacent cells
to swap them. If the swap creates a line of 3+ matching symbols,
those cells are cleared, tiles drop via gravity, and empty spaces are refilled.
Cascades (chain reactions) score extra.

## Project structure

```
web/src/
  core/
    core.ts       # Layer 0: Grid primitives (Pos, Grid, pipe)
    board.ts      # Layer 1: Elements, gravity, fill
    match.ts      # Layer 2: Pattern detection (lines + crosses)
    cascade.ts    # Layer 3: Cascade step stream for animation
    rules.ts      # Layer 4: Validation, scoring, game state
    rng.ts        # Seedable PRNG
  api.ts          # Stateful API bridge (only impure module)
  controller.ts   # User input state machine
  renderer.ts     # DOM rendering
  animator.ts     # Cascade animation
  symbols.ts      # Symbol-to-emoji mapping
  types.ts        # Frontend type definitions
docs/
  architecture.md
```

Each layer imports only from layers below it. Pure logic in layers 0–4, side effects only in the shell.

## Documentation

- [Architecture](docs/architecture.md) — layered design, types, what each layer makes inexpressible
