class ReferencePrice:
    def __init__(self, symbol: str, bid_price: float, ask_price: float):
        self.symbol: str = symbol
        self.bid_price: float = bid_price
        self.ask_price: float = ask_price
