export type Pos = [number, number]
export type Board = string[][]
export type MatchKind = "line3" | "line4" | "line5" | "cross"

export type SerializedMatch = {
    kind: MatchKind
    symbol: string
    positions: Pos[]
}

export type CascadePhase = {
    board_before: Board
    matches: SerializedMatch[]
    cleared: Board
    fallen: Board
    filled: Board
}

export type GameState = {
    board: Board
    size: number
    score: number
    drowsiness: number
}

export type ValidMoveResult = {
    tag: "valid"
    score: number
    phases: CascadePhase[]
    state: GameState
    has_possible_moves: boolean
}

export type InvalidMoveResult = {
    tag: "invalid"
    reason: string
}

export type MoveResult = ValidMoveResult | InvalidMoveResult
