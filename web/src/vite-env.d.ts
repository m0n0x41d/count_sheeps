/// <reference types="vite/client" />

interface PyodideInterface {
    FS: {
        mkdir(path: string): void
        writeFile(path: string, data: string): void
    }
    runPython(code: string): unknown
    globals: {
        get(name: string): (...args: unknown[]) => unknown
    }
}

declare function loadPyodide(): Promise<PyodideInterface>
