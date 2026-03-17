/**
 * App.jsx — Root component of the React application.
 *
 * This component sets up:
 * 1. AuthProvider — wraps the entire app with authentication context
 * 2. React Router — client-side routing for all pages
 * 3. Navbar — persistent navigation bar across all pages
 * 4. ProtectedRoute — guards Dashboard and Analytics pages (requires login)
 * 5. Toaster — toast notifications (success, error messages)
 *
 * Routes:
 *   /                      → HomePage (URL shortener form + features)
 *   /login                 → LoginPage (email/password + Google OAuth)
 *   /signup                → SignupPage (create new account)
 *   /dashboard             → DashboardPage (list user's links) [protected]
 *   /analytics/:shortCode  → AnalyticsPage (click analytics)   [protected]
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import AnalyticsPage from './pages/AnalyticsPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'

function App() {
  return (
    // AuthProvider makes user/session available to all child components
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-slate-950">
          {/* Navbar is shown on every page */}
          <Navbar />
          <Routes>
            {/* Public routes — anyone can access */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />

            {/* Protected routes — redirect to /login if not authenticated */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics/:shortCode"
              element={
                <ProtectedRoute>
                  <AnalyticsPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
        {/* Toast notifications styled to match the dark theme */}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#1e293b',
              color: '#e2e8f0',
              border: '1px solid #334155',
            },
          }}
        />
      </Router>
    </AuthProvider>
  )
}

export default App
