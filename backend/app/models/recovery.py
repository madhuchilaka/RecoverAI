from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecoveryAction(str, enum.Enum):
    RETRY_PAYMENT = "RETRY_PAYMENT"
    GENERATE_PAYMENT_LINK = "GENERATE_PAYMENT_LINK"
    SEND_CUSTOMER_REMINDER = "SEND_CUSTOMER_REMINDER"
    OFFER_ALTERNATIVE_PAYMENT = "OFFER_ALTERNATIVE_PAYMENT"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"
    NO_ACTION = "NO_ACTION"


class RecoveryAttemptStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    ESCALATED = "ESCALATED"
    REJECTED = "REJECTED"


class RecoveryAttempt(Base):
    __tablename__ = "recovery_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), index=True, nullable=False)
    action: Mapped[RecoveryAction] = mapped_column(Enum(RecoveryAction), nullable=False)
    status: Mapped[RecoveryAttemptStatus] = mapped_column(Enum(RecoveryAttemptStatus), default=RecoveryAttemptStatus.PENDING, nullable=False)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    result: Mapped[str | None] = mapped_column(String(200), nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    transaction: Mapped["Transaction"] = relationship(back_populates="recovery_attempts")
