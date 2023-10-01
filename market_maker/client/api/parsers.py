import logging
import time
from typing import Optional

import requests

from market_maker.models import Account, Asset, Market, Order, Position
from market_maker.submission import (
    BatchMarketInstruction,
    OrderAmendment,
    OrderCancellation,
    OrderSubmission,
)
from market_maker.config import Config
from market_maker.utils.decimal_utils import convert_to_decimals


def parse_asset(node: dict) -> Asset:
    details = node["details"]
    return Asset(
        node["id"],
        node["status"],
        details["name"],
        details["symbol"],
        int(details["decimals"]),
    )


def parse_account(node: dict, asset_decimal_places: int) -> Account:
    return Account(
        node["owner"],
        node["type"],
        convert_to_decimals(asset_decimal_places, float(node["balance"])),
        node["asset"],
        node["marketId"],
    )


def parse_order(
    node: dict, position_decimal_places: int, price_decimal_places: int
) -> Order:
    if "remaining" in node:
        return Order(
            node["id"],
            node["marketId"],
            convert_to_decimals(position_decimal_places, float(node["size"])),
            convert_to_decimals(position_decimal_places, float(node["remaining"])),
            convert_to_decimals(price_decimal_places, float(node["price"])),
            node["type"],
            node["timeInForce"],
            node["status"],
            node["partyId"],
    )
    else:
        return Order(
            node["id"],
            node["marketId"],
            convert_to_decimals(position_decimal_places, float(node["size"])),
            0,
            convert_to_decimals(price_decimal_places, float(node["price"])),
            node["type"],
            node["timeInForce"],
            node["status"],
            node["partyId"],
        )


def parse_position(
    node: dict,
    position_decimal_places: int,
    price_decimal_places: int,
    asset_decimal_places: int,
) -> Position:
    if "openVolume" in node:
        return Position(
            node["partyId"],
            node["marketId"],
            convert_to_decimals(position_decimal_places, float(node["openVolume"])),
            convert_to_decimals(price_decimal_places, float(node["averageEntryPrice"])),
            convert_to_decimals(asset_decimal_places, float(node["unrealisedPnl"])),
            convert_to_decimals(asset_decimal_places, float(node["realisedPnl"])),
        )
    else:
        return Position(
            node["partyId"],
            node["marketId"],
            0,
            convert_to_decimals(price_decimal_places, float(node["averageEntryPrice"])),
            convert_to_decimals(asset_decimal_places, float(node["unrealisedPnl"])),
            convert_to_decimals(asset_decimal_places, float(node["realisedPnl"])),
        )


def parse_market(node: dict) -> Market:
    instrument = node["tradableInstrument"]["instrument"]
    if "future" in instrument:
        return Market(
            node["id"],
            node["state"],
            node["tradingMode"],
            int(node["decimalPlaces"]),
            int(node["positionDecimalPlaces"]),
            instrument["code"],
            instrument["name"],
            instrument["future"]["settlementAsset"],
        )
    elif "perpetual" in instrument:
        return Market(
        node["id"],
        node["state"],
        node["tradingMode"],
        int(node["decimalPlaces"]),
        int(node["positionDecimalPlaces"]),
        instrument["code"],
        instrument["name"],
        instrument["perpetual"]["settlementAsset"],
    )
    else:
        raise Exception("Unknown instrumet!")

def parse_liquidity_commitment(node: dict, commitment: float) -> float:
    if node["status"] == "STATUS_ACTIVE":
        commitment = node["commitmentAmount"]
        
    return commitment

parsers = {
    "markets": parse_market,
    "assets": parse_asset,
    "accounts": parse_account,
    "orders": parse_order,
    "positions": parse_position,
}
