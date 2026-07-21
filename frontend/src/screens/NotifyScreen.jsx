import { useState, useEffect } from 'react'
import { Bell, RefreshCw, AlertTriangle, ShieldAlert, BookOpen, Zap, ChevronDown, ChevronUp } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'

import SourceCard from '../components/SourceCard'
import Spinner from '../components/Spinner'

const NOTIFY_SECTIONS = [
  { key: 'Active Risk Alerts',             icon: AlertTriangle, accent: 'border-black',    defaultOpen: true  },
  { key: 'Compliance Flags',               icon: ShieldAlert,   accent: 'border-gray-600', defaultOpen: true  },
  { key: 'Lessons from Similar Incidents', icon: BookOpen,      accent: 'border-gray-400', defaultOpen: false },
  { key: 'Recommended Immediate Actions',  icon: Zap,           accent: 'border-gray-300', defaultOpen: true  },
]

function parseSections(answer) {
  const result = {}
  const lines  = answer.split('\n')
  let current  = null, buf = []
  for (const line of lines) {
    const m = line.match(/^##\s+(.+)$/)
    if (m) {
      if (current) result[current] = buf.join('\n').trim()
      current = m[1].trim(); buf = []
    } else if (current) {
      buf.push(line)
    }
  }
  if (current) result[current] = buf.join('\n').trim()
  return result
}

function AlertSection({ title, content, icon: Icon, accent, defaultOpen }) {
  const [open, setOpen] = useState(defaultOpen)
  if (!content?.trim()) return null

  return (
    <div className={`rounded-xl border-l-4 ${accent} border border-gray-200 bg-white overflow-hidden shadow-sm`}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors"
      >
        <span className="flex items-center gap-2 text-[15px] font-bold text-black">
          <Icon size={16} className="text-black" />
          {title}
        </span>
        {open ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
      </button>
      {open && (
        <div className="border-t border-gray-100 px-5 pb-5 pt-4 prose-industrial">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      )}
    </div>
  )
}

export default function NotifyScreen() {
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
  const [lastRefresh, setLastRefresh] = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try {
      const res = await api.notifications()
      setResult(res.data)
      setLastRefresh(new Date())
    } catch (err) {
      setError(err?.response?.data?.detail ?? err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const sections    = result ? parseSections(result.answer) : {}
  const alertCount  = NOTIFY_SECTIONS.filter(s => sections[s.key]?.trim()).length

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-display font-bold text-black">Notifications</h2>
          <p className="text-base text-gray-600 mt-1">
            Proactive alert digest — the system scans the knowledge base for active risk patterns,
            compliance flags, and lessons from incidents. Pushed to you, not pulled.
          </p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg border-2 border-gray-200 bg-white px-4 py-2.5 text-sm font-bold text-black hover:border-black disabled:opacity-40 transition-all shrink-0"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Status bar */}
      {!loading && result && (
        <div className="flex items-center gap-4 rounded-xl border-2 border-black bg-black px-5 py-4 text-white">
          <div className="relative">
            <Bell size={20} className="text-white" />
            {alertCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-white text-black text-[9px] flex items-center justify-center font-bold">
                {alertCount}
              </span>
            )}
          </div>
          <div className="flex-1">
            <p className="text-[15px] font-bold">
              {alertCount} alert section{alertCount !== 1 ? 's' : ''} active
            </p>
            {lastRefresh && (
              <p className="text-sm text-gray-400 mt-0.5">
                Last scanned: {lastRefresh.toLocaleTimeString()}
              </p>
            )}
          </div>
          <span className="text-xs text-gray-500 font-mono">{result.chunks_retrieved} chunks</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 rounded-lg border-2 border-black bg-gray-100 px-4 py-3 text-sm font-bold text-black">
          <AlertTriangle size={16} className="shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-4 rounded-xl border-2 border-black bg-black p-5 text-white">
          <Spinner size={20} className="text-white" />
          <div>
            <p className="text-[15px] font-bold">Scanning knowledge base…</p>
            <p className="text-sm text-gray-300 mt-0.5">Checking for risk patterns, compliance flags, and incident lessons</p>
          </div>
        </div>
      )}

      {/* Alert sections */}
      {!loading && result && (
        <div className="space-y-4">
          {NOTIFY_SECTIONS.map(s =>
            sections[s.key] ? (
              <AlertSection
                key={s.key}
                title={s.key}
                content={sections[s.key]}
                icon={s.icon}
                accent={s.accent}
                defaultOpen={s.defaultOpen}
              />
            ) : null
          )}

          {/* Fallback */}
          {Object.keys(sections).length === 0 && (
            <div className="rounded-xl border-2 border-gray-200 bg-white p-5 prose-industrial">
              <ReactMarkdown>{result.answer}</ReactMarkdown>
            </div>
          )}

          {/* Sources */}
          {result.sources?.length > 0 && (
            <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <details className="group">
                <summary className="px-5 py-3 text-sm font-bold text-black cursor-pointer hover:bg-gray-50 list-none flex items-center justify-between uppercase tracking-wide">
                  <span>Alert Sources ({result.sources.length})</span>
                  <ChevronDown size={14} className="group-open:rotate-180 transition-transform" />
                </summary>
                <div className="grid grid-cols-2 gap-3 px-5 pb-5">
                  {result.sources.map(s => <SourceCard key={s.index} source={s} />)}
                </div>
              </details>
            </div>
          )}
        </div>
      )}

      {/* How it works */}
      <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
        <p className="text-xs font-bold text-gray-600 mb-2 uppercase tracking-wide">How this works</p>
        <p className="text-sm text-gray-600 leading-relaxed">
          This feed is generated by the same RAG pipeline as the other screens but with a proactive scan prompt
          — no user question needed. In production it runs on a scheduler every 6 hours and pushes results
          to the notification feed automatically. The scan covers: active failure precursor patterns,
          regulatory requirements approaching or overdue, and lessons from historical incidents matching
          current plant conditions.
        </p>
      </div>
    </div>
  )
}
