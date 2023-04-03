from threading import Lock
from typing import Optional

import market_maker.client.api.parsers as parsers
import market_maker.client.api.vega_api_client as api
from market_maker.client.ws.vega_web_socket_client import VegaWebSocketClient
from market_maker.config import Config
from market_maker.models import Account, Asset, Market, Order, Position
from market_maker.utils.decimal_utils import convert_to_decimals


class VegaStore:
    def __init__(self, config: Config):
        self._accounts: dict[str, Account] = {}
        self._orders: dict[str, Order] = {}
        self._assets: dict[str, Asset] = {}
        self._positions: dict[str, Position] = {}
        self._markets: dict[str, Market] = {}

        self._accounts_lock = Lock()
        self._orders_lock = Lock()
        self._positions_lock = Lock()
        self._markets_lock = Lock()

        self._config = config
        self._ws_client = VegaWebSocketClient(data_node_url=config.ws_url)

    def start(self, market_id: str, party_id: str) -> None:
        self.load_data(party_id=party_id)

        self._ws_client.subscribe_market_data(
            market_id=market_id, callback=self._update_market_data
        )

        self._ws_client.subscribe_accounts(
            party_id=party_id, market_id=market_id, callback=self._update_accounts
        )

        self._ws_client.subscribe_orders(
            market_id=market_id, party_id=party_id, callback=self._update_order
        )

        self._ws_client.subscribe_positions(
            market_id=market_id, party_id=party_id, callback=self._update_position
        )

    def stop(self):
        self._ws_client.stop()

    ###########################################################
    #                   All item loaders                      #
    ###########################################################

    def get_markets(self) -> list[Market]:
        with self._markets_lock:
            return list(self._markets.values())

    def get_accounts(self) -> list[Account]:
        with self._accounts_lock:
            return list(self._accounts.values())

    def get_assets(self) -> list[Asset]:
        return list(self._assets.values())

    def get_positions(self) -> list[Position]:
        with self._positions_lock:
            return list(self._positions.values())

    def get_orders(self) -> list[Order]:
        with self._orders_lock:
            return list(self._orders.values())

    ###########################################################
    #               Individual item loaders                   #
    ###########################################################

    def get_market_by_id(self, market_id: str) -> Optional[Market]:
        return self._markets.get(market_id)

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def get_position_by_market_id(self, market_id: str) -> Optional[Position]:
        return self._positions.get(market_id)

    def get_asset_by_id(self, asset_id: str) -> Optional[Asset]:
        return self._assets.get(asset_id)

    ###########################################################
    #                   Update functions                      #
    ###########################################################

    def _update_market_data(self, market_dict: dict) -> None:
        market_data = market_dict["marketData"][0]
        with self._markets_lock:
            market = self._markets[market_data["market"]]
            market.mark_price = convert_to_decimals(
                market.decimal_places, float(market_data["markPrice"])
            )
            market.best_bid_price = convert_to_decimals(
                market.decimal_places,
                float(market_data["bestBidPrice"]),
            )
            market.best_offer_price = convert_to_decimals(
                market.decimal_places,
                float(market_data["bestOfferPrice"]),
            )
            market.best_bid_volume = convert_to_decimals(
                market.decimal_places,
                float(market_data["bestBidVolume"]),
            )
            market.best_offer_volume = convert_to_decimals(
                market.decimal_places,
                float(market_data["bestOfferVolume"]),
            )
            market.open_interest = convert_to_decimals(
                market.decimal_places,
                float(market_data["openInterest"]),
            )
            market.trading_mode = market_data["marketTradingMode"]
            market.state = market_data["marketState"]

    def _update_order(self, order_dict: dict) -> None:
        orders = [
            parsers.parse_order(
                order,
                position_decimal_places=self.get_market_by_id(
                    order["marketId"]
                ).position_decimal_places,
                price_decimal_places=self.get_market_by_id(
                    order["marketId"]
                ).decimal_places,
            )
            for order in order_dict.get("snapshot", order_dict.get("updates")).get(
                "orders", []
            )
        ]
        with self._orders_lock:
            for order in orders:
                if order.status != "STATUS_ACTIVE":
                    self._orders.pop(order.order_id, None)
                else:
                    self._orders[order.order_id] = order

    def _update_position(self, position_dict: dict) -> None:
        position_dict = position_dict.get("snapshot", position_dict.get("updates"))[
            "positions"
        ][0]

        market = self.get_market_by_id(position_dict["marketId"])
        asset = self.get_asset_by_id(market.settlement_asset_id)
        position = parsers.parse_position(
            position_dict,
            position_decimal_places=market.position_decimal_places,
            price_decimal_places=market.decimal_places,
            asset_decimal_places=asset.decimal_places,
        )
        with self._positions_lock:
            self._positions[position.market_id] = position

    def _update_accounts(self, account_dict: dict) -> None:
        account_dict = account_dict.get("snapshot", account_dict.get("updates"))
        if not account_dict.get("accounts"):
            return
        account_dict = account_dict["accounts"][0]
        asset = self.get_asset_by_id(account_dict["asset"])
        account = parsers.parse_account(
            account_dict,
            asset_decimal_places=asset.decimal_places,
        )
        with self._accounts_lock:
            self._accounts[account.get_id()] = account

    def load_data(self, party_id: str) -> None:
        self._assets = {
            a["id"]: parsers.parse_asset(a) for a in api.get_assets(config=self._config)
        }

        markets = {
            m["id"]: parsers.parse_market(m)
            for m in api.get_markets(config=self._config)
        }
        with self._markets_lock:
            self._markets = markets

        new_accts = {}
        for acct in api.get_accounts(config=self._config, party_id=party_id):
            acct = parsers.parse_account(
                acct,
                asset_decimal_places=self.get_asset_by_id(acct["asset"]).decimal_places,
            )
            new_accts[acct.get_id()] = acct

        with self._accounts_lock:
            self._accounts = new_accts

        orders = {
            o["id"]: parsers.parse_order(
                o,
                self.get_market_by_id(o["marketId"]).decimal_places,
                self.get_market_by_id(o["marketId"]).position_decimal_places,
            )
            for o in api.get_open_orders(party_id=party_id, config=self._config)
        }

        with self._orders_lock:
            self._orders = orders

        posns = {
            p["marketId"]: parsers.parse_position(
                p,
                position_decimal_places=self.get_market_by_id(
                    p["marketId"]
                ).position_decimal_places,
                price_decimal_places=self.get_market_by_id(
                    p["marketId"]
                ).decimal_places,
                asset_decimal_places=self.get_asset_by_id(
                    self.get_market_by_id(p["marketId"]).settlement_asset_id
                ).decimal_places,
            )
            for p in api.get_positions(party_id=party_id, config=self._config)
        }
        with self._positions_lock:
            self._positions = posns
