import { useState } from 'react'
import { ShieldCheck, ChevronDown, ChevronUp, AlertTriangle, CheckCircle2, Info } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'

import SourceCard from '../components/SourceCard'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

const PRESETS = [
  { topic: 'Pressure relief valve testing and recertification', area: 'CDU overhead system' },
  { topic: 'Emergency siren codes and emergency classification', area: 'Refinery site' },
  { topic: 'Fire water system hydrant spacing and pump capacity', area: 'Tank farm' },
  { topic: 'Pressure vessel inspection intervals under PESO', area: 'HDS unit' },
  { topic: 'Work permit system for hot work and confined space', area: 'Maintenance department' },
]

const COMPLIANCE_SECTIONS = [
  { key: 'Applicable Regulations',       color: 'border-blue-700',   icon: '📜', defaultOpen: true  },
  { key: 'Current State Assessment',     color: 'border-gray-600',   icon: '📊', defaultOpen: true  },
  { key: 'Compliance Gaps Identified',   color: 'border-red-700',    icon: '❌', defaultOpen: true  },
  { key: 'Evidence Pack',                color: 'border-green-700',  icon: '📁', defaultOpen: true  },
  { key: 'Recommended Corrective Actions', color: 'border-orange-700', icon: '🔧', defaultOpen: false },
]

// Priority badge inside corrective actions
function PriorityBadge({ text }) {
  const upper = text.toUpperCase()
  if (upper.includes('CRITICAL')) return <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-900/60 text-red-300 border border-red-700">CRITICAL</span>
  if (upper.includes('HIGH'))     return <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-orange-900/60 text-orange-300 border border-orange-700">HIGH</span>
  if (upper.includes('MEDIUM'))   return <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-yellow-900/60 text-yellow-300 border border-yellow-700">MEDIUM</span>
  if (upper.includes('LOW'))      return <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-gray-700 text-gray-400 border border-gray-600">LOW</span>
  return null
}

function ComplianceSection({ title, content, color, icon, defaultOpen }) {
  const [open, setOpen] = useState(defaultOpen)
  if (!content?.trim()) return null

  // Gaps section gets a special warning treatment
  const isGaps     = title === 'Compliance Gaps Identified'
  const isEvidence = title === 'Evidence Pack'

  return (
    <div className={`rounded-xl border-l-4 ${color} bg-surface-800 border border-surface-600 overflow-hidden`}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-surface-700/30 transition-colors"
      >
        <span className="flex items-center gap-2 text-sm font-medium text-gray-200">
          <span>{icon}</span> {title}
        </span>
        {open ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
      </button>

      {open && (
        <div className={`border-t border-surface-600 px-4 pb-4 pt-3
          ${isGaps ? 'bg-red-950/20' : isEvidence ? 'bg-green-950/20' : ''}`}>
          {isGaps && (
            <div className="flex items-center gap-2 mb-3 text-xs text-red-400">
              <AlertTriangle size={12} /> Gaps require corrective action before next audit
            </div>
          )}
          {isEvidence && (
            <div className="flex items-center gap-2 mb-3 text-xs text-green-400">
              <CheckCircle2 size={12} /> These documents constitute your compliance evidence pack
            </div>
          )}
          <div className="prose-industrial">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}

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

export default function ComplianceScreen() {
  const [topic, setTopic]   = useState('')
  const [area, setArea]     = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)
  const [showSources, setShowSources] = useState(false)

  const run = async () => {
    if (!topic.trim()) return
    setError(null); setResult(null); setLoading(true)
    try {
      const res = await api.compliance(topic.trim(), area.trim() || null)
      setResult(res.data)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  const sections = result ? parseSections(result.answer) : {}

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Compliance Intel</h2>
        <p className="text-sm text-gray-500 mt-1">
          Maps live equipment or procedure state against OISD, PESO, Factories Act, and DGMS requirements.
          Identifies gaps and generates an evidence pack ready for auditors.
        </p>
      </div>

      {/* Form */}
      <div className="rounded-xl border border-surface-600 bg-surface-800 p-5 space-y-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1.5 font-medium">Compliance Topic *</label>
          <input
            value={topic}
            onChange={e => setTopic(e.target.value)}
            placeholder="e.g. pressure relief valve testing, fire water system, work permit"
            className="w-full bg-surface-700 border border-surface-500 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-accent-blue"
          />
        </div>
        <div className="flex gap-3">
          <div className="flex-1">
            <label className="block text-xs text-gray-500 mb-1.5 font-medium">Equipment / Area <span className="text-gray-700">(optional)</span></label>
            <input
              value={area}
              onChange={e => setArea(e.target.value)}
              placeholder="e.g. CDU unit, P-101A, Tank Farm"
              className="w-full bg-surface-700 border border-surface-500 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-accent-blue"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={run}
              disabled={!topic.trim() || loading}
              className="flex items-center gap-2 rounded-lg bg-accent-blue px-5 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? <Spinner size={15} className="text-white" /> : <ShieldCheck size={15} />}
              {loading ? 'Checking…' : 'Check Compliance'}
            </button>
          </div>
        </div>
      </div>

      {/* Preset topics */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Info size={12} className="text-gray-600" />
          <span className="text-xs text-gray-600">Common compliance checks</span>
        </div>
        <div className="space-y-1.5">
          {PRESETS.map(p => (
            <button
              key={p.topic}
              onClick={() => { setTopic(p.topic); setArea(p.area) }}
              className="w-full text-left flex items-start gap-3 rounded-lg border border-surface-600 px-3 py-2 hover:border-surface-500 hover:bg-surface-800 transition-all group"
            >
              <ShieldCheck size={13} className="text-gray-600 group-hover:text-accent-blue shrink-0 mt-0.5" />
              <div>
                <div className="text-xs text-gray-300 group-hover:text-gray-200">{p.topic}</div>
                <div className="text-[10px] text-gray-600 mt-0.5">{p.area}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <ErrorBanner error={error} onDismiss={() => setError(null)} />

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-3 rounded-xl border border-surface-600 bg-surface-800 p-5">
          <Spinner size={20} />
          <div>
            <p className="text-sm font-medium text-gray-200">Checking compliance…</p>
            <p className="text-xs text-gray-500 mt-0.5">Retrieving OISD, PESO, Factories Act, DGMS requirements…</p>
          </div>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-3">
          {/* Meta bar */}
          <div className="flex items-center gap-3 px-4 py-2.5 rounded-xl border border-surface-600 bg-surface-800">
            <ShieldCheck size={15} className="text-accent-blue shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-200 truncate">{topic}</div>
              {area && <div className="text-xs text-gray-500">{area}</div>}
            </div>

            <span className="text-xs text-gray-600 font-mono shrink-0">{result.chunks_retrieved} chunks</span>
          </div>

          {/* Sections */}
          {COMPLIANCE_SECTIONS.map(({ key, color, icon, defaultOpen }) =>
            sections[key] && (
              <ComplianceSection
                key={key} title={key} content={sections[key]}
                color={color} icon={icon} defaultOpen={defaultOpen}
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
              <button
                onClick={() => setShowSources(s => !s)}
                className="w-full flex items-center justify-between px-4 py-3 text-xs text-gray-400 hover:bg-surface-700/30"
              >
                <span>Compliance Sources ({result.sources.length})</span>
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
