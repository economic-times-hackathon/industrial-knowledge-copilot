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
        className="cursor-pointer"
        style={{ color: isActive ? '#000' : '#9ca3af' }}
        onClick={() => onClick(id)}
      >
        {children}
        <text
          y={labelOffset}
          textAnchor="middle"
          fill={isActive ? '#000' : '#6b7280'}
          style={{ fontSize: '10px', fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: '0.05em' }}
        >
          {id}
        </text>
      </g>
    )
  }

  return (
    <div className="w-full bg-white border-2 border-gray-200 rounded-xl overflow-hidden relative shadow-sm">
      <div className="absolute top-3 left-4 text-xs font-bold text-gray-500 uppercase tracking-widest">
        Interactive P&amp;ID Map
      </div>
      <svg viewBox="0 0 800 360" className="w-full h-auto max-h-[400px]">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#9ca3af" />
          </marker>
        </defs>

        {/* Piping */}
        <path d="M 80 180 L 160 180" stroke="#d1d5db" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />
        <path d="M 220 180 L 320 180" stroke="#d1d5db" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />
        <path d="M 380 180 L 460 180" stroke="#d1d5db" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />
        <path d="M 520 180 L 620 180" stroke="#d1d5db" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />
        <path d="M 650 250 L 650 300 L 520 300" stroke="#d1d5db" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />
        <path d="M 650 110 L 650 60 L 740 60 L 740 100" stroke="#d1d5db" strokeWidth="2" markerEnd="url(#arrow)" fill="none" />

        <Node id="TK-001" x="50" y="180" labelOffset="45" onClick={onSelectTag}>
          <path d="M -30 -30 Q 0 -45 30 -30 L 30 30 L -30 30 Z" stroke="currentColor" strokeWidth="2" fill="transparent" />
        </Node>
        <Node id="P-101A" x="190" y="180" labelOffset="35" onClick={onSelectTag}>
          <circle cx="0" cy="0" r="20" stroke="currentColor" strokeWidth="2" fill="transparent" />
          <path d="M -15 0 L 15 -15 L 15 15 Z" fill="currentColor" opacity="0.15" />
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
          <path d="M -15 -10 L -15 10 L 15 -10 L 15 10 Z" stroke="currentColor" strokeWidth="2" fill="currentColor" opacity="0.08" />
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

const CAT_LABEL = {
  oem_manuals: 'OEM Manual', maintenance_data: 'Maintenance',
  incident_reports: 'Incident', regulatory: 'Regulatory',
  pids: 'P&ID', uploaded: 'Uploaded',
}

function GroupedSources({ sources }) {
  const groups = sources.reduce((acc, s) => {
    const key = s.category || 'other';
    (acc[key] = acc[key] || []).push(s)
    return acc
  }, {})

  return (
    <div className="space-y-4">
      {Object.entries(groups).map(([cat, items]) => (
        <div key={cat}>
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2 h-2 rounded-full bg-black shrink-0" />
            <span className="text-xs font-bold text-gray-700 uppercase tracking-wide">
              {CAT_LABEL[cat] ?? cat} <span className="font-normal text-gray-500">({items.length})</span>
            </span>
          </div>
          <div className="space-y-1.5 pl-4">
            {items.map(s => (
              <div
                key={s.index}
                className="flex items-start gap-2 rounded-lg border border-gray-200 px-3 py-2 text-xs bg-gray-50 hover:border-black transition-colors"
              >
                <span className="font-mono font-bold text-black shrink-0">[{s.index}]</span>
                <div className="min-w-0">
                  <div className="font-semibold text-black truncate">{s.filename.replace('.pdf', '')}</div>
                  <div className="text-gray-500 mt-0.5 line-clamp-1">{s.description}</div>
                </div>
                <span className="ml-auto shrink-0 font-mono font-bold text-gray-600">
                  {(s.relevance_score * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
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
    setError(null); setResult(null); setLoading(true); setSearched(q)
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
    <div className="space-y-8">
      {/* Intro */}
      <div>
        <h2 className="text-2xl font-display font-bold text-black">Asset Explorer</h2>
        <p className="text-base text-gray-600 mt-1">
          Enter any equipment tag to pull everything the knowledge base knows about it — specs, manuals, work orders, incidents, and standards.
        </p>
      </div>

      {/* Search bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Tag size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            value={tag}
            onChange={e => setTag(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === 'Enter' && search()}
            placeholder="e.g. P-101A, E-203, PSV-301, TIC-205…"
            className="w-full bg-white border-2 border-gray-200 rounded-xl pl-9 pr-4 py-3 text-[15px] font-mono text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors"
          />
        </div>
        <button
          onClick={() => search()}
          disabled={!tag.trim() || loading}
          className="flex items-center gap-2 rounded-xl bg-black px-6 py-3 text-[15px] font-bold text-white hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? <Spinner size={15} className="text-white" /> : <Search size={15} />}
          Look up
        </button>
      </div>

      {/* P&ID Map */}
      <InteractivePIDMap onSelectTag={(t) => { setTag(t); search(t) }} activeTag={tag} />

      <ErrorBanner error={error} onDismiss={() => setError(null)} />

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-4 rounded-xl border-2 border-black bg-black p-5 text-white">
          <Spinner size={18} className="text-white" />
          <div>
            <p className="text-[15px] font-bold">Looking up <span className="font-mono">{searched}</span></p>
            <p className="text-sm text-gray-300 mt-0.5">Searching across all document categories…</p>
          </div>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-5">
          {/* Tag header */}
          <div className="flex items-center gap-3 rounded-xl border-2 border-black bg-black px-5 py-4 text-white">
            <div className="w-9 h-9 rounded-lg bg-white flex items-center justify-center shrink-0">
              <Cpu size={16} className="text-black" />
            </div>
            <div>
              <div className="text-[15px] font-mono font-bold">{searched}</div>
              <div className="text-sm text-gray-300">
                {result.chunks_retrieved} relevant chunks across {result.sources?.length ?? 0} documents
              </div>
            </div>
            <ChevronRight size={16} className="ml-auto text-gray-500" />
          </div>

          {/* Grouped source list */}
          {result.sources?.length > 0 && (
            <div className="rounded-xl border-2 border-gray-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-bold text-gray-500 mb-4 uppercase tracking-wide">Linked Documents</p>
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
