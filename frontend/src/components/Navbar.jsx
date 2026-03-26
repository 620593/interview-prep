import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const NAV_LINKS = [
  { to: '/', label: 'Home', icon: '🏠' },
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()

  return (
    <header className="fixed top-0 inset-x-0 z-50 border-b border-slate-800/60 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <Link to="/" className="flex items-center gap-2 group">
            <span className="text-2xl">🎯</span>
            <span className="text-xl font-bold bg-gradient-to-r from-brand-400 to-purple-400 bg-clip-text text-transparent group-hover:opacity-90 transition-opacity">
              PrepAI
            </span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden sm:flex items-center gap-4">
            {NAV_LINKS.map(({ to, label, icon }) => {
              const active = pathname === to || (to !== '/' && pathname.startsWith(to))
              return (
                <Link
                  key={to}
                  to={to}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                    active
                      ? 'bg-brand-600/20 text-brand-300 border border-brand-500/30'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <span>{icon}</span>
                  {label}
                </Link>
              )
            })}
            
            {/* User Info / Logout */}
            <div className="flex items-center gap-3 pl-4 border-l border-slate-700">
              <span className="text-sm text-slate-300 truncate max-w-[120px]">
                {localStorage.getItem('prep_user') || 'Guest'}
              </span>
              <button
                onClick={() => {
                  localStorage.removeItem('prep_user')
                  localStorage.removeItem('prep_session_id')
                  window.location.href = '/login'
                }}
                className="text-xs px-3 py-1.5 rounded-md bg-slate-800 hover:bg-red-900/50 text-slate-400 hover:text-red-300 transition-colors"
              >
                Logout
              </button>
            </div>
          </nav>

          {/* Mobile hamburger */}
          <button
            onClick={() => setOpen((o) => !o)}
            className="sm:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {open
                ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="sm:hidden border-t border-slate-800 bg-slate-950/95 px-4 py-3 space-y-1 animate-fade-in">
          {NAV_LINKS.map(({ to, label, icon }) => (
            <Link
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className="flex items-center gap-2 px-4 py-3 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors text-sm font-medium"
            >
              <span>{icon}</span>
              {label}
            </Link>
          ))}
        </div>
      )}
    </header>
  )
}
