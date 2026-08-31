from __future__ import annotations

from dataclasses import dataclass

from app.agents.recovery_agent import RecoveryRecommendation
from app.config import settings
from app.models.recovery import RecoveryAction, RecoveryAttempt, RecoveryAttemptStatus
from app.models.transaction import RecoveryStatus, RiskLevel, Transaction, TransactionStatus


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    requires_human_approval: bool
    reason: str
    policy_rule: str


class PolicyEngine:
    """Deterministic guardrails for simulated recovery actions."""

    HIGH_VALUE_THRESHOLD = settings.high_value_threshold
    MAX_AUTOMATIC_RETRY_ATTEMPTS = 2
    ALLOWED_ACTIONS = frozenset(RecoveryAction)

    def check(
        self,
        transaction: Transaction,
        action: RecoveryAction,
        recommendation: RecoveryRecommendation | None = None,
        attempts: list[RecoveryAttempt] | None = None,
    ) -> PolicyDecision:
        attempts = attempts or []
        if action not in self.ALLOWED_ACTIONS:
            return PolicyDecision(False, False, "Action is not in the recovery allowlist.", "RULE_7_INVALID_ACTION")
        if transaction.status == TransactionStatus.SUCCESS or transaction.recovery_status == RecoveryStatus.RECOVERED:
            return PolicyDecision(False, False, "The transaction is already successful or recovered.", "RULE_6_TERMINAL_STATE")
        if action == RecoveryAction.RETRY_PAYMENT and transaction.retry_count >= self.MAX_AUTOMATIC_RETRY_ATTEMPTS:
            return PolicyDecision(False, False, "Maximum automatic retry attempts reached.", "RULE_2_RETRY_LIMIT")
        failed_attempts = sum(attempt.status == RecoveryAttemptStatus.FAILED for attempt in attempts)
        if failed_attempts >= 2:
            return PolicyDecision(False, False, "A previous recovery failure requires escalation before another automatic action.", "RULE_5_REPEATED_FAILURE")
        critical = recommendation is not None and recommendation.risk_level == RiskLevel.CRITICAL
        high_value = transaction.amount > self.HIGH_VALUE_THRESHOLD
        explicit_escalation = action == RecoveryAction.ESCALATE_TO_HUMAN
        if critical or high_value or explicit_escalation:
            reason = "Critical risk requires approval." if critical else "High-value transaction requires approval." if high_value else "The recommended action requires human review."
            return PolicyDecision(True, True, reason, "RULE_3_4_HUMAN_APPROVAL")
        return PolicyDecision(True, False, "Action passes deterministic recovery guardrails.", "ALLOWLIST_AND_STATE_CHECK")
