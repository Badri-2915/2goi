import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { getUserLinks, deleteLink } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import {
  Trash2, Copy, Check, ExternalLink, BarChart3,
  ChevronLeft, ChevronRight, ArrowUpDown, Loader2
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function DashboardPage() {
  const { user } = useAuth()
  const [links, setLinks] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [sortBy, setSortBy] = useState('created_at')
  const [loading, setLoading] = useState(true)
  const [copiedId, setCopiedId] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  const fetchLinks = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getUserLinks(page, pageSize, sortBy)
      setLinks(data.links)
      setTotal(data.total)
    } catch (err) {
      toast.error('Failed to load links')
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, sortBy])

  useEffect(() => {
    fetchLinks()
  }, [fetchLinks])

  const handleCopy = async (shortUrl, linkId) => {
    await navigator.clipboard.writeText(shortUrl)
    setCopiedId(linkId)
    toast.success('Copied!')
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleDelete = async (linkId) => {
    if (!confirm('Are you sure you want to delete this link?')) return
    setDeletingId(linkId)
    try {
      await deleteLink(linkId)
      toast.success('Link deleted')
      fetchLinks()
    } catch (err) {
      toast.error('Failed to delete link')
    } finally {
      setDeletingId(null)
    }
  }

  const totalPages = Math.ceil(total / pageSize)

  const sortOptions = [
    { value: 'created_at', label: 'Newest' },
    { value: 'click_count', label: 'Most Clicks' },
    { value: 'expires_at', label: 'Expiring Soon' },
  ]

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>
            <p className="text-slate-400 text-sm mt-1">
              {total} link{total !== 1 ? 's' : ''} total
            </p>
          </div>
          <div className="flex items-center gap-2">
            <ArrowUpDown className="w-4 h-4 text-slate-400" />
            <select
              value={sortBy}
              onChange={(e) => { setSortBy(e.target.value); setPage(1) }}
              className="bg-slate-800 border border-slate-700 text-slate-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-violet-500 focus:outline-none"
            >
              {sortOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Links Table */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
          </div>
        ) : links.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-slate-400 text-lg mb-4">No links yet</p>
            <Link
              to="/"
              className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-5 py-2.5 rounded-lg font-medium transition-colors no-underline"
            >
              Create your first short link
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider py-3 px-4">Short URL</th>
                  <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider py-3 px-4 hidden md:table-cell">Original URL</th>
                  <th className="text-center text-xs font-medium text-slate-400 uppercase tracking-wider py-3 px-4">Clicks</th>
                  <th className="text-left text-xs font-medium text-slate-400 uppercase tracking-wider py-3 px-4 hidden sm:table-cell">Created</th>
                  <th className="text-right text-xs font-medium text-slate-400 uppercase tracking-wider py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {links.map((link) => (
                  <tr key={link.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4">
                      <a
                        href={link.short_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-violet-400 hover:text-violet-300 font-medium text-sm no-underline flex items-center gap-1"
                      >
                        {link.short_url.replace('https://', '')}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>
                    <td className="py-3 px-4 hidden md:table-cell">
                      <p className="text-slate-400 text-sm truncate max-w-xs" title={link.original_url}>
                        {link.original_url}
                      </p>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-700/50 text-slate-300">
                        {link.click_count}
                      </span>
                    </td>
                    <td className="py-3 px-4 hidden sm:table-cell">
                      <span className="text-slate-400 text-sm">
                        {new Date(link.created_at).toLocaleDateString()}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => handleCopy(link.short_url, link.id)}
                          className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-md transition-colors bg-transparent border-none cursor-pointer"
                          title="Copy URL"
                        >
                          {copiedId === link.id ? (
                            <Check className="w-4 h-4 text-green-400" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </button>
                        <Link
                          to={`/analytics/${link.short_code}`}
                          className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-md transition-colors no-underline"
                          title="View Analytics"
                        >
                          <BarChart3 className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => handleDelete(link.id)}
                          disabled={deletingId === link.id}
                          className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-md transition-colors bg-transparent border-none cursor-pointer disabled:opacity-50"
                          title="Delete"
                        >
                          {deletingId === link.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-6 pt-6 border-t border-slate-800">
            <p className="text-sm text-slate-400">
              Page {page} of {totalPages}
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-slate-300 rounded-lg transition-colors border-none cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-slate-300 rounded-lg transition-colors border-none cursor-pointer"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
