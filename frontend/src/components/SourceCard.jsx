import { useState } from 'react'
import PdfViewerModal from './PdfViewerModal'

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
  const [showViewer, setShowViewer] = useState(false)

  const cls = CAT_COLOR[source.category] ?? CAT_COLOR.uploaded
  const label = CAT_LABEL[source.category] ?? source.category

  if (compact) {
    return (
      <>
        <button 
          onClick={() => setShowViewer(true)}
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs hover:opacity-80 transition-opacity cursor-pointer ${cls}`}
        >
          [{source.index}] {source.filename.replace('.pdf', '')}
        </button>
        {showViewer && <PdfViewerModal source={source} onClose={() => setShowViewer(false)} />}
      </>
    )
  }

  // Google-style source card
  return (
    <>
      <div 
        onClick={() => setShowViewer(true)}
        className="bg-surface-800 border border-surface-600 rounded-lg p-3 hover:border-accent-blue/50 hover:bg-surface-700 cursor-pointer transition-all group max-w-full"
      >
        {/* Header with category badge and relevance */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <span className={`px-2 py-0.5 rounded text-[10px] font-medium shrink-0 ${cls}`}>
              {label}
            </span>
            <span className="font-mono text-xs text-gray-400 shrink-0">
              [{source.index}]
            </span>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            <span className="text-xs text-accent-blue font-medium">
              {(source.relevance_score * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Title */}
        <div className="text-sm font-medium text-gray-200 mb-1 line-clamp-1 group-hover:text-accent-blue transition-colors">
          {source.filename.replace('.pdf', '').replace(/_/g, ' ')}
        </div>

        {/* Description/excerpt */}
        <div className="text-xs text-gray-400 line-clamp-2 mb-2">
          {source.excerpt || source.description}
        </div>

        {/* Click hint */}
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-gray-600 group-hover:text-gray-400 transition-colors">
            Click to view • {source.document_type}
          </span>
        </div>
      </div>
      {showViewer && <PdfViewerModal source={source} onClose={() => setShowViewer(false)} />}
    </>
  )
}
