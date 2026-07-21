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
  { topic: 'Pressure vessel inspection intervals under PESO',   area: 'HDS unit' },
  { topic: 'Work permit system for hot work and confined space', area: 'Maintenance department' },
]

const COMPLIANCE_SECTIONS = [
  { key: 'Applicable Regulations',         icon: '📜', accent: 'border-black',    defaultOpen: true  },
  { key: 'Current State Assessment',       icon: '📊', accent: 'border-gray-600', defaultOpen: true  },
  { key: 'Compliance Gaps Identified',     icon: '❌', accent: 'border-gray-500', defaultOpen: true  },
  { key: 'Evidence Pack',                  icon: '📁', accent: 'border-gray-400', defaultOpen: true  },
  { key: 'Recommended Corrective Actions', icon: '🔧', accent: 'border-gray-300', defaultOpen: false },
]

function ComplianceSection({ title, content, accent, icon, defaultOpen }) {
  const [open, setOpen] = useState(defaultOpen)
  if (!content?.trim()) return null

  const isGaps     = title === 'Compliance Gaps Identified'
  const isEvidence = title === 'Evidence Pack'

  return (
    <div className={`rounded-xl border-l-4 ${accent} border border-gray-200 bg-white overflow-hidden shadow-sm`}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors"
      >
        <span className="flex items-center gap-2 text-[15px] font-bold text-black">
          <span>{icon}</span> {title}
        </span>
        {open ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
      </button>

      {open && (
        <div className={`border-t border-gray-100 px-5 pb-5 pt-4 ${isGaps ? 'bg-gray-50' : isEvidence ? 'bg-gray-50' : ''}`}>
          {isGaps && (
            <div className="flex items-center gap-2 mb-3 text-xs font-bold text-black">
              <AlertTriangle size={13} /> Gaps require corrective action before next audit
            </div>
          )}
          {isEvidence && (
            <div className="flex items-center gap-2 mb-3 text-xs font-bold text-black">
              <CheckCircle2 size={13} /> These documents constitute your compliance evidence pack
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

export default function ComplianceScreen() {
  const [topic, setTopic]     = useState('')
  const [area, setArea]       = useState('')
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
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
    <div className="space-y-8">
      {/* Intro */}
      <div>
        <h2 className="text-2xl font-display font-bold text-black">Compliance Intel</h2>
        <p className="text-base text-gray-600 mt-1">
          Maps live equipment or procedure state against OISD, PESO, Factories Act, and DGMS requirements.
          Identifies gaps and generates an evidence pack ready for auditors.
        </p>
      </div>

      {/* Form */}
      <div className="rounded-xl border-2 border-gray-200 bg-white p-6 space-y-5 shadow-sm">
        <div>
          <label className="block text-sm font-bold text-black mb-2">Compliance Topic *</label>
          <input
            value={topic}
            onChange={e => setTopic(e.target.value)}
            placeholder="e.g. pressure relief valve testing, fire water system, work permit"
            className="w-full bg-white border-2 border-gray-200 rounded-lg px-3 py-2.5 text-[15px] text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors"
          />
        </div>
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-bold text-black mb-2">
              Equipment / Area <span className="font-normal text-gray-500">(optional)</span>
            </label>
            <input
              value={area}
              onChange={e => setArea(e.target.value)}
              placeholder="e.g. CDU unit, P-101A, Tank Farm"
              className="w-full bg-white border-2 border-gray-200 rounded-lg px-3 py-2.5 text-[15px] text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={run}
              disabled={!topic.trim() || loading}
              className="flex items-center gap-2 rounded-lg bg-black px-5 py-2.5 text-[15px] font-bold text-white hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? <Spinner size={15} className="text-white" /> : <ShieldCheck size={15} />}
              {loading ? 'Checking…' : 'Check Compliance'}
            </button>
          </div>
        </div>
      </div>

      {/* Presets */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Info size={13} className="text-gray-500" />
          <span className="text-sm font-bold text-gray-600 uppercase tracking-wide">Common compliance checks</span>
        </div>
        <div className="space-y-2">
          {PRESETS.map(p => (
            <button
              key={p.topic}
              onClick={() => { setTopic(p.topic); setArea(p.area) }}
              className="w-full text-left flex items-start gap-3 rounded-xl border border-gray-200 px-4 py-3 hover:border-black hover:bg-gray-50 transition-all group"
            >
              <ShieldCheck size={14} className="text-gray-400 group-hover:text-black shrink-0 mt-0.5 transition-colors" />
              <div>
                <div className="text-sm font-semibold text-black group-hover:underline">{p.topic}</div>
                <div className="text-xs text-gray-500 mt-0.5">{p.area}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <ErrorBanner error={error} onDismiss={() => setError(null)} />

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-4 rounded-xl border-2 border-black bg-black p-5 text-white">
          <Spinner size={20} className="text-white" />
          <div>
            <p className="text-[15px] font-bold">Checking compliance…</p>
            <p className="text-sm text-gray-300 mt-0.5">Retrieving OISD, PESO, Factories Act, DGMS requirements…</p>
          </div>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-4">
          {/* Meta bar */}
          <div className="flex items-center gap-3 px-5 py-3 rounded-xl border-2 border-black bg-black text-white">
            <ShieldCheck size={16} className="text-white shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="text-[15px] font-bold truncate">{topic}</div>
              {area && <div className="text-sm text-gray-300">{area}</div>}
            </div>
            <span className="text-xs text-gray-500 font-mono shrink-0">{result.chunks_retrieved} chunks</span>
          </div>

          {/* Sections */}
          {COMPLIANCE_SECTIONS.map(({ key, accent, icon, defaultOpen }) =>
            sections[key] ? (
              <ComplianceSection
                key={key} title={key} content={sections[key]}
                accent={accent} icon={icon} defaultOpen={defaultOpen}
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
                <span>Compliance Sources ({result.sources.length})</span>
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
