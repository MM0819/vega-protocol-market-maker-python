class Order:
    def __init__(self, order_id: str, market_id: str, size: float, remaining_size: float, price: float,
                 order_type: str, time_in_force: str, status: str, party_id: str):
        self.order_id: str = order_id
        self.market_id: str = market_id
        self.size: float = size
        self.remaining_size: float = remaining_size
        self.price: float = price
        self.order_type: str = order_type
        self.time_in_force: str = time_in_force
        self.status: str = status
        self.party_id: str = party_id
