import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import TransactionDetails from './pages/TransactionDetails'
import RecoveryCenter from './pages/RecoveryCenter'
import Analytics from './pages/Analytics'
import AuditLogs from './pages/AuditLogs'
import NotFound from './pages/NotFound'

export default function App() {
  return <Routes><Route element={<Layout />}><Route path="/" element={<Dashboard />} /><Route path="/transactions" element={<Transactions />} /><Route path="/transactions/:id" element={<TransactionDetails />} /><Route path="/recovery" element={<RecoveryCenter />} /><Route path="/analytics" element={<Analytics />} /><Route path="/audit" element={<AuditLogs />} /><Route path="/404" element={<NotFound />} /><Route path="*" element={<Navigate to="/404" replace />} /></Route></Routes>
}
