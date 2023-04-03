import logging
import time
from typing import Optional

import requests

from market_maker.config import Config
from market_maker.submission import (
    BatchMarketInstruction,
    OrderAmendment,
    OrderCancellation,
    OrderSubmission,
)


def execute_get_request(path: str, key: str, config: Config):
    query_url = f"{config.node_url}/{path}"

    response = requests.get(query_url)
    response.raise_for_status()

    results = []
    response_json = response.json()
    edges = response_json[key]["edges"]
    for edge in edges:
        results.append(edge["node"])

    # Here we unroll any paginated queries.
    # Each query will have a 'pageInfo' component which gives details about pagination.
    # Use the `endCursor` field to start the next query's results
    while response_json[key]["pageInfo"]["hasNextPage"]:
        response = requests.get(
            query_url
            + f"&pagination.after={response_json[key]['pageInfo']['endCursor']}"
        )
        response.raise_for_status()
        response_json = response.json()
        edges = response_json[key]["edges"]
        for edge in edges:
            results.append(edge["node"])

    return results


def get_markets(config: Config) -> list[dict]:
    return execute_get_request("markets", "markets", config=config)


def get_assets(config: Config) -> list[dict]:
    return execute_get_request("assets", "assets", config=config)


def get_accounts(party_id: str, config: Config) -> list[dict]:
    return execute_get_request(
        f"accounts?filter.partyIds={party_id}", "accounts", config=config
    )


def get_open_orders(party_id: str, node_url: str) -> list[dict]:
    return execute_get_request(
        f"orders?filter.partyIds={party_id}&liveOnly=true", "orders", node_url=node_url
    )


def get_positions(
    party_id: str, node_url: str, market_id: Optional[str] = None
) -> list[dict]:
    filt = f"positions?filter.partyIds={party_id}"
    if market_id is not None:
        filt += "&filter.marketIds={market_id}"
    return execute_get_request(
        filt,
        "positions",
        node_url=node_url,
    )


def get_token(config: Config) -> Optional[str]:
    response = requests.post(
        f"{config.wallet_url}/api/v1/auth/token",
        json={"wallet": config.wallet_username, "passphrase": config.wallet_password},
    )
    response.raise_for_status()

    return response.json()["token"]


def send_batch_market_instruction(
    submissions: list[OrderSubmission],
    cancellations: list[OrderCancellation],
    amendments: list[OrderAmendment],
    config: Config,
) -> Optional[str]:
    token = get_token()
    if token is not None:
        batch_market_instruction = BatchMarketInstruction(
            submissions, cancellations, amendments
        )
        payload = {
            "batchMarketInstructions": batch_market_instruction.__dict__,
            "pubKey": config.party_id,
            "propagate": True,
        }
        response = requests.post(
            f"{config.wallet_url}/api/v1/auth/token",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        tx_hash = response.json()["txHash"]
        print_error_if_exists(tx_hash, config=config)
        return tx_hash


def print_error_if_exists(tx_hash: str, config: Config):
    print_error_if_exists_retry(tx_hash, 0, config=config)


def print_error_if_exists_retry(tx_hash: str, attempt: int, config: Config):
    response = requests.get(f"{config.tendermint_url}/tx?hash=0x{tx_hash}")
    if response.status_code != 200:
        logging.error(response.json())
    elif response.json().get("result") is not None:
        tx_result = response.json()["result"]["tx_result"]
        code = tx_result["code"]
        if code > 0:
            logging.error(tx_result["info"])
    elif response.json().get("error") is not None:
        if attempt < 10:
            time.sleep(0.25)
            print_error_if_exists_retry(tx_hash, attempt + 1)
        else:
            logging.error(f"Transaction not found: {tx_hash}")
