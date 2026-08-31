from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.transaction import FailureReason, RecoveryStatus, RiskLevel, TransactionStatus, TransactionType


class TransactionBase(BaseModel):
    external_transaction_id: str = Field(..., min_length=1, max_length=80)
    customer_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=10)
    transaction_type: TransactionType
    status: TransactionStatus
    failure_reason: FailureReason | None = None
    retry_count: int = Field(default=0, ge=0)
    recovery_status: RecoveryStatus = RecoveryStatus.NOT_ANALYZED
    recovery_probability: float | None = Field(default=None, ge=0, le=1)
    risk_level: RiskLevel = RiskLevel.LOW

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        return value.upper()


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
