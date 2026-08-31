from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import SessionLocal, init_db
from app.models.audit import AuditLog
from app.models.customer import Customer
from app.models.recovery import RecoveryAction, RecoveryAttempt, RecoveryAttemptStatus
from app.models.transaction import (
    FailureReason,
    RecoveryStatus,
    RiskLevel,
    Transaction,
    TransactionStatus,
    TransactionType,
)

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "recoverai.db"


def generate_phone() -> str:
    return f"+91{random.randint(7000000000, 9999999999)}"


def generate_email(name: str) -> str:
    safe = name.lower().replace(" ", "").replace(".", "")
    return f"{safe}{random.randint(100, 9999)}@example.com"


def generate_customer_name() -> str:
    first = random.choice([
        "Aarav", "Ishita", "Karan", "Meera", "Rohan", "Priya", "Nisha", "Aniket",
        "Saanvi", "Vikram", "Aanya", "Rahul", "Pooja", "Harsh", "Neha", "Tanvi",
        "Aditya", "Ritika", "Kunal", "Suhani", "Dev", "Mira", "Yash", "Shreya"
    ])
    last = random.choice([
        "Sharma", "Patel", "Mehta", "Singh", "Nair", "Reddy", "Iyer", "Gupta",
        "Joshi", "Kapoor", "Verma", "Saxena", "Khan", "Chopra", "Desai", "Malhotra"
    ])
    return f"{first} {last}"


def generate_customer_data() -> list[Customer]:
    customers: list[Customer] = []
    customer_count = 400

    for idx in range(1, customer_count + 1):
        name = generate_customer_name()
        customer = Customer(
            external_customer_id=f"CUST-{idx:06d}",
            name=name,
            email=generate_email(name),
            phone=generate_phone(),
            total_transactions=0,
            successful_transactions=0,
            failed_transactions=0,
            lifetime_value=0.0,
        )
        customers.append(customer)

    return customers


def generate_amount() -> float:
    bucket = random.choices(
        [
            (100, 1000),
            (1001, 10000),
            (10001, 50000),
            (50001, 200000),
        ],
        weights=[0.35, 0.40, 0.20, 0.05],
        k=1,
    )[0]
    return round(random.uniform(bucket[0], bucket[1]), 2)


def generate_failure_reason() -> FailureReason | None:
    reasons = [
        FailureReason.INSUFFICIENT_FUNDS,
        FailureReason.NETWORK_ERROR,
        FailureReason.BANK_DECLINED,
        FailureReason.EXPIRED_CARD,
        FailureReason.AUTHENTICATION_FAILED,
        FailureReason.UNKNOWN,
    ]
    return random.choices(reasons, weights=[0.22, 0.22, 0.18, 0.16, 0.12, 0.10], k=1)[0]


def generate_status() -> tuple[TransactionStatus, FailureReason | None, int]:
    outcome = random.choices(
        [
            (TransactionStatus.SUCCESS, None, 0),
            (TransactionStatus.FAILED, generate_failure_reason(), 0),
            (TransactionStatus.FAILED, generate_failure_reason(), 1),
            (TransactionStatus.FAILED, generate_failure_reason(), 2),
            (TransactionStatus.ABANDONED, None, 0),
            (TransactionStatus.PENDING, None, 0),
        ],
        weights=[0.60, 0.18, 0.12, 0.05, 0.03, 0.02],
        k=1,
    )[0]
    return outcome[0], outcome[1], outcome[2]


def generate_transaction_type() -> TransactionType:
    return random.choices(
        [TransactionType.PAYMENT, TransactionType.SUBSCRIPTION, TransactionType.CHECKOUT],
        weights=[0.56, 0.22, 0.22],
        k=1,
    )[0]


def generate_recovery_status(status: TransactionStatus, retry_count: int, risk_level: RiskLevel) -> RecoveryStatus:
    if status == TransactionStatus.SUCCESS:
        return RecoveryStatus.NOT_ANALYZED
    if risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL} and retry_count >= 1:
        return RecoveryStatus.AT_RISK
    return RecoveryStatus.NOT_ANALYZED


def generate_transaction_data(customers: list[Customer]) -> list[Transaction]:
    transactions: list[Transaction] = []
    now = datetime.utcnow()

    for idx in range(1, 2001):
        customer = random.choice(customers)
        customer_id = customer.id
        tx_type = generate_transaction_type()
        status, failure_reason, retry_count = generate_status()
        amount = generate_amount()
        risk_level = RiskLevel.LOW

        if status == TransactionStatus.SUCCESS:
            failure_reason = None
            retry_count = random.choices([0, 1], weights=[0.9, 0.1], k=1)[0]
            risk_level = RiskLevel.LOW
        elif status == TransactionStatus.FAILED:
            if retry_count >= 2 or amount >= 50000:
                risk_level = RiskLevel.HIGH if random.random() < 0.7 else RiskLevel.CRITICAL
            elif amount >= 15000:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
        elif status == TransactionStatus.ABANDONED:
            risk_level = RiskLevel.MEDIUM if amount >= 5000 else RiskLevel.LOW
        else:
            risk_level = RiskLevel.MEDIUM

        recovery_status = generate_recovery_status(status, retry_count, risk_level)
        probability = None
        if recovery_status == RecoveryStatus.AT_RISK:
            probability = round(random.uniform(0.45, 0.9), 2)
        elif status == TransactionStatus.FAILED and random.random() < 0.35:
            probability = round(random.uniform(0.2, 0.75), 2)

        tx = Transaction(
            external_transaction_id=f"TXN-{idx:06d}",
            customer_id=customer_id,
            amount=amount,
            currency="INR",
            transaction_type=tx_type,
            status=status,
            failure_reason=failure_reason,
            retry_count=retry_count,
            recovery_status=recovery_status,
            recovery_probability=probability,
            risk_level=risk_level,
            created_at=now - timedelta(days=random.randint(0, 180), hours=random.randint(0, 23), minutes=random.randint(0, 59)),
            updated_at=now,
        )
        transactions.append(tx)

    return transactions


def seed_database() -> dict:
    init_db()
    db: Session = SessionLocal()
    try:
        db.query(Customer).delete()
        db.query(Transaction).delete()
        db.query(RecoveryAttempt).delete()
        db.query(AuditLog).delete()
        db.commit()

        customers = generate_customer_data()
        db.add_all(customers)
        db.commit()

        for customer in customers:
            db.refresh(customer)

        transactions = generate_transaction_data(customers)
        db.add_all(transactions)
        db.commit()

        for transaction in transactions:
            db.refresh(transaction)

        for customer in customers:
            customer.total_transactions = sum(1 for tx in transactions if tx.customer_id == customer.id)
            customer.successful_transactions = sum(1 for tx in transactions if tx.customer_id == customer.id and tx.status == TransactionStatus.SUCCESS)
            customer.failed_transactions = sum(1 for tx in transactions if tx.customer_id == customer.id and tx.status == TransactionStatus.FAILED)
            customer.lifetime_value = round(sum(tx.amount for tx in transactions if tx.customer_id == customer.id), 2)

        db.commit()

        recovery_attempts: list[RecoveryAttempt] = []
        for idx, tx in enumerate(transactions[:300], start=1):
            if tx.status == TransactionStatus.FAILED:
                action = random.choice([
                    RecoveryAction.RETRY_PAYMENT,
                    RecoveryAction.GENERATE_PAYMENT_LINK,
                    RecoveryAction.SEND_CUSTOMER_REMINDER,
                    RecoveryAction.OFFER_ALTERNATIVE_PAYMENT,
                    RecoveryAction.ESCALATE_TO_HUMAN,
                ])
                attempt = RecoveryAttempt(
                    transaction_id=tx.id,
                    action=action,
                    status=random.choice([RecoveryAttemptStatus.SUCCESS, RecoveryAttemptStatus.FAILED, RecoveryAttemptStatus.BLOCKED]),
                    amount=tx.amount,
                    attempt_number=1,
                    reason="Synthetic demo recovery action",
                    result="Synthetic demo result",
                )
                recovery_attempts.append(attempt)

        if recovery_attempts:
            db.add_all(recovery_attempts)
            db.commit()

        audit_logs: list[AuditLog] = []
        for tx in transactions[:150]:
            if tx.status == TransactionStatus.FAILED:
                audit_logs.append(
                    AuditLog(
                        transaction_id=tx.id,
                        actor="SYSTEM",
                        action="DATA_SEED",
                        reason="Synthetic transaction dataset generation",
                        previous_state="NEW",
                        new_state="RECORDED",
                        result="OK",
                        details='{"synthetic": true, "phase": 2}',
                    )
                )

        if audit_logs:
            db.add_all(audit_logs)
            db.commit()

        stats = {
            "customers": len(customers),
            "transactions": len(transactions),
            "successful": sum(1 for tx in transactions if tx.status == TransactionStatus.SUCCESS),
            "failed": sum(1 for tx in transactions if tx.status == TransactionStatus.FAILED),
            "abandoned": sum(1 for tx in transactions if tx.status == TransactionStatus.ABANDONED),
            "pending": sum(1 for tx in transactions if tx.status == TransactionStatus.PENDING),
            "total_value": round(sum(tx.amount for tx in transactions), 2),
            "failed_value": round(sum(tx.amount for tx in transactions if tx.status == TransactionStatus.FAILED), 2),
        }
        db.close()
        return stats

    finally:
        db.close()


if __name__ == "__main__":
    stats = seed_database()
    print("RecoverAI Demo Dataset")
    print("----------------------")
    print(f"Customers: {stats['customers']}")
    print(f"Transactions: {stats['transactions']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Abandoned: {stats['abandoned']}")
    print(f"Pending: {stats['pending']}")
    print(f"Total transaction value: ₹{stats['total_value']:,}")
    print(f"Failed transaction value: ₹{stats['failed_value']:,}")
