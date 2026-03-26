import { useEffect, useState, useCallback } from 'react'
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom'
import { getPrep, getProgress, saveProgress } from '../api/prepApi'
import Sidebar from '../components/Sidebar'
import PlanCard from '../components/PlanCard'
import ProgressBar from '../components/ProgressBar'
import TopicCheckbox from '../components/TopicCheckbox'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Dashboard() {
  const { sessionId } = useParams()
  const location       = useLocation()
  const navigate       = useNavigate()

  const [session,  setSession]  = useState(location.state || null)
  const [progress, setProgress] = useState({})
  const [loading,  setLoading]  = useState(!location.state)
  const [saving,   setSaving]   = useState(false)
  const [error,    setError]    = useState('')

  /* Fetch session if not passed via navigation state */
  useEffect(() => {
    if (location.state) {
      setSession(location.state)
      setLoading(false)
    }
    fetchProgress()
  }, [sessionId]) // eslint-disable-line

  const fetchSession = useCallback(async () => {
    try {
      const data = await getPrep(sessionId)
      setSession(data)
    } catch {
      setError('Could not load the preparation plan.')
    } finally {
      setLoading(false)
    }
  }, [sessionId])

  const fetchProgress = useCallback(async () => {
    try {
      const data = await getProgress(sessionId)
      setProgress(data.progress || {})
    } catch {
      /* progress is non-critical, silently ignore */
    }
  }, [sessionId])

  useEffect(() => {
    if (!location.state) fetchSession()
  }, [fetchSession, location.state])

  /* Toggle a topic checkbox */
  const handleToggle = async (topic) => {
    const updated = { ...progress, [topic]: !progress[topic] }
    setProgress(updated)
    setSaving(true)
    try {
      await saveProgress(sessionId, updated)
    } catch {
      /* Revert on failure */
      setProgress(progress)
    } finally {
      setSaving(false)
    }
  }

  /* Derive topic list from progress map */
  const topics = Object.keys(progress)

  if (loading) return <LoadingSpinner message="Loading your plan…" />

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-24 text-center px-4">
        <p className="text-4xl mb-4">😕</p>
        <h2 className="text-xl font-bold text-white mb-2">Failed to load plan</h2>
        <p className="text-slate-400 mb-6">{error}</p>
        <Link to="/" className="btn-primary">← Go back home</Link>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
      <div className="flex gap-6">
        <Sidebar sessionId={sessionId} />

        {/* Main content */}
        <div className="flex-1 min-w-0 space-y-6">

          {/* Page header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-in">
            <div>
              <h1 className="text-2xl font-bold text-white">
                {session?.role ? `${session.role} Prep Plan` : 'Interview Prep Dashboard'}
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                {session?.company && `Target: ${session.company} · `}
                {session?.timeline_days && `${session.timeline_days}-day roadmap`}
              </p>
            </div>
            <button
              onClick={() => navigate('/')}
              className="btn-secondary self-start sm:self-auto"
            >
              + New Plan
            </button>
          </div>

          {/* Progress widget */}
          {topics.length > 0 && (
            <div className="card p-5 animate-slide-up">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-white">Progress Tracker</h2>
                {saving && (
                  <span className="flex items-center gap-1.5 text-xs text-slate-400">
                    <span className="w-3 h-3 border border-slate-400 border-t-transparent rounded-full animate-spin" />
                    Saving…
                  </span>
                )}
              </div>
              <ProgressBar progress={progress} />
              <div className="mt-4 space-y-1 max-h-64 overflow-y-auto pr-1">
                {topics.map((topic) => (
                  <TopicCheckbox
                    key={topic}
                    topic={topic}
                    checked={!!progress[topic]}
                    onChange={() => handleToggle(topic)}
                    disabled={saving}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Plan content */}
          <PlanCard
            company={session?.company}
            role={session?.role}
            timelineDays={session?.timeline_days}
            htmlOutput={session?.html_output}
          />
        </div>
      </div>
    </div>
  )
}
