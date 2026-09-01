import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export function RevenueChart({ summary }) {
  const data = [{ name: 'Revenue', Initial: summary.initial_revenue_at_risk || 0, Current: summary.current_revenue_at_risk ?? summary.revenue_at_risk ?? 0, Recovered: summary.recovered_revenue || 0 }]
  return <ResponsiveContainer width="100%" height={260}><BarChart data={data} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} /><XAxis dataKey="name" hide /><YAxis tickFormatter={(value) => `₹${Math.round(value / 1000)}k`} stroke="#64748b" fontSize={12} /><Tooltip formatter={(value) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(value)} /><Legend /><Bar dataKey="Initial" fill="#9aa9c2" radius={[5, 5, 0, 0]} /><Bar dataKey="Current" fill="#3564d4" radius={[5, 5, 0, 0]} /><Bar dataKey="Recovered" fill="#16a394" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer>
}

export function DistributionChart({ distribution }) {
  const colors = ['#94a3b8', '#5b7cdb', '#ed9b4f', '#d95f63']
  const data = Object.entries(distribution || {}).map(([name, value]) => ({ name, value }))
  return <ResponsiveContainer width="100%" height={260}><PieChart><Pie data={data} dataKey="value" nameKey="name" innerRadius={66} outerRadius={94} paddingAngle={3}>{data.map((entry, index) => <Cell key={entry.name} fill={colors[index % colors.length]} />)}</Pie><Tooltip /><Legend /></PieChart></ResponsiveContainer>
}

export function OutcomeChart({ summary }) {
  const data = [{ name: 'Outcomes', Successful: summary.successful_recoveries || 0, Failed: summary.failed_recoveries || 0, Escalated: summary.escalations || 0, Blocked: summary.blocked_actions || 0 }]
  return <ResponsiveContainer width="100%" height={260}><BarChart data={data} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} /><XAxis dataKey="name" hide /><YAxis allowDecimals={false} stroke="#64748b" fontSize={12} /><Tooltip /><Legend /><Bar dataKey="Successful" fill="#16a394" radius={[5, 5, 0, 0]} /><Bar dataKey="Failed" fill="#d95f63" radius={[5, 5, 0, 0]} /><Bar dataKey="Escalated" fill="#ed9b4f" radius={[5, 5, 0, 0]} /><Bar dataKey="Blocked" fill="#64748b" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer>
}

export function CategoryDistributionChart({ data, color = '#3564d4' }) {
  return <ResponsiveContainer width="100%" height={260}><BarChart data={data} layout="vertical" margin={{ top: 8, right: 18, left: 22, bottom: 8 }}><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} /><XAxis type="number" allowDecimals={false} stroke="#64748b" fontSize={12} /><YAxis type="category" dataKey="name" width={130} stroke="#64748b" fontSize={11} /><Tooltip /><Bar dataKey="value" name="Transactions" fill={color} radius={[0, 5, 5, 0]} /></BarChart></ResponsiveContainer>
}
