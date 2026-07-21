import axios from 'axios'

const BASE = '/api'

const client = axios.create({ baseURL: BASE, timeout: 120000 })

export const api = {
  health:      ()           => client.get('/health'),
  stats:       ()           => client.get('/corpus/stats'),
  categories:  ()           => client.get('/corpus/categories'),

  query: (question, category = null, top_k = 8) =>
    client.post('/query', { question, category, top_k }),

  upload: (file, onProgress) => {
    const fd = new FormData()
    fd.append('file', file)
    return client.post('/upload', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: e => onProgress && onProgress(Math.round((e.loaded * 100) / e.total)),
    })
  },

  listDocuments: () => client.get('/documents'),

  asset:       (tag, top_k = 12) => client.get(`/asset/${encodeURIComponent(tag)}`, { params: { top_k } }),

  rca: (equipment_tag, symptom, top_k = 10) =>
    client.post('/maintenance/rca', { equipment_tag, symptom, top_k }),

  compliance: (topic, equipment_or_area = null, top_k = 10) =>
    client.post('/compliance', { topic, equipment_or_area, top_k }),

  notifications: (top_k = 10) => client.get('/notifications', { params: { top_k } }),

  captureKnowledge: (captureData) => client.post('/capture/process', captureData),
}
