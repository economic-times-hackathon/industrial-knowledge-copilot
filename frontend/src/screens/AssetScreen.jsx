import { useState } from 'react'
import { Search, Tag, ChevronRight, Cpu } from 'lucide-react'
import { api } from '../api'
import AnswerPanel from '../components/AnswerPanel'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

const InteractivePIDMap = ({ onSelectTag, activeTag }) => {
  const Node = ({ id, x, y, labelOffset = 25, onClick, children }) => {
    const isActive = activeTag === id
    return (
      <g
        transform={`translate(${x}, ${y})`}
        className={`cursor-pointer transition-colors duration-200 ${isActive ? 'text-accent-blue' : 'text-gray-400 hover:text-gray-200'}`}
        onClick={() => onClick(id)}
      >
        {children}
        <text y={labelOffset} textAnchor="middle" fill="currentColor" className="text-[10px] font-mono font-bold tracking-wider pointer-events-none drop-shadow-md">
          {id}
        </text>
      </g>
    )
  }

  return (
    <div className="w-full bg-surface-800 border border-surface-600 rounded-xl overflow-hidden relative">
      <div className="absolute top-3 left-4 text-xs font-medium text-gray-500 uppercase tracking-widest">
        Interactive P&ID Map
      </div>
      <svg viewBox="0 0 800 360" className="w-full h-auto max-h-[400px]">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#4B5563" />
          </marker>
        </defs>

        {/* Piping Lines */}
        <path d="M 80 180 L 160 180" stroke="#4B5563" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />
        <path d="M 220 180 L 320 180" stroke="#4B5563" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />
        <path d="M 380 180 L 460 180" stroke="#4B5563" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />
        <path d="M 520 180 L 620 180" stroke="#4B5563" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />
        
        {/* Branch down from V-101 */}
        <path d="M 650 250 L 650 300 L 520 300" stroke="#4B5563" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />
        
        {/* Branch up from V-101 */}
        <path d="M 650 110 L 650 60 L 740 60 L 740 100" stroke="#4B5563" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />

        {/* Nodes */}
        <Node id="TK-001" x="50" y="180" labelOffset="45" onClick={onSelectTag}>
          <path d="M -30 -30 Q 0 -45 30 -30 L 30 30 L -30 30 Z" stroke="currentColor" strokeWidth="2" fill="transparent" />
        </Node>

        <Node id="P-101A" x="190" y="180" labelOffset="35" onClick={onSelectTag}>
          <circle cx="0" cy="0" r="20" stroke="currentColor" strokeWidth="2" fill="transparent" />
          <path d="M -15 0 L 15 -15 L 15 15 Z" fill="currentColor" opacity="0.3" />
        </Node>

        <Node id="E-101" x="350" y="180" labelOffset="40" onClick={onSelectTag}>
          <circle cx="0" cy="0" r="24" stroke="currentColor" strokeWidth="2" fill="transparent" />
          <path d="M -24 -10 L 24 -10 M -24 10 L 24 10 M -20 0 L 20 0" stroke="currentColor" strokeWidth="2" fill="transparent" />
        </Node>

        <Node id="F-101" x="490" y="180" labelOffset="45" onClick={onSelectTag}>
          <rect x="-25" y="-30" width="50" height="60" rx="4" stroke="currentColor" strokeWidth="2" fill="transparent" />
          <path d="M -15 -10 L 0 -25 L 15 -10" stroke="currentColor" strokeWidth="2" fill="transparent" strokeLinejoin="round" />
        </Node>

        <Node id="V-101" x="650" y="180" labelOffset="85" onClick={onSelectTag}>
          <rect x="-25" y="-70" width="50" height="140" rx="25" stroke="currentColor" strokeWidth="2" fill="transparent" />
          <path d="M -25 -30 L 25 -30 M -25 0 L 25 0 M -25 30 L 25 30" stroke="currentColor" strokeWidth="1" strokeDasharray="4 2" />
        </Node>

        <Node id="FIC-101" x="270" y="180" labelOffset="25" onClick={onSelectTag}>
          <path d="M -15 -10 L -15 10 L 15 -10 L 15 10 Z" stroke="currentColor" strokeWidth="2" fill="currentColor" opacity="0.1" />
          <path d="M -15 -10 L -15 10 L 15 -10 L 15 10 Z" stroke="currentColor" strokeWidth="2" fill="none" />
          <circle cx="0" cy="-10" r="4" fill="currentColor" />
        </Node>

        <Node id="B-101" x="480" y="300" labelOffset="35" onClick={onSelectTag}>
          <rect x="-30" y="-20" width="60" height="40" rx="8" stroke="currentColor" strokeWidth="2" fill="transparent" />
          <path d="M -20 -10 C 0 -30 20 -10 20 10" stroke="currentColor" strokeWidth="2" fill="transparent" />
        </Node>
        
        <Node id="E-201" x="740" y="130" labelOffset="35" onClick={onSelectTag}>
          <circle cx="0" cy="0" r="20" stroke="currentColor" strokeWidth="2" fill="transparent" />
          <path d="M -20 -8 L 20 -8 M -20 8 L 20 8" stroke="currentColor" strokeWidth="2" fill="transparent" />
        </Node>
      </svg>
    </div>
  )
}

const CAT_COLORS = {
  oem_manuals:       { dot: 'bg-purple-400', badge: 'text-purple-300 bg-purple-900/40 border-purple-800' },
  maintenance_data:  { dot: 'bg-teal-400',   badge: 'text-teal-300 bg-teal-900/40 border-teal-800' },
  incident_reports:  { dot: 'bg-red-400',    badge: 'text-red-300 bg-red-900/40 border-red-800' },
  regulatory:        { dot: 'bg-orange-400', badge: 'text-orange-300 bg-orange-900/40 border-orange-800' },
  pids:              { dot: 'bg-blue-400',   badge: 'text-blue-300 bg-blue-900/40 border-blue-800' },
  uploaded:          { dot: 'bg-gray-400',   badge: 'text-gray-300 bg-gray-800 border-gray-700' },
}
const CAT_LABEL = {
  oem_manuals: 'OEM Manual', maintenance_data: 'Maintenance',
  incident_reports: 'Incident', regulatory: 'Regulatory',
  pids: 'P&ID', uploaded: 'Uploaded',
}

function GroupedSources({ sources }) {
  const groups = sources.reduce((acc, s) => {
    const key = s.category || 'other'
    ;(acc[key] = acc[key] || []).push(s)
    return acc
  }, {})

  return (
    <div className="space-y-4">
      {Object.entries(groups).map(([cat, items]) => {
        const colors = CAT_COLORS[cat] ?? CAT_COLORS.uploaded
        return (
          <div key={cat}>
            <div className="flex items-center gap-2 mb-2">
              <span className={`w-2 h-2 rounded-full shrink-0 ${colors.dot}`} />
              <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                {CAT_LABEL[cat] ?? cat} <span className="text-gray-600 normal-case">({items.length})</span>
              </span>
            </div>
            <div className="space-y-1.5 pl-4">
              {items.map(s => (
                <div key={s.index}
                  className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-xs ${colors.badge}`}>
                  <span className="font-mono font-semibold shrink-0">[{s.index}]</span>
                  <div className="min-w-0">
                    <div className="font-medium truncate">{s.filename.replace('.pdf', '')}</div>
                    <div className="opacity-70 mt-0.5 line-clamp-1">{s.description}</div>
                  </div>
                  <span className="ml-auto shrink-0 font-mono opacity-60">
                    {(s.relevance_score * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default function AssetScreen() {
  const [tag, setTag]       = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)
  const [searched, setSearched] = useState('')

  const search = async (t) => {
    const q = (t ?? tag).trim().toUpperCase()
    if (!q) return
    setError(null)
    setResult(null)
    setLoading(true)
    setSearched(q)
    try {
      const res = await api.asset(q)
      setResult(res.data)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Asset Explorer</h2>
        <p className="text-sm text-gray-500 mt-1">
          Enter any equipment tag to pull everything the knowledge base knows about it — specs, manuals, work orders, incidents, and standards.
        </p>
      </div>

      {/* Search bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Tag size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            value={tag}
            onChange={e => setTag(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === 'Enter' && search()}
            placeholder="e.g. P-101A, E-203, PSV-301, TIC-205…"
            className="w-full bg-surface-700 border border-surface-500 rounded-xl pl-9 pr-4 py-2.5 text-sm font-mono text-gray-200 placeholder-gray-600 focus:outline-none focus:border-accent-blue transition-colors"
          />
        </div>
        <button
          onClick={() => search()}
          disabled={!tag.trim() || loading}
          className="flex items-center gap-2 rounded-xl bg-accent-blue px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? <Spinner size={15} className="text-white" /> : <Search size={15} />}
          Look up
        </button>
      </div>

      {/* Interactive P&ID Map */}
      <div className="mb-4">
        <InteractivePIDMap onSelectTag={(t) => { setTag(t); search(t) }} activeTag={tag} />
      </div>

      <ErrorBanner error={error} onDismiss={() => setError(null)} />

      {/* Results */}
      {loading && (
        <div className="flex items-center gap-3 rounded-xl border border-surface-600 bg-surface-800 p-5">
          <Spinner size={18} />
          <div>
            <p className="text-sm font-medium text-gray-200">Looking up <span className="font-mono text-accent-blue">{searched}</span></p>
            <p className="text-xs text-gray-500 mt-0.5">Searching across all document categories…</p>
          </div>
        </div>
      )}

      {result && !loading && (
        <div className="space-y-5">
          {/* Tag header */}
          <div className="flex items-center gap-3 rounded-xl border border-surface-600 bg-surface-800 px-4 py-3">
            <div className="w-8 h-8 rounded-lg bg-accent-blue/15 border border-accent-blue/30 flex items-center justify-center">
              <Cpu size={15} className="text-accent-blue" />
            </div>
            <div>
              <div className="text-sm font-mono font-bold text-accent-blue">{searched}</div>
              <div className="text-xs text-gray-500">{result.chunks_retrieved} relevant chunks across {result.sources?.length ?? 0} documents</div>
            </div>
            <ChevronRight size={14} className="ml-auto text-gray-600" />
          </div>

          {/* Grouped source list */}
          {result.sources?.length > 0 && (
            <div className="rounded-xl border border-surface-600 bg-surface-800 p-4">
              <p className="text-xs font-medium text-gray-400 mb-3 uppercase tracking-wide">Linked Documents</p>
              <GroupedSources sources={result.sources} />
            </div>
          )}

          {/* Full answer */}
          <AnswerPanel result={result} title={`Knowledge summary — ${searched}`} />
        </div>
      )}
    </div>
  )
}
