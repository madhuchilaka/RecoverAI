import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { analyzeTransaction, executeRecovery, getCustomer, getRecoveryHistory, getTransaction } from '../services/api'
import { useApi } from '../hooks/useApi'
import StatusBadge from '../components/StatusBadge'
import RiskBadge from '../components/RiskBadge'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import AIRecommendation from '../components/AIRecommendation'
import GuardrailPanel from '../components/GuardrailPanel'
import RecoveryTimeline from '../components/RecoveryTimeline'

const money = (value, currency = 'INR') => new Intl.NumberFormat('en-IN', { style: 'currency', currency }).format(value || 0)
export default function TransactionDetails() {
  const { id } = useParams(); const navigate = useNavigate(); const [busy, setBusy] = useState(false); const [message, setMessage] = useState(''); const [recommendation, setRecommendation] = useState(null); const [execution, setExecution] = useState(null)
  const transaction = useApi(() => getTransaction(id), [id]); const customer = useApi(() => transaction.data ? getCustomer(transaction.data.customer_id) : Promise.resolve(null), [transaction.data?.customer_id]); const history = useApi(() => getRecoveryHistory(id), [id])
  const analyze = async () => { setBusy(true); setMessage(''); try { setRecommendation(await analyzeTransaction(id)); await history.run() } catch (error) { setMessage(error.response?.data?.detail || 'Analysis failed.') } finally { setBusy(false) } }
  const execute = async () => { if (!recommendation || !window.confirm('Execute simulated recovery action? No real payment or communication will occur.')) return; setBusy(true); setMessage(''); try { const result = await executeRecovery(id, recommendation.recommended_action); setExecution(result); await history.run() } catch (error) { setMessage(error.response?.data?.detail || 'Execution failed.') } finally { setBusy(false) } }
  if (transaction.loading) return <LoadingState label="Loading transaction..." />
  if (transaction.error || !transaction.data) return <ErrorState message={transaction.error || 'Transaction not found.'} onRetry={() => transaction.run().catch(() => {})} />
  const item = transaction.data
  return <div className="page-stack"><button className="back-link" onClick={() => navigate('/transactions')}>← Back to transactions</button><section className="detail-heading"><div><span className="eyebrow">Transaction detail</span><h2>{item.external_transaction_id}</h2><p className="page-subtitle">{customer.data?.name || `Customer #${item.customer_id}`} · Synthetic test-mode record</p></div><div className="badge-row"><StatusBadge value={item.status} /><RiskBadge value={recommendation?.risk_level || item.risk_level} /></div></section><div className="detail-grid"><section className="panel"><div className="panel-heading"><h3>Transaction overview</h3></div><dl className="detail-list"><div><dt>Amount</dt><dd>{money(item.amount, item.currency)}</dd></div><div><dt>Type</dt><dd>{item.transaction_type}</dd></div><div><dt>Failure reason</dt><dd>{item.failure_reason || 'None'}</dd></div><div><dt>Retry count</dt><dd>{item.retry_count}</dd></div><div><dt>Created</dt><dd>{new Date(item.created_at).toLocaleString()}</dd></div></dl></section><section className="panel"><div className="panel-heading"><h3>AI recovery recommendation</h3><span className="soft-label">Deterministic baseline</span></div><AIRecommendation recommendation={recommendation} /><div className="action-row"><button className="button button-primary" disabled={busy} onClick={analyze}>{busy ? 'Analyzing...' : 'Analyze Transaction'}</button>{recommendation && <button className="button button-secondary" disabled={busy || recommendation.requires_human_approval} onClick={execute}>{recommendation.requires_human_approval ? 'Awaiting Human Approval' : 'Execute Recovery'}</button>}</div>{message && <p className="inline-error">{message}</p>}{execution && <div className={`result-banner ${execution.status === 'RECOVERED' ? 'result-success' : 'result-warning'}`}><strong>{execution.status.replaceAll('_', ' ')}</strong><span>{execution.message}</span></div>}</section><GuardrailPanel recommendation={recommendation} execution={execution} /><section className="panel"><div className="panel-heading"><h3>Recovery history</h3></div>{history.loading ? <LoadingState /> : <RecoveryTimeline attempts={history.data?.recovery_attempts} events={history.data?.audit_events} />}</section></div></div>
}
