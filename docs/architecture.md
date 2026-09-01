# RecoverAI Architecture

## Overview

RecoverAI is a demo fintech MVP for AI-assisted revenue recovery. The platform models revenue-at-risk transactions, diagnoses their likely cause, and recommends a bounded recovery workflow that is validated through a deterministic guardrail engine.

## Design principles

- Synthetic-data only for demo and testing
- Deterministic policy rules independent of the LLM
- No real payment execution
- Structured, auditable decision records
- Human escalation for high-risk or repeated failures

## Phase 1 foundation

This phase establishes the project structure and a minimal runnable backend/frontend scaffold. The backend exposes a health endpoint and the frontend loads a polished dashboard shell.

## Phase 3 intelligence layer

The Phase 3 request path is:

```text
Transaction + Customer history
	|
	v
Baseline Risk Analyzer
	|
	v
Diagnosis Engine
	|
	v
Baseline Recovery Probability Estimator
	|
	v
Allowlisted Decision Engine
	|
	v
Structured Recovery Recommendation
```

`RecoveryAgent` coordinates these components and exposes `analyze_transaction(transaction_id)` as the stable application interface. The API returns the recommendation without executing its action. Human approval is deterministic: it is required for high-value transactions, critical risk, repeated failures, and escalation decisions.

Revenue at risk is defined for this MVP as `FAILED` and `ABANDONED` transaction value with a baseline recovery probability of at least `0.25`. Successful transactions are excluded, and pending transactions remain unresolved rather than being counted as at risk.

The Phase 3 intelligence engine is a deterministic baseline suitable for demonstration and testing. It is not presented as a trained machine-learning model.

## Phase 4 bounded execution

The Phase 4 workflow extends the recommendation path:

```text
AI Decision
	|
	v
Policy Engine
	|
	v
Human Approval (when required)
	|
	v
Recovery Executor
	|
	v
Transaction Update
	|
	v
Audit Log
	|
	v
Analytics
```

The policy engine enforces the allowlist, maximum automatic retry attempts, terminal-state protection, repeated-failure escalation, and high-value/critical-risk approval. Reaching the retry limit or repeated failure changes the transaction to `ESCALATED`, records a blocked attempt, writes an audit event, and stops automation. The executor uses deterministic test-mode outcomes and never calls payment or messaging providers. Pending approval records are persisted as recovery attempts and rechecked before execution. Attempt numbers are sequential per transaction across all recovery actions.

Each successful recommendation also creates an `AI_AGENT / RECOVERY_RECOMMENDATION` audit event with concise structured decision metadata. Initial revenue at risk is calculated from the transaction's qualifying failed or abandoned state before recovery-state transitions; current revenue at risk excludes `RECOVERED`, `ESCALATED`, and `NOT_RECOVERABLE` transactions. Recovered revenue counts each `RECOVERED` transaction once, and recovery rate is `recovered_revenue / initial_revenue_at_risk`.

All recovery operations in this MVP are simulated/test-mode operations and do not move real funds.

## Planned future phases

1. Database models and schemas
2. Transaction ingestion and synthetic dataset generation
3. Deterministic risk and diagnosis engine
4. AI recovery agent
5. Guardrail policy engine
6. Recovery execution simulator
7. Analytics and audit APIs
8. React dashboard and flow interactions
9. Integration testing and polish

## Runtime separation

The backend and frontend are intentionally designed to run independently during development. The backend runs on port 8000, while the Vite frontend runs on port 5173.
