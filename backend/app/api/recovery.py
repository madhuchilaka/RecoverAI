import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.policy_engine import PolicyEngine
from app.agents.recovery_agent import RecoveryAgent
from app.database import get_db
from app.models.audit import AuditLog
from app.models.recovery import RecoveryAction, RecoveryAttempt, RecoveryAttemptStatus
from app.models.transaction import RecoveryStatus, Transaction
from app.services.recovery_executor import RecoveryExecutor
from app.schemas.recovery import (
    AtRiskTransaction,
    ExecuteRecoveryRequest,
    RecoveryAnalysis,
    RecoveryExecutionResponse,
    RecoveryHistory,
    RecoverySummary,
)
from app.services.analytics import calculate_revenue_at_risk, get_at_risk_transactions

router = APIRouter(prefix="/api/recovery", tags=["recovery intelligence"])


@router.post("/analyze/{transaction_id}", response_model=RecoveryAnalysis)
def analyze_transaction(transaction_id: int, db: Session = Depends(get_db)):
    recommendation = RecoveryAgent(db).analyze_transaction(transaction_id)
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return recommendation


@router.get("/at-risk", response_model=list[AtRiskTransaction])
def list_at_risk_transactions(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    transactions = get_at_risk_transactions(db)[offset : offset + limit]
    agent = RecoveryAgent(db)
    return [
        AtRiskTransaction(
            transaction_id=transaction.id,
            external_transaction_id=transaction.external_transaction_id,
            customer_id=transaction.customer_id,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            risk_level=(recommendation := agent.analyze_transaction(transaction.id)).risk_level,
            recovery_probability=recommendation.recovery_probability,
        )
        for transaction in transactions
    ]


@router.get("/summary", response_model=RecoverySummary)
def recovery_summary(db: Session = Depends(get_db)):
    return calculate_revenue_at_risk(db)


def _audit(db: Session, transaction: Transaction, actor: str, action: str, reason: str, previous_state: str | None, new_state: str | None, result: str, details: dict | None = None) -> None:
    db.add(AuditLog(
        transaction_id=transaction.id,
        actor=actor,
        action=action,
        reason=reason[:200],
        previous_state=previous_state,
        new_state=new_state,
        result=result,
        details=json.dumps(details) if details else None,
    ))


def _attempt_number(db: Session, transaction_id: int) -> int:
    attempts = db.execute(select(RecoveryAttempt).where(RecoveryAttempt.transaction_id == transaction_id)).scalars().all()
    return max((attempt.attempt_number for attempt in attempts), default=0) + 1


def _execution_response(status: str, transaction: Transaction, action: RecoveryAction, message: str, stopped: bool, stop_reason: str | None, attempt_id: int | None = None, requires_human_approval: bool = False) -> RecoveryExecutionResponse:
    return RecoveryExecutionResponse(
        status=status,
        transaction_id=transaction.id,
        action=action,
        amount=transaction.amount,
        message=message,
        stopped=stopped,
        stop_reason=stop_reason,
        attempt_id=attempt_id,
        requires_human_approval=requires_human_approval,
    )


@router.post("/execute/{transaction_id}", response_model=RecoveryExecutionResponse)
def execute_recovery(transaction_id: int, request: ExecuteRecoveryRequest, db: Session = Depends(get_db)):
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    try:
        action = RecoveryAction(request.action)
    except ValueError:
        _audit(db, transaction, "POLICY_ENGINE", "INVALID_ACTION", "Requested action is not valid.", transaction.recovery_status.value, transaction.recovery_status.value, "BLOCKED")
        db.commit()
        raise HTTPException(status_code=422, detail="Invalid recovery action")

    recommendation = RecoveryAgent(db).analyze_transaction(transaction_id)
    attempts = db.execute(select(RecoveryAttempt).where(RecoveryAttempt.transaction_id == transaction_id)).scalars().all()
    policy = PolicyEngine().check(transaction, action, recommendation, attempts)
    attempt = RecoveryAttempt(transaction_id=transaction.id, action=action, status=RecoveryAttemptStatus.PENDING, amount=transaction.amount, attempt_number=_attempt_number(db, transaction.id), reason=policy.reason)
    db.add(attempt)
    if not policy.allowed:
        attempt.status = RecoveryAttemptStatus.BLOCKED
        attempt.result = policy.reason
        _audit(db, transaction, "POLICY_ENGINE", "POLICY_BLOCK", policy.reason, transaction.recovery_status.value, transaction.recovery_status.value, "BLOCKED", {"policy_rule": policy.policy_rule})
        db.commit()
        return _execution_response("BLOCKED", transaction, action, policy.reason, True, policy.reason, attempt.id)
    if policy.requires_human_approval:
        _audit(db, transaction, "POLICY_ENGINE", "POLICY_APPROVAL_REQUIRED", policy.reason, transaction.recovery_status.value, transaction.recovery_status.value, "PENDING", {"policy_rule": policy.policy_rule})
        db.commit()
        return _execution_response("AWAITING_HUMAN_APPROVAL", transaction, action, policy.reason, True, policy.reason, attempt.id, True)

    previous_state = transaction.recovery_status.value
    transaction.recovery_status = RecoveryStatus.RECOVERY_IN_PROGRESS
    _audit(db, transaction, "POLICY_ENGINE", "POLICY_APPROVED", policy.reason, previous_state, transaction.recovery_status.value, "APPROVED")
    result = RecoveryExecutor().execute(transaction, action)
    transaction.recovery_status = result.next_state
    if action == RecoveryAction.RETRY_PAYMENT:
        transaction.retry_count += 1
    attempt.status = RecoveryAttemptStatus.SUCCESS if result.success else RecoveryAttemptStatus.ESCALATED if result.next_state == RecoveryStatus.ESCALATED else RecoveryAttemptStatus.FAILED
    attempt.result = result.message
    _audit(db, transaction, "SYSTEM", "SIMULATED_RECOVERY", result.stop_reason or result.message, previous_state, result.next_state.value, "SUCCESS" if result.success else "FAILED", {"simulated": True, "action": action.value})
    db.commit()
    return _execution_response("RECOVERED" if result.success else "ESCALATED" if result.next_state == RecoveryStatus.ESCALATED else "FAILED", transaction, action, result.message, result.stopped, result.stop_reason, attempt.id)


def _approve_or_reject(attempt_id: int, approve: bool, db: Session):
    attempt = db.get(RecoveryAttempt, attempt_id)
    if attempt is None:
        raise HTTPException(status_code=404, detail="Recovery attempt not found")
    if attempt.status != RecoveryAttemptStatus.PENDING:
        raise HTTPException(status_code=409, detail="Recovery attempt is no longer pending")
    transaction = db.get(Transaction, attempt.transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not approve:
        attempt.status = RecoveryAttemptStatus.REJECTED
        attempt.result = "Rejected by human reviewer."
        _audit(db, transaction, "HUMAN_REVIEWER", "HUMAN_REJECTION", "Recovery action rejected by human reviewer.", transaction.recovery_status.value, transaction.recovery_status.value, "REJECTED")
        db.commit()
        return _execution_response("REJECTED", transaction, attempt.action, attempt.result, True, "Human approval was rejected.", attempt.id)

    recommendation = RecoveryAgent(db).analyze_transaction(transaction.id)
    attempts = db.execute(select(RecoveryAttempt).where(RecoveryAttempt.transaction_id == transaction.id, RecoveryAttempt.id != attempt.id)).scalars().all()
    policy = PolicyEngine().check(transaction, attempt.action, recommendation, attempts)
    if not policy.allowed:
        attempt.status = RecoveryAttemptStatus.BLOCKED
        attempt.result = policy.reason
        _audit(db, transaction, "POLICY_ENGINE", "POLICY_BLOCK", policy.reason, transaction.recovery_status.value, transaction.recovery_status.value, "BLOCKED", {"policy_rule": policy.policy_rule, "rechecked": True})
        db.commit()
        return _execution_response("BLOCKED", transaction, attempt.action, policy.reason, True, policy.reason, attempt.id)

    previous_state = transaction.recovery_status.value
    transaction.recovery_status = RecoveryStatus.RECOVERY_IN_PROGRESS
    _audit(db, transaction, "HUMAN_REVIEWER", "HUMAN_APPROVAL", "Pending recovery action approved by human reviewer.", previous_state, transaction.recovery_status.value, "APPROVED")
    result = RecoveryExecutor().execute(transaction, attempt.action)
    transaction.recovery_status = result.next_state
    if attempt.action == RecoveryAction.RETRY_PAYMENT:
        transaction.retry_count += 1
    attempt.status = RecoveryAttemptStatus.SUCCESS if result.success else RecoveryAttemptStatus.ESCALATED if result.next_state == RecoveryStatus.ESCALATED else RecoveryAttemptStatus.FAILED
    attempt.result = result.message
    _audit(db, transaction, "SYSTEM", "SIMULATED_RECOVERY", result.stop_reason or result.message, previous_state, result.next_state.value, "SUCCESS" if result.success else "FAILED", {"simulated": True, "approved": True})
    db.commit()
    return _execution_response("RECOVERED" if result.success else "ESCALATED" if result.next_state == RecoveryStatus.ESCALATED else "FAILED", transaction, attempt.action, result.message, result.stopped, result.stop_reason, attempt.id)


@router.post("/attempts/{attempt_id}/approve", response_model=RecoveryExecutionResponse)
def approve_recovery(attempt_id: int, db: Session = Depends(get_db)):
    return _approve_or_reject(attempt_id, True, db)


@router.post("/attempts/{attempt_id}/reject", response_model=RecoveryExecutionResponse)
def reject_recovery(attempt_id: int, db: Session = Depends(get_db)):
    return _approve_or_reject(attempt_id, False, db)


@router.get("/transactions/{transaction_id}/history", response_model=RecoveryHistory)
def recovery_history(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    attempts = db.execute(select(RecoveryAttempt).where(RecoveryAttempt.transaction_id == transaction_id).order_by(RecoveryAttempt.executed_at.desc())).scalars().all()
    audits = db.execute(select(AuditLog).where(AuditLog.transaction_id == transaction_id).order_by(AuditLog.timestamp.desc())).scalars().all()
    return RecoveryHistory(transaction_id=transaction_id, current_recovery_state=transaction.recovery_status.value, recovery_attempts=attempts, audit_events=audits)
