class Glyph:
    def __init__(self, symbol: str, capital: bool = False, double: bool = False):
        self.symbol = symbol
        self.capital = capital
        self.double = double

    def __repr__(self):
        return (
            f"Glyph(symbol={self.symbol}, capital={self.capital}, double={self.double})"
        )
