import type { CascadePhase } from "./types"
import {
    renderBoard,
    highlightMatches,
    clearCells,
    renderBoardAnimated,
} from "./renderer"

export type AnimationTiming = {
    matchHighlight: number
    clear: number
    drop: number
    fill: number
}

const DEFAULT_TIMING: AnimationTiming = {
    matchHighlight: 500,
    clear: 300,
    drop: 300,
    fill: 250,
}

function delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
}

export async function animateCascade(
    phases: CascadePhase[],
    timing: AnimationTiming = DEFAULT_TIMING,
): Promise<void> {
    for (const phase of phases) {
        renderBoard(phase.board_before)
        highlightMatches(phase.matches)
        await delay(timing.matchHighlight)

        clearCells(phase.cleared)
        await delay(timing.clear)

        renderBoardAnimated(phase.fallen)
        await delay(timing.drop)

        renderBoardAnimated(phase.filled)
        await delay(timing.fill)
    }
}
