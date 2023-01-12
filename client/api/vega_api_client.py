import logging
from typing import Optional

import requests

from model.account import Account
from model.asset import Asset
from model.config import config
from model.market import Market
from model.order import Order
from model.position import Position
from store.vega_store import vega_store
from submission.batch_market_instruction import BatchMarketInstruction
from submission.order_amendment import OrderAmendment
from submission.order_cancellation import OrderCancellation
from submission.order_submission import OrderSubmission
from utils.decimal_utils import convert_to_decimals


def parse_asset(node: dict) -> Asset:
    details = node["details"]
    return Asset(node["id"],
                 node["status"],
                 details["name"],
                 details["symbol"],
                 details["decimals"])


def parse_account(node: dict) -> Account:
    asset_id = node["asset"]
    asset = vega_store.get_asset_by_id(asset_id)
    if asset is None:
        pass  # Now what?
    balance = convert_to_decimals(asset.decimal_places, node["balance"])
    return Account(node["owner"],
                   node["type"],
                   balance,
                   asset_id,
                   node["marketId"])


def parse_order(node: dict) -> Order:
    market_id = node["marketId"]
    market = vega_store.get_market_by_id(market_id)
    if market is None:
        pass  # Now what?
    size = convert_to_decimals(market.position_decimal_places, node["size"])
    remaining = convert_to_decimals(market.position_decimal_places, node["remaining"])
    price = convert_to_decimals(market.decimal_places, node["size"])
    return Order(node["id"],
                 market_id,
                 size,
                 remaining,
                 price,
                 node["type"],
                 node["timeInForce"],
                 node["status"],
                 node["partyId"])


def parse_position(node: dict) -> Position:
    market_id = node["marketId"]
    market = vega_store.get_market_by_id(market_id)
    if market is None:
        pass  # Now what?
    asset = vega_store.get_asset_by_id(market.settlement_asset_id)
    if asset is None:
        pass  # Now what?
    open_volume = convert_to_decimals(market.position_decimal_places, node["openVolume"])
    average_entry_price = convert_to_decimals(market.decimal_places, node["averageEntryPrice"])
    realised_pnl = convert_to_decimals(asset.decimal_places, node["realisedPnl"])
    unrealised_pnl = convert_to_decimals(asset.decimal_places, node["unrealisedPnl"])
    return Position(node["partyId"], market_id, open_volume, average_entry_price, unrealised_pnl, realised_pnl)


def parse_market(node: dict) -> Market:
    instrument = node["tradableInstrument"]["instrument"]
    return Market(node["id"],
                  node["state"],
                  node["tradingMode"],
                  node["decimalPlaces"],
                  node["positionDecimalPlaces"],
                  instrument["code"],
                  instrument["name"],
                  instrument["future"]["settlementAsset"])


parsers = {
    'markets': parse_market,
    'assets': parse_asset,
    'accounts': parse_account,
    'orders': parse_order,
    'positions': parse_position
}


def execute_get_request(path: str, key: str):
    if parsers[key] is None:
        return []
    response = requests.get(f"{config.node_url}/{path}")
    if response.status_code != 200:
        logging.error(response.json())
        return []
    edges = response.json()[key]["edges"]
    results = []
    for edge in edges:
        results.append(parsers[key](edge["node"]))
    return results


def get_markets() -> list[Market]:
    return execute_get_request("markets", "markets")


def get_assets() -> list[Asset]:
    return execute_get_request("assets", "assets")


def get_accounts(party_id: str) -> list[Asset]:
    return execute_get_request(f"accounts?filter.partyIds={party_id}", "accounts")


def get_open_orders(party_id: str) -> list[Asset]:
    return execute_get_request(f"orders?partyId={party_id}&liveOnly=true", "orders")


def get_positions(party_id: str) -> list[Asset]:
    return execute_get_request(f"positions?partyId={party_id}", "positions")


def get_token() -> Optional[str]:
    response = requests.post(f"{config.wallet_url}/api/v1/auth/token", json={
        "wallet": config.wallet_username,
        "passphrase": config.wallet_password
    })
    if response.status_code != 200:
        logging.error(response.json())
        return Optional[None]
    return Optional[response.json()["token"]]


def send_batch_market_instruction(submissions: list[OrderSubmission],
                                  cancellations: list[OrderCancellation],
                                  amendments: list[OrderAmendment]) -> Optiona[str]:
    token = get_token()
    if token is not None:
        batch_market_instruction = BatchMarketInstruction(submissions, cancellations, amendments)
        payload = {
            'batchMarketInstructions': batch_market_instruction.__dict__,
            'pubKey': config.party_id,
            'propagate': True
        }
        response = requests.post(f"{config.wallet_url}/api/v1/auth/token",
                                 json=payload,
                                 headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            logging.error(response.json())
            return Optional[None]
        tx_hash = response.json()["txHash"]
        print_error_if_exists(tx_hash)
        return Optional[tx_hash]


def print_error_if_exists(tx_hash: str):
    print_error_if_exists_retry(tx_hash, 0)


def print_error_if_exists_retry(tx_hash: str, attempt: int):
    pass
