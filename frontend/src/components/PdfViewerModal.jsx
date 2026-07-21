import { X } from 'lucide-react'

export default function PdfViewerModal({ source, onClose }) {
  if (!source) return null

  const getPdfUrl = () => {
    const baseUrl = 'http://localhost:8000'
    let url = source.category === 'uploaded'
      ? `${baseUrl}/uploads/${source.filename}`
      : `${baseUrl}/corpus/${source.category}/${source.filename}`

    if (source.excerpt) {
      const searchTerms = source.excerpt.split(' ').slice(0, 5).join(' ').replace(/['".,]/g, '')
      if (searchTerms) {
        url += `#search="${encodeURIComponent(searchTerms)}"&toolbar=0&navpanes=0&scrollbar=1`
        return url
      }
    }
    return url + '#toolbar=0&navpanes=0&scrollbar=1'
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 md:p-8">
      <div className="bg-white border-2 border-black rounded-xl shadow-2xl w-full h-full max-w-6xl flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b-2 border-black bg-black">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold text-white text-sm truncate">
              {source.filename}
            </h3>
            <span className="text-[10px] bg-white text-black px-2 py-0.5 rounded font-bold uppercase tracking-wide">
              {source.category}
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-300 hover:text-white hover:bg-gray-700 rounded-lg p-1.5 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Viewer */}
        <div className="flex-1 bg-gray-100 relative">
          <iframe
            src={getPdfUrl()}
            className="absolute inset-0 w-full h-full border-0"
            title="PDF Viewer"
          />
        </div>
      </div>
    </div>
  )
}
