import { symbolToSprite } from "./symbols"
import type { Board, Pos, SerializedMatch } from "./types"

let boardEl: HTMLElement
let scoreEl: HTMLElement
let drowsinessBar: HTMLElement
let messageEl: HTMLElement
let size: number

export function createUI(container: HTMLElement, boardSize: number): void {
    size = boardSize
    container.innerHTML = ""

    const hud = document.createElement("div")
    hud.className = "hud"

    scoreEl = document.createElement("div")
    scoreEl.className = "score"
    scoreEl.textContent = "Score: 0"

    const drowsinessContainer = document.createElement("div")
    drowsinessContainer.className = "drowsiness-container"

    const drowsinessLabel = document.createElement("span")
    drowsinessLabel.textContent = "\uD83D\uDCA4 "

    drowsinessBar = document.createElement("div")
    drowsinessBar.className = "drowsiness-bar"
    const drowsinessFill = document.createElement("div")
    drowsinessFill.className = "drowsiness-fill"
    drowsinessBar.appendChild(drowsinessFill)

    drowsinessContainer.appendChild(drowsinessLabel)
    drowsinessContainer.appendChild(drowsinessBar)

    hud.appendChild(scoreEl)
    hud.appendChild(drowsinessContainer)
    container.appendChild(hud)

    boardEl = document.createElement("div")
    boardEl.className = "board"
    boardEl.style.gridTemplateColumns = `repeat(${size}, 1fr)`

    for (let row = 0; row < size; row++) {
        for (let col = 0; col < size; col++) {
            const cell = document.createElement("div")
            cell.className = "cell"
            cell.dataset.row = String(row)
            cell.dataset.col = String(col)
            boardEl.appendChild(cell)
        }
    }
    container.appendChild(boardEl)

    messageEl = document.createElement("div")
    messageEl.className = "message"
    container.appendChild(messageEl)
}

export function getBoardElement(): HTMLElement {
    return boardEl
}

function cellAt(row: number, col: number): HTMLElement | null {
    return boardEl.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`)
}

function setCellSprite(cell: HTMLElement, symbol: string): void {
    const src = symbolToSprite(symbol)
    if (!src) {
        cell.innerHTML = ""
        return
    }
    const existing = cell.querySelector("img")
    if (existing) {
        existing.src = src
    } else {
        const img = document.createElement("img")
        img.src = src
        img.draggable = false
        cell.innerHTML = ""
        cell.appendChild(img)
    }
}

export function renderBoard(board: Board): void {
    const cells = boardEl.querySelectorAll<HTMLElement>(".cell")
    cells.forEach(cell => {
        const row = Number(cell.dataset.row)
        const col = Number(cell.dataset.col)
        setCellSprite(cell, board[row][col])
        cell.className = "cell"
    })
}

export function selectCell(pos: Pos): void {
    const cell = cellAt(pos[0], pos[1])
    if (cell) cell.classList.add("selected")
}

export function deselectAll(): void {
    boardEl.querySelectorAll(".selected").forEach(el =>
        el.classList.remove("selected"),
    )
}

export function highlightMatches(matches: SerializedMatch[]): void {
    for (const match of matches) {
        for (const [row, col] of match.positions) {
            const cell = cellAt(row, col)
            if (cell) cell.classList.add("matched")
        }
    }
}

export function clearCells(board: Board): void {
    for (let row = 0; row < size; row++) {
        for (let col = 0; col < size; col++) {
            if (board[row][col] === "0") {
                const cell = cellAt(row, col)
                if (cell) {
                    cell.classList.add("clearing")
                    cell.innerHTML = ""
                }
            }
        }
    }
}

export function renderBoardAnimated(board: Board): void {
    const cells = boardEl.querySelectorAll<HTMLElement>(".cell")
    cells.forEach(cell => {
        const row = Number(cell.dataset.row)
        const col = Number(cell.dataset.col)
        const symbol = board[row][col]
        const wasEmpty = !cell.querySelector("img")
        cell.className = "cell"
        setCellSprite(cell, symbol)
        if (wasEmpty && symbol !== "0") {
            cell.classList.add("filling")
        }
    })
}

export function updateScore(score: number): void {
    scoreEl.textContent = `Score: ${score}`
}

export function updateDrowsiness(drowsiness: number): void {
    const fill = drowsinessBar.querySelector<HTMLElement>(".drowsiness-fill")
    if (fill) {
        fill.style.width = `${drowsiness * 100}%`
    }
}

export function showMessage(text: string): void {
    messageEl.textContent = text
    messageEl.classList.add("visible")
    setTimeout(() => messageEl.classList.remove("visible"), 2000)
}

export function showGameOver(score: number, onRestart: () => void): void {
    const overlay = document.createElement("div")
    overlay.className = "game-over-overlay"
    overlay.innerHTML = `
        <div class="game-over-content">
            <h2>Game Over</h2>
            <p>Final Score: ${score}</p>
            <button class="restart-btn">New Game</button>
        </div>
    `
    overlay.querySelector(".restart-btn")!.addEventListener("click", () => {
        overlay.remove()
        onRestart()
    })
    document.getElementById("app")!.appendChild(overlay)
}
