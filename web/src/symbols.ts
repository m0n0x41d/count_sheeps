const SYMBOL_SPRITE: Record<string, string> = {
    "A": "./sprites/sheep_pink.png",
    "B": "./sprites/sheep_blue.png",
    "C": "./sprites/sheep_yellow.png",
    "D": "./sprites/sheep_white.png",
    "E": "./sprites/sheep_black.png",
    "F": "./sprites/sheep_brown.png",
    "0": "",
}

export function symbolToSprite(symbol: string): string {
    return SYMBOL_SPRITE[symbol] ?? ""
}
