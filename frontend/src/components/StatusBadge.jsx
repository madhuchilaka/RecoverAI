export default function StatusBadge({ value }) {
  return <span className={`badge badge-status-${String(value || '').toLowerCase().replaceAll('_', '-')}`}>{String(value || 'UNKNOWN').replaceAll('_', ' ')}</span>
}
