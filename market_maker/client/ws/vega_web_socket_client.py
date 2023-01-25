import websocket
import rel
import logging
import json
from typing import Callable, Any


logger = logging.getLogger(__name__)


class VegaWebSocketClient:
    def __init__(self, data_node_url: str):
        self._data_node_url = data_node_url

        self._messages = {}

    def _on_error(self, ws, err):
        logger.exception(err)

    def _on_message(
        self,
        message: str,
        msg_type: str,
        callback: Callable[[dict], Any],
    ) -> None:
        self._messages[msg_type] = self._messages.get(msg_type, "") + message

        # Websocket results are received line by line, so must check whether
        # we've now received a full JSON object and return to the callback if so
        try:
            obj = json.loads(self._messages[msg_type])["result"]
        except json.decoder.JSONDecodeError:
            pass
        else:
            self._messages[msg_type] = ""
            callback(obj)

    def stop(self):
        rel.abort()

    # https://docs.vega.xyz/testnet/api/rest/data-v2/trading-data-service-observe-markets-data
    def subscribe_market_data(
        self, market_id: str, callback: Callable[[dict], Any]
    ) -> None:
        self.subscribe_endpoint(
            f"{self._data_node_url}/stream/markets/data?marketIds={market_id}",
            "market_data",
            callback=callback,
        )

    # https://docs.vega.xyz/testnet/api/rest/data-v2/trading-data-service-observe-orders
    def subscribe_orders(
        self, market_id: str, party_id: str, callback: Callable[[dict], Any]
    ) -> None:
        self.subscribe_endpoint(
            f"{self._data_node_url}/stream/orders?marketId={market_id}&partyId={party_id}",
            "orders",
            callback=callback,
        )

    # https://docs.vega.xyz/testnet/api/rest/data-v2/trading-data-service-observe-positions
    def subscribe_positions(
        self, market_id: str, party_id: str, callback: Callable[[dict], Any]
    ) -> None:
        self.subscribe_endpoint(
            f"{self._data_node_url}/stream/positions?marketId={market_id}&partyId={party_id}",
            "positions",
            callback=callback,
        )

    # https://docs.vega.xyz/testnet/api/rest/data-v2/trading-data-service-observe-accounts
    def subscribe_accounts(
        self, market_id: str, party_id: str, callback: Callable[[dict], Any]
    ) -> None:
        self.subscribe_endpoint(
            f"{self._data_node_url}/stream/accounts?marketId={market_id}&partyId={party_id}",
            "accounts",
            callback=callback,
        )

    def subscribe_endpoint(
        self, url: str, msg_type: str, callback: Callable[[dict], Any]
    ) -> None:
        ws = websocket.WebSocketApp(
            url,
            on_message=lambda _, msg: self._on_message(
                message=msg, msg_type=msg_type, callback=callback
            ),
            on_error=self._on_error,
        )
        ws.run_forever(dispatcher=rel, reconnect=5)
