export default function ErrorState({ message, onRetry }) {
  return <div className="state-card state-error"><strong>{message || 'Unable to load data.'}</strong>{onRetry && <button className="button button-secondary" onClick={onRetry}>Try again</button>}</div>
}
