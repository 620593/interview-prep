import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')

  const handleLogin = (e) => {
    e.preventDefault()
    if (!username.trim()) return

    // "Basic" login: just store realistic identifier
    localStorage.setItem('prep_user', username)
    
    // Check if they already have an existing session
    const existingSessionId = localStorage.getItem('prep_session_id')
    if (existingSessionId) {
      navigate(`/dashboard/${existingSessionId}`)
    } else {
      navigate('/')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 -z-10 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-brand-700/20 rounded-full blur-3xl opacity-50" />
      </div>

      <div className="w-full max-w-md card p-8 glass animate-slide-up relative">
        <div className="text-center mb-8">
          <span className="text-4xl block mb-4">🎯</span>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-brand-400 to-purple-400 bg-clip-text text-transparent">
            Welcome to PrepAI
          </h1>
          <p className="text-sm text-slate-400 mt-2">Sign in to sync your interview plans.</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Username or Email
            </label>
            <input
              type="text"
              placeholder="e.g. alex@example.com"
              className="input-field w-full"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              required
            />
          </div>

          <button
            type="submit"
            disabled={!username.trim()}
            className="btn-primary w-full justify-center py-3"
          >
            Start Prepping 🚀
          </button>
        </form>

        <p className="text-xs text-center text-slate-500 mt-6">
          Basic demo login. No password required.
        </p>
      </div>
    </div>
  )
}
