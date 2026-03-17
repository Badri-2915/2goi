/**
 * Supabase Client — Initializes the Supabase JS client for frontend authentication.
 *
 * Environment variables (set at build time by Vite):
 * - VITE_SUPABASE_URL: The Supabase project URL
 * - VITE_SUPABASE_ANON_KEY: The public anonymous key (safe to expose in frontend)
 *
 * The anon key is NOT a secret — it only allows RLS-restricted operations.
 * The actual secret (service_role key) is only used on the backend.
 *
 * This client is used by AuthContext.jsx for login, signup, and Google OAuth.
 */

import { createClient } from '@supabase/supabase-js'

// Read Supabase credentials from Vite environment variables
// These are embedded at build time (not runtime) by Vite's import.meta.env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Warn if credentials are missing (app will still load but auth won't work)
if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Missing Supabase environment variables. Auth will not work.')
}

// Create and export the Supabase client instance (shared across the app)
export const supabase = createClient(
  supabaseUrl || 'https://placeholder.supabase.co',
  supabaseAnonKey || 'placeholder-key'
)
