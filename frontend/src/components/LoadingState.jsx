export default function LoadingState({ label = 'Loading recovery data...' }) {
  return <div className="state-card"><span className="spinner" />{label}</div>
}
