from typing import Optional

from model.reference_price import ReferencePrice


class BinanceStore:
    def __init__(self):
        self.reference_prices: dict[str, ReferencePrice] = {}

    def get_reference_prices(self) -> list[ReferencePrice]:
        return list(self.reference_prices.values())

    def save_reference_price(self, reference_price: ReferencePrice):
        self.reference_prices[reference_price.symbol] = reference_price

    def get_reference_price_by_symbol(self, symbol: str) -> Optional[ReferencePrice]:
        return self.reference_prices[symbol]


binance_store = BinanceStore()
