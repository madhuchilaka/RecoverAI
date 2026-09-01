export default function StatCard({ label, value, detail, tone = 'blue' }) {
  return <article className="stat-card"><div className={`stat-icon stat-${tone}`} /><div><p>{label}</p><strong>{value}</strong>{detail && <small>{detail}</small>}</div></article>
}
