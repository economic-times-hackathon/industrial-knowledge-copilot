export default function ConfidenceBadge({ level }) {
  const map = {
    HIGH:   'bg-green-900/60 text-green-300 border-green-700',
    MEDIUM: 'bg-yellow-900/60 text-yellow-300 border-yellow-700',
    LOW:    'bg-red-900/60 text-red-300 border-red-700',
  }
  const cls = map[level] ?? map.MEDIUM
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs font-mono font-medium ${cls}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${
        level === 'HIGH' ? 'bg-green-400' : level === 'LOW' ? 'bg-red-400' : 'bg-yellow-400'
      }`} />
      {level ?? 'MEDIUM'}
    </span>
  )
}
