from __future__ import annotations

from app.models.transaction import FailureReason, RiskLevel, TransactionStatus, TransactionType


def classify_risk(amount: float, retry_count: int, status: TransactionStatus, failure_reason: FailureReason | None, transaction_type: TransactionType) -> RiskLevel:
    score = 0

    if amount >= 50000:
        score += 3
    elif amount >= 10000:
        score += 2
    elif amount >= 1000:
        score += 1

    if retry_count >= 2:
        score += 2
    elif retry_count == 1:
        score += 1

    if status in {TransactionStatus.PENDING, TransactionStatus.ABANDONED}:
        score += 1
    elif status == TransactionStatus.FAILED:
        score += 1

    if failure_reason in {
        FailureReason.INSUFFICIENT_FUNDS,
        FailureReason.BANK_DECLINED,
        FailureReason.AUTHENTICATION_FAILED,
    }:
        score += 2
    elif failure_reason in {FailureReason.NETWORK_ERROR, FailureReason.EXPIRED_CARD}:
        score += 1

    if transaction_type == TransactionType.CHECKOUT and status in {TransactionStatus.ABANDONED, TransactionStatus.FAILED}:
        score += 1

    if score >= 6:
        return RiskLevel.CRITICAL
    if score >= 4:
        return RiskLevel.HIGH
    if score >= 2:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def estimate_recovery_probability(amount: float, retry_count: int, status: TransactionStatus, failure_reason: FailureReason | None, transaction_type: TransactionType) -> float:
    if status == TransactionStatus.SUCCESS:
        return 0.0

    score = 0.42

    if failure_reason in {FailureReason.NETWORK_ERROR, FailureReason.EXPIRED_CARD}:
        score += 0.25
    elif failure_reason in {FailureReason.INSUFFICIENT_FUNDS, FailureReason.BANK_DECLINED}:
        score += 0.12
    elif failure_reason == FailureReason.AUTHENTICATION_FAILED:
        score -= 0.10

    if amount < 5000:
        score += 0.18
    elif amount > 50000:
        score -= 0.10

    if retry_count == 1:
        score += 0.10
    elif retry_count >= 2:
        score -= 0.10

    if transaction_type == TransactionType.CHECKOUT:
        score += 0.08
    elif transaction_type == TransactionType.SUBSCRIPTION:
        score += 0.05

    if status == TransactionStatus.ABANDONED:
        score += 0.08

    return max(0.0, min(1.0, round(score, 2)))
