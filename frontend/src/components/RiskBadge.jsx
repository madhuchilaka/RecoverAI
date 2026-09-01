export default function RiskBadge({ value }) {
  return <span className={`badge badge-${String(value || 'LOW').toLowerCase()}`}>{value || 'LOW'}</span>
}
