from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit import AuditLog
from app.models.customer import Customer
from app.models.recovery import RecoveryAttempt
from app.models.transaction import Transaction
from app.schemas.audit import AuditLog as AuditLogSchema
from app.schemas.customer import Customer as CustomerSchema
from app.schemas.recovery import RecoveryAttempt as RecoveryAttemptSchema
from app.schemas.transaction import Transaction as TransactionSchema

router = APIRouter(prefix="/api", tags=["transactions"])


@router.get("/transactions", response_model=list[TransactionSchema])
def list_transactions(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Transaction).offset(offset).limit(limit).order_by(Transaction.created_at.desc())
    return db.execute(stmt).scalars().all()


@router.get("/transactions/{transaction_id}", response_model=TransactionSchema)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    item = db.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return item


@router.get("/customers", response_model=list[CustomerSchema])
def list_customers(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Customer).offset(offset).limit(limit).order_by(Customer.created_at.desc())
    return db.execute(stmt).scalars().all()


@router.get("/customers/{customer_id}", response_model=CustomerSchema)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    item = db.get(Customer, customer_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return item


@router.get("/recovery-attempts", response_model=list[RecoveryAttemptSchema])
def list_recovery_attempts(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(RecoveryAttempt).offset(offset).limit(limit).order_by(RecoveryAttempt.executed_at.desc())
    return db.execute(stmt).scalars().all()


@router.get("/audit-logs", response_model=list[AuditLogSchema])
def list_audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(AuditLog).offset(offset).limit(limit).order_by(AuditLog.timestamp.desc())
    return db.execute(stmt).scalars().all()
