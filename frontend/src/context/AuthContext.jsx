/**
 * AuthContext — React context for managing authentication state.
 *
 * Provides:
 * - user: The currently logged-in user object (or null)
 * - session: The current Supabase session with JWT tokens
 * - loading: Whether the auth state is still being loaded
 * - signUp: Create a new account with email/password
 * - signIn: Log in with email/password
 * - signInWithGoogle: Log in with Google OAuth (redirects to Google)
 * - signOut: Log out and clear session
 *
 * How it works:
 * 1. On mount, checks for existing session (e.g., from localStorage)
 * 2. Subscribes to auth state changes (login, logout, token refresh)
 * 3. Updates user/session state whenever auth state changes
 * 4. All child components can access auth via useAuth() hook
 *
 * Usage in any component:
 *   const { user, signIn, signOut } = useAuth()
 */

import { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'

// Create the context with empty default value
const AuthContext = createContext({})

// Custom hook for easy access to auth context
export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)      // Current user object
  const [session, setSession] = useState(null) // Current Supabase session (has JWT)
  const [loading, setLoading] = useState(true)  // True until initial auth check completes

  useEffect(() => {
    // Check if there's an existing session (e.g., page refresh)
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Subscribe to auth state changes (login, logout, token refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    // Cleanup subscription on unmount
    return () => subscription.unsubscribe()
  }, [])

  /** Create a new account with email and password */
  const signUp = async (email, password) => {
    const { data, error } = await supabase.auth.signUp({ email, password })
    if (error) throw error
    // Supabase returns a fake user with empty identities if the email already exists
    if (data?.user?.identities?.length === 0) {
      throw new Error('An account with this email already exists. Please sign in instead.')
    }
    return data
  }

  /** Log in with email and password */
  const signIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    return data
  }

  /** Log in with Google OAuth (redirects to Google's login page) */
  const signInWithGoogle = async () => {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/dashboard`, // Redirect back to dashboard after Google login
      },
    })
    if (error) throw error
    return data
  }

  /** Log out and clear the session */
  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }

  // All auth-related values exposed to child components
  const value = {
    user,
    session,
    loading,
    signUp,
    signIn,
    signInWithGoogle,
    signOut,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
