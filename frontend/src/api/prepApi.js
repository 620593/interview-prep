import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120_000, // 2 min — LLM pipeline can take 30-90 s
  headers: { 'Content-Type': 'application/json' },
})

/**
 * POST /prep/generate
 * @param {string} query  — free-text query (role, company, skills, goals)
 * @returns {Promise<{ session_id, company, role, timeline_days, html_output }>}
 */
export const generatePrep = (query) =>
  api.post('/prep/generate', { query }).then((r) => r.data)

/**
 * GET /prep/:sessionId
 * @param {string} sessionId
 * @returns {Promise<object>} full session document
 */
export const getPrep = (sessionId) =>
  api.get(`/prep/${sessionId}`).then((r) => r.data)

/**
 * GET /progress/:sessionId
 * @param {string} sessionId
 * @returns {Promise<{ progress: Record<string, boolean> }>}
 */
export const getProgress = (sessionId) =>
  api.get(`/progress/${sessionId}`).then((r) => r.data)

/**
 * PATCH /progress/:sessionId
 * @param {string} sessionId
 * @param {Record<string, boolean>} progress
 * @returns {Promise<{ status: string }>}
 */
export const saveProgress = (sessionId, progress) =>
  api.patch(`/progress/${sessionId}`, { progress }).then((r) => r.data)

export default api
