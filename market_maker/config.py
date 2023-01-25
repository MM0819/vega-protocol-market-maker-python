import os
from dataclasses import dataclass


@dataclass
class Config:
    node_url: str
    tendermint_url: str
    ws_url: str
    wallet_url: str
    wallet_token: str
    market_id: str
    party_id: str
    binance_market: str
    binance_ws_url: str

    @classmethod
    def from_env(cls):
        return cls(
            node_url=os.environ.get("NODE_URL"),
            tendermint_url=os.environ.get("TENDERMINT_URL"),
            ws_url=os.environ.get("WS_URL"),
            wallet_url=os.environ.get("WALLET_URL"),
            wallet_token=os.environ.get("WALLET_TOKEN"),
            market_id=os.environ.get("MARKET_ID"),
            party_id=os.environ.get("PARTY_ID"),
            binance_market=os.environ.get("BINANCE_MARKET"),
            binance_ws_url=os.environ.get("BINANCE_WS_URL"),
        )
