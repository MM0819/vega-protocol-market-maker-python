class OrderSubmission:
    def __init__(self, market_id: str, size: float, price: float, time_in_force: str, order_type: str, side: str):
        self.market_id: str = market_id
        self.size: float = size
        self.price: float = price
        self.time_in_force: str = time_in_force
        self.order_type: str = order_type
        self.side: str = side
