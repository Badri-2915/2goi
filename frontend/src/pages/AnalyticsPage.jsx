import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getLinkAnalytics } from '../lib/api'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { ArrowLeft, MousePointerClick, Globe, Monitor, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

const COLORS = ['#8b5cf6', '#06b6d4', '#f59e0b', '#ef4444', '#10b981', '#f472b6', '#6366f1', '#14b8a6']

export default function AnalyticsPage() {
  const { shortCode } = useParams()
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true)
      try {
        const data = await getLinkAnalytics(shortCode, days)
        setAnalytics(data)
      } catch (err) {
        toast.error('Failed to load analytics')
      } finally {
        setLoading(false)
      }
    }
    fetchAnalytics()
  }, [shortCode, days])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-slate-400 text-lg">Analytics not found</p>
        <Link to="/dashboard" className="text-violet-400 hover:text-violet-300 no-underline">
          Back to Dashboard
        </Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors no-underline"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-white">Analytics</h1>
              <p className="text-violet-400 text-sm font-medium mt-0.5">
                2goi.in/{analytics.short_code}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {[7, 30, 90].map(d => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border-none cursor-pointer ${
                  days === d
                    ? 'bg-violet-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div className="p-5 bg-slate-800/40 border border-slate-700/40 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-violet-600/20 rounded-lg flex items-center justify-center">
                <MousePointerClick className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{analytics.total_clicks}</p>
                <p className="text-xs text-slate-400">Total Clicks</p>
              </div>
            </div>
          </div>
          <div className="p-5 bg-slate-800/40 border border-slate-700/40 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-cyan-600/20 rounded-lg flex items-center justify-center">
                <Globe className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{analytics.countries.length}</p>
                <p className="text-xs text-slate-400">Countries</p>
              </div>
            </div>
          </div>
          <div className="p-5 bg-slate-800/40 border border-slate-700/40 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-amber-600/20 rounded-lg flex items-center justify-center">
                <Monitor className="w-5 h-5 text-amber-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{analytics.devices.length}</p>
                <p className="text-xs text-slate-400">Device Types</p>
              </div>
            </div>
          </div>
        </div>

        {/* Clicks Over Time */}
        {analytics.daily_clicks.length > 0 && (
          <div className="p-6 bg-slate-800/40 border border-slate-700/40 rounded-xl mb-6">
            <h2 className="text-lg font-semibold text-white mb-4">Clicks Over Time</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics.daily_clicks}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#e2e8f0' }}
                  itemStyle={{ color: '#8b5cf6' }}
                />
                <Line type="monotone" dataKey="count" stroke="#8b5cf6" strokeWidth={2} dot={{ fill: '#8b5cf6', r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Bottom Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Countries */}
          {analytics.countries.length > 0 && (
            <div className="p-6 bg-slate-800/40 border border-slate-700/40 rounded-xl">
              <h2 className="text-lg font-semibold text-white mb-4">Top Countries</h2>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={analytics.countries} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                  <YAxis dataKey="country" type="category" stroke="#94a3b8" tick={{ fontSize: 12 }} width={80} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                    labelStyle={{ color: '#e2e8f0' }}
                  />
                  <Bar dataKey="count" fill="#06b6d4" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Devices */}
          {analytics.devices.length > 0 && (
            <div className="p-6 bg-slate-800/40 border border-slate-700/40 rounded-xl">
              <h2 className="text-lg font-semibold text-white mb-4">Device Types</h2>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={analytics.devices}
                    dataKey="count"
                    nameKey="device_type"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ device_type, percent }) => `${device_type} ${(percent * 100).toFixed(0)}%`}
                  >
                    {analytics.devices.map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                    labelStyle={{ color: '#e2e8f0' }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Browsers */}
        {analytics.browsers.length > 0 && (
          <div className="p-6 bg-slate-800/40 border border-slate-700/40 rounded-xl mt-6">
            <h2 className="text-lg font-semibold text-white mb-4">Browsers</h2>
            <div className="space-y-3">
              {analytics.browsers.map((b, i) => {
                const maxCount = Math.max(...analytics.browsers.map(x => x.count))
                const pct = maxCount > 0 ? (b.count / maxCount) * 100 : 0
                return (
                  <div key={i} className="flex items-center gap-3">
                    <span className="text-sm text-slate-300 w-24 shrink-0">{b.browser}</span>
                    <div className="flex-1 bg-slate-700/30 rounded-full h-2.5 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-violet-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-sm text-slate-400 w-10 text-right">{b.count}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
