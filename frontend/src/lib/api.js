import axios from 'axios'
import { supabase } from './supabase'

const API_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach auth token to every request if available
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})

// API methods
export const shortenUrl = async (url, customAlias = null, expiresIn = null) => {
  const payload = { url }
  if (customAlias) payload.custom_alias = customAlias
  if (expiresIn) payload.expires_in = expiresIn
  const { data } = await api.post('/api/shorten', payload)
  return data
}

export const getUserLinks = async (page = 1, pageSize = 20, sortBy = 'created_at') => {
  const { data } = await api.get('/api/links', {
    params: { page, page_size: pageSize, sort_by: sortBy },
  })
  return data
}

export const getLinkAnalytics = async (shortCode, days = 30) => {
  const { data } = await api.get(`/api/analytics/${shortCode}`, {
    params: { days },
  })
  return data
}

export const deleteLink = async (linkId) => {
  await api.delete(`/api/links/${linkId}`)
}

export const healthCheck = async () => {
  const { data } = await api.get('/api/health')
  return data
}

export default api
