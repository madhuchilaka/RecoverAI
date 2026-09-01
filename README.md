# RecoverAI

RecoverAI is a fintech demo project focused on AI-assisted revenue recovery for merchants. This MVP is built for demonstration and testing workflows only, with all payment operations simulated in sandbox/test mode.

## Project structure

- `backend/` — FastAPI application and service layer
- `frontend/` — React + Vite dashboard frontend
- `docs/` — architecture and design notes

## Phase 1 status

This repository currently contains the foundational scaffold for the MVP. The backend exposes a health endpoint and the frontend boots as a professional landing/dashboard shell.

## Phase 3 - Revenue Recovery Intelligence

Phase 3 adds a deterministic intelligence layer behind the recovery API. It analyzes each transaction using transparent factors including amount, status, failure reason, retry count, transaction type, and customer history.

- **Risk scoring:** Produces a bounded `0.0` to `1.0` score, an explainable risk level, and decision factors.
- **Diagnosis:** Maps failure and abandonment states to concise operational diagnoses and accounts for repeated retries.
- **Recovery probability:** A configurable baseline recovery probability estimator. It is not a trained machine-learning model.
- **Decision engine:** Selects only allowlisted actions such as retry, payment link, reminder, alternative payment, escalation, or no action.
- **Human approval:** Required for transactions over the configured high-value threshold, critical risk, repeated failures, or escalation decisions.
- **Revenue at risk:** For this MVP, this means the amount associated with `FAILED` and `ABANDONED` transactions whose baseline recovery probability is at least `0.25`. `SUCCESS` and `PENDING` transactions are excluded.

The intelligence API only recommends actions. It does not execute payments or send customer communications.

## Phase 4 - Bounded Recovery Execution

Phase 4 turns recommendations into a guarded workflow using simulated/test-mode actions only. The policy engine validates the allowlist, terminal transaction state, retry limit, repeated failures, critical risk, and the configurable `HIGH_VALUE_THRESHOLD` (default `50000`). Actions requiring approval create a pending recovery attempt and do not execute until approved.

Every execution, block, approval, rejection, state transition, stopping rule, and successful AI recommendation is stored in the audit log. Recovery attempts are numbered sequentially per transaction across retries and alternative actions. Retry outcomes and communication outcomes are deterministic and reproducible; they do not call payment, email, or SMS providers.

The recovery state machine marks successful work `RECOVERED`, recoverable failures `AT_RISK`, and retry-limit, repeated-failure, or human-escalation stops `ESCALATED`. `NOT_RECOVERABLE` is used when no recovery action remains. Initial revenue at risk is the immutable eligibility baseline: qualifying `FAILED` and `ABANDONED` transaction value with plausible recovery probability before recovery state changes. Current revenue at risk excludes recovered, escalated, and not-recoverable transactions. Recovered revenue is the sum of transaction amounts with `recovery_status=RECOVERED`, counted once, and recovery rate is recovered revenue divided by initial revenue at risk.

Successful analysis writes concise `AI_AGENT` recommendation audit metadata, including risk, probability, action, confidence, and approval requirement. No hidden chain-of-thought is stored.

Phase 4 endpoints:

- `POST /api/recovery/execute/{transaction_id}`
- `POST /api/recovery/attempts/{attempt_id}/approve`
- `POST /api/recovery/attempts/{attempt_id}/reject`
- `GET /api/recovery/transactions/{transaction_id}/history`

Endpoints:

- `POST /api/recovery/analyze/{transaction_id}`
- `GET /api/recovery/at-risk`
- `GET /api/recovery/summary`

## Run backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

## Verify

- Backend: http://localhost:8000/health
- Frontend: http://localhost:5173

## Notes

- This project uses synthetic/demo data only.
- No real financial transactions are executed.
- The Phase 3 agent interface is deterministic and does not claim to use an LLM.
- All payment and recovery operations are simulated/test-mode operations and do not move real funds.

## Demo Walkthrough

1. Start FastAPI from `backend/` with `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.
2. Start the frontend from `frontend/` with `npm run dev -- --host 0.0.0.0`.
3. Open the Dashboard and show the live revenue-at-risk, recovered-revenue, recovery-rate, and at-risk transaction metrics.
4. Open transaction `TXN-000051` at `/transactions/51`.
5. Click **Analyze Transaction** and review the deterministic risk, probability, diagnosis, recommended action, confidence, and approval requirement.
6. Open Recovery Center, review the pending approval, and approve or reject it through the backend workflow.
7. Return to Dashboard, click **Refresh**, and inspect the updated metrics.
8. Open Audit Logs and expand the transaction events.

All payment and recovery operations shown in this MVP are simulated/test-mode operations.
