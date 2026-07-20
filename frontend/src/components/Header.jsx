import { useEffect, useState } from 'react'
import { api } from '../api'
import { Database, FileText, Layers, RefreshCw } from 'lucide-react'

export default function Header({ screenTitle }) {
  const [stats, setStats] = useState(null)

  const load = () => api.stats().then(r => setStats(r.data)).catch(() => {})
  useEffect(() => { load() }, [])

  const kpis = stats
    ? [
        { icon: FileText, label: 'Documents', value: '102' },
        { icon: Layers,   label: 'Chunks',    value: stats.total_chunks?.toLocaleString() ?? '—' },
        { icon: Database, label: 'Categories', value: Object.keys(stats.chunks_by_category ?? {}).length },
      ]
    : []

  return (
    <header className="fixed top-0 left-56 right-0 h-14 bg-surface-800 border-b border-surface-600 flex items-center justify-between px-6 z-10">
      {/* Screen title */}
      <h1 className="text-sm font-semibold text-gray-200 truncate">{screenTitle}</h1>

      {/* KPI strip */}
      <div className="flex items-center gap-6">
        {kpis.map(({ icon: Icon, label, value }) => (
          <div key={label} className="flex items-center gap-1.5 text-xs text-gray-400">
            <Icon size={13} className="text-accent-blue shrink-0" />
            <span className="font-mono font-medium text-gray-200">{value}</span>
            <span className="text-gray-600">{label}</span>
          </div>
        ))}
        <button
          onClick={load}
          className="text-gray-600 hover:text-gray-300 transition-colors"
          title="Refresh stats"
        >
          <RefreshCw size={13} />
        </button>
      </div>
    </header>
  )
}
