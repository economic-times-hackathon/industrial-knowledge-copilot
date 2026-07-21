import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Filter, RotateCcw } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'

import SourceCard from '../components/SourceCard'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

const CATEGORIES = [
  { value: '',                 label: 'All categories' },
  { value: 'pids',             label: 'P&IDs' },
  { value: 'oem_manuals',      label: 'OEM Manuals' },
  { value: 'regulatory',       label: 'Regulatory' },
  { value: 'incident_reports', label: 'Incidents' },
  { value: 'maintenance_data', label: 'Maintenance' },
  { value: 'uploaded',         label: 'Uploaded Docs' },
  { value: 'expert_knowledge', label: 'Expert Knowledge' },
]

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full bg-black border border-black flex items-center justify-center mt-0.5">
          <Bot size={14} className="text-white" />
        </div>
      )}

      <div className={`max-w-[85%] space-y-3 flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Bubble */}
        <div className={`rounded-xl px-4 py-3 text-[15px] max-w-full shadow-sm ${
          isUser
            ? 'bg-black text-white rounded-br-sm'
            : 'bg-white border-2 border-gray-200 text-gray-900 rounded-bl-sm'
        }`}>
          {isUser
            ? <p className="break-words leading-relaxed">{msg.content}</p>
            : <div className="prose-industrial max-w-none"><ReactMarkdown>{msg.content}</ReactMarkdown></div>
          }
        </div>

        {/* Metadata */}
        {!isUser && msg.chunks && (
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-gray-500 font-mono">{msg.chunks} chunks used</span>
          </div>
        )}

        {/* Source chips */}
        {!isUser && msg.sources?.length > 0 && (
          <div className="grid gap-2 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 max-w-full">
            {msg.sources.slice(0, 3).map(s => <SourceCard key={s.index} source={s} />)}
            {msg.sources.length > 3 && (
              <div className="col-span-full">
                <button className="text-xs text-black font-semibold underline underline-offset-2 hover:text-gray-600 transition-colors">
                  +{msg.sources.length - 3} more sources
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full bg-gray-200 border border-gray-300 flex items-center justify-center mt-0.5">
          <User size={14} className="text-gray-700" />
        </div>
      )}
    </div>
  )
}

export default function CopilotScreen() {
  const [messages, setMessages]   = useState([])
  const [input, setInput]         = useState('')
  const [category, setCategory]   = useState('')
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [sampleQuestions, setSampleQuestions] = useState([
    'What is process safety management?',
    'How do you perform pump maintenance?',
    'What are the safety requirements for confined spaces?',
    'Tell me about pressure relief valve testing',
    'What should I know about emergency procedures?',
  ])
  const bottomRef = useRef(null)
  const inputRef  = useRef(null)

  useEffect(() => {
    const loadSampleQuestions = async () => {
      try {
        const statsResponse = await api.stats()
        const categories = Object.keys(statsResponse.chunks_by_category || {})
        if (categories.length > 0) {
          const q = []
          if (categories.includes('incident_reports'))  q.push('What caused the BP Texas City explosion?')
          if (categories.includes('maintenance_data'))  q.push('How do you perform pump bearing maintenance?')
          if (categories.includes('regulatory'))        q.push('What are OISD safety requirements?')
          if (categories.includes('oem_manuals'))       q.push('How do you install centrifugal pumps?')
          if (categories.includes('uploaded'))          q.push('What information is in the uploaded documents?')
          if (q.length > 0) setSampleQuestions(q)
        }
      } catch {}
    }
    loadSampleQuestions()
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = async (question) => {
    const q = (question ?? input).trim()
    if (!q || loading) return
    setInput('')
    setError(null)
    setMessages(prev => [...prev, { role: 'user', content: q, id: Date.now() }])
    setLoading(true)

    try {
      const res = await api.query(q, category || null)
      const { answer, confidence, sources, chunks_retrieved } = res.data
      setMessages(prev => [...prev, {
        role: 'assistant', content: answer, confidence,
        sources, chunks: chunks_retrieved, id: Date.now() + 1,
      }])
    } catch (err) {
      let errorMsg = 'Failed to get response'
      if (err.response?.status === 500)         errorMsg = 'Database error — try uploading documents first.'
      else if (err.response?.data?.detail)      errorMsg = err.response.data.detail
      setError({ message: errorMsg })
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const clear = () => { setMessages([]); setError(null) }

  return (
    <div className="flex flex-col h-[calc(100vh-88px)]">
      {/* Toolbar */}
      <div className="flex items-center gap-3 pb-4 border-b-2 border-gray-200 mb-5">
        <Filter size={14} className="text-gray-500 shrink-0" />
        <select
          value={category}
          onChange={e => setCategory(e.target.value)}
          className="text-sm bg-white border border-gray-300 rounded-lg px-3 py-1.5 text-black focus:outline-none focus:border-black transition-colors flex-1 sm:flex-initial font-medium"
        >
          {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
        {messages.length > 0 && (
          <button
            onClick={clear}
            className="ml-auto flex items-center gap-1.5 text-sm text-gray-500 hover:text-black transition-colors font-medium shrink-0"
          >
            <RotateCcw size={13} />
            <span className="hidden sm:inline">Clear chat</span>
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-5 pr-1">
        {messages.length === 0 && (
          <div className="space-y-5 py-6">
            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-black flex items-center justify-center mx-auto mb-4">
                <Bot size={28} className="text-white" />
              </div>
              <p className="text-base font-semibold text-black">Ask anything about your industrial knowledge base</p>
              <p className="text-sm text-gray-500 mt-1">102 documents · 13,779 indexed chunks · GPT-4o</p>
            </div>
            <div className="grid gap-2 max-w-xl mx-auto">
              {sampleQuestions.map(s => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-left text-sm text-gray-700 font-medium border border-gray-200 rounded-xl px-4 py-3 hover:border-black hover:bg-white hover:shadow-sm transition-all"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map(msg => <Message key={msg.id} msg={msg} />)}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center shrink-0">
              <Bot size={14} className="text-white" />
            </div>
            <div className="bg-white border-2 border-gray-200 rounded-xl rounded-bl-sm px-4 py-3 shadow-sm">
              <div className="flex items-center gap-2 text-sm text-gray-500 font-medium">
                <Spinner size={14} /> Retrieving and generating…
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && <ErrorBanner error={error} onDismiss={() => setError(null)} className="mt-3" />}

      {/* Input */}
      <div className="mt-4 pt-4 border-t-2 border-gray-200">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
            placeholder="Ask a question about your industrial documents…"
            className="flex-1 bg-white border-2 border-gray-200 rounded-xl px-4 py-3 text-[15px] text-black placeholder-gray-400 focus:outline-none focus:border-black transition-colors font-medium"
          />
          <button
            onClick={() => send()}
            disabled={!input.trim() || loading}
            className="shrink-0 w-11 h-11 rounded-xl bg-black flex items-center justify-center text-white hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? <Spinner size={16} className="text-white" /> : <Send size={16} />}
          </button>
        </div>
        <p className="text-[11px] text-gray-400 mt-1.5 pl-1 hidden sm:block font-mono">
          Enter to send · Shift+Enter for newline
        </p>
      </div>
    </div>
  )
}
