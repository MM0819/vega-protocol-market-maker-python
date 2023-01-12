from submission.order_submission import OrderSubmission
from submission.order_cancellation import OrderCancellation
from submission.order_amendment import OrderAmendment


class BatchMarketInstruction:
    def __init__(self, submissions: list[OrderSubmission],
                 cancellations: list[OrderCancellation], amendments: list[OrderAmendment]):
        self.submissions: list[OrderSubmission] = submissions
        self.cancellations: list[OrderCancellation] = cancellations
        self.amendments: list[OrderAmendment] = amendments
