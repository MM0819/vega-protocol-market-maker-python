class Position:
    def __init__(self, party_id: str, market_id: str, open_volume: float, average_entry_price: float,
                 unrealised_pnl: float, realised_pnl: float):
        self.party_id: str = party_id
        self.market_id: str = market_id
        self.open_volume: float = open_volume
        self.average_entry_price: float = average_entry_price
        self.unrealised_pnl: float = unrealised_pnl
        self.realised_pnl: float = realised_pnl
