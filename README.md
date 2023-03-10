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
  - To do so, follow the instructions at [get-started](https://docs.vega.xyz/testnet/api/vega-wallet/v2-api/get-started#connect-with-bots), specifically those under the 'connect with bots' section. 
    - Make a note of the token you are given, and update `WALLET_TOKEN` in your `.env` file to the value.
    - Update `PARTY_ID` in `.env` to be the public key for your generated wallet
- Once completed, run the wallet service with `vegawallet service run --load-tokens --network fairground --automatic-consent`. This connects the wallet to the `fairground` network and `--automatic-consent` means that the wallet will skip requesting manual approval when it receives a transaction and instead always propagates it.
- Now that the wallet service is up and running, we can start the market maker itself.
  - Open the [console](https://console.fairground.wtf) and select a market of interest. Find the ID for the market either in the URL once that market is selected or the `Key Details` tab on the market page ![image](https://user-images.githubusercontent.com/702798/216101979-1966edb1-c99e-4128-a46a-cf97313385a4.png)
  - Set `MARKET_ID` in `.env` to this ID
  - Set `BINANCE_MARKET` in `.env` to the name of a market from which to draw reference prices. This should be a Binance Spot symbol
  - Enter your Python environment and run `python -m main` to start up the market maker. You should now be able to log in to the Fairground [console](https://console.fairground.wtf) and see the orders being placed.
