from market_maker.store.vega_store import VegaStore
from market_maker.store.binance_store import BinanceStore

from market_maker.config import Config
from market_maker.models import Market
from market_maker.submission import (
    OrderCancellation,
    OrderSubmission,
    BatchMarketInstruction,
    instruction_to_json,
)
from market_maker.wallet import VegaWallet
from market_maker.strategy.base import BaseStrategy

import dataclasses
import logging
import threading
import time


class SimpleMarketMaker(BaseStrategy):
    def __init__(
        self,
        binance_store: BinanceStore,
        vega_store: VegaStore,
        config: Config,
        wallet: VegaWallet,
        update_freq_seconds: int = 30,
    ):
        super().__init__(config=config)
        self._binance_store = binance_store
        self._vega_store = vega_store
        self._wallet = wallet
        self._update_freq_seconds = update_freq_seconds

    def get_total_balance(self, settlement_asset_id: str) -> float:
        balance = 0
        accounts = self._vega_store.get_accounts()
        for account in accounts:
            if (
                account.owner == self.config.party_id
                and account.asset_id == settlement_asset_id
            ):
                balance += account.balance
        return balance

    def build_order_submissions(
        self,
        reference_price: float,
        side: str,
        market: Market,
        target_volume: float,
    ) -> list[OrderSubmission]:
        """Generates a curve of five orders on a given side of
        the book with equal sizes.
        """
        submissions = []
        size = target_volume / 5
        for i in range(5):
            offset = (i + 1) * 0.002
            price = (
                reference_price * (1 - offset)
                if side == "BUY"
                else reference_price * (1 + offset)
            )
            submissions.append(
                OrderSubmission(
                    market.market_id,
                    size / price,
                    price,
                    "TIME_IN_FORCE_GTC",
                    "TYPE_LIMIT",
                    f"SIDE_{side}",
                )
            )
        return submissions

    def execute(self) -> None:
        logging.info("Executing trading strategy...")
        market = self._vega_store.get_market_by_id(self.config.market_id)
        if market:
            logging.info(f"Updating quotes for {market.name}")
            reference_price = self._binance_store.get_reference_price_by_symbol(
                self.config.binance_market
            )
            if reference_price:
                # First load current position for info
                position = self._vega_store.get_position_by_market_id(market.market_id)
                open_volume = position.open_volume if position else 0
                average_entry_price = position.average_entry_price if position else 0

                # Then current balance to correctly size orders
                balance = self.get_total_balance(market.settlement_asset_id)
                bid_volume = max(
                    (balance * 0.5) - (open_volume * average_entry_price), 0
                )
                offer_volume = max(
                    (balance * 0.5) + (open_volume * average_entry_price), 0
                )

                logging.info(
                    f"Open volume = {open_volume}; "
                    f"Entry price = {average_entry_price}; "
                    f"Notional exposure = {abs(open_volume * average_entry_price)}"
                )
                logging.info(
                    f"Bid volume = {bid_volume}; Offer volume = {offer_volume}"
                )

                # Now generate orders, first cancelling any which exist
                # then placing the new shape
                orders = self._vega_store.get_orders()
                cancellations = []

                # Simple setup, we will cancel all existing orders,
                # then replace new ones at the new levels we want.
                for order in orders:
                    cancellations.append(
                        OrderCancellation(order.order_id, order.market_id)
                    )

                buy_submissions = self.build_order_submissions(
                    reference_price.bid_price, "BUY", market, bid_volume
                )
                sell_submissions = self.build_order_submissions(
                    reference_price.ask_price, "SELL", market, offer_volume
                )
                submissions = sell_submissions + buy_submissions
                logging.info(
                    f"Cancellations = {len(cancellations)}; Amendments = 0; Submissions"
                    f" = {len(submissions)}"
                )
                batch_instruction = BatchMarketInstruction(
                    submissions=submissions, cancellations=cancellations, amendments=[]
                )

                self._wallet.submit_transaction(
                    instruction_to_json(
                        batch_instruction,
                        price_decimals=market.decimal_places,
                        position_decimals=market.position_decimal_places,
                    )
                )

    def _run(self):
        while True:
            self.execute()
            time.sleep(self._update_freq_seconds)

    def run(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
