import { AlertTriangle, X } from 'lucide-react'

export default function ErrorBanner({ error, onDismiss }) {
  if (!error) return null
  const msg = error?.response?.data?.detail ?? error?.message ?? 'An unexpected error occurred.'
  return (
    <div className="flex items-start gap-3 rounded-lg border-2 border-black bg-gray-100 px-4 py-3 text-sm text-black">
      <AlertTriangle size={16} className="shrink-0 mt-0.5 text-black" />
      <span className="flex-1 font-medium">{msg}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="shrink-0 opacity-50 hover:opacity-100 transition-opacity">
          <X size={14} />
        </button>
      )}
    </div>
  )
}
