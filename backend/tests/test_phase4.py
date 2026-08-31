from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.audit import AuditLog
from app.models.customer import Customer
from app.models.recovery import RecoveryAction, RecoveryAttempt, RecoveryAttemptStatus
from app.models.transaction import FailureReason, RecoveryStatus, RiskLevel, Transaction, TransactionStatus, TransactionType
from app.services.recovery_executor import RecoveryExecutor


@pytest.fixture
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def add_customer(db: Session) -> Customer:
    customer = Customer(external_customer_id="CUST-P4", name="Phase Four", email="phase4@example.com", total_transactions=10, successful_transactions=8, failed_transactions=2, lifetime_value=100_000)
    db.add(customer)
    db.flush()
    return customer


def add_transaction(db: Session, customer: Customer, **overrides) -> Transaction:
    values = {
        "external_transaction_id": f"TXN-P4-{id(overrides)}",
        "customer_id": customer.id,
        "amount": 2_000.0,
        "currency": "INR",
        "transaction_type": TransactionType.PAYMENT,
        "status": TransactionStatus.FAILED,
        "failure_reason": FailureReason.NETWORK_ERROR,
        "retry_count": 0,
        "recovery_status": RecoveryStatus.AT_RISK,
        "risk_level": RiskLevel.MEDIUM,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    values.update(overrides)
    transaction = Transaction(**values)
    db.add(transaction)
    db.flush()
    return transaction


def test_executor_is_deterministic_and_test_mode():
    transaction = Transaction(id=1, amount=2_000, status=TransactionStatus.FAILED, failure_reason=FailureReason.NETWORK_ERROR, retry_count=0)
    first = RecoveryExecutor().execute(transaction, RecoveryAction.RETRY_PAYMENT)
    second = RecoveryExecutor().execute(transaction, RecoveryAction.RETRY_PAYMENT)
    assert first == second
    assert first.success is True
    assert first.next_state == RecoveryStatus.RECOVERED
    assert "Simulated/test-mode" in first.message


def test_execute_success_updates_state_attempt_and_audit(client, db_session: Session):
    customer = add_customer(db_session)
    transaction = add_transaction(db_session, customer)
    db_session.commit()

    response = client.post(f"/api/recovery/execute/{transaction.id}", json={"action": "RETRY_PAYMENT"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "RECOVERED"
    assert body["stopped"] is True
    db_session.refresh(transaction)
    assert transaction.recovery_status == RecoveryStatus.RECOVERED
    assert db_session.query(RecoveryAttempt).count() == 1
    assert db_session.query(RecoveryAttempt).one().status == RecoveryAttemptStatus.SUCCESS
    assert db_session.query(AuditLog).count() >= 2


def test_failed_retry_escalates_after_second_retry_and_limit_blocks(client, db_session: Session):
    customer = add_customer(db_session)
    transaction = add_transaction(db_session, customer, external_transaction_id="TXN-FAIL-RETRY", retry_count=1, failure_reason=FailureReason.NETWORK_ERROR)
    db_session.commit()

    failed = client.post(f"/api/recovery/execute/{transaction.id}", json={"action": "RETRY_PAYMENT"})
    assert failed.json()["status"] == "FAILED"
    db_session.refresh(transaction)
    assert transaction.recovery_status == RecoveryStatus.AT_RISK
    blocked = client.post(f"/api/recovery/execute/{transaction.id}", json={"action": "RETRY_PAYMENT"})
    assert blocked.json()["status"] == "BLOCKED"
    assert "retry" in blocked.json()["message"].lower()


def test_failed_retry_allows_payment_link_fallback(client, db_session: Session):
    customer = add_customer(db_session)
    transaction = add_transaction(db_session, customer, external_transaction_id="TXN-FALLBACK", retry_count=1)
    db_session.commit()
    failed = client.post(f"/api/recovery/execute/{transaction.id}", json={"action": "RETRY_PAYMENT"})
    assert failed.json()["status"] == "FAILED"
    link = client.post(f"/api/recovery/execute/{transaction.id}", json={"action": "GENERATE_PAYMENT_LINK"})
    assert link.json()["status"] == "RECOVERED"


def test_payment_link_abandoned_alternative_and_escalation_actions(client, db_session: Session):
    customer = add_customer(db_session)
    abandoned = add_transaction(db_session, customer, external_transaction_id="TXN-ABANDONED", status=TransactionStatus.ABANDONED, failure_reason=None, transaction_type=TransactionType.CHECKOUT)
    db_session.commit()
    reminder = client.post(f"/api/recovery/execute/{abandoned.id}", json={"action": "SEND_CUSTOMER_REMINDER"})
    assert reminder.status_code == 200
    assert reminder.json()["status"] in {"RECOVERED", "FAILED"}

    card = add_transaction(db_session, customer, external_transaction_id="TXN-CARD", failure_reason=FailureReason.EXPIRED_CARD)
    db_session.commit()
    alternative = client.post(f"/api/recovery/execute/{card.id}", json={"action": "OFFER_ALTERNATIVE_PAYMENT"})
    assert alternative.status_code == 200
    assert alternative.json()["action"] == "OFFER_ALTERNATIVE_PAYMENT"


def test_high_value_approval_approve_and_reject(client, db_session: Session):
    customer = add_customer(db_session)
    high_value = add_transaction(db_session, customer, external_transaction_id="TXN-HIGH-VALUE", amount=60_000)
    rejected = add_transaction(db_session, customer, external_transaction_id="TXN-REJECTED", amount=60_000)
    db_session.commit()

    pending = client.post(f"/api/recovery/execute/{high_value.id}", json={"action": "RETRY_PAYMENT"})
    assert pending.json()["status"] == "AWAITING_HUMAN_APPROVAL"
    attempt_id = pending.json()["attempt_id"]
    approved = client.post(f"/api/recovery/attempts/{attempt_id}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] in {"RECOVERED", "FAILED"}

    pending_rejection = client.post(f"/api/recovery/execute/{rejected.id}", json={"action": "RETRY_PAYMENT"})
    rejected_response = client.post(f"/api/recovery/attempts/{pending_rejection.json()['attempt_id']}/reject")
    assert rejected_response.json()["status"] == "REJECTED"
    db_session.refresh(rejected)
    assert rejected.recovery_status == RecoveryStatus.AT_RISK


def test_invalid_action_terminal_state_history_and_summary(client, db_session: Session):
    customer = add_customer(db_session)
    transaction = add_transaction(db_session, customer, external_transaction_id="TXN-INVALID")
    terminal = add_transaction(db_session, customer, external_transaction_id="TXN-TERMINAL", recovery_status=RecoveryStatus.RECOVERED)
    terminal.amount = 1_000
    db_session.commit()

    invalid = client.post(f"/api/recovery/execute/{transaction.id}", json={"action": "SEND_MONEY"})
    assert invalid.status_code == 422
    assert db_session.query(AuditLog).filter(AuditLog.action == "INVALID_ACTION").count() == 1
    blocked = client.post(f"/api/recovery/execute/{terminal.id}", json={"action": "RETRY_PAYMENT"})
    assert blocked.json()["status"] == "BLOCKED"

    history = client.get(f"/api/recovery/transactions/{transaction.id}/history")
    assert history.status_code == 200
    assert history.json()["current_recovery_state"] == "AT_RISK"
    assert history.json()["audit_events"]
    summary = client.get("/api/recovery/summary")
    assert summary.status_code == 200
    body = summary.json()
    assert body["recovered_revenue"] == 1_000
    assert body["recovery_rate"] > 0
    assert body["recovery_attempts"] >= 1
