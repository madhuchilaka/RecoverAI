from __future__ import annotations

from dataclasses import dataclass

from app.models.recovery import RecoveryAction
from app.models.transaction import FailureReason, RecoveryStatus, Transaction, TransactionStatus


@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    action: RecoveryAction
    transaction_id: int
    amount: float
    message: str
    next_state: RecoveryStatus
    stopped: bool
    stop_reason: str | None = None


class RecoveryExecutor:
    """Executes simulated, deterministic recovery outcomes. It never moves real funds."""

    def execute(self, transaction: Transaction, action: RecoveryAction) -> ExecutionResult:
        if action == RecoveryAction.NO_ACTION:
            return self._result(False, transaction, action, "No recovery action was requested.", RecoveryStatus.NOT_RECOVERABLE, True, "No action selected.")
        if action == RecoveryAction.ESCALATE_TO_HUMAN:
            return self._result(False, transaction, action, "Simulated escalation created for human review.", RecoveryStatus.ESCALATED, True, "Human escalation triggered.")
        success = self._deterministic_outcome(transaction, action)
        if success:
            message = f"Simulated/test-mode {action.value.lower()} succeeded. No real payment or communication was performed."
            return self._result(True, transaction, action, message, RecoveryStatus.RECOVERED, True, "Transaction recovered in simulation.")
        state = RecoveryStatus.AT_RISK
        stop_reason = "The simulated action failed; the transaction remains at risk."
        message = f"Simulated/test-mode {action.value.lower()} failed. No real payment or communication was performed."
        return self._result(False, transaction, action, message, state, state == RecoveryStatus.ESCALATED, stop_reason)

    @staticmethod
    def _deterministic_outcome(transaction: Transaction, action: RecoveryAction) -> bool:
        reason = transaction.failure_reason
        if action == RecoveryAction.RETRY_PAYMENT:
            return reason == FailureReason.NETWORK_ERROR and transaction.retry_count == 0 and transaction.id % 4 != 0
        if action == RecoveryAction.GENERATE_PAYMENT_LINK:
            return transaction.id % 3 != 0
        if action == RecoveryAction.SEND_CUSTOMER_REMINDER:
            return transaction.status == TransactionStatus.ABANDONED and transaction.id % 2 == 0
        if action == RecoveryAction.OFFER_ALTERNATIVE_PAYMENT:
            return reason == FailureReason.EXPIRED_CARD and transaction.id % 2 == 1
        return False

    @staticmethod
    def _result(success: bool, transaction: Transaction, action: RecoveryAction, message: str, state: RecoveryStatus, stopped: bool, stop_reason: str) -> ExecutionResult:
        return ExecutionResult(success, action, transaction.id, transaction.amount, message, state, stopped, stop_reason)
