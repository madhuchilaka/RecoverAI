from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.recovery import RecoveryAction, RecoveryAttemptStatus
from app.models.transaction import RiskLevel, TransactionStatus


class RecoveryAttemptBase(BaseModel):
    transaction_id: int = Field(..., gt=0)
    action: RecoveryAction
    status: RecoveryAttemptStatus = RecoveryAttemptStatus.PENDING
    amount: float | None = Field(default=None, gt=0)
    attempt_number: int = Field(default=1, ge=1)
    reason: str | None = Field(default=None, max_length=200)
    result: str | None = Field(default=None, max_length=200)


class RecoveryAttemptCreate(RecoveryAttemptBase):
    pass


class RecoveryAttempt(RecoveryAttemptBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    executed_at: datetime


class RecoveryAnalysis(BaseModel):
    transaction_id: int = Field(..., gt=0)
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=1)
    recovery_probability: float = Field(..., ge=0, le=1)
    diagnosis: str = Field(..., min_length=1)
    recommended_action: RecoveryAction
    reasoning: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0, le=1)
    requires_human_approval: bool


class AtRiskTransaction(BaseModel):
    transaction_id: int = Field(..., gt=0)
    external_transaction_id: str
    customer_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    currency: str
    status: TransactionStatus
    risk_level: RiskLevel
    recovery_probability: float = Field(..., ge=0, le=1)


class RecoverySummary(BaseModel):
    initial_revenue_at_risk: float = Field(default=0, ge=0)
    revenue_at_risk: float = Field(..., ge=0)
    current_revenue_at_risk: float = Field(default=0, ge=0)
    at_risk_transaction_count: int = Field(..., ge=0)
    average_transaction_value: float = Field(..., ge=0)
    risk_distribution: dict[RiskLevel, int]
    recovered_revenue: float = Field(default=0, ge=0)
    recovery_rate: float = Field(default=0, ge=0, le=1)
    at_risk_transactions: int = Field(default=0, ge=0)
    recovery_attempts: int = Field(default=0, ge=0)
    successful_recoveries: int = Field(default=0, ge=0)
    failed_recoveries: int = Field(default=0, ge=0)
    escalations: int = Field(default=0, ge=0)
    blocked_actions: int = Field(default=0, ge=0)
    pending_approvals: int = Field(default=0, ge=0)


class ExecuteRecoveryRequest(BaseModel):
    action: str = Field(..., min_length=1, max_length=80)


class RecoveryExecutionResponse(BaseModel):
    status: str
    transaction_id: int
    action: RecoveryAction
    amount: float = Field(..., gt=0)
    message: str
    stopped: bool
    stop_reason: str | None = None
    attempt_id: int | None = None
    requires_human_approval: bool = False


class AuditEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor: str
    action: str
    reason: str | None = None
    previous_state: str | None = None
    new_state: str | None = None
    result: str | None = None
    details: str | None = None
    timestamp: datetime


class RecoveryHistory(BaseModel):
    transaction_id: int
    current_recovery_state: str
    recovery_attempts: list[RecoveryAttempt]
    audit_events: list[AuditEvent]
