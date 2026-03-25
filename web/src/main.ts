import { loadBridge } from "./bridge"
import { startGame } from "./controller"
import "./style.css"

async function main(): Promise<void> {
    const loading = document.getElementById("loading")!
    loading.textContent = "Loading Pyodide..."

    try {
        await loadBridge()
        startGame()
    } catch (err) {
        loading.textContent = `Failed to load: ${err}`
        console.error(err)
    }
}

main()
