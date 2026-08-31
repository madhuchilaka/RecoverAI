import { Link, Route, Routes } from 'react-router-dom'

const stats = [
  { label: 'Revenue At Risk', value: '$184,230', tone: 'amber' },
  { label: 'Revenue Recovered', value: '$72,410', tone: 'emerald' },
  { label: 'Recovery Rate', value: '39.3%', tone: 'cyan' },
  { label: 'Transactions Analyzed', value: '1,240', tone: 'violet' },
]

const navItems = [
  { label: 'Dashboard', href: '/' },
  { label: 'Transactions', href: '/transactions' },
  { label: 'Recovery Center', href: '/recovery' },
  { label: 'Analytics', href: '/analytics' },
  { label: 'Audit Logs', href: '/audit' },
]

function StatCard({ label, value, tone }) {
  const toneMap = {
    amber: 'bg-amber-500/10 text-amber-300 ring-amber-500/30',
    emerald: 'bg-emerald-500/10 text-emerald-300 ring-emerald-500/30',
    cyan: 'bg-cyan-500/10 text-cyan-300 ring-cyan-500/30',
    violet: 'bg-violet-500/10 text-violet-300 ring-violet-500/30',
  }

  return (
    <div className={`rounded-2xl p-4 ring-1 ${toneMap[tone]}`}>
      <div className="text-sm text-slate-300">{label}</div>
      <div className="mt-3 text-3xl font-semibold text-white">{value}</div>
    </div>
  )
}

function DashboardPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-emerald-300">Revenue intelligence</p>
          <h1 className="mt-2 text-3xl font-semibold text-white">RecoverAI dashboard</h1>
        </div>
        <button className="rounded-xl bg-emerald-500 px-4 py-2 font-medium text-slate-950 shadow-lg shadow-emerald-500/20 transition hover:bg-emerald-400">
          Run demo flow
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <StatCard key={stat.label} {...stat} />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-panel">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Recovery performance</h2>
            <span className="rounded-full bg-slate-800 px-2 py-1 text-xs text-slate-300">SYNTHETIC DEMO</span>
          </div>
          <div className="h-64 rounded-xl bg-gradient-to-br from-slate-800 to-slate-900 p-4">
            <div className="flex h-full items-end gap-3">
              {[35, 48, 42, 74, 68, 91, 80, 110].map((height, index) => (
                <div key={index} className="flex-1 rounded-t-lg bg-gradient-to-t from-emerald-500 to-cyan-400" style={{ height: `${height}%` }} />
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-panel">
          <h2 className="text-xl font-semibold text-white">Operational signals</h2>
          <div className="mt-6 space-y-4 text-sm text-slate-300">
            <div className="flex items-center justify-between rounded-xl bg-slate-800/80 p-3">
              <span>Recovery attempts</span>
              <strong className="text-white">142</strong>
            </div>
            <div className="flex items-center justify-between rounded-xl bg-slate-800/80 p-3">
              <span>Successful recoveries</span>
              <strong className="text-emerald-300">67</strong>
            </div>
            <div className="flex items-center justify-between rounded-xl bg-slate-800/80 p-3">
              <span>Failed recoveries</span>
              <strong className="text-rose-300">23</strong>
            </div>
            <div className="flex items-center justify-between rounded-xl bg-slate-800/80 p-3">
              <span>Human escalations</span>
              <strong className="text-amber-300">11</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function TransactionsPage() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-panel">
      <h1 className="text-2xl font-semibold text-white">Transactions</h1>
      <div className="mt-6 overflow-hidden rounded-xl border border-slate-800">
        <table className="min-w-full divide-y divide-slate-800 text-left text-sm text-slate-300">
          <thead className="bg-slate-800/80 text-slate-200">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Customer</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Risk</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 bg-slate-900">
            {[1, 2, 3, 4].map((item) => (
              <tr key={item}>
                <td className="px-4 py-3">TXN-{item + 1000}</td>
                <td className="px-4 py-3">Cust-{100 + item}</td>
                <td className="px-4 py-3">PAYMENT</td>
                <td className="px-4 py-3">${(120 + item * 80).toLocaleString()}</td>
                <td className="px-4 py-3"><span className="rounded-full bg-amber-500/10 px-2 py-1 text-amber-300">FAILED</span></td>
                <td className="px-4 py-3"><span className="text-amber-300">MEDIUM</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function RecoveryCenterPage() {
  return (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-panel">
        <h1 className="text-2xl font-semibold text-white">Recovery center</h1>
        <div className="mt-6 space-y-4">
          <div className="rounded-xl bg-slate-800/80 p-4">
            <div className="text-sm text-slate-400">Selected transaction</div>
            <div className="mt-1 text-xl font-semibold text-white">TXN-1042</div>
          </div>
          <div className="rounded-xl bg-slate-800/80 p-4">
            <div className="text-sm text-slate-400">AI recommendation</div>
            <div className="mt-2 text-lg text-emerald-300">GENERATE_PAYMENT_LINK</div>
            <p className="mt-2 text-slate-300">Temporary decline pattern suggests a recoverable failure with a strong chance of conversion via a payment link.</p>
          </div>
          <div className="flex gap-3">
            <button className="rounded-xl bg-emerald-500 px-4 py-2 font-medium text-slate-950 hover:bg-emerald-400">Approve action</button>
            <button className="rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 font-medium text-slate-100 hover:bg-slate-700">Execute simulated recovery</button>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-panel">
        <h2 className="text-xl font-semibold text-white">Guardrail status</h2>
        <div className="mt-6 space-y-3 text-sm text-slate-300">
          <div className="rounded-xl bg-slate-800/80 p-3">Retry count: <strong className="text-white">1</strong></div>
          <div className="rounded-xl bg-slate-800/80 p-3">Recovery probability: <strong className="text-emerald-300">0.82</strong></div>
          <div className="rounded-xl bg-slate-800/80 p-3">Human approval: <strong className="text-amber-300">Not required</strong></div>
          <div className="rounded-xl bg-slate-800/80 p-3">Simulation mode: <strong className="text-cyan-300">Sandbox</strong></div>
        </div>
      </div>
    </div>
  )
}

function AnalyticsPage() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-panel">
      <h1 className="text-2xl font-semibold text-white">Analytics</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {[
          ['Revenue at risk', '$184,230'],
          ['Recovered revenue', '$72,410'],
          ['Recovery rate', '39.3%'],
          ['Attempts', '142'],
          ['Successful recoveries', '67'],
          ['Escalations', '11'],
        ].map(([label, value]) => (
          <div key={label} className="rounded-xl border border-slate-800 bg-slate-800/60 p-4">
            <div className="text-sm text-slate-400">{label}</div>
            <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function AuditLogsPage() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-panel">
      <h1 className="text-2xl font-semibold text-white">Audit logs</h1>
      <div className="mt-6 space-y-3">
        {[
          ['2026-08-31T10:13:42Z', 'TXN-1042', 'AI_AGENT', 'GENERATE_PAYMENT_LINK', 'Recoverable network failure', 'OK'],
          ['2026-08-31T09:44:03Z', 'TXN-981', 'POLICY_ENGINE', 'NO_ACTION', 'High-risk limit reached', 'BLOCKED'],
          ['2026-08-31T09:10:18Z', 'TXN-224', 'HUMAN', 'ESCALATE_TO_HUMAN', 'Repeated retry failure', 'ESCALATED'],
        ].map(([time, txn, actor, action, reason, result]) => (
          <div key={`${time}-${txn}`} className="rounded-xl border border-slate-800 bg-slate-800/60 p-4 text-sm text-slate-300">
            <div className="flex items-center justify-between gap-4">
              <span className="font-medium text-white">{txn}</span>
              <span className="rounded-full bg-slate-700 px-2 py-1 text-xs text-slate-200">{result}</span>
            </div>
            <div className="mt-3 grid gap-1 md:grid-cols-3">
              <div><span className="text-slate-400">Time:</span> {time}</div>
              <div><span className="text-slate-400">Actor:</span> {actor}</div>
              <div><span className="text-slate-400">Action:</span> {action}</div>
            </div>
            <div className="mt-2 text-slate-400">Reason: {reason}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function AppShell() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/15 text-lg font-bold text-emerald-300">R</div>
            <div>
              <div className="text-lg font-semibold text-white">RecoverAI</div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate-400">Demo operations</div>
            </div>
          </div>
          <nav className="hidden items-center gap-6 md:flex">
            {navItems.map((item) => (
              <Link key={item.label} to={item.href} className="text-sm text-slate-300 transition hover:text-white">
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300">
            Sandbox mode
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
          <Route path="/recovery" element={<RecoveryCenterPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/audit" element={<AuditLogsPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return <AppShell />
}
