import { useEffect, useState } from 'react'
import { api } from '../api'
import { Database, FileText, Layers, RefreshCw } from 'lucide-react'

export default function Header({ screenTitle }) {
  const [stats, setStats] = useState(null)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const load = async () => {
    setIsRefreshing(true)
    try {
      const r = await api.stats()
      setStats(r.data)
    } catch {}
    setTimeout(() => setIsRefreshing(false), 500)
  }
  useEffect(() => { load() }, [])

  const kpis = stats
    ? [
        { icon: FileText, label: 'DOCS', value: '102' },
        { icon: Layers,   label: 'CHUNKS',    value: stats.total_chunks?.toLocaleString() ?? '—' },
        { icon: Database, label: 'CATEGORIES', value: Object.keys(stats.chunks_by_category ?? {}).length },
      ]
    : []

  return (
    <header className="fixed top-0 left-64 right-0 h-16 bg-white/80 backdrop-blur-xl border-b border-surface-200 flex items-center justify-between px-8 z-30 shadow-sm">
      {/* Screen title */}
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-display font-semibold text-gray-900 tracking-wide truncate">{screenTitle}</h1>
        <div className="h-4 w-px bg-surface-300"></div>
        <div className="flex items-center gap-1.5 text-[10px] font-mono text-accent-cyan uppercase tracking-wider bg-accent-cyan/10 px-2 py-0.5 rounded border border-accent-cyan/20">
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-cyan opacity-75"></span>
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-accent-cyan"></span>
          </span>
          Live
        </div>
      </div>

      {/* KPI strip */}
      <div className="flex items-center gap-5">
        {kpis.map(({ icon: Icon, label, value }) => (
          <div key={label} className="flex items-center gap-2 bg-surface-50 px-3 py-1.5 rounded-lg border border-surface-200 shadow-sm">
            <Icon size={14} className="text-accent-cyan shrink-0 drop-shadow-[0_0_5px_rgba(2,132,199,0.3)]" />
            <span className="font-mono font-bold text-gray-900 text-sm leading-none">{value}</span>
            <span className="text-[10px] font-mono text-gray-500 uppercase tracking-wider">{label}</span>
          </div>
        ))}
        <button
          onClick={load}
          className={`text-gray-400 hover:text-accent-cyan hover:drop-shadow-[0_0_8px_rgba(2,132,199,0.3)] transition-all ml-2 ${isRefreshing ? 'animate-spin text-accent-cyan' : ''}`}
          title="Refresh stats"
        >
          <RefreshCw size={16} />
        </button>
      </div>
    </header>
  )
}
