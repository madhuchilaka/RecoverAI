from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.recovery_agent import RecoveryAgent
from app.models.recovery import RecoveryAttempt, RecoveryAttemptStatus
from app.models.transaction import RecoveryStatus, RiskLevel, Transaction, TransactionStatus


AT_RISK_STATUSES = {TransactionStatus.FAILED, TransactionStatus.ABANDONED}
MIN_PLAUSIBLE_RECOVERY_PROBABILITY = 0.25


@dataclass(frozen=True)
class RevenueAtRiskSummary:
    revenue_at_risk: float
    at_risk_transaction_count: int
    average_transaction_value: float
    risk_distribution: dict[str, int]
    at_risk_transactions: int = 0
    recovered_revenue: float = 0.0
    recovery_rate: float = 0.0
    recovery_attempts: int = 0
    successful_recoveries: int = 0
    failed_recoveries: int = 0
    escalations: int = 0
    blocked_actions: int = 0
    pending_approvals: int = 0


def get_at_risk_transactions(db: Session) -> list[Transaction]:
    transactions = db.execute(
        select(Transaction)
        .where(Transaction.status.in_(AT_RISK_STATUSES))
        .order_by(Transaction.created_at.desc())
    ).scalars().all()
    agent = RecoveryAgent(db)
    return [
        transaction
        for transaction in transactions
        if (recommendation := agent.analyze_transaction(transaction.id)) is not None
        and recommendation.recovery_probability >= MIN_PLAUSIBLE_RECOVERY_PROBABILITY
    ]


def calculate_revenue_at_risk(db: Session) -> RevenueAtRiskSummary:
    transactions = get_at_risk_transactions(db)
    distribution = Counter()
    total = 0.0
    agent = RecoveryAgent(db)
    for transaction in transactions:
        recommendation = agent.analyze_transaction(transaction.id)
        if recommendation is not None:
            total += transaction.amount
            distribution[recommendation.risk_level.value] += 1
    count = len(transactions)
    recovered_revenue = db.query(Transaction).filter(Transaction.recovery_status == RecoveryStatus.RECOVERED).with_entities(Transaction.amount).all()
    recovered_total = round(sum(row[0] for row in recovered_revenue), 2)
    initial_at_risk_total = total + recovered_total
    attempts = db.query(RecoveryAttempt).all()
    return RevenueAtRiskSummary(
        revenue_at_risk=round(total, 2),
        at_risk_transaction_count=count,
        average_transaction_value=round(total / count, 2) if count else 0.0,
        risk_distribution={level.value: distribution.get(level.value, 0) for level in RiskLevel},
        at_risk_transactions=count,
        recovered_revenue=recovered_total,
        recovery_rate=round(recovered_total / initial_at_risk_total, 4) if initial_at_risk_total else 0.0,
        recovery_attempts=len(attempts),
        successful_recoveries=sum(attempt.status == RecoveryAttemptStatus.SUCCESS for attempt in attempts),
        failed_recoveries=sum(attempt.status == RecoveryAttemptStatus.FAILED for attempt in attempts),
        escalations=sum(attempt.status == RecoveryAttemptStatus.ESCALATED for attempt in attempts),
        blocked_actions=sum(attempt.status == RecoveryAttemptStatus.BLOCKED for attempt in attempts),
        pending_approvals=sum(attempt.status == RecoveryAttemptStatus.PENDING for attempt in attempts),
    )
