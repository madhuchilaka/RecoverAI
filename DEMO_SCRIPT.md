# RecoverAI Demo Script

The live UI segment is designed for approximately 60-90 seconds inside a five-minute submission video.

## 0:00-0:30 - Problem

Merchants lose potential revenue when payments fail or checkout is abandoned. The challenge is deciding which transactions deserve attention, why they failed, and what action is safe.

## 0:30-1:00 - Solution

RecoverAI combines deterministic intelligence, policy guardrails, human approval, simulated recovery, analytics, and an audit trail in one merchant workspace. All payment and recovery operations shown in this MVP are simulated/test-mode operations.

## 1:00-1:45 - Dashboard

Open `http://127.0.0.1:5179/`. Point to Initial Revenue at Risk, Current Revenue at Risk, Recovered Revenue, Recovery Rate, and At-Risk Transactions. Mention that the values come from the FastAPI summary endpoint and synthetic SQLite data.

## 1:45-2:30 - Transaction Intelligence

On a freshly seeded dataset, open `/transactions/51`, transaction `TXN-000051`. Click **Analyze Transaction**. Show `MEDIUM` risk, score approximately `0.28`, recovery probability approximately `0.83`, the network-failure diagnosis, `RETRY_PAYMENT`, confidence, and the approval requirement. Do not describe any hidden reasoning.

## 2:30-3:20 - Recovery and Guardrails

Click **Execute Recovery** and confirm the dialog, which explicitly says no real payment or communication occurs. The deterministic simulation should succeed for transaction `51`. Show the `RECOVERED` result, the simulated message, and the recovery timeline.

## 3:20-4:00 - Human Approval and Escalation

Open Recovery Center and explain that a high-value candidate such as transaction `1273` enters **AWAITING HUMAN APPROVAL** before execution. Approve or reject a pending attempt to show the backend workflow. Transaction `631` demonstrates retry-limit blocking; transaction `1611` demonstrates high-value escalation.

## 4:00-4:30 - Analytics

Open `/analytics`. Show revenue comparison, risk distribution, recovery outcomes, failure-reason distribution, and transaction-type distribution. Emphasize that the category charts are derived from the full paginated transaction API, not hard-coded values.

## 4:30-5:00 - Audit Trail and Business Value

Open `/audit`, search visually for transaction `51`, and expand its events. Show `AI_AGENT`, policy, `SYSTEM`, state, result, timestamp, and metadata. Close by explaining that RecoverAI turns revenue-risk signals into explainable, bounded actions while keeping every operation test-only and auditable.

## Exact Primary Demo Flow

1. Dashboard: `/`
2. Transactions: click **Transactions** in the sidebar
3. Details: click `TXN-000051` or open `/transactions/51`
4. Click **Analyze Transaction**
5. Review recommendation and guardrail
6. Click **Execute Recovery**, then **Confirm**
7. Return to Dashboard and click **Refresh**
8. Open **Audit Logs** and expand the transaction events

Primary demo transaction on a fresh seed: `TXN-000051` / ID `51`, amount `₹3,090.75`, failed `NETWORK_ERROR`, retry count `0`. Expected result: simulated retry succeeds and the transaction becomes `RECOVERED`.

Fallback: if the transaction has already been executed in the demo database, use transaction `1273` to demonstrate `AWAITING_HUMAN_APPROVAL` and rejection, or transaction `631` to demonstrate retry-limit blocking. Do not repeatedly execute the same transaction.
