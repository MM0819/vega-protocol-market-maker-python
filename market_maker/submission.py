from dataclasses import dataclass
from market_maker.utils.decimal_utils import convert_from_decimals


@dataclass
class OrderAmendment:
    order_id: str
    size_delta: float
    price: float


@dataclass
class OrderCancellation:
    order_id: str
    market_id: str


@dataclass
class OrderSubmission:
    market_id: str
    size: float
    price: float
    time_in_force: str
    type: str
    side: str


@dataclass
class BatchMarketInstruction:
    submissions: list[OrderSubmission]
    cancellations: list[OrderCancellation]
    amendments: list[OrderAmendment]


def _submission_to_json(
    submission: OrderSubmission, price_decimals: int, position_decimals: int
) -> dict[str, str]:
    return {
        "marketId": submission.market_id,
        "timeInForce": submission.time_in_force,
        "type": submission.type,
        "side": submission.side,
        "size": str(convert_from_decimals(position_decimals, submission.size)),
        "price": str(convert_from_decimals(price_decimals, submission.price)),
        "postOnly": True,
    }


def _cancellation_to_json(cancellation: OrderCancellation) -> dict[str, str]:
    return {"marketId": cancellation.market_id, "orderId": cancellation.order_id}


def _amendment_to_json(
    amendment: OrderAmendment, price_decimals: int, position_decimals: int
) -> dict[str, str]:
    return {
        "orderId": amendment.order_id,
        "size_delta": str(
            convert_from_decimals(position_decimals, amendment.size_delta)
        ),
        "price": str(convert_from_decimals(price_decimals, amendment.price)),
    }


def instruction_to_json(
    instruction: BatchMarketInstruction, price_decimals: int, position_decimals: int
) -> dict:
    return {
        "batchMarketInstructions": {
            "submissions": [
                _submission_to_json(
                    s,
                    price_decimals=price_decimals,
                    position_decimals=position_decimals,
                )
                for s in instruction.submissions
            ],
            "amendments": [
                _amendment_to_json(
                    s,
                    price_decimals=price_decimals,
                    position_decimals=position_decimals,
                )
                for s in instruction.amendments
            ],
            "cancellations": [
                _cancellation_to_json(s) for s in instruction.cancellations
            ],
        }
    }

def liquidity_commitment_submission(
    market_id: str, amount: float, asset_decimals: int, proposed_fee: float
):
    return {
        "liquidityProvisionSubmission": _liquidity_provision_base(
            market_id=market_id,
            amount=amount,
            asset_decimals=asset_decimals,
            proposed_fee=proposed_fee,
        )
    }


def liquidity_commitment_amendment(
    market_id: str, amount: float, asset_decimals: int, proposed_fee: float
):
    return {
        "liquidityProvisionAmendment": _liquidity_provision_base(
            market_id=market_id,
            amount=amount,
            asset_decimals=asset_decimals,
            proposed_fee=proposed_fee,
        )
    }


def liquidity_commitment_cancellation(market_id: str):
    return {
        "liquidityProvisionCancellation": {
            "marketId": market_id,
        },
    }


def _liquidity_provision_base(
    market_id: str, amount: float, asset_decimals: int, proposed_fee: float
):
    return {
        "marketId": market_id,
        "commitmentAmount": str(
            convert_from_decimals(decimal_places=asset_decimals, number=amount)
        ),
        "fee": str(proposed_fee),
        "buys": [
            {
                "offset": "0",
                "proportion": "1",
                "reference": "PEGGED_REFERENCE_BEST_BID",
            },
        ],
        "sells": [
            {
                "offset": "0",
                "proportion": "1",
                "reference": "PEGGED_REFERENCE_BEST_ASK",
            },
        ],
    }
