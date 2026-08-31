from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.customer import Customer
from app.models.transaction import FailureReason, RiskLevel, Transaction, TransactionStatus, TransactionType
from app.agents.diagnosis import DiagnosisEngine
from app.agents.decision_engine import DecisionEngine
from app.agents.recovery_agent import RecoveryAgent
from app.agents.risk_analyzer import RiskAnalyzer, RiskAssessment
from app.models.recovery import RecoveryAction


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


def make_transaction(**overrides) -> Transaction:
    values = {
        "external_transaction_id": "TXN-TEST",
        "customer_id": 1,
        "amount": 2_000.0,
        "currency": "INR",
        "transaction_type": TransactionType.PAYMENT,
        "status": TransactionStatus.FAILED,
        "failure_reason": FailureReason.NETWORK_ERROR,
        "retry_count": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    values.update(overrides)
    return Transaction(**values)


def test_risk_analyzer_covers_low_medium_high_and_repeated_failure():
    analyzer = RiskAnalyzer()
    customer = Customer(total_transactions=10, successful_transactions=9, failed_transactions=1, lifetime_value=10_000)
    assert analyzer.analyze(make_transaction(status=TransactionStatus.SUCCESS), customer).risk_level == RiskLevel.LOW
    assert analyzer.analyze(make_transaction(amount=12_000, failure_reason=FailureReason.NETWORK_ERROR), customer).risk_level == RiskLevel.MEDIUM
    assert analyzer.analyze(make_transaction(amount=60_000, failure_reason=FailureReason.BANK_DECLINED), customer).risk_level == RiskLevel.HIGH
    repeated = analyzer.analyze(make_transaction(amount=60_000, failure_reason=FailureReason.BANK_DECLINED, retry_count=2), customer)
    assert repeated.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
    assert repeated.risk_score > analyzer.analyze(make_transaction(amount=60_000, failure_reason=FailureReason.BANK_DECLINED), customer).risk_score
    assert 0 <= repeated.risk_score <= 1


@pytest.mark.parametrize(
    ("transaction", "code"),
    [
        (make_transaction(failure_reason=FailureReason.NETWORK_ERROR), "NETWORK_ERROR"),
        (make_transaction(failure_reason=FailureReason.BANK_DECLINED), "BANK_DECLINED"),
        (make_transaction(failure_reason=FailureReason.EXPIRED_CARD), "EXPIRED_CARD"),
        (make_transaction(status=TransactionStatus.ABANDONED, transaction_type=TransactionType.CHECKOUT, failure_reason=None), "ABANDONED"),
    ],
)
def test_diagnosis_engine(transaction, code):
    diagnosis = DiagnosisEngine().diagnose(transaction)
    assert diagnosis.code == code
    assert diagnosis.message


def test_decision_engine_covers_allowlisted_actions():
    engine = DecisionEngine()
    risk = RiskAssessment(RiskLevel.MEDIUM, 0.4, [])
    assert engine.decide(make_transaction(failure_reason=FailureReason.NETWORK_ERROR), None, risk, 0.8).action == RecoveryAction.RETRY_PAYMENT
    assert engine.decide(make_transaction(failure_reason=FailureReason.NETWORK_ERROR, retry_count=2), None, risk, 0.8).action == RecoveryAction.GENERATE_PAYMENT_LINK
    assert engine.decide(make_transaction(status=TransactionStatus.ABANDONED), None, risk, 0.7).action == RecoveryAction.SEND_CUSTOMER_REMINDER
    assert engine.decide(make_transaction(failure_reason=FailureReason.EXPIRED_CARD), None, risk, 0.7).action == RecoveryAction.OFFER_ALTERNATIVE_PAYMENT
    assert engine.decide(make_transaction(failure_reason=FailureReason.BANK_DECLINED, retry_count=2), None, risk, 0.2).action == RecoveryAction.ESCALATE_TO_HUMAN
    assert engine.decide(make_transaction(failure_reason=FailureReason.BANK_DECLINED), None, risk, 0.1).action == RecoveryAction.NO_ACTION


def test_api_analysis_404_and_analytics(client, db_session: Session):
    customer = Customer(external_customer_id="CUST-TEST", name="Test Customer", email="test@example.com", total_transactions=8, successful_transactions=7, failed_transactions=1, lifetime_value=20_000)
    db_session.add(customer)
    db_session.flush()
    failed = make_transaction(customer_id=customer.id)
    abandoned = make_transaction(external_transaction_id="TXN-TEST-2", customer_id=customer.id, status=TransactionStatus.ABANDONED, transaction_type=TransactionType.CHECKOUT, failure_reason=None)
    success = make_transaction(external_transaction_id="TXN-TEST-3", customer_id=customer.id, status=TransactionStatus.SUCCESS, failure_reason=None)
    db_session.add_all([failed, abandoned, success])
    db_session.commit()

    response = client.post(f"/api/recovery/analyze/{failed.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["recommended_action"] == "RETRY_PAYMENT"
    assert 0 <= body["risk_score"] <= 1
    assert 0 <= body["recovery_probability"] <= 1
    assert client.post("/api/recovery/analyze/99999").status_code == 404

    at_risk = client.get("/api/recovery/at-risk?limit=10&offset=0")
    assert at_risk.status_code == 200
    assert len(at_risk.json()) == 2
    summary = client.get("/api/recovery/summary")
    assert summary.status_code == 200
    assert summary.json()["at_risk_transaction_count"] == 2
    assert summary.json()["revenue_at_risk"] == 4000.0
    assert sum(summary.json()["risk_distribution"].values()) == 2


def test_human_approval_for_high_value_critical_and_repeated_failures(db_session: Session):
    customer = Customer(external_customer_id="CUST-APPROVAL", name="Approval Customer", email="approval@example.com", total_transactions=3, successful_transactions=1, failed_transactions=2, lifetime_value=100_000)
    db_session.add(customer)
    db_session.flush()
    high_value = make_transaction(external_transaction_id="TXN-HIGH", customer_id=customer.id, amount=60_000, failure_reason=FailureReason.NETWORK_ERROR)
    critical = make_transaction(external_transaction_id="TXN-CRITICAL", customer_id=customer.id, amount=60_000, failure_reason=FailureReason.BANK_DECLINED, retry_count=2)
    repeated = make_transaction(external_transaction_id="TXN-REPEATED", customer_id=customer.id, retry_count=2, amount=2_000)
    db_session.add_all([high_value, critical, repeated])
    db_session.commit()

    agent = RecoveryAgent(db_session)
    assert agent.analyze_transaction(high_value.id).requires_human_approval is True
    assert agent.analyze_transaction(critical.id).requires_human_approval is True
    assert agent.analyze_transaction(repeated.id).requires_human_approval is True
