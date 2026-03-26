import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { generatePrep } from '../api/prepApi'
import LoadingSpinner from '../components/LoadingSpinner'

const EXAMPLE_QUERIES = [
  'Software Engineer at Google, 30 days, focus on DSA and system design',
  'Frontend Developer at Stripe, 3 weeks, React, TypeScript, CSS',
  'Data Scientist at Meta, 45 days, ML algorithms, Python, SQL, statistics',
]

export default function Home() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    try {
      const data = await generatePrep(query.trim())
      navigate(`/dashboard/${data.session_id}`, { state: data })
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message || 'Something went wrong. Please try again.'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {loading && <LoadingSpinner fullscreen message="Generating your personalised plan…" />}

      <main className="min-h-screen flex flex-col">
        {/* Hero */}
        <section className="flex-1 flex flex-col items-center justify-center px-4 py-24 text-center relative overflow-hidden">
          {/* Background glow */}
          <div className="absolute inset-0 -z-10 pointer-events-none">
            <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-brand-700/20 rounded-full blur-3xl" />
            <div className="absolute top-1/2 left-1/4 w-[300px] h-[300px] bg-purple-700/10 rounded-full blur-3xl" />
          </div>

          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-brand-500/30 bg-brand-900/30 text-brand-300 text-sm font-medium mb-6 animate-fade-in">
            <span className="w-2 h-2 rounded-full bg-brand-400 animate-pulse" />
            AI-Powered Interview Prep System
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight mb-6 animate-slide-up">
            Ace Your Next{' '}
            <span className="bg-gradient-to-r from-brand-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Interview
            </span>
            <br />with AI-Crafted Plans
          </h1>

          <p className="max-w-xl text-lg text-slate-400 mb-10 animate-slide-up">
            Describe your target role and goals in plain English. Our AI creates a
            personalised day-by-day prep plan — with resources, topics, and progress tracking.
          </p>

          {/* Form */}
          <form
            onSubmit={handleSubmit}
            className="w-full max-w-2xl glass p-6 space-y-4 animate-slide-up"
          >
            <label className="block text-left">
              <span className="text-sm font-semibold text-slate-300 mb-2 block">
                Describe your interview goal
              </span>
              <textarea
                className="input-field h-32"
                placeholder={`e.g. "${EXAMPLE_QUERIES[0]}"`}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                required
                disabled={loading}
              />
            </label>

            {/* Quick examples */}
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-slate-500">Try:</span>
              {EXAMPLE_QUERIES.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => setQuery(q)}
                  className="text-xs px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 transition-colors"
                >
                  {q.split(',')[0]}…
                </button>
              ))}
            </div>

            {error && (
              <div className="flex items-start gap-3 px-4 py-3 rounded-xl bg-red-900/30 border border-red-700/40 text-red-300 text-sm animate-fade-in">
                <span className="text-base shrink-0">⚠️</span>
                <p>{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="btn-primary w-full justify-center text-base py-4"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Generating Plan…
                </>
              ) : (
                <>
                  <span>✨</span>
                  Generate My Plan
                </>
              )}
            </button>
          </form>

          {/* Features row */}
          <div className="flex flex-wrap justify-center gap-6 mt-14 animate-fade-in">
            {[
              { icon: '🧠', text: 'AI-powered roadmap' },
              { icon: '📅', text: 'Day-by-day schedule' },
              { icon: '✅', text: 'Progress tracking' },
              { icon: '🔗', text: 'Curated resources' },
            ].map(({ icon, text }) => (
              <div key={text} className="flex items-center gap-2 text-slate-400 text-sm">
                <span>{icon}</span>
                {text}
              </div>
            ))}
          </div>
        </section>
      </main>
    </>
  )
}
