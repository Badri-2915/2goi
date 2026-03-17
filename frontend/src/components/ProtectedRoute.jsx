/**
 * ProtectedRoute — Route guard that requires authentication.
 *
 * Wraps any page that should only be visible to logged-in users.
 * - If loading: shows a spinner (waiting for auth check)
 * - If not logged in: redirects to /login
 * - If logged in: renders the child component
 *
 * Usage in App.jsx:
 *   <ProtectedRoute><DashboardPage /></ProtectedRoute>
 */

import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-400"></div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}
