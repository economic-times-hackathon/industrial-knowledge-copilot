import { useState, useEffect } from 'react'
import { Bell, RefreshCw, AlertTriangle, ShieldAlert, BookOpen, Zap, ChevronDown, ChevronUp } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'
import ConfidenceBadge from '../components/ConfidenceBadge'
import SourceCard from '../components/SourceCard'
import Spinner from '../components/Spinner'

const NOTIFY_SECTIONS = [
  { key: 'Active Risk Alerts',          icon: AlertTriangle,  color: 'border-red-700    bg-red-950/20',   badge: 'text-red-300 bg-red-900/40 border-red-800',    defaultOpen: true  },
  { key: 'Compliance Flags',            icon: ShieldAlert,    color: 'border-orange-700 bg-orange-950/20', badge: 'text-orange-300 bg-orange-900/40 border-orange-800', defaultOpen: true  },
  { key: 'Lessons from Similar Incidents', icon: BookOpen,   color: 'border-blue-700   bg-blue-950/20',  badge: 'text-blue-300 bg-blue-900/40 border-blue-800',   defaultOpen: false },
  { key: 'Recommended Immediate Actions', icon: Zap,         color: 'border-green-700  bg-green-950/20', badge: 'text-green-300 bg-green-900/40 border-green-800', defaultOpen: true  },
]

function parseSections(answer) {
  const result = {}
  const lines  = answer.split('\n')
  let current  = null
  let buf      = []
  for (const line of lines) {
    const m = line.match(/^##\s+(.+)$/)
    if (m) {
      if (current) result[current] = buf.join('\n').trim()
      current = m[1].trim()
      buf = []
    } else if (current) {
      buf.push(line)
    }
  }
  if (current) result[current] = buf.join('\n').trim()
  return result
}

function AlertSection({ title, content, icon: Icon, color, badge, defaultOpen }) {
  const [open, setOpen] = useState(defaultOpen)
  if (!content?.trim()) return null
  const [border, bg] = color.split(' ')
  return (
    <div className={`rounded-xl border-l-4 ${border} ${bg} border border-surface-600 overflow-hidden`}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 hover:brightness-110 transition-all"
      >
        <span className={`flex items-center gap-1.5 px-2 py-0.5 rounded border text-[10px] font-semibold uppercase ${badge}`}>
          <Icon size={10} /> {title}
        </span>
        <span className="ml-auto text-gray-600">
          {open ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
        </span>
      </button>
      {open && (
        <div className="border-t border-surface-600/50 px-4 pb-4 pt-3 prose-industrial">
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

  // Auto-load on mount
  useEffect(() => { load() }, [])

  const sections = result ? parseSections(result.answer) : {}
  const alertCount = NOTIFY_SECTIONS.filter(s => sections[s.key]?.trim()).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-100">Notifications</h2>
          <p className="text-sm text-gray-500 mt-1">
            Proactive alert digest — the system scans the knowledge base for active risk patterns,
            compliance flags, and lessons from incidents. Pushed to you, not pulled.
          </p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg border border-surface-600 bg-surface-800 px-3 py-2 text-xs text-gray-400 hover:text-gray-200 hover:border-surface-500 disabled:opacity-40 transition-all"
        >
          {loading ? <Spinner size={13} /> : <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />}
          Refresh
        </button>
      </div>

      {/* Status bar */}
      {!loading && result && (
        <div className="flex items-center gap-3 rounded-xl border border-surface-600 bg-surface-800 px-4 py-3">
          <div className="relative">
            <Bell size={18} className="text-accent-orange" />
            {alertCount > 0 && (
              <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-accent-red text-white text-[8px] flex items-center justify-center font-bold">
                {alertCount}
              </span>
            )}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-200">
              {alertCount} alert section{alertCount !== 1 ? 's' : ''} active
            </p>
            {lastRefresh && (
              <p className="text-[10px] text-gray-600 mt-0.5">
                Last scanned: {lastRefresh.toLocaleTimeString()}
              </p>
            )}
          </div>
          <ConfidenceBadge level={result.confidence} />
          <span className="text-xs text-gray-600 font-mono">{result.chunks_retrieved} chunks</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 rounded-lg border border-red-800 bg-red-900/30 px-4 py-3 text-sm text-red-300">
          <AlertTriangle size={16} className="shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="flex items-center gap-3 rounded-xl border border-surface-600 bg-surface-800 p-5">
          <Spinner size={20} />
          <div>
            <p className="text-sm font-medium text-gray-200">Scanning knowledge base…</p>
            <p className="text-xs text-gray-500 mt-0.5">Checking for risk patterns, compliance flags, and incident lessons</p>
          </div>
        </div>
      )}

      {/* Alert sections */}
      {!loading && result && (
        <div className="space-y-3">
          {NOTIFY_SECTIONS.map(s =>
            sections[s.key] && (
              <AlertSection
                key={s.key}
                title={s.key}
                content={sections[s.key]}
                icon={s.icon}
                color={s.color}
                badge={s.badge}
                defaultOpen={s.defaultOpen}
              />
            )
          )}

          {/* Fallback */}
          {Object.keys(sections).length === 0 && (
            <div className="rounded-xl border border-surface-600 bg-surface-800 p-4 prose-industrial">
              <ReactMarkdown>{result.answer}</ReactMarkdown>
            </div>
          )}

          {/* Sources */}
          {result.sources?.length > 0 && (
            <div className="rounded-xl border border-surface-600 bg-surface-800 overflow-hidden">
              <details className="group">
                <summary className="px-4 py-3 text-xs text-gray-400 cursor-pointer hover:bg-surface-700/30 list-none flex items-center justify-between">
                  <span>Alert Sources ({result.sources.length})</span>
                  <ChevronDown size={13} className="group-open:rotate-180 transition-transform" />
                </summary>
                <div className="grid grid-cols-2 gap-2 px-4 pb-4">
                  {result.sources.map(s => <SourceCard key={s.index} source={s} />)}
                </div>
              </details>
            </div>
          )}
        </div>
      )}

      {/* How it works footer */}
      <div className="rounded-xl border border-surface-600/50 bg-surface-800/50 p-4">
        <p className="text-xs text-gray-600 font-medium mb-2">How this works</p>
        <p className="text-xs text-gray-700 leading-relaxed">
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
