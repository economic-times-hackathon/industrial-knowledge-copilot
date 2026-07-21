export default function ConfidenceBadge({ level }) {
  const map = {
    HIGH:   'bg-accent-emerald/10 text-accent-emerald border-accent-emerald/30 shadow-[0_0_10px_rgba(5,150,105,0.1)]',
    MEDIUM: 'bg-accent-amber/10 text-accent-amber border-accent-amber/30 shadow-[0_0_10px_rgba(217,119,6,0.1)]',
    LOW:    'bg-accent-red/10 text-accent-red border-accent-red/30 shadow-[0_0_10px_rgba(225,29,72,0.1)]',
  }
  const cls = map[level] ?? map.MEDIUM
  
  const dotColor = level === 'HIGH' ? 'bg-accent-emerald shadow-[0_0_8px_rgba(5,150,105,0.6)]' 
                 : level === 'LOW' ? 'bg-accent-red shadow-[0_0_8px_rgba(225,29,72,0.6)]' 
                 : 'bg-accent-amber shadow-[0_0_8px_rgba(217,119,6,0.6)]'

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-[11px] font-mono font-medium tracking-wider ${cls}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor} animate-pulse`} />
      {level ?? 'MEDIUM'}
    </span>
  )
}
