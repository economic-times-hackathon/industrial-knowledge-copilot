import { X } from 'lucide-react'

export default function PdfViewerModal({ source, onClose }) {
  if (!source) return null

  // Construct URL based on category
  const getPdfUrl = () => {
    const baseUrl = 'http://localhost:8000'
    let url = ''
    if (source.category === 'uploaded') {
      url = `${baseUrl}/uploads/${source.filename}`
    } else {
      url = `${baseUrl}/corpus/${source.category}/${source.filename}`
    }
    
    // Add search param to highlight text (browser native PDF viewer feature)
    // We use the first 4-5 words of the chunk excerpt (which holds the text)
    if (source.excerpt) {
      const searchTerms = source.excerpt.split(' ').slice(0, 5).join(' ').replace(/['".,]/g, '')
      if (searchTerms) {
        url += `#search="${encodeURIComponent(searchTerms)}"&toolbar=0&navpanes=0&scrollbar=1`
        return url
      }
    }
    return url + '#toolbar=0&navpanes=0&scrollbar=1'
  }

  const pdfUrl = getPdfUrl()

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 md:p-8">
      <div className="bg-surface-800 border border-surface-600 rounded-xl shadow-2xl w-full h-full max-w-6xl flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-surface-600 bg-surface-700">
          <div className="flex items-center gap-3">
            <h3 className="font-medium text-gray-200">
              {source.filename}
            </h3>
            <span className="text-xs bg-surface-600 text-gray-400 px-2 py-1 rounded">
              {source.category}
            </span>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-200 bg-surface-600 hover:bg-surface-500 rounded-lg p-1.5 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Viewer */}
        <div className="flex-1 bg-surface-900 relative">
          <iframe 
            src={pdfUrl}
            className="absolute inset-0 w-full h-full border-0"
            title="PDF Viewer"
          />
        </div>
      </div>
    </div>
  )
}
