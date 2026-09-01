import { getAllTransactions, getRecoverySummary } from '../services/api'
import { useApi } from '../hooks/useApi'
import { CategoryDistributionChart, DistributionChart, OutcomeChart, RevenueChart } from '../components/MetricChart'
import StatCard from '../components/StatCard'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import EmptyState from '../components/EmptyState'

function countBy(items, getLabel) {
	const counts = new Map()
	items.forEach((item) => {
		const label = getLabel(item) || 'UNKNOWN'
		counts.set(label, (counts.get(label) || 0) + 1)
	})
	return [...counts.entries()].map(([name, value]) => ({ name: String(name).replaceAll('_', ' '), value })).sort((a, b) => b.value - a.value)
}

export default function Analytics() {
	const query = useApi(getRecoverySummary)
	const transactions = useApi(getAllTransactions)
	const data = query.data || {}
	const cards = [['Initial revenue at risk', data.initial_revenue_at_risk, 'blue'], ['Current revenue at risk', data.current_revenue_at_risk ?? data.revenue_at_risk, 'orange'], ['Recovered revenue', data.recovered_revenue, 'green'], ['Recovery rate', `${((data.recovery_rate || 0) * 100).toFixed(1)}%`, 'teal'], ['Attempts', data.recovery_attempts, 'blue'], ['Successes', data.successful_recoveries, 'green'], ['Failures', data.failed_recoveries, 'orange'], ['Escalations', data.escalations, 'purple'], ['Blocked actions', data.blocked_actions, 'blue']]
	const rows = transactions.data || []
	const atRiskRows = rows.filter((item) => item.status === 'FAILED' || item.status === 'ABANDONED')
	const failureReasons = countBy(atRiskRows, (item) => item.failure_reason)
	const transactionTypes = countBy(rows, (item) => item.transaction_type)
	const retry = () => { query.run().catch(() => {}); transactions.run().catch(() => {}) }
	const error = query.error || transactions.error
	return <div className="page-stack"><section className="hero-row"><div><span className="eyebrow">Performance intelligence</span><h2>Recovery Analytics</h2><p className="page-subtitle">Synthetic/test-mode metrics from the recovery engine.</p></div></section>{query.loading || transactions.loading ? <LoadingState /> : error ? <ErrorState message={error} onRetry={retry} /> : <><div className="analytics-kpis">{cards.map(([label, value, tone]) => <StatCard key={label} label={label} value={typeof value === 'number' && label.includes('revenue') ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(value) : value || 0} tone={tone} />)}</div><div className="chart-grid"><section className="panel chart-panel"><div className="panel-heading"><h3>Revenue at risk vs recovered</h3></div><RevenueChart summary={data} /></section><section className="panel chart-panel"><div className="panel-heading"><h3>Risk distribution</h3></div><DistributionChart distribution={data.risk_distribution} /></section><section className="panel chart-panel"><div className="panel-heading"><h3>Recovery outcomes</h3></div><OutcomeChart summary={data} /></section><section className="panel chart-panel"><div className="panel-heading"><h3>Failure Reason Distribution</h3></div>{failureReasons.length ? <CategoryDistributionChart data={failureReasons} color="#d95f63" /> : <EmptyState title="No failure reason data available." />}</section><section className="panel chart-panel"><div className="panel-heading"><h3>Transaction Type Distribution</h3></div>{transactionTypes.length ? <CategoryDistributionChart data={transactionTypes} color="#5b7cdb" /> : <EmptyState title="No transaction type data available." />}</section></div></>}</div>
}
