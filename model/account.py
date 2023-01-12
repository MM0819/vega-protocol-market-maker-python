class Account:
    def __init__(self, owner: str, account_type: str, balance: float, asset_id: str, market_id: str):
        self.owner: str = owner
        self.account_type: str = account_type
        self.balance: float = balance
        self.asset_id: str = asset_id
        self.market_id: str = market_id

    def get_id(self):
        return f'{self.owner}-{self.market_id}-{self.account_type}-{self.asset_id}'