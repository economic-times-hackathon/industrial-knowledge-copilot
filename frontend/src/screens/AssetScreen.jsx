import { useState } from 'react'
import { Search, Tag, ChevronRight, Cpu } from 'lucide-react'
import { api } from '../api'
import AnswerPanel from '../components/AnswerPanel'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

const QUICK_TAGS = [
  'P-101A', 'P-201A', 'E-101', 'E-201', 'V-101', 'V-601',
  'PSV-101', 'FIC-101', 'TIC-205', 'R-601', 'K-601', 'F-101',
  'CT-401', 'B-101', 'TK-001',
]

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

      {/* Quick-access tags */}
      <div>
        <p className="text-xs text-gray-600 mb-2">Quick access</p>
        <div className="flex flex-wrap gap-1.5">
          {QUICK_TAGS.map(t => (
            <button
              key={t}
              onClick={() => { setTag(t); search(t) }}
              className="px-2.5 py-1 text-xs font-mono rounded-lg border border-surface-600 text-gray-400 hover:border-accent-blue/50 hover:text-accent-blue hover:bg-accent-blue/5 transition-all"
            >
              {t}
            </button>
          ))}
        </div>
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
