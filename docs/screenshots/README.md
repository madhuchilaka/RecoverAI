# RecoverAI Screenshots

This directory contains screenshots captured from the RecoverAI application running in Simulation / Test Mode.

The screenshots demonstrate the main application workflow, including the dashboard, transaction investigation, AI recovery analysis, recovery operations, analytics, and auditability.

## Screenshots

### 1. Dashboard

**File:** `dashboard.png`

**Route:** `/`

**Purpose:**
- RecoverAI branding
- Simulation / Test Mode indicator
- Revenue-at-risk metrics
- Recovery KPIs
- Recovery performance charts
- Risk distribution
- Recovery outcomes
- Priority recovery opportunities

---

### 2. Transactions

**File:** `transactions.png`

**Route:** `/transactions`

**Purpose:**
- Transaction listing
- Customer information
- Transaction amounts
- Transaction types
- Payment status
- Failure reasons
- Risk levels
- Recovery probability
- Transaction creation dates
- Search and filtering

---

### 3. Transaction Detail

**File:** `transaction-detail.png`

**Transaction:** `TXN-000631`

**Purpose:**
- Transaction overview
- Failed transaction details
- Customer information
- Failure reason
- Retry count
- Guardrail decision
- Recovery history
- AI recovery analysis entry point

This screenshot shows the transaction before generating a new AI recovery recommendation.

---

### 4. Transaction AI Analysis

**File:** `transaction-ai-analysis.png`

**Transaction:** `TXN-001306`

**Purpose:**
- AI recovery recommendation
- Recommended recovery action
- Risk score
- Recovery probability
- Confidence score
- Approval requirement
- Decision factors
- Execute Recovery action

This screenshot demonstrates the transaction after AI analysis has generated a recovery recommendation.

---

### 5. Recovery Center

**File:** `recovery-center.png`

**Route:** `/recovery`

**Purpose:**
- Revenue at risk
- Recovery attempts
- Successful recoveries
- Pending human approvals
- At-risk transaction queue
- Recovery actions available for review

The captured screen shows the Recovery Center in Simulation / Test Mode with the current human-review queue.

---

### 6. Analytics

**File:** `analytics.png`

**Route:** `/analytics`

**Purpose:**
- Initial revenue at risk
- Current revenue at risk
- Recovered revenue
- Recovery rate
- Recovery attempts
- Successful recoveries
- Failures
- Escalations
- Blocked actions
- Revenue and recovery performance
- Risk distribution
- Recovery outcomes
- Failure reason distribution
- Transaction type distribution

---

### 7. Audit Trail

**File:** `audit-logs.png`

**Route:** `/audit`

**Purpose:**
- Timestamped recovery events
- AI agent actions
- Policy engine decisions
- Human reviewer actions
- Recovery recommendations
- Policy approvals and blocks
- Recovery states
- Action results

The audit trail demonstrates explainability, traceability, and accountability within the synthetic recovery environment.

---

## Screenshot Workflow

The screenshots represent the following application flow:

```text
Dashboard
↓
Transactions
↓
Transaction Detail
↓
AI Recovery Analysis
↓
Recovery Center
↓
Analytics
↓
Audit Trail

## Notes

- All screenshots were captured from the running RecoverAI application.
- The application is operating in **Simulation / Test Mode**.
- The displayed transaction data and recovery metrics are synthetic test data.
- Screenshots should be regenerated whenever the UI or application behavior changes significantly.