/**
 * ShortenForm — The main URL shortening form on the homepage.
 *
 * Features:
 * - URL input with validation
 * - Advanced options (custom alias, expiration time)
 * - Shows shortened URL with copy-to-clipboard button
 * - Displays QR code with download option
 * - Works for both anonymous and logged-in users
 *
 * Flow: User enters URL → calls POST /api/shorten → displays result with QR code
 */

import { useState } from 'react'
import { shortenUrl } from '../lib/api'
import { Link2, Copy, Check, QrCode, Settings, ChevronDown, ChevronUp } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ShortenForm() {
  const [url, setUrl] = useState('')
  const [customAlias, setCustomAlias] = useState('')
  const [expiresIn, setExpiresIn] = useState('')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setResult(null)
    try {
      const data = await shortenUrl(
        url.trim(),
        customAlias.trim() || null,
        expiresIn ? parseInt(expiresIn) : null
      )
      setResult(data)
      setUrl('')
      setCustomAlias('')
      setExpiresIn('')
      toast.success('URL shortened successfully!')
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to shorten URL'
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = async () => {
    if (!result) return
    await navigator.clipboard.writeText(result.short_url)
    setCopied(true)
    toast.success('Copied to clipboard!')
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadQR = () => {
    if (!result?.qr_code) return
    const link = document.createElement('a')
    link.href = `data:image/png;base64,${result.qr_code}`
    link.download = `2goi-${result.short_code}.png`
    link.click()
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Link2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Paste your long URL here..."
              className="w-full pl-11 pr-4 py-3.5 bg-slate-800/50 border border-slate-600/50 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-base"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="px-6 py-3.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all text-base whitespace-nowrap"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Shortening...
              </span>
            ) : (
              'Shorten'
            )}
          </button>
        </div>

        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-300 transition-colors bg-transparent border-none cursor-pointer mx-auto"
        >
          <Settings className="w-3.5 h-3.5" />
          Advanced options
          {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {showAdvanced && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-4 bg-slate-800/30 rounded-xl border border-slate-700/30">
            <div>
              <label className="block text-xs text-slate-400 mb-1.5 text-left">Custom alias</label>
              <input
                type="text"
                value={customAlias}
                onChange={(e) => setCustomAlias(e.target.value)}
                placeholder="e.g. myresume"
                maxLength={20}
                className="w-full px-3 py-2.5 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1.5 text-left">Expires in (seconds)</label>
              <input
                type="number"
                value={expiresIn}
                onChange={(e) => setExpiresIn(e.target.value)}
                placeholder="e.g. 86400 (1 day)"
                min={1}
                className="w-full px-3 py-2.5 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
              />
            </div>
          </div>
        )}
      </form>

      {result && (
        <div className="mt-6 p-5 bg-slate-800/50 border border-slate-700/50 rounded-xl space-y-4">
          <div className="flex items-center gap-3">
            <div className="flex-1 text-left">
              <p className="text-xs text-slate-400 mb-1">Your shortened URL</p>
              <a
                href={result.short_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-400 hover:text-indigo-300 font-semibold text-lg no-underline break-all"
              >
                {result.short_url}
              </a>
            </div>
            <button
              onClick={copyToClipboard}
              className="p-2.5 bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-500/30 rounded-lg transition-all cursor-pointer"
            >
              {copied ? (
                <Check className="w-5 h-5 text-green-400" />
              ) : (
                <Copy className="w-5 h-5 text-indigo-400" />
              )}
            </button>
          </div>

          <div className="flex items-center gap-4 pt-3 border-t border-slate-700/50">
            {result.qr_code && (
              <div className="flex items-center gap-3">
                <img
                  src={`data:image/png;base64,${result.qr_code}`}
                  alt="QR Code"
                  className="w-20 h-20 rounded-lg bg-white p-1"
                />
                <button
                  onClick={downloadQR}
                  className="flex items-center gap-1.5 text-sm text-slate-300 hover:text-white bg-slate-700/50 hover:bg-slate-700 px-3 py-2 rounded-lg transition-all cursor-pointer border-none"
                >
                  <QrCode className="w-4 h-4" />
                  Download QR
                </button>
              </div>
            )}

            <div className="text-left text-xs text-slate-400 ml-auto">
              <p className="truncate max-w-xs" title={result.original_url}>
                {result.original_url}
              </p>
              {result.expires_at && (
                <p className="mt-1">Expires: {new Date(result.expires_at).toLocaleString()}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
