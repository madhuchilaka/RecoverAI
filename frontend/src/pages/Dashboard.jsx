import { useNavigate } from 'react-router-dom'
import { getAtRiskTransactions, getCustomers, getRecoverySummary } from '../services/api'
import { useApi } from '../hooks/useApi'
import StatCard from '../components/StatCard'
import TransactionTable from '../components/TransactionTable'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import EmptyState from '../components/EmptyState'
import { DistributionChart, OutcomeChart, RevenueChart } from '../components/MetricChart'

const money = (value) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(value || 0)

export default function Dashboard() {
  const navigate = useNavigate()
  const summary = useApi(getRecoverySummary)
  const atRisk = useApi(() => getAtRiskTransactions({ limit: 8, offset: 0 }))
  const customers = useApi(() => getCustomers({ limit: 500, offset: 0 }))
  const refresh = () => { summary.run().catch(() => {}); atRisk.run().catch(() => {}); customers.run().catch(() => {}) }
  const data = summary.data || {}
  const customerMap = Object.fromEntries((customers.data || []).map((item) => [item.id, item]))
  const cards = [['Initial revenue at risk', money(data.initial_revenue_at_risk), 'blue'], ['Current revenue at risk', money(data.current_revenue_at_risk ?? data.revenue_at_risk), 'orange'], ['Recovered revenue', money(data.recovered_revenue), 'green'], ['Recovery rate', `${((data.recovery_rate || 0) * 100).toFixed(1)}%`, 'teal'], ['At-risk transactions', data.at_risk_transactions ?? data.at_risk_transaction_count ?? 0, 'purple'], ['Recovery attempts', data.recovery_attempts || 0, 'blue'], ['Successful recoveries', data.successful_recoveries || 0, 'green'], ['Human escalations', data.escalations || 0, 'orange']]
  return <div className="page-stack"><section className="hero-row"><div><span className="eyebrow">AI-powered recovery intelligence for merchant revenue</span><h2>Revenue Recovery Overview</h2><p className="page-subtitle">A focused view of synthetic revenue opportunities, policy outcomes, and recovery momentum.</p></div><button className="button button-secondary" onClick={refresh}>↻ Refresh</button></section><div className="kpi-grid">{cards.map(([label, value, tone]) => <StatCard key={label} label={label} value={value} tone={tone} />)}</div>{summary.loading ? <LoadingState /> : summary.error ? <ErrorState message={summary.error} onRetry={() => summary.run().catch(() => {})} /> : <div className="chart-grid"><section className="panel chart-panel"><div className="panel-heading"><div><span className="eyebrow">Portfolio view</span><h3>Recovery performance</h3></div><span className="soft-label">INR · Synthetic</span></div><RevenueChart summary={data} /></section><section className="panel chart-panel"><div className="panel-heading"><div><span className="eyebrow">Risk mix</span><h3>Risk distribution</h3></div></div><DistributionChart distribution={data.risk_distribution} /></section><section className="panel chart-panel"><div className="panel-heading"><div><span className="eyebrow">Operational outcomes</span><h3>Recovery outcomes</h3></div></div><OutcomeChart summary={data} /></section></div>}<section className="panel"><div className="panel-heading"><div><span className="eyebrow">Priority queue</span><h3>Recent recovery opportunities</h3></div><button className="text-button" onClick={() => navigate('/recovery')}>Open Recovery Center →</button></div>{atRisk.loading ? <LoadingState /> : atRisk.error ? <ErrorState message={atRisk.error} onRetry={() => atRisk.run().catch(() => {})} /> : !atRisk.data?.length ? <EmptyState /> : <TransactionTable transactions={atRisk.data} customers={customerMap} compact />}</section></div>
}
