import { Link } from 'react-router-dom'
export default function NotFound(){return <div className="not-found"><span className="eyebrow">404</span><h2>That page is outside the workspace.</h2><p>Return to the recovery overview to continue.</p><Link className="button button-primary" to="/">Back to dashboard</Link></div>}
