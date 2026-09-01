import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'

const titles = { '/': 'Revenue Recovery Overview', '/transactions': 'Transactions', '/recovery': 'Recovery Center', '/analytics': 'Recovery Analytics', '/audit': 'Audit Trail' }

export default function Layout() {
  const [open, setOpen] = useState(false)
  const location = useLocation()
  const title = location.pathname.startsWith('/transactions/') ? 'Transaction Details' : titles[location.pathname] || 'Page not found'
  return <div className="app-shell"><Sidebar open={open} onClose={() => setOpen(false)} />{open && <button className="sidebar-scrim" aria-label="Close navigation" onClick={() => setOpen(false)} /> }<div className="main-shell"><Topbar title={title} onMenu={() => setOpen(true)} /><main className="page-content"><Outlet /></main></div></div>
}
