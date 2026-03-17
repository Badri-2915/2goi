/**
 * Navbar — Top navigation bar shown on every page.
 *
 * Shows different content based on auth state:
 * - Logged out: Home link + Sign In button
 * - Logged in: Home link + Dashboard link + Sign Out button
 *
 * Uses Lucide icons and TailwindCSS for styling.
 */

import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Link2, LogOut, LayoutDashboard, Home } from 'lucide-react'

export default function Navbar() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  const handleSignOut = async () => {
    await signOut()
    navigate('/')
  }

  return (
    <nav className="bg-slate-900/80 backdrop-blur-md border-b border-slate-700/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 text-white font-bold text-xl no-underline">
            <Link2 className="w-6 h-6 text-indigo-400" />
            <span className="bg-gradient-to-r from-indigo-400 to-blue-400 bg-clip-text text-transparent">
              2GOI
            </span>
          </Link>

          <div className="flex items-center gap-3">
            <Link
              to="/"
              className="text-slate-300 hover:text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors no-underline flex items-center gap-1.5"
            >
              <Home className="w-4 h-4" />
              Home
            </Link>

            {user ? (
              <>
                <Link
                  to="/dashboard"
                  className="text-slate-300 hover:text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors no-underline flex items-center gap-1.5"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Dashboard
                </Link>
                <button
                  onClick={handleSignOut}
                  className="text-slate-400 hover:text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 bg-transparent border-none cursor-pointer"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors no-underline"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
