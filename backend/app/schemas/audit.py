from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    transaction_id: int = Field(..., gt=0)
    actor: str = Field(..., min_length=1, max_length=80)
    action: str = Field(..., min_length=1, max_length=80)
    reason: str | None = Field(default=None, max_length=200)
    previous_state: str | None = Field(default=None, max_length=80)
    new_state: str | None = Field(default=None, max_length=80)
    result: str | None = Field(default=None, max_length=80)
    details: str | None = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLog(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
