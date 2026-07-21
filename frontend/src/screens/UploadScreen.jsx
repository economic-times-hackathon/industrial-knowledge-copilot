import { useState, useCallback, useEffect, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, X, RefreshCw } from 'lucide-react'
import { api } from '../api'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

const STATUS = { idle: 'idle', uploading: 'uploading', processing: 'processing', done: 'done', error: 'error' }

function FileRow({ item, onRemove }) {
  const icon = {
    idle:       <div className="w-2.5 h-2.5 rounded-full bg-gray-300 border border-gray-400" />,
    uploading:  <Spinner size={15} />,
    processing: <Spinner size={15} className="text-gray-600" />,
    done:       <CheckCircle2 size={15} className="text-black" />,
    error:      <AlertTriangle size={15} className="text-black" />,
  }[item.status]

  const bar = {
    idle:       'bg-gray-300',
    uploading:  'bg-black',
    processing: 'bg-gray-600',
    done:       'bg-black',
    error:      'bg-gray-400',
  }[item.status]

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-center gap-3">
        <FileText size={16} className="text-gray-400 shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-sm text-black truncate font-semibold">{item.file.name}</span>
            <span className="text-[11px] text-gray-500 shrink-0 font-mono">
              {(item.file.size / 1024).toFixed(0)} KB
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-gray-100 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${bar}`}
              style={{ width: item.status === 'done' ? '100%' : `${item.progress}%` }}
            />
          </div>
          {item.message && (
            <p className="text-[11px] mt-1.5 text-gray-500 font-medium">{item.message}</p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {icon}
          {(item.status === 'idle' || item.status === 'error') && (
            <button onClick={() => onRemove(item.id)} className="text-gray-400 hover:text-black transition-colors">
              <X size={14} />
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
  const [indexedDocs, setIndexedDocs] = useState([])
  const [showDocs, setShowDocs] = useState(false)
  const [docsLoading, setDocsLoading] = useState(false)
  const prevDoneCount = useRef(0)

  const refreshDocs = useCallback(() => {
    setDocsLoading(true)
    api.listDocuments()
      .then(res => { if (res.data.files) setIndexedDocs(res.data.files) })
      .catch(err => console.error('Failed to list documents', err))
      .finally(() => setDocsLoading(false))
  }, [])

  useEffect(() => { refreshDocs() }, [refreshDocs])

  const doneCount = files.filter(f => f.status === STATUS.done).length
  useEffect(() => {
    if (doneCount > prevDoneCount.current) {
      prevDoneCount.current = doneCount
      const t = setTimeout(refreshDocs, 1500)
      return () => clearTimeout(t)
    }
  }, [doneCount, refreshDocs])

  const onDrop = useCallback(accepted => {
    const newItems = accepted.map(f => ({
      id: crypto.randomUUID(), file: f,
      status: STATUS.idle, progress: 0, message: '',
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
        f.id === id ? { ...f, status: STATUS.processing, progress: 100, message: 'Parsing & indexing…' } : f
      ))
      setTimeout(() => {
        setFiles(prev => prev.map(f =>
          f.id === id ? { ...f, status: STATUS.done, message: 'Indexed — available in search' } : f
        ))
      }, 4000)
      setTimeout(refreshDocs, 32000)
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

  const pending = files.filter(f => f.status === STATUS.idle).length
  const done    = files.filter(f => f.status === STATUS.done).length
  const active  = files.filter(f => [STATUS.uploading, STATUS.processing].includes(f.status)).length

  return (
    <div className="space-y-8">
      {/* Intro */}
      <div>
        <h2 className="text-2xl font-display font-bold text-black">Document Upload</h2>
        <p className="text-base text-gray-600 mt-1">
          Drop PDFs — they are parsed, chunked, and embedded automatically. Available in all screens within ~30 seconds.
        </p>
      </div>

      <ErrorBanner error={globalError} onDismiss={() => setGlobalError(null)} />

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`
          rounded-xl border-2 border-dashed p-12 text-center cursor-pointer transition-all
          ${isDragActive
            ? 'border-black bg-gray-50'
            : 'border-gray-300 hover:border-gray-500 hover:bg-gray-50'}
        `}
      >
        <input {...getInputProps()} />
        <UploadCloud size={40} className={`mx-auto mb-4 ${isDragActive ? 'text-black' : 'text-gray-400'}`} />
        <p className="text-base font-semibold text-black">
          {isDragActive ? 'Drop to add files' : 'Drag & drop PDF files here, or click to select'}
        </p>
        <p className="text-sm text-gray-500 mt-1.5">PDF only · Max 50 MB per file · Multiple files supported</p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600 font-medium">
              {files.length} file{files.length !== 1 ? 's' : ''} selected
              {done > 0 && <span className="ml-2 text-black font-bold">· {done} indexed</span>}
              {active > 0 && <span className="ml-2 text-gray-600">· {active} processing</span>}
            </p>
            {pending > 0 && (
              <button
                onClick={uploadAll}
                className="flex items-center gap-2 rounded-lg bg-black px-5 py-2 text-sm font-bold text-white hover:bg-gray-800 transition-colors"
              >
                <UploadCloud size={14} />
                Upload {pending} file{pending !== 1 ? 's' : ''}
              </button>
            )}
          </div>
          <div className="space-y-2">
            {files.map(item => <FileRow key={item.id} item={item} onRemove={removeFile} />)}
          </div>
        </div>
      )}

      {/* Pipeline steps */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { step: '1', label: 'Parse',  desc: 'PyMuPDF extracts text from every page' },
          { step: '2', label: 'Chunk',  desc: 'Split into 800-char overlapping segments' },
          { step: '3', label: 'Embed',  desc: 'FastEmbed locally → ChromaDB vector index' },
        ].map(({ step, label, desc }) => (
          <div key={step} className="rounded-xl border-2 border-gray-200 bg-white p-5 text-center hover:border-black transition-colors">
            <div className="w-8 h-8 rounded-full bg-black text-white text-sm font-bold flex items-center justify-center mx-auto mb-3">
              {step}
            </div>
            <div className="text-sm font-bold text-black">{label}</div>
            <div className="text-xs text-gray-500 mt-1.5 leading-relaxed">{desc}</div>
          </div>
        ))}
      </div>

      {/* Indexed Documents */}
      <div className="pt-4 border-t-2 border-gray-200">
        <div className="flex gap-2">
          <button
            onClick={() => setShowDocs(!showDocs)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-white border-2 border-gray-200 hover:border-black text-sm font-bold text-black transition-colors flex-1 justify-center"
          >
            <FileText size={16} />
            {showDocs ? 'Hide Indexed Documents' : 'View Indexed Documents'} ({indexedDocs.length})
          </button>
          <button
            onClick={refreshDocs}
            disabled={docsLoading}
            title="Refresh document list"
            className="flex items-center justify-center w-11 rounded-lg bg-white border-2 border-gray-200 hover:border-black text-gray-600 hover:text-black transition-colors disabled:opacity-40"
          >
            <RefreshCw size={15} className={docsLoading ? 'animate-spin' : ''} />
          </button>
        </div>

        {showDocs && (
          <div className="mt-4 space-y-2 max-h-96 overflow-y-auto pr-2">
            {indexedDocs.map((doc, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 rounded-xl border border-gray-200 bg-white hover:border-gray-400 transition-colors">
                <div className="flex items-center gap-3 min-w-0">
                  <FileText size={16} className={doc.source === 'upload' ? 'text-black' : 'text-gray-400'} />
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-black truncate">{doc.name}</p>
                    <p className="text-[11px] text-gray-500 flex gap-2 font-mono mt-0.5">
                      <span>{(doc.size / 1024).toFixed(0)} KB</span>
                      <span>·</span>
                      <span className="uppercase">{doc.category}</span>
                      <span>·</span>
                      <span>{doc.source === 'upload' ? 'User Upload' : 'Base Corpus'}</span>
                    </p>
                  </div>
                </div>
                <CheckCircle2 size={16} className="text-black shrink-0" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
