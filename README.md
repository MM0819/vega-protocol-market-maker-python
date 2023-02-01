# Vega Protocol - Python Market Maker Example

Example Python setup code running a simple market maker on a Vega Protocol network.

The Market-Maker has several components:

- Websocket connections to Binance and a Vega Protocol data node
- Local stores for each of the websocket connections to cache received updates
- A wallet class to handle conversion of generated orders into signed bundles
- A market maker themselves

The logic of the market maker is contained within `market_maker/strategy/simple_market_maker.py` and consists simply of listening to a Binance websocket stream for a reference price, then updating a number of quotes on either side of this price at a configurable frequency.

### Setup

Configuration for running this example is as follows:

- With a Python 3.10 environment manager of choice, configure an environment based on `requirements.txt`. (If you're currently lacking a manager, `poetry` is a good choice for a full-featured manager or `venv` for light virtual environments.)
- Follow the instructions at [create-wallet](https://docs.vega.xyz/testnet/tools/vega-wallet/cli-wallet/latest/create-wallet) to download a CLI wallet for your system, import networks (`fairground` for the testnet) and ensure you are able to generate wallets
- The Vega Wallet v2 API requires a token to be generated which the bot will later attach to transaction requests, so this must be set up next.
  - Make a copy of `.env.sample` to a file called `.env`
  - To do so, follow the instructions at [get-started](https://docs.vega.xyz/testnet/api/vega-wallet/v2-api/get-started#connect-with-bots), specifically those under the 'connect with bots' section. Make a note of the token you are given, and update `WALLET_TOKEN` in your `.env` file to the value.
- Once completed, run the wallet service with `vegawallet service run --load-tokens --network fairground --automatic-consent`. This connects the wallet to the `fairground` network and `--automatic-consent` means that the wallet will skip requesting manual approval when it receives a transaction and instead always propagates it.
- Now that the wallet service is up and running, enter your Python environment and run `python -m main` to start up the market maker. You should now be able to log in to the Fairground console at [fairground.wtf](http://fairground.wtf) and see the orders being placed.
