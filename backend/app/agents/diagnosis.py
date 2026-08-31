from __future__ import annotations

from dataclasses import dataclass

from app.models.transaction import FailureReason, Transaction, TransactionStatus


@dataclass(frozen=True)
class Diagnosis:
    code: str
    message: str


class DiagnosisEngine:
    def diagnose(self, transaction: Transaction) -> Diagnosis:
        if transaction.status == TransactionStatus.ABANDONED:
            message = "Checkout was started but payment was not completed."
            code = "ABANDONED"
        else:
            messages = {
                FailureReason.NETWORK_ERROR: ("NETWORK_ERROR", "Temporary payment/network failure. Retry may be appropriate."),
                FailureReason.INSUFFICIENT_FUNDS: ("INSUFFICIENT_FUNDS", "Payment could not be completed due to insufficient available funds."),
                FailureReason.BANK_DECLINED: ("BANK_DECLINED", "Bank declined the transaction. Repeated automatic retries may have low value."),
                FailureReason.EXPIRED_CARD: ("EXPIRED_CARD", "Payment method may need to be updated."),
                FailureReason.AUTHENTICATION_FAILED: ("AUTHENTICATION_FAILED", "Additional authentication may be required."),
                FailureReason.UNKNOWN: ("UNKNOWN", "Failure reason is unclear and requires cautious recovery."),
            }
            code, message = messages.get(FailureReason.UNKNOWN, ("UNKNOWN", "Failure reason is unclear and requires cautious recovery."))
            if transaction.failure_reason in messages:
                code, message = messages[transaction.failure_reason]

        if transaction.retry_count >= 2:
            message += " The retry limit has been reached, so another automatic retry is discouraged."
        return Diagnosis(code, message)
