import ShortenForm from '../components/ShortenForm'
import { Link2, Zap, BarChart3, QrCode, Shield, Globe } from 'lucide-react'

const features = [
  {
    icon: Zap,
    title: 'Lightning Fast',
    desc: 'Redis-cached redirects in under 5ms. 90% of requests are served from memory.',
  },
  {
    icon: BarChart3,
    title: 'Click Analytics',
    desc: 'Track every click with country, browser, device, and time-series data.',
  },
  {
    icon: QrCode,
    title: 'QR Codes',
    desc: 'Every short link comes with a downloadable QR code automatically.',
  },
  {
    icon: Shield,
    title: 'Custom Aliases',
    desc: 'Choose your own short code like 2goi.in/myresume for branded links.',
  },
  {
    icon: Globe,
    title: 'Link Expiration',
    desc: 'Set TTL on any link. Expired links return 410 Gone automatically.',
  },
  {
    icon: Link2,
    title: '916M+ Codes',
    desc: 'Base62 encoding with 5 characters gives over 916 million unique URLs.',
  },
]

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative pt-20 pb-16 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-violet-900/20 via-transparent to-transparent pointer-events-none" />
        <div className="relative max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-violet-500/10 border border-violet-500/20 rounded-full text-violet-300 text-sm mb-6">
            <Zap className="w-3.5 h-3.5" />
            Sub-5ms redirects powered by Redis
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white leading-tight tracking-tight mb-6">
            Shorten URLs.
            <br />
            <span className="bg-gradient-to-r from-violet-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              Track Everything.
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Transform long URLs into short, shareable links with real-time analytics,
            custom aliases, QR codes, and blazing-fast redirects.
          </p>

          <ShortenForm />
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Everything you need in a URL shortener
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((feature, i) => (
              <div
                key={i}
                className="p-6 bg-slate-800/40 border border-slate-700/40 rounded-xl hover:border-violet-500/30 transition-all group"
              >
                <div className="w-10 h-10 bg-violet-600/20 rounded-lg flex items-center justify-center mb-4 group-hover:bg-violet-600/30 transition-colors">
                  <feature.icon className="w-5 h-5 text-violet-400" />
                </div>
                <h3 className="text-white font-semibold text-lg mb-2">{feature.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-slate-800">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-slate-400 text-sm">
            <Link2 className="w-4 h-4 text-violet-400" />
            <span className="font-semibold text-white">2GOI</span>
            <span>- Production-grade URL shortener</span>
          </div>
          <p className="text-slate-500 text-sm">
            Built with FastAPI, React, Redis & Supabase
          </p>
        </div>
      </footer>
    </div>
  )
}
