from store.vega_store import vega_store
from store.binance_store import binance_store
from model.config import config
from model.order import Order
from model.market import Market
from submission.order_cancellation import OrderCancellation
from submission.order_submission import OrderSubmission
from client.api.vega_api_client import VegaApiClient
import logging


def get_total_balance(settlement_asset_id: str) -> float:
    balance = 0
    accounts = vega_store.get_accounts()
    for account in accounts:
        if account.owner == config.party_id and account.asset_id == settlement_asset_id:
            balance += account.balance
    return balance


def add_order_submissions(submissions: list[OrderSubmission], reference_price: float, side: str,
                          market: Market, target_volume: float):
    size = target_volume / 5
    for i in range(5):
        offset = (i + 1) * 0.002
        price = reference_price * (1 - offset) if side == "BUY" else reference_price * (1 + offset)
        submissions.append(
            OrderSubmission(market.market_id, size, price, "TIME_IN_FORCE_GTC", "TYPE_LIMIT", f"SIDE_{side}")
        )


def execute():
    logging.info("Executing trading strategy...")
    market = vega_store.get_market_by_id(config.market_id)
    if market:
        logging.info(f"Updating quotes for {market.name}")
        reference_price = binance_store.get_reference_price_by_symbol(config.binance_market)
        if reference_price:
            position = vega_store.get_position_by_market_id(market.market_id)
            open_volume = position.open_volume if position else 0
            average_entry_price = position.average_entry_price if position else 0
            balance = get_total_balance(market.settlement_asset_id)
            bid_volume = (balance * 0.5) - (open_volume * average_entry_price)
            offer_volume = (balance * 0.5) + (open_volume * average_entry_price)
            bid_volume = max(bid_volume, 0)
            offer_volume = max(offer_volume, 0)
            notional_exposure = abs(open_volume * average_entry_price)
            logging.info(f"Open volume = {open_volume}; "
                         f"Entry price = {average_entry_price}; "
                         f"Notional exposure = {notional_exposure}")
            logging.info(f"Bid volume = {bid_volume}; "
                         f"Offer volume = {offer_volume}")
            orders = vega_store.get_orders()
            cancellations = []
            submissions = []
            for order in orders:
                cancellations.append(OrderCancellation(order.order_id, order.market_id))
            add_order_submissions(submissions, reference_price.bid_price, "BUY", market, bid_volume)
            add_order_submissions(submissions, reference_price.ask_price, "BUY", market, offer_volume)
            logging.info(f"Cancellations = {len(cancellations)}; Amendments = 0; Submissions = {len(submissions)}")
            # TODO - send batch market instruction


simple_market_maker = SimpleMarketMaker()
