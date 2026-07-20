import ReactMarkdown from 'react-markdown'
import ConfidenceBadge from './ConfidenceBadge'
import SourceCard from './SourceCard'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

export default function AnswerPanel({ result, title = 'Answer' }) {
  const [showSources, setShowSources] = useState(true)
  if (!result) return null

  return (
    <div className="rounded-xl border border-surface-600 bg-surface-800 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-surface-600 bg-surface-700/50">
        <span className="text-sm font-medium text-gray-200">{title}</span>
        <div className="flex items-center gap-2">
          <ConfidenceBadge level={result.confidence} />
          <span className="text-xs text-gray-500 font-mono">{result.chunks_retrieved} chunks</span>
        </div>
      </div>

      {/* Answer */}
      <div className="p-4 prose-industrial overflow-x-auto">
        <ReactMarkdown>{result.answer}</ReactMarkdown>
      </div>

      {/* Sources toggle */}
      {result.sources?.length > 0 && (
        <div className="border-t border-surface-600">
          <button
            onClick={() => setShowSources(s => !s)}
            className="w-full flex items-center justify-between px-4 py-2 text-xs text-gray-400 hover:text-gray-200 hover:bg-surface-700/30 transition-colors"
          >
            <span>Sources ({result.sources.length})</span>
            {showSources ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          {showSources && (
            <div className="px-4 pb-4 grid grid-cols-1 sm:grid-cols-2 gap-2">
              {result.sources.map(s => <SourceCard key={s.index} source={s} />)}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
