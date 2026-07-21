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
]

const STARTERS = [
  'What is process safety management?',
  'How do you perform pump maintenance?',
  'What are the safety requirements for confined spaces?',
  'Tell me about pressure relief valve testing',
  'What should I know about emergency procedures?',
]

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="shrink-0 w-7 h-7 rounded-full bg-accent-blue/20 border border-accent-blue/30 flex items-center justify-center mt-0.5">
          <Bot size={13} className="text-accent-blue" />
        </div>
      )}

      <div className={`max-w-[85%] space-y-3 ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        {/* Bubble */}
        <div className={`rounded-xl px-3 py-2 sm:px-4 sm:py-3 text-sm max-w-full ${
          isUser
            ? 'bg-accent-blue/20 border border-accent-blue/30 text-gray-100 rounded-br-sm'
            : 'bg-surface-700 border border-surface-600 text-gray-200 rounded-bl-sm'
        }`}>
          {isUser
            ? <p className="break-words">{msg.content}</p>
            : <div className="prose-industrial prose-sm max-w-none"><ReactMarkdown>{msg.content}</ReactMarkdown></div>
          }
        </div>

        {/* Metadata row for assistant messages */}
        {!isUser && msg.chunks && (
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[10px] text-gray-600 font-mono">{msg.chunks} chunks used</span>
          </div>
        )}

        {/* Source chips */}
        {!isUser && msg.sources?.length > 0 && (
          <div className="grid gap-2 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 max-w-full">
            {msg.sources.slice(0, 3).map(s => <SourceCard key={s.index} source={s} />)}
            {msg.sources.length > 3 && (
              <div className="col-span-full">
                <button className="text-xs text-accent-blue hover:underline">
                  +{msg.sources.length - 3} more sources
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="shrink-0 w-7 h-7 rounded-full bg-surface-600 border border-surface-500 flex items-center justify-center mt-0.5">
          <User size={13} className="text-gray-400" />
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
  const bottomRef = useRef(null)
  const inputRef  = useRef(null)

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
      console.error('Query error:', err);
      let errorMsg = 'Failed to get response';
      
      if (err.response?.status === 500) {
        errorMsg = 'Database error - try uploading documents first or check if ChromaDB is properly initialized';
      } else if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      }
      
      setError({ message: errorMsg });
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const clear = () => { setMessages([]); setError(null) }

  return (
    <div className="flex flex-col h-[calc(100vh-88px)] px-2 sm:px-4">
      {/* Toolbar */}
      <div className="flex items-center gap-2 sm:gap-3 pb-3 border-b border-surface-600 mb-4">
        <Filter size={14} className="text-gray-500 shrink-0" />
        <select
          value={category}
          onChange={e => setCategory(e.target.value)}
          className="text-xs bg-surface-700 border border-surface-500 rounded-lg px-2 py-1.5 sm:px-3 text-gray-300 focus:outline-none focus:border-accent-blue flex-1 sm:flex-initial"
        >
          {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
        {messages.length > 0 && (
          <button
            onClick={clear}
            className="ml-auto flex items-center gap-1 text-xs text-gray-600 hover:text-gray-300 transition-colors shrink-0"
          >
            <RotateCcw size={12} /> <span className="hidden sm:inline">Clear</span>
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 sm:space-y-5 pr-1">
        {messages.length === 0 && (
          <div className="space-y-4 py-4">
            <div className="text-center">
              <Bot size={36} className="mx-auto text-gray-700 mb-3" />
              <p className="text-sm text-gray-500 px-4">Ask anything about your industrial knowledge base.</p>
              <p className="text-xs text-gray-700 mt-1 px-4">102 documents • 13,779 indexed chunks • GPT-4o</p>
            </div>
            <div className="grid gap-2 px-4">
              {STARTERS.map(s => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-left text-xs text-gray-400 border border-surface-600 rounded-lg px-3 py-2 hover:border-accent-blue/50 hover:text-gray-200 hover:bg-surface-800 transition-all"
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
            <div className="w-7 h-7 rounded-full bg-accent-blue/20 border border-accent-blue/30 flex items-center justify-center">
              <Bot size={13} className="text-accent-blue" />
            </div>
            <div className="bg-surface-700 border border-surface-600 rounded-xl rounded-bl-sm px-4 py-3">
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Spinner size={12} /> Retrieving and generating…
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Error */}
      {error && <ErrorBanner error={error} onDismiss={() => setError(null)} className="mt-3" />}

      {/* Input */}
      <div className="mt-4 pt-4 border-t border-surface-600 px-2 sm:px-0">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
            placeholder="Ask a question about your industrial documents…"
            className="flex-1 bg-surface-700 border border-surface-500 rounded-xl px-3 py-2.5 sm:px-4 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-accent-blue transition-colors"
          />
          <button
            onClick={() => send()}
            disabled={!input.trim() || loading}
            className="shrink-0 w-10 h-10 rounded-xl bg-accent-blue flex items-center justify-center text-white hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? <Spinner size={16} className="text-white" /> : <Send size={16} />}
          </button>
        </div>
        <p className="text-[10px] text-gray-700 mt-1.5 pl-1 hidden sm:block">Enter to send · Shift+Enter for newline</p>
      </div>
    </div>
  )
}
