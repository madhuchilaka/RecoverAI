from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.agents.diagnosis import DiagnosisEngine
from app.agents.decision_engine import DecisionEngine
from app.agents.risk_analyzer import RiskAnalyzer
from app.models.customer import Customer
from app.models.recovery import RecoveryAction
from app.models.transaction import RiskLevel, Transaction, TransactionStatus


@dataclass(frozen=True)
class RecoveryRecommendation:
    transaction_id: int
    risk_level: RiskLevel
    risk_score: float
    recovery_probability: float
    diagnosis: str
    recommended_action: RecoveryAction
    reasoning: str
    confidence: float
    requires_human_approval: bool


class RecoveryAgent:
    """Deterministic agent facade designed for a future interchangeable LLM implementation."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.risk_analyzer = RiskAnalyzer()
        self.diagnosis_engine = DiagnosisEngine()
        self.decision_engine = DecisionEngine()

    def analyze_transaction(self, transaction_id: int) -> RecoveryRecommendation | None:
        transaction = self.db.get(Transaction, transaction_id)
        if transaction is None:
            return None
        customer = self.db.get(Customer, transaction.customer_id)
        risk = self.risk_analyzer.analyze(transaction, customer)
        diagnosis = self.diagnosis_engine.diagnose(transaction)
        probability = self._estimate_probability(transaction, customer)
        decision = self.decision_engine.decide(transaction, customer, risk, probability)
        requires_approval = (
            transaction.amount > self.decision_engine.HIGH_VALUE_THRESHOLD
            or risk.risk_level == RiskLevel.CRITICAL
            or transaction.retry_count >= 2
            or decision.action == RecoveryAction.ESCALATE_TO_HUMAN
        )
        history = self._history_text(customer)
        reasoning = f"{diagnosis.message} {history} {decision.reasoning}"
        confidence = round(max(0.5, min(0.98, 0.65 + abs(probability - 0.5) * 0.5)), 2)
        return RecoveryRecommendation(
            transaction_id=transaction.id,
            risk_level=risk.risk_level,
            risk_score=risk.risk_score,
            recovery_probability=probability,
            diagnosis=diagnosis.message,
            recommended_action=decision.action,
            reasoning=reasoning,
            confidence=confidence,
            requires_human_approval=requires_approval,
        )

    def _estimate_probability(self, transaction: Transaction, customer: Customer | None) -> float:
        if transaction.status == TransactionStatus.SUCCESS:
            return 0.0
        score = 0.45
        reason = transaction.failure_reason
        if reason is not None:
            score += {
                "NETWORK_ERROR": 0.25,
                "EXPIRED_CARD": 0.18,
                "AUTHENTICATION_FAILED": 0.08,
                "INSUFFICIENT_FUNDS": -0.05,
                "BANK_DECLINED": -0.15,
                "UNKNOWN": -0.08,
            }.get(reason.value, -0.08)
        if transaction.status == TransactionStatus.ABANDONED:
            score += 0.12
        if transaction.transaction_type.value == "CHECKOUT":
            score += 0.05
        elif transaction.transaction_type.value == "SUBSCRIPTION":
            score += 0.03
        if transaction.amount < 5_000:
            score += 0.10
        elif transaction.amount > 50_000:
            score -= 0.12
        if transaction.retry_count == 1:
            score -= 0.05
        elif transaction.retry_count >= 2:
            score -= 0.18
        if customer is not None and customer.total_transactions:
            success_rate = customer.successful_transactions / customer.total_transactions
            score += (success_rate - 0.5) * 0.30
        return round(max(0.0, min(1.0, score)), 2)

    @staticmethod
    def _history_text(customer: Customer | None) -> str:
        if customer is None or customer.total_transactions == 0:
            return "No customer history is available, so the estimate uses transaction factors only."
        rate = customer.successful_transactions / customer.total_transactions
        return f"The customer has completed {customer.successful_transactions} of {customer.total_transactions} previous transactions successfully ({rate:.0%})."
