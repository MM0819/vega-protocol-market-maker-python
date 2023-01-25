from dataclasses import dataclass


@dataclass
class ReferencePrice:
    symbol: str
    bid_price: float
    ask_price: float


@dataclass
class Position:
    party_id: str
    market_id: str
    open_volume: float
    average_entry_price: float
    unrealised_pnl: float
    realised_pnl: float


@dataclass
class Order:
    order_id: str
    market_id: str
    size: float
    remaining_size: float
    price: float
    order_type: str
    time_in_force: str
    status: str
    party_id: str


@dataclass
class Market:
    market_id: str
    state: str
    trading_mode: str
    decimal_places: int
    position_decimal_places: int
    code: str
    name: str
    settlement_asset_id: str

    mark_price: float = 0
    best_bid_price: float = 0
    best_offer_price: float = 0
    best_bid_volume: float = 0
    best_offer_volume: float = 0
    open_interest: float = 0


@dataclass
class Asset:
    asset_id: str
    status: str
    name: str
    symbol: str
    decimal_places: int


@dataclass
class Account:
    owner: str
    account_type: str
    balance: float
    asset_id: str
    market_id: str

    def get_id(self):
        return f"{self.owner}-{self.market_id}-{self.account_type}-{self.asset_id}"


@dataclass
class AppState:
    accounts: list[Account]
    orders: list[Order]
    positions: list[Position]
    assets: list[Asset]
    reference_prices: list[ReferencePrice]
    markets: list[Market]
