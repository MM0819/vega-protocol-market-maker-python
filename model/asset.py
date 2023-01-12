class Asset:
    def __init__(self, asset_id: str, status: str, name: str, symbol: str, decimal_places: int):
        self.asset_id: str = asset_id
        self.status: str = status
        self.name: str = name
        self.symbol: str = symbol
        self.decimal_places: int = decimal_places
