# RecoverAI Demo Script

## 60-90 Second Flow

1. **Problem:** Merchants lose revenue when valuable transactions fail, are abandoned, or need human review.
2. **Dashboard:** Open `http://127.0.0.1:5177/` and point to the live Initial Revenue at Risk, Current Revenue at Risk, Recovered Revenue, Recovery Rate, and At-Risk Transactions cards.
3. **Select opportunity:** Open Transactions, choose `TXN-000051` at `/transactions/51`, a failed network-error synthetic transaction with a retry available.
4. **AI analysis:** Click **Analyze Transaction**. Show the risk level, risk score, recovery probability, diagnosis, recommended action, confidence, and approval requirement.
5. **Guardrail:** Point out that the policy panel allows the bounded retry because the retry count is zero and the transaction is not high value.
6. **Simulated recovery:** Click **Execute Recovery**, confirm the action, and state clearly that this is a simulation and no funds move.
7. **Outcome:** Show the simulated successful recovery, updated transaction state, and recovery history.
8. **Business value:** Return to Dashboard, click **Refresh**, and show updated attempts and recovery metrics.
9. **Audit trail:** Open Audit Logs and expand the tested transaction events to show AI recommendation, policy, human review, and simulated execution records.
10. **Closing:** RecoverAI turns revenue-risk signals into explainable, policy-controlled next steps while keeping every operation in test mode.

Primary demo transaction: `TXN-000051` / transaction ID `51`.

All payment and recovery operations shown in this MVP are simulated/test-mode operations.
