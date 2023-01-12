from model.account import Account
from model.asset import Asset
from model.market import Market
from model.order import Order
from model.position import Position
from typing import Optional


class VegaStore:
    def __init__(self):
        self.accounts: dict[str, Account] = {}
        self.orders: dict[str, Order] = {}
        self.assets: dict[str, Asset] = {}
        self.positions: dict[str, Position] = {}
        self.markets: dict[str, Market] = {}

    def get_markets(self) -> list[Market]:
        return list(self.markets.values())

    def get_accounts(self) -> list[Account]:
        return list(self.accounts.values())

    def get_assets(self) -> list[Asset]:
        return list(self.assets.values())

    def get_positions(self) -> list[Position]:
        return list(self.positions.values())

    def get_orders(self) -> list[Order]:
        return list(self.orders.values())

    def save_market(self, market: Market):
        self.markets[market.market_id] = market

    def save_asset(self, asset: Asset):
        self.assets[asset.asset_id] = asset

    def save_account(self, account: Account):
        self.accounts[account.get_id()] = account

    def save_position(self, position: Position):
        self.positions[position.market_id] = position

    def save_order(self, order: Order):
        if order.status != 'STATUS_ACTIVE':
            del self.orders[order.order_id]
        else:
            self.orders[order.order_id] = order

    def get_market_by_id(self, market_id: str) -> Optional[Market]:
        return self.markets[market_id]

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        return self.orders[order_id]

    def get_position_by_market_id(self, market_id: str) -> Optional[Position]:
        return self.positions[market_id]

    def get_asset_by_id(self, asset_id: str) -> Optional[Asset]:
        return self.assets[asset_id]


vega_store = VegaStore()
