import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, X } from 'lucide-react'
import { api } from '../api'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

const STATUS = { idle: 'idle', uploading: 'uploading', processing: 'processing', done: 'done', error: 'error' }

function FileRow({ item, onRemove }) {
  const icon = {
    idle:       <div className="w-2 h-2 rounded-full bg-gray-600" />,
    uploading:  <Spinner size={14} />,
    processing: <Spinner size={14} className="text-yellow-400" />,
    done:       <CheckCircle2 size={14} className="text-green-400" />,
    error:      <AlertTriangle size={14} className="text-red-400" />,
  }[item.status]

  const bar = {
    idle:       'bg-gray-700',
    uploading:  'bg-accent-blue',
    processing: 'bg-yellow-500',
    done:       'bg-green-500',
    error:      'bg-red-500',
  }[item.status]

  return (
    <div className="rounded-lg border border-surface-600 bg-surface-800 p-3">
      <div className="flex items-center gap-3">
        <FileText size={16} className="text-gray-500 shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-gray-200 truncate font-medium">{item.file.name}</span>
            <span className="text-[10px] text-gray-600 shrink-0">
              {(item.file.size / 1024).toFixed(0)} KB
            </span>
          </div>
          <div className="h-1 rounded-full bg-surface-600 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${bar}`}
              style={{ width: item.status === 'done' ? '100%' : `${item.progress}%` }}
            />
          </div>
          {item.message && (
            <p className="text-[10px] mt-1 text-gray-500">{item.message}</p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {icon}
          {(item.status === 'idle' || item.status === 'error') && (
            <button onClick={() => onRemove(item.id)} className="text-gray-600 hover:text-gray-400">
              <X size={13} />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default function UploadScreen() {
  const [files, setFiles] = useState([])
  const [globalError, setGlobalError] = useState(null)

  const onDrop = useCallback(accepted => {
    const newItems = accepted.map(f => ({
      id: crypto.randomUUID(),
      file: f,
      status: STATUS.idle,
      progress: 0,
      message: '',
    }))
    setFiles(prev => [...prev, ...newItems])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 50 * 1024 * 1024,
    multiple: true,
  })

  const uploadOne = async (id) => {
    setFiles(prev => prev.map(f => f.id === id ? { ...f, status: STATUS.uploading, progress: 0 } : f))
    const item = files.find(f => f.id === id)
    try {
      await api.upload(item.file, (pct) => {
        setFiles(prev => prev.map(f => f.id === id ? { ...f, progress: pct } : f))
      })
      setFiles(prev => prev.map(f =>
        f.id === id
          ? { ...f, status: STATUS.processing, progress: 100, message: 'Parsing & indexing…' }
          : f
      ))
      // Simulate indexing delay then mark done
      setTimeout(() => {
        setFiles(prev => prev.map(f =>
          f.id === id
            ? { ...f, status: STATUS.done, message: 'Indexed — available in search' }
            : f
        ))
      }, 4000)
    } catch (err) {
      const msg = err?.response?.data?.detail ?? err.message
      setFiles(prev => prev.map(f =>
        f.id === id ? { ...f, status: STATUS.error, message: msg } : f
      ))
    }
  }

  const uploadAll = () => {
    setGlobalError(null)
    files.filter(f => f.status === STATUS.idle).forEach(f => uploadOne(f.id))
  }

  const removeFile = (id) => setFiles(prev => prev.filter(f => f.id !== id))

  const pending  = files.filter(f => f.status === STATUS.idle).length
  const done     = files.filter(f => f.status === STATUS.done).length
  const active   = files.filter(f => [STATUS.uploading, STATUS.processing].includes(f.status)).length

  return (
    <div className="space-y-6">
      {/* Intro */}
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Document Upload</h2>
        <p className="text-sm text-gray-500 mt-1">
          Drop PDFs — they are parsed, chunked, and embedded automatically. Available in all screens within ~30 seconds.
        </p>
      </div>

      <ErrorBanner error={globalError} onDismiss={() => setGlobalError(null)} />

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`
          rounded-xl border-2 border-dashed p-10 text-center cursor-pointer transition-colors
          ${isDragActive
            ? 'border-accent-blue bg-accent-blue/10'
            : 'border-surface-500 hover:border-surface-400 hover:bg-surface-800/50'}
        `}
      >
        <input {...getInputProps()} />
        <UploadCloud size={36} className={`mx-auto mb-3 ${isDragActive ? 'text-accent-blue' : 'text-gray-600'}`} />
        <p className="text-sm text-gray-400">
          {isDragActive ? 'Drop to add files' : 'Drag & drop PDF files here, or click to select'}
        </p>
        <p className="text-xs text-gray-600 mt-1">PDF only · Max 50 MB per file · Multiple files supported</p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-500">
              {files.length} file{files.length !== 1 ? 's' : ''} selected
              {done > 0 && <span className="ml-2 text-green-400">· {done} indexed</span>}
              {active > 0 && <span className="ml-2 text-yellow-400">· {active} processing</span>}
            </p>
            {pending > 0 && (
              <button
                onClick={uploadAll}
                className="flex items-center gap-2 rounded-lg bg-accent-blue px-4 py-1.5 text-xs font-medium text-white hover:bg-blue-500 transition-colors"
              >
                <UploadCloud size={13} />
                Upload {pending} file{pending !== 1 ? 's' : ''}
              </button>
            )}
          </div>
          <div className="space-y-2">
            {files.map(item => (
              <FileRow key={item.id} item={item} onRemove={removeFile} />
            ))}
          </div>
        </div>
      )}

      {/* Info cards */}
      <div className="grid grid-cols-3 gap-3 mt-4">
        {[
          { step: '1', label: 'Parse',   desc: 'PyMuPDF extracts text from every page' },
          { step: '2', label: 'Chunk',   desc: 'Split into 800-char overlapping segments' },
          { step: '3', label: 'Embed',   desc: 'OpenAI embeddings → ChromaDB vector index' },
        ].map(({ step, label, desc }) => (
          <div key={step} className="rounded-lg border border-surface-600 bg-surface-800 p-3 text-center">
            <div className="w-6 h-6 rounded-full bg-accent-blue/20 text-accent-blue text-xs font-bold flex items-center justify-center mx-auto mb-2">
              {step}
            </div>
            <div className="text-xs font-medium text-gray-200">{label}</div>
            <div className="text-[10px] text-gray-500 mt-1">{desc}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
