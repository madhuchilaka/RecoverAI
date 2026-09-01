import axios from 'axios'

const api = axios.create({
  baseURL: process.env.API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 10000,
})

const get = (path, params) => api.get(path, { params }).then(({ data }) => data)

export const getHealth = () => get('/health')
export const getTransactions = (params) => get('/api/transactions', params)
export async function getAllTransactions() {
  const pageSize = 500
  const transactions = []
  let offset = 0
  let page = []
  do {
    page = await getTransactions({ limit: pageSize, offset })
    transactions.push(...(Array.isArray(page) ? page : []))
    offset += pageSize
  } while (page.length === pageSize)
  return transactions
}
export const getTransaction = (id) => get(`/api/transactions/${id}`)
export const getCustomers = (params) => get('/api/customers', params)
export const getCustomer = (id) => get(`/api/customers/${id}`)
export const getRecoverySummary = () => get('/api/recovery/summary')
export const getAtRiskTransactions = (params) => get('/api/recovery/at-risk', params)
export const analyzeTransaction = (id) => api.post(`/api/recovery/analyze/${id}`).then(({ data }) => data)
export const executeRecovery = (id, action) => api.post(`/api/recovery/execute/${id}`, { action }).then(({ data }) => data)
export const getRecoveryHistory = (id) => get(`/api/recovery/transactions/${id}/history`)
export const approveRecovery = (attemptId) => api.post(`/api/recovery/attempts/${attemptId}/approve`).then(({ data }) => data)
export const rejectRecovery = (attemptId) => api.post(`/api/recovery/attempts/${attemptId}/reject`).then(({ data }) => data)
export const getRecoveryAttempts = (params) => get('/api/recovery-attempts', params)
export const getAuditLogs = (params) => get('/api/audit-logs', params)

export function getErrorMessage(error) {
  if (!error?.response) return 'Backend unavailable. Make sure the RecoverAI FastAPI server is running.'
  if (error.response.status === 404) return 'The requested record was not found.'
  if (error.response.status === 400 || error.response.status === 422) return error.response.data?.detail || 'The request could not be validated.'
  return 'Something went wrong while contacting the backend.'
}
