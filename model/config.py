import os


class Config:
    def __init__(self):
        self.node_url: str = os.environ.get("NODE_URL")
        self.tendermint_url: str = os.environ.get("TENDERMINT_URL")
        self.ws_url: str = os.environ.get("WS_URL")
        self.wallet_url: str = os.environ.get("WALLET_URL")
        self.wallet_username: str = os.environ.get("WALLET_USERNAME")
        self.wallet_password: str = os.environ.get("WALLET_PASSWORD")
        self.market_id: str = os.environ.get("MARKET_ID")
        self.party_id: str = os.environ.get("PARTY_ID")
        self.binance_market: str = os.environ.get("BINANCE_MARKET")
        self.binance_ws_url: str = os.environ.get("BINANCE_WS_URL")


config = Config()
