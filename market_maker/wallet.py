"""
The VegaWallet class uses vegawallet's v2 interaction format.

This requires some setup with the vegawallet itself prior to running a bot.
Instructions to do this can be found at:
https://docs.vega.xyz/testnet/api/vega-wallet/v2-api/get-started#connect-with-bots

First a long living token must be generated, then the vegawallet run with specific
flags. An additional flag of `--automatic-consent` is also useful, which will cause
all transactions to be approved, skipping manual confirmation (otherwise there will
be a manual confirmation prompt each time the market maker bot sends a transaction.)
"""

import requests


class VegaWallet:
    def __init__(self, token: str, wallet_url: str, pub_key: str):
        self.token = token
        self.wallet_url = wallet_url
        self.pub_key = pub_key

        self.session = requests.Session()
        self.session.headers = {"Origin": "MMBot", "Authorization": f"VWT {self.token}"}

    def submit_transaction(self, transaction: dict) -> None:
        self.session.post(
            self.wallet_url + "/api/v2/requests",
            json={
                "jsonrpc": "2.0",
                "method": "client.send_transaction",
                "params": {
                    "publicKey": self.pub_key,
                    "sendingMode": "TYPE_SYNC",
                    "transaction": transaction,
                },
                "id": "request",
            },
        ).raise_for_status()
