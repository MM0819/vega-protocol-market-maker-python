from market_maker.store.binance_store import BinanceStore
from market_maker.store.vega_store import VegaStore
from market_maker.config import Config
from market_maker.strategy.simple_market_maker import SimpleMarketMaker
from market_maker.wallet import VegaWallet

import rel
import dotenv

import logging


def main():
    dotenv.load_dotenv()
    config = Config.from_env()

    store = VegaStore(config)
    binance_store = BinanceStore(symbols_to_subscribe=[config.binance_market])

    store.start(
        market_id=config.market_id,
        party_id=config.party_id,
    )
    binance_store.start()

    wallet = VegaWallet(
        token=config.wallet_token, wallet_url=config.wallet_url, pub_key=config.party_id
    )

    smm = SimpleMarketMaker(
        binance_store=binance_store, vega_store=store, config=config, wallet=wallet
    )
    smm.run()

    # Now run event loop (Send SIGINT (Ctrl+C) to close)
    rel.dispatch()
    store.stop()
    binance_store.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
    )
    main()
