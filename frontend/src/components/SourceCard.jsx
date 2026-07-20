const CAT_COLOR = {
  pids:              'bg-blue-900/50 text-blue-300 border-blue-800',
  oem_manuals:       'bg-purple-900/50 text-purple-300 border-purple-800',
  regulatory:        'bg-orange-900/50 text-orange-300 border-orange-800',
  incident_reports:  'bg-red-900/50 text-red-300 border-red-800',
  maintenance_data:  'bg-teal-900/50 text-teal-300 border-teal-800',
  uploaded:          'bg-gray-700/50 text-gray-300 border-gray-600',
}

const CAT_LABEL = {
  pids:             'P&ID',
  oem_manuals:      'OEM Manual',
  regulatory:       'Regulatory',
  incident_reports: 'Incident',
  maintenance_data: 'Maintenance',
  uploaded:         'Uploaded',
}

export default function SourceCard({ source, compact = false }) {
  const cls = CAT_COLOR[source.category] ?? CAT_COLOR.uploaded
  const label = CAT_LABEL[source.category] ?? source.category

  if (compact) {
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs ${cls}`}>
        [{source.index}] {source.filename.replace('.pdf', '')}
      </span>
    )
  }

  return (
    <div className={`rounded-lg border p-3 text-xs space-y-1 ${cls}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono font-semibold">[{source.index}]</span>
          <span className="font-medium truncate max-w-[200px]" title={source.filename}>
            {source.filename.replace('.pdf', '')}
          </span>
        </div>
        <span className="shrink-0 font-mono text-[10px] opacity-70">
          {(source.relevance_score * 100).toFixed(0)}%
        </span>
      </div>
      <div className="opacity-80 line-clamp-2">{source.description}</div>
      {source.source_url && source.source_url !== 'user-upload' && (
        <a
          href={source.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="underline opacity-60 hover:opacity-100 truncate block"
        >
          {source.source_url.replace('https://', '').substring(0, 50)}…
        </a>
      )}
    </div>
  )
}
