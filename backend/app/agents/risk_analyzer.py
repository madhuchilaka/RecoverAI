from __future__ import annotations

from dataclasses import dataclass

from app.models.customer import Customer
from app.models.transaction import (
    FailureReason,
    RiskLevel,
    Transaction,
    TransactionStatus,
    TransactionType,
)


@dataclass(frozen=True)
class RiskAssessment:
    risk_level: RiskLevel
    risk_score: float
    reasons: list[str]


class RiskAnalyzer:
    """Transparent baseline risk scoring; this is not a trained ML model."""

    HIGH_VALUE_THRESHOLD = 50_000.0
    MEDIUM_VALUE_THRESHOLD = 10_000.0

    def analyze(self, transaction: Transaction, customer: Customer | None = None) -> RiskAssessment:
        score = 0.0
        reasons: list[str] = []

        if transaction.amount >= self.HIGH_VALUE_THRESHOLD:
            score += 0.25
            reasons.append("High transaction value increases revenue exposure.")
        elif transaction.amount >= self.MEDIUM_VALUE_THRESHOLD:
            score += 0.12
            reasons.append("Above-average transaction value increases revenue exposure.")

        if transaction.status == TransactionStatus.FAILED:
            score += 0.22
            reasons.append("The transaction failed and its value is currently at risk.")
        elif transaction.status == TransactionStatus.ABANDONED:
            score += 0.16
            reasons.append("The checkout was abandoned before payment completed.")
        elif transaction.status == TransactionStatus.PENDING:
            score += 0.08
            reasons.append("The transaction is still pending and needs cautious handling.")

        failure_weights = {
            FailureReason.BANK_DECLINED: (0.18, "The bank declined the payment."),
            FailureReason.INSUFFICIENT_FUNDS: (0.14, "Available funds may be insufficient."),
            FailureReason.AUTHENTICATION_FAILED: (0.12, "Authentication did not complete."),
            FailureReason.EXPIRED_CARD: (0.10, "The payment method may be expired."),
            FailureReason.NETWORK_ERROR: (0.06, "A temporary network failure may be recoverable."),
            FailureReason.UNKNOWN: (0.10, "The failure reason is unclear."),
        }
        if transaction.failure_reason in failure_weights:
            weight, reason = failure_weights[transaction.failure_reason]
            score += weight
            reasons.append(reason)

        if transaction.retry_count >= 2:
            score += 0.16
            reasons.append("Repeated retries increase intervention risk.")
        elif transaction.retry_count == 1:
            score += 0.06
            reasons.append("One retry has already been attempted.")

        if transaction.transaction_type == TransactionType.CHECKOUT and transaction.status == TransactionStatus.ABANDONED:
            score += 0.08
            reasons.append("An abandoned checkout may need customer re-engagement.")

        if customer is not None and customer.total_transactions > 0:
            success_rate = customer.successful_transactions / customer.total_transactions
            if success_rate >= 0.8:
                score -= 0.10
                reasons.append(f"Customer history is strong ({success_rate:.0%} successful transactions).")
            elif success_rate < 0.5:
                score += 0.10
                reasons.append(f"Customer history shows repeated failures ({success_rate:.0%} successful transactions).")

            if customer.failed_transactions > 2:
                score += 0.06
                reasons.append("Customer has more than two previous failures.")

        score = round(max(0.0, min(1.0, score)), 2)
        if score >= 0.75:
            level = RiskLevel.CRITICAL
        elif score >= 0.50:
            level = RiskLevel.HIGH
        elif score >= 0.25:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        return RiskAssessment(level, score, reasons)
