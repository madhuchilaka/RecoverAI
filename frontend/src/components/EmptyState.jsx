export default function EmptyState({ title = 'Nothing to show yet', text = 'Data will appear here when it becomes available.' }) {
  return <div className="state-card"><strong>{title}</strong><span>{text}</span></div>
}
