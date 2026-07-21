export default function ConfidenceBadge({ level }) {
  const map = {
    HIGH:   'bg-black text-white border-black',
    MEDIUM: 'bg-gray-700 text-white border-gray-700',
    LOW:    'bg-gray-300 text-gray-900 border-gray-400',
  }
  const cls = map[level] ?? map.MEDIUM

  const dotColor =
    level === 'HIGH'   ? 'bg-white' :
    level === 'LOW'    ? 'bg-gray-600' :
                         'bg-gray-200'

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded border text-[11px] font-mono font-bold tracking-widest uppercase ${cls}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor} animate-pulse`} />
      {level ?? 'MEDIUM'}
    </span>
  )
}
