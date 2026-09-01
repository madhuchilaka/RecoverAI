import { useEffect, useState } from 'react'
import { getCustomers, getTransactions } from '../services/api'
import { useApi } from '../hooks/useApi'
import TransactionTable from '../components/TransactionTable'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import EmptyState from '../components/EmptyState'

export default function Transactions() {
  const [page, setPage] = useState(0)
  const [query, setQuery] = useState('')
  const [filters, setFilters] = useState({ status: '', risk: '', type: '', reason: '' })
  const transactions = useApi(() => getTransactions({ limit: 25, offset: page * 25 }))
  const customers = useApi(() => getCustomers({ limit: 500, offset: 0 }))
  useEffect(() => { transactions.run().catch(() => {}) }, [page])
  const rows = (transactions.data || []).filter((item) => `${item.external_transaction_id} ${item.customer_id}`.toLowerCase().includes(query.toLowerCase())).filter((item) => !filters.status || item.status === filters.status).filter((item) => !filters.risk || item.risk_level === filters.risk).filter((item) => !filters.type || item.transaction_type === filters.type).filter((item) => !filters.reason || item.failure_reason === filters.reason)
  const setFilter = (key, value) => { setFilters((current) => ({ ...current, [key]: value })); setPage(0) }
  return <div className="page-stack"><section className="hero-row"><div><span className="eyebrow">Operations</span><h2>Transactions</h2><p className="page-subtitle">Inspect payment outcomes and open any transaction for bounded recovery actions.</p></div></section><section className="panel"><div className="filter-bar"><input aria-label="Search transactions" placeholder="Search transaction or customer ID" value={query} onChange={(event) => setQuery(event.target.value)} />{[['status', 'Status', ['SUCCESS', 'FAILED', 'ABANDONED', 'PENDING']], ['risk', 'Risk', ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']], ['type', 'Type', ['PAYMENT', 'SUBSCRIPTION', 'CHECKOUT']], ['reason', 'Failure reason', ['NETWORK_ERROR', 'BANK_DECLINED', 'EXPIRED_CARD', 'INSUFFICIENT_FUNDS', 'AUTHENTICATION_FAILED']]].map(([key, label, options]) => <select key={key} aria-label={label} value={filters[key]} onChange={(event) => setFilter(key, event.target.value)}><option value="">All {label}</option>{options.map((option) => <option key={option} value={option}>{option.replaceAll('_', ' ')}</option>)}</select>)}</div>{transactions.loading ? <LoadingState /> : transactions.error ? <ErrorState message={transactions.error} onRetry={() => transactions.run().catch(() => {})} /> : !rows.length ? <EmptyState title="No matching transactions" text="Try changing the search or filters." /> : <TransactionTable transactions={rows} customers={Object.fromEntries((customers.data || []).map((item) => [item.id, item]))} />}<div className="pagination"><button className="button button-secondary" disabled={page === 0} onClick={() => setPage(page - 1)}>← Previous</button><span>Page {page + 1}</span><button className="button button-secondary" disabled={!transactions.data || transactions.data.length < 25} onClick={() => setPage(page + 1)}>Next →</button></div></section></div>
}
