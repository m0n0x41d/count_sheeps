const SYMBOL_EMOJI: Record<string, string> = {
    "A": "\uD83D\uDC11",
    "B": "\uD83D\uDC04",
    "C": "\uD83C\uDF19",
    "D": "\u2B50",
    "E": "\u2601\uFE0F",
    "F": "\uD83D\uDCA4",
    "0": "",
}

export function symbolToEmoji(symbol: string): string {
    return SYMBOL_EMOJI[symbol] ?? "?"
}
