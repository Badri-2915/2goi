/**
 * API Client — Axios instance configured for the 2GOI backend API.
 *
 * Key features:
 * - Base URL is empty string (relative paths) because frontend and backend
 *   are on the same domain (2goi.in) in the single-domain architecture
 * - Automatically attaches Supabase JWT token to every request
 * - Exports clean helper functions for each API endpoint
 *
 * Auth flow:
 * 1. Axios interceptor runs before every request
 * 2. Gets the current Supabase session (if user is logged in)
 * 3. Attaches the access_token as Bearer token in Authorization header
 * 4. Backend verifies this token using Supabase JWKS
 */

import axios from 'axios'
import { supabase } from './supabase'

// API_URL is empty in production (same domain), can be set for local dev
const API_URL = import.meta.env.VITE_API_URL || ''

// Create Axios instance with default JSON headers
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: automatically attach Supabase JWT to every API call
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})

// ---- API Helper Functions ----

/** POST /api/shorten — Create a new short link */
export const shortenUrl = async (url, customAlias = null, expiresIn = null) => {
  const payload = { url }
  if (customAlias) payload.custom_alias = customAlias
  if (expiresIn) payload.expires_in = expiresIn
  const { data } = await api.post('/api/shorten', payload)
  return data
}

/** GET /api/links — Get paginated list of user's links (requires auth) */
export const getUserLinks = async (page = 1, pageSize = 20, sortBy = 'created_at') => {
  const { data } = await api.get('/api/links', {
    params: { page, page_size: pageSize, sort_by: sortBy },
  })
  return data
}

/** GET /api/analytics/{shortCode} — Get click analytics for a link (requires auth) */
export const getLinkAnalytics = async (shortCode, days = 30) => {
  const { data } = await api.get(`/api/analytics/${shortCode}`, {
    params: { days },
  })
  return data
}

/** DELETE /api/links/{linkId} — Soft-delete a link (requires auth) */
export const deleteLink = async (linkId) => {
  await api.delete(`/api/links/${linkId}`)
}

/** GET /api/health — Check if backend, DB, and Redis are running */
export const healthCheck = async () => {
  const { data } = await api.get('/api/health')
  return data
}

export default api
