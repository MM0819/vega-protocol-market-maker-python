from model.account import Account
from model.order import Order
from model.asset import Asset
from model.position import Position
from model.market import Market
from model.reference_price import ReferencePrice


class AppState:
    def __init__(self, accounts: list[Account], orders: list[Order], positions: list[Position], assets: list[Asset],
                 reference_prices: list[ReferencePrice], markets: list[Market]):
        self.accounts = accounts
        self.orders = orders
        self.positions = positions
        self.assets = assets
        self.markets = markets
        self.reference_prices = reference_prices
