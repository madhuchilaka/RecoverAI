from __future__ import annotations

from dataclasses import dataclass

from app.agents.risk_analyzer import RiskAssessment
from app.config import settings
from app.models.customer import Customer
from app.models.recovery import RecoveryAction
from app.models.transaction import FailureReason, RiskLevel, Transaction, TransactionStatus


@dataclass(frozen=True)
class Decision:
    action: RecoveryAction
    reasoning: str


class DecisionEngine:
    HIGH_VALUE_THRESHOLD = settings.high_value_threshold
    MIN_RECOVERY_PROBABILITY = 0.25

    def decide(self, transaction: Transaction, customer: Customer | None, risk: RiskAssessment, recovery_probability: float) -> Decision:
        if transaction.status == TransactionStatus.SUCCESS:
            return Decision(RecoveryAction.NO_ACTION, "The transaction is already successful, so no recovery action is needed.")
        if risk.risk_level == RiskLevel.CRITICAL or transaction.amount > self.HIGH_VALUE_THRESHOLD:
            return Decision(RecoveryAction.ESCALATE_TO_HUMAN, "The transaction exposure or risk is high enough to require human review.")
        if transaction.retry_count >= 2:
            if recovery_probability >= 0.55:
                return Decision(RecoveryAction.GENERATE_PAYMENT_LINK, "Retries are exhausted, but the recovery estimate supports a customer-directed payment link.")
            return Decision(RecoveryAction.ESCALATE_TO_HUMAN, "Retries are exhausted and the recovery estimate is not strong enough for an automatic action.")
        if recovery_probability < self.MIN_RECOVERY_PROBABILITY:
            return Decision(RecoveryAction.NO_ACTION, "The estimated recovery probability is too low to justify outreach or another attempt.")
        if transaction.status == TransactionStatus.ABANDONED:
            return Decision(RecoveryAction.SEND_CUSTOMER_REMINDER, "The checkout was abandoned, so a reminder is the least intrusive recovery step.")
        if transaction.failure_reason == FailureReason.NETWORK_ERROR:
            return Decision(RecoveryAction.RETRY_PAYMENT, "The temporary network failure and available retry make a payment retry appropriate.")
        if transaction.failure_reason == FailureReason.EXPIRED_CARD:
            return Decision(RecoveryAction.OFFER_ALTERNATIVE_PAYMENT, "The payment method may be expired, so an alternative payment method is recommended.")
        if transaction.failure_reason == FailureReason.BANK_DECLINED:
            return Decision(RecoveryAction.ESCALATE_TO_HUMAN, "The bank declined the payment, so repeated automatic retries are discouraged.")
        if transaction.failure_reason == FailureReason.AUTHENTICATION_FAILED:
            return Decision(RecoveryAction.GENERATE_PAYMENT_LINK, "A payment link can give the customer a fresh opportunity to complete authentication.")
        return Decision(RecoveryAction.GENERATE_PAYMENT_LINK, "A customer-directed payment link provides a controlled recovery path for this failed payment.")
