class OrderAmendment:
    def __init__(self, order_id: str, size_delta: float, price: float):
        self.order_id: str = order_id
        self.size_delta: float = size_delta
        self.price: float = price
