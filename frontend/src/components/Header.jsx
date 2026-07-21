import { useEffect, useState } from 'react'
import { api } from '../api'
import { Database, FileText, Layers, RefreshCw } from 'lucide-react'

export default function Header({ screenTitle, sidebarWidth = 256 }) {
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
        { icon: FileText, label: 'DOCS',       value: '102' },
        { icon: Layers,   label: 'CHUNKS',     value: stats.total_chunks?.toLocaleString() ?? '—' },
        { icon: Database, label: 'CATEGORIES', value: Object.keys(stats.chunks_by_category ?? {}).length },
      ]
    : []

  return (
    <header
      className="fixed top-0 right-0 h-16 bg-white border-b-2 border-gray-200 flex items-center justify-between px-8 z-30 shadow-sm transition-all duration-300 ease-in-out"
      style={{ left: sidebarWidth }}
    >
      {/* Screen title */}
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-display font-bold text-black tracking-wide truncate">
          {screenTitle}
        </h1>
        <div className="h-4 w-px bg-gray-300" />
        <div className="flex items-center gap-1.5 text-[11px] font-mono text-black uppercase tracking-wider bg-gray-100 px-2.5 py-1 rounded border border-gray-300">
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-black opacity-50" />
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-black" />
          </span>
          Live
        </div>
      </div>

      {/* KPI strip */}
      <div className="flex items-center gap-4">
        {kpis.map(({ icon: Icon, label, value }) => (
          <div
            key={label}
            className="flex items-center gap-2 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200 shadow-sm"
          >
            <Icon size={14} className="text-black shrink-0" />
            <span className="font-mono font-bold text-black text-sm leading-none">{value}</span>
            <span className="text-[10px] font-mono text-gray-500 uppercase tracking-wider">{label}</span>
          </div>
        ))}
        <button
          onClick={load}
          className={`text-gray-400 hover:text-black transition-colors ml-1 ${isRefreshing ? 'animate-spin text-black' : ''}`}
          title="Refresh stats"
        >
          <RefreshCw size={16} />
        </button>
      </div>
    </header>
  )
}
