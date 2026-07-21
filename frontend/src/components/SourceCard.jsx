import { useState } from 'react'
import PdfViewerModal from './PdfViewerModal'

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
  const label = CAT_LABEL[source.category] ?? source.category

  if (compact) {
    return (
      <>
        <button
          onClick={() => setShowViewer(true)}
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded border border-gray-400 text-xs text-gray-700 font-medium hover:bg-gray-100 transition-colors cursor-pointer"
        >
          [{source.index}] {source.filename.replace('.pdf', '')}
        </button>
        {showViewer && <PdfViewerModal source={source} onClose={() => setShowViewer(false)} />}
      </>
    )
  }

  return (
    <>
      <div
        onClick={() => setShowViewer(true)}
        className="bg-white border border-gray-200 rounded-xl p-4 hover:border-black hover:shadow-md cursor-pointer transition-all group"
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <span className="px-2 py-0.5 rounded bg-black text-white text-[10px] font-bold uppercase tracking-wide shrink-0">
              {label}
            </span>
            <span className="font-mono text-xs text-gray-500 shrink-0">
              [{source.index}]
            </span>
          </div>
          <span className="text-xs font-bold text-black shrink-0">
            {(source.relevance_score * 100).toFixed(0)}%
          </span>
        </div>

        {/* Title */}
        <div className="text-sm font-semibold text-black mb-1 line-clamp-1 group-hover:underline">
          {source.filename.replace('.pdf', '').replace(/_/g, ' ')}
        </div>

        {/* Excerpt */}
        <div className="text-xs text-gray-600 line-clamp-2 mb-2 leading-relaxed">
          {source.excerpt || source.description}
        </div>

        {/* Footer hint */}
        <div className="text-[10px] text-gray-400 group-hover:text-gray-700 transition-colors uppercase tracking-wide">
          Click to view · {source.document_type}
        </div>
      </div>
      {showViewer && <PdfViewerModal source={source} onClose={() => setShowViewer(false)} />}
    </>
  )
}
