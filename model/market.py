class Market:
    def __init__(self, market_id: str, state: str, trading_mode: str, decimal_places: int,
                 position_decimal_places: int, code: str, name: str, settlement_asset_id: str):
        self.market_id: str = market_id
        self.state: str = state
        self.trading_mode: str = trading_mode
        self.decimal_places: int = decimal_places
        self.position_decimal_places: int = position_decimal_places
        self.code: str = code
        self.name: str = name
        self.settlement_asset_id: str = settlement_asset_id
        self.mark_price: float = 0
        self.best_bid_price: float = 0
        self.best_offer_price: float = 0
        self.best_bid_volume: float = 0
        self.best_offer_volume: float = 0
        self.open_interest: float = 0
