from enum import Enum


class TransactionStatusType(Enum):
    # SPEC_paypal_payment.md §4.1. Milestone 1 only produces CREATED -> CAPTURED (OQ2); the rest
    # exist for the recurring/lifecycle milestone (M2).
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
