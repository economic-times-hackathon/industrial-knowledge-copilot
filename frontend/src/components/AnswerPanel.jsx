import ReactMarkdown from 'react-markdown'
import SourceCard from './SourceCard'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

export default function AnswerPanel({ result, title = 'Answer' }) {
  const [showSources, setShowSources] = useState(true)
  if (!result) return null

  return (
    <div className="rounded-xl border-2 border-black bg-white overflow-hidden shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-gray-200 bg-gray-50">
        <span className="text-sm font-bold text-black tracking-wide">{title}</span>
        <span className="text-xs text-gray-500 font-mono">{result.chunks_retrieved} chunks</span>
      </div>

      {/* Answer */}
      <div className="p-5 prose-industrial overflow-x-auto">
        <ReactMarkdown>{result.answer}</ReactMarkdown>
      </div>

      {/* Sources toggle */}
      {result.sources?.length > 0 && (
        <div className="border-t border-gray-200">
          <button
            onClick={() => setShowSources(s => !s)}
            className="w-full flex items-center justify-between px-5 py-3 text-xs font-semibold text-black hover:bg-gray-50 transition-colors uppercase tracking-wide"
          >
            <span>Sources ({result.sources.length})</span>
            {showSources ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          {showSources && (
            <div className="px-5 pb-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
              {result.sources.map(s => <SourceCard key={s.index} source={s} />)}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
