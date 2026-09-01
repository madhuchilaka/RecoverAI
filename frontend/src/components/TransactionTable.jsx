import { Link } from 'react-router-dom'
import RiskBadge from './RiskBadge'
import StatusBadge from './StatusBadge'

const money = (value, currency = 'INR') => new Intl.NumberFormat('en-IN', { style: 'currency', currency, maximumFractionDigits: 2 }).format(value || 0)

export default function TransactionTable({ transactions, customers = {}, compact = false }) {
  return <div className="table-wrap"><table><thead><tr><th>Transaction</th><th>Customer</th><th>Amount</th><th>Type</th><th>Status</th><th>Failure reason</th><th>Risk</th><th>Recovery</th><th>{compact ? 'Open' : 'Created'}</th></tr></thead><tbody>{transactions.map((item) => { const transactionId = item.id ?? item.transaction_id; return <tr key={transactionId}><td><Link className="table-link" to={`/transactions/${transactionId}`}>{item.external_transaction_id}</Link></td><td>{customers[item.customer_id]?.name || `Customer #${item.customer_id}`}</td><td className="numeric">{money(item.amount, item.currency)}</td><td>{item.transaction_type}</td><td><StatusBadge value={item.status} /></td><td>{item.failure_reason || '—'}</td><td><RiskBadge value={item.risk_level} /></td><td>{item.recovery_probability == null ? '—' : `${Math.round(item.recovery_probability * 100)}%`}</td><td>{compact ? <Link className="text-button" to={`/transactions/${transactionId}`}>View</Link> : new Date(item.created_at).toLocaleDateString()}</td></tr> })}</tbody></table></div>
}
