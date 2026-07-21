import { useState } from 'react'
import { Wrench, AlertTriangle, ChevronDown, ChevronUp, History } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'

import SourceCard from '../components/SourceCard'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

const PRESETS = [
  { tag: 'P-101A',  symptom: 'High bearing temperature alarm at 88°C, vibration trending from 2.1 to 6.8 mm/s over 72 hours' },
  { tag: 'E-101',   symptom: 'Reduced heat transfer efficiency, high pressure drop across tube side, suspected fouling' },
  { tag: 'PSV-101', symptom: 'Valve found passing after last inspection, set pressure drifted +4.4% above design' },
  { tag: 'K-601',   symptom: 'High vibration trip, suspected impeller imbalance, catalyst fines carryover observed' },
  { tag: 'TIC-205', symptom: 'False high temperature reading causing spurious control action, thermowell suspected' },
]

const RCA_SECTIONS = [
  { key: 'Failure Summary',              icon: '📋', accent: 'border-black' },
  { key: 'Probable Root Causes',         icon: '🔍', accent: 'border-gray-700' },
  { key: 'Contributing Factors',         icon: '⚠️', accent: 'border-gray-500' },
  { key: 'Recommended Actions',          icon: '✅', accent: 'border-gray-400' },
  { key: 'Similar Historical Incidents', icon: '📚', accent: 'border-gray-300' },
]

function RCASection({ title, content, accent, icon, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen)
  if (!content?.trim()) return null
  return (
    <div className={`rounded-xl border-l-4 ${accent} border border-gray-200 bg-white overflow-hidden shadow-sm`}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors"
      >
        <span className="flex items-center gap-2 text-[15px] font-bold text-black">
          <span>{icon}</span> {title}
        </span>
        {open
          ? <ChevronUp size={15} className="text-gray-500" />
          : <ChevronDown size={15} className="text-gray-500" />}
      </button>
      {open && (
        <div className="px-5 pb-5 prose-industrial border-t border-gray-100 pt-4">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      )}
    </div>
  )
}

function parseRCASections(answer) {
  const result = {}
  const lines = answer.split('\n')
  let current = null, buf = []
  for (const line of lines) {
    const match = line.match(/^##\s+(.+)$/)
    if (match) {
      if (current) result[current] = buf.join('\n').trim()
      current = match[1].trim(); buf = []
    } else if (current) {
      buf.push(line)
    }
  }
  if (current) result[current] = buf.join('\n').trim()
  return result
}

export default function MaintenanceScreen() {
  const [tag, setTag]         = useState('')
  const [symptom, setSymptom] = useState('')
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
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
    <div className="space-y-8">
      {/* Intro */}
      <div>
        <h2 className="text-2xl font-display font-bold text-black">Maintenance Intel</h2>
        <p className="text-base text-gray-600 mt-1">
          Enter an equipment tag and observed symptom. The RCA engine joins work order history,
          OEM manuals, inspection findings, and incident reports to surface probable root causes
          and recommended actions.
        </p>
      </div>

      {/* Form */}
      <div className="rounded-xl border-2 border-gray-200 bg-white p-6 space-y-5 shadow-sm">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-bold text-black mb-2">Equipment Tag *</label>
            <input
              value={tag}
              onChange={e => setTag(e.target.value.toUpperCase())}
              placeholder="e.g. P-101A"
              className="w-full bg-white border-2 border-gray-200 rounded-lg px-3 py-2.5 text-[15px] font-mono text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={run}
              disabled={!tag.trim() || !symptom.trim() || loading}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-black px-4 py-2.5 text-[15px] font-bold text-white hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? <Spinner size={15} className="text-white" /> : <Wrench size={15} />}
              {loading ? 'Analysing…' : 'Run RCA'}
            </button>
          </div>
        </div>
        <div>
          <label className="block text-sm font-bold text-black mb-2">Observed Symptom / Failure Description *</label>
          <textarea
            value={symptom}
            onChange={e => setSymptom(e.target.value)}
            rows={3}
            placeholder="Describe what was observed: alarms, readings, behaviour, timeline…"
            className="w-full bg-white border-2 border-gray-200 rounded-lg px-3 py-2.5 text-[15px] text-black placeholder-gray-400 focus:outline-none focus:border-black resize-none transition-colors"
          />
        </div>
      </div>

      {/* Presets */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <History size={14} className="text-gray-500" />
          <span className="text-sm font-bold text-gray-600 uppercase tracking-wide">Example cases</span>
        </div>
        <div className="space-y-2">
          {PRESETS.map(p => (
            <button
              key={p.tag}
              onClick={() => applyPreset(p)}
              className="w-full text-left flex items-start gap-4 rounded-xl border border-gray-200 px-4 py-3 hover:border-black hover:bg-gray-50 transition-all group"
            >
              <span className="font-mono text-sm font-bold text-black shrink-0 mt-0.5 w-16">{p.tag}</span>
              <span className="text-sm text-gray-600 group-hover:text-black line-clamp-1 transition-colors">{p.symptom}</span>
            </button>
          ))}
        </div>
      </div>

      <ErrorBanner error={error} onDismiss={() => setError(null)} />

      {/* Loading state */}
      {loading && (
        <div className="flex items-center gap-4 rounded-xl border-2 border-black bg-black p-5 text-white">
          <Spinner size={20} className="text-white" />
          <div>
            <p className="text-[15px] font-bold">Running RCA for <span className="font-mono">{tag}</span></p>
            <p className="text-sm text-gray-300 mt-0.5">Retrieving work orders, manuals, inspection records, incident history…</p>
          </div>
        </div>
      )}

      {/* RCA Output */}
      {result && !loading && (
        <div className="space-y-4">
          {/* Meta bar */}
          <div className="flex items-center gap-3 px-5 py-3 rounded-xl border-2 border-black bg-black text-white">
            <AlertTriangle size={16} className="text-white shrink-0" />
            <span className="text-[15px] font-mono font-bold">{tag}</span>
            <span className="text-sm text-gray-300 flex-1 truncate">{symptom.slice(0, 60)}…</span>
            <span className="text-xs text-gray-500 font-mono">{result.chunks_retrieved} chunks</span>
          </div>

          {/* Structured sections */}
          {RCA_SECTIONS.map(({ key, accent, icon }) =>
            sections[key] ? (
              <RCASection
                key={key}
                title={key}
                content={sections[key]}
                accent={accent}
                icon={icon}
                defaultOpen={['Failure Summary', 'Probable Root Causes', 'Recommended Actions'].includes(key)}
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
              <button
                onClick={() => setShowSources(s => !s)}
                className="w-full flex items-center justify-between px-5 py-3 text-sm font-bold text-black hover:bg-gray-50 uppercase tracking-wide transition-colors"
              >
                <span>Sources ({result.sources.length})</span>
                {showSources ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
              {showSources && (
                <div className="grid grid-cols-2 gap-3 px-5 pb-5">
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
