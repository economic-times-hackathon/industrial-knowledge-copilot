import { useState } from 'react'
import { Wrench, AlertTriangle, ChevronDown, ChevronUp, History } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'
import ConfidenceBadge from '../components/ConfidenceBadge'
import SourceCard from '../components/SourceCard'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

const PRESETS = [
  { tag: 'P-101A', symptom: 'High bearing temperature alarm at 88°C, vibration trending from 2.1 to 6.8 mm/s over 72 hours' },
  { tag: 'E-101',  symptom: 'Reduced heat transfer efficiency, high pressure drop across tube side, suspected fouling' },
  { tag: 'PSV-101',symptom: 'Valve found passing after last inspection, set pressure drifted +4.4% above design' },
  { tag: 'K-601',  symptom: 'High vibration trip, suspected impeller imbalance, catalyst fines carryover observed' },
  { tag: 'TIC-205',symptom: 'False high temperature reading causing spurious control action, thermowell suspected' },
]

// Parse the structured markdown sections from the RCA response
const RCA_SECTIONS = [
  { key: 'Failure Summary',          color: 'border-gray-600', icon: '📋' },
  { key: 'Probable Root Causes',     color: 'border-red-700',  icon: '🔍' },
  { key: 'Contributing Factors',     color: 'border-orange-700', icon: '⚠️' },
  { key: 'Recommended Actions',      color: 'border-green-700', icon: '✅' },
  { key: 'Similar Historical Incidents', color: 'border-blue-700', icon: '📚' },
]

function RCASection({ title, content, color, icon, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen)
  if (!content?.trim()) return null
  return (
    <div className={`rounded-xl border-l-4 ${color} bg-surface-800 border border-surface-600 overflow-hidden`}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-surface-700/40 transition-colors"
      >
        <span className="flex items-center gap-2 text-sm font-medium text-gray-200">
          <span>{icon}</span> {title}
        </span>
        {open ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
      </button>
      {open && (
        <div className="px-4 pb-4 prose-industrial border-t border-surface-600 pt-3">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      )}
    </div>
  )
}

function parseRCASections(answer) {
  const result = {}
  const lines = answer.split('\n')
  let current = null
  let buf = []

  for (const line of lines) {
    const match = line.match(/^##\s+(.+)$/)
    if (match) {
      if (current) result[current] = buf.join('\n').trim()
      current = match[1].trim()
      buf = []
    } else if (current) {
      buf.push(line)
    }
  }
  if (current) result[current] = buf.join('\n').trim()
  return result
}

export default function MaintenanceScreen() {
  const [tag, setTag]       = useState('')
  const [symptom, setSymptom] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)
  const [showSources, setShowSources] = useState(false)

  const run = async () => {
    if (!tag.trim() || !symptom.trim()) return
    setError(null); setResult(null); setLoading(true)
    try {
      const res = await api.rca(tag.trim().toUpperCase(), symptom.trim())
      setResult(res.data)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  const applyPreset = (p) => { setTag(p.tag); setSymptom(p.symptom) }

  const sections = result ? parseRCASections(result.answer) : {}

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Maintenance Intel</h2>
        <p className="text-sm text-gray-500 mt-1">
          Enter an equipment tag and observed symptom. The RCA engine joins work order history,
          OEM manuals, inspection findings, and incident reports to surface probable root causes
          and recommended actions.
        </p>
      </div>

      {/* Form */}
      <div className="rounded-xl border border-surface-600 bg-surface-800 p-5 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1.5 font-medium">Equipment Tag *</label>
            <input
              value={tag}
              onChange={e => setTag(e.target.value.toUpperCase())}
              placeholder="e.g. P-101A"
              className="w-full bg-surface-700 border border-surface-500 rounded-lg px-3 py-2 text-sm font-mono text-gray-200 placeholder-gray-600 focus:outline-none focus:border-accent-blue"
            />
          </div>
          <div className="col-span-1 flex items-end">
            <button
              onClick={run}
              disabled={!tag.trim() || !symptom.trim() || loading}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-accent-blue px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? <Spinner size={15} className="text-white" /> : <Wrench size={15} />}
              {loading ? 'Analysing…' : 'Run RCA'}
            </button>
          </div>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1.5 font-medium">Observed Symptom / Failure Description *</label>
          <textarea
            value={symptom}
            onChange={e => setSymptom(e.target.value)}
            rows={3}
            placeholder="Describe what was observed: alarms, readings, behaviour, timeline…"
            className="w-full bg-surface-700 border border-surface-500 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-accent-blue resize-none"
          />
        </div>
      </div>

      {/* Presets */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <History size={13} className="text-gray-600" />
          <span className="text-xs text-gray-600">Example cases</span>
        </div>
        <div className="space-y-1.5">
          {PRESETS.map(p => (
            <button
              key={p.tag}
              onClick={() => applyPreset(p)}
              className="w-full text-left flex items-start gap-3 rounded-lg border border-surface-600 px-3 py-2 hover:border-surface-500 hover:bg-surface-800 transition-all group"
            >
              <span className="font-mono text-xs font-bold text-accent-blue shrink-0 mt-0.5 w-16">{p.tag}</span>
              <span className="text-xs text-gray-500 group-hover:text-gray-300 line-clamp-1">{p.symptom}</span>
            </button>
          ))}
        </div>
      </div>

      <ErrorBanner error={error} onDismiss={() => setError(null)} />

      {/* RCA Output */}
      {loading && (
        <div className="flex items-center gap-3 rounded-xl border border-surface-600 bg-surface-800 p-5">
          <Spinner size={20} />
          <div>
            <p className="text-sm font-medium text-gray-200">Running RCA for <span className="font-mono text-accent-blue">{tag}</span></p>
            <p className="text-xs text-gray-500 mt-0.5">Retrieving work orders, manuals, inspection records, incident history…</p>
          </div>
        </div>
      )}

      {result && !loading && (
        <div className="space-y-3">
          {/* Meta bar */}
          <div className="flex items-center gap-3 px-4 py-2.5 rounded-xl border border-surface-600 bg-surface-800">
            <AlertTriangle size={15} className="text-yellow-400 shrink-0" />
            <span className="text-sm font-mono font-bold text-yellow-300">{tag}</span>
            <span className="text-xs text-gray-500 flex-1 truncate">{symptom.slice(0, 60)}…</span>
            <ConfidenceBadge level={result.confidence} />
            <span className="text-xs text-gray-600 font-mono">{result.chunks_retrieved} chunks</span>
          </div>

          {/* Structured sections */}
          {RCA_SECTIONS.map(({ key, color, icon }) => (
            sections[key] && (
              <RCASection
                key={key}
                title={key}
                content={sections[key]}
                color={color}
                icon={icon}
                defaultOpen={key === 'Failure Summary' || key === 'Probable Root Causes' || key === 'Recommended Actions'}
              />
            )
          ))}

          {/* Fallback: render raw if sections didn't parse */}
          {Object.keys(sections).length === 0 && (
            <div className="rounded-xl border border-surface-600 bg-surface-800 p-4 prose-industrial">
              <ReactMarkdown>{result.answer}</ReactMarkdown>
            </div>
          )}

          {/* Sources */}
          {result.sources?.length > 0 && (
            <div className="rounded-xl border border-surface-600 bg-surface-800 overflow-hidden">
              <button
                onClick={() => setShowSources(s => !s)}
                className="w-full flex items-center justify-between px-4 py-3 text-xs text-gray-400 hover:bg-surface-700/30"
              >
                <span>Sources ({result.sources.length})</span>
                {showSources ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
              </button>
              {showSources && (
                <div className="grid grid-cols-2 gap-2 px-4 pb-4">
                  {result.sources.map(s => <SourceCard key={s.index} source={s} />)}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
