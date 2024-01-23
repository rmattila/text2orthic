# symbols that are not connected to each other when printed and for which
# no double-letter symbol should be rendered
SPECIAL_SYMBOLS = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "0",
    ";",
    ",",
    ":",
    ".",
    "?",
    "-",
]


class Glyph:
    def __init__(self, symbol: str, capital: bool = False, double: bool = False):
        self.symbol = symbol
        self.capital = capital
        self.double = double

    def __repr__(self):
        return (
            f"Glyph(symbol={self.symbol}, capital={self.capital}, double={self.double})"
        )
