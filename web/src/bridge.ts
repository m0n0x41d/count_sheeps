import type { GameState, MoveResult } from "./types"

import initPy from "../../src/__init__.py?raw"
import corePy from "../../src/core.py?raw"
import boardPy from "../../src/board.py?raw"
import matchPy from "../../src/match.py?raw"
import cascadePy from "../../src/cascade.py?raw"
import rulesPy from "../../src/rules.py?raw"
import apiPy from "../../src/api.py?raw"

const PY_FILES: [string, string][] = [
    ["__init__.py", initPy],
    ["core.py", corePy],
    ["board.py", boardPy],
    ["match.py", matchPy],
    ["cascade.py", cascadePy],
    ["rules.py", rulesPy],
    ["api.py", apiPy],
]

let initGame: (size: number) => string
let tryMoveRaw: (r1: number, c1: number, r2: number, c2: number) => string
let getStateRaw: () => string

export async function loadBridge(): Promise<void> {
    const pyodide = await loadPyodide()

    pyodide.FS.mkdir("/src")
    for (const [name, content] of PY_FILES) {
        pyodide.FS.writeFile(`/src/${name}`, content)
    }

    pyodide.runPython(`
import sys
sys.path.insert(0, "/")
from src.api import init_game, try_move, get_state
`)

    initGame = pyodide.globals.get("init_game") as typeof initGame
    tryMoveRaw = pyodide.globals.get("try_move") as typeof tryMoveRaw
    getStateRaw = pyodide.globals.get("get_state") as typeof getStateRaw
}

export function bridgeInitGame(size: number): GameState {
    return JSON.parse(initGame(size))
}

export function bridgeTryMove(
    r1: number, c1: number,
    r2: number, c2: number,
): MoveResult {
    return JSON.parse(tryMoveRaw(r1, c1, r2, c2))
}

export function bridgeGetState(): GameState {
    return JSON.parse(getStateRaw())
}
