import { NavLink } from 'react-router-dom'

const items = [
  ['/', 'Dashboard', '⌂'],
  ['/transactions', 'Transactions', '↔'],
  ['/recovery', 'Recovery Center', '◎'],
  ['/analytics', 'Analytics', '▥'],
  ['/audit', 'Audit Logs', '≡'],
]

export default function Sidebar({ open, onClose }) {
  return <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}><div className="brand"><div className="brand-mark">R</div><div><strong>RecoverAI</strong><span>AI revenue recovery</span></div></div><nav>{items.map(([to, label, icon]) => <NavLink key={to} to={to} end={to === '/'} onClick={onClose} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}><span>{icon}</span>{label}</NavLink>)}</nav><div className="sidebar-foot"><strong>Demo / Test Mode</strong><span>All actions are simulated</span></div></aside>
}
