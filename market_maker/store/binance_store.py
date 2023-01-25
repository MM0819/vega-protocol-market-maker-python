from threading import Lock
from typing import Any, Optional

from binance import ThreadedWebsocketManager
from binance.client import Client

from market_maker.config import Config
from market_maker.models import ReferencePrice


class BinanceStore:
    def __init__(self, symbols_to_subscribe: list[str]):
        """Runs a websocket client listening to a list of binance tickers
        and storing their latest best bid/ask prices to be consumed later.

        Start the client by calling `start`.

        Args:
            symbols_to_subscribe:
                list[str], list of binance symbols to which to listen
        """
        self._ws_client = ThreadedWebsocketManager()
        self._client = Client()

        self._symbols = symbols_to_subscribe
        self._lock = Lock()

        # Elements in a list to allow atomic updates and avoid locks
        self._reference_prices = {}

    def start(self) -> None:
        """Start the websocket client, listening to passed symbols
        and storing their market data on each tick to be read on demand
        by trader.
        """
        for symb in self._symbols:
            ticker = self._client.get_orderbook_ticker(symbol=symb)
            self._reference_prices[ticker["symbol"]] = ReferencePrice(
                symbol=ticker["symbol"],
                bid_price=float(ticker["bidPrice"]),
                ask_price=float(ticker["askPrice"]),
            )

        self._ws_client.start()
        self._ws_client.start_multiplex_socket(
            callback=self._on_tick,
            streams=[f"{symb.lower()}@bookTicker" for symb in self._symbols],
        )

    def stop(self) -> None:
        """Stops the websocket client"""
        self._ws_client.stop()

    def _on_tick(self, tick: dict[str, Any]) -> None:
        tick_data = tick["data"]
        ref_price = ReferencePrice(
            symbol=tick_data["s"],
            bid_price=float(tick_data["b"]),
            ask_price=float(tick_data["a"]),
        )
        with self._lock:
            self._reference_prices[ref_price.symbol] = ref_price

    def get_reference_prices(self) -> list[ReferencePrice]:
        with self._lock:
            return list(self._reference_prices.values())

    def get_reference_price_by_symbol(self, symbol: str) -> Optional[ReferencePrice]:
        with self._lock:
            return self._reference_prices[symbol]
