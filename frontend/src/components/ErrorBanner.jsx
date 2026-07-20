import { AlertTriangle, X } from 'lucide-react'

export default function ErrorBanner({ error, onDismiss }) {
  if (!error) return null
  const msg = error?.response?.data?.detail ?? error?.message ?? 'An unexpected error occurred.'
  return (
    <div className="flex items-start gap-3 rounded-lg border border-red-800 bg-red-900/30 px-4 py-3 text-sm text-red-300">
      <AlertTriangle size={16} className="shrink-0 mt-0.5" />
      <span className="flex-1">{msg}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="shrink-0 opacity-60 hover:opacity-100">
          <X size={14} />
        </button>
      )}
    </div>
  )
}
