import { Link, useLocation } from 'react-router-dom'

const SIDEBAR_ITEMS = [
  { to: '/',          icon: '🏠', label: 'New Plan'    },
  { to: '/dashboard', icon: '📋', label: 'My Dashboard' },
]

export default function Sidebar({ sessionId }) {
  const { pathname } = useLocation()

  return (
    <aside className="hidden lg:flex flex-col w-60 shrink-0">
      <div className="sticky top-20 card p-4 space-y-1">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest px-2 mb-3">
          Navigation
        </p>

        {SIDEBAR_ITEMS.map(({ to, icon, label }) => {
          const dest = to === '/dashboard' && sessionId ? `/dashboard/${sessionId}` : to
          const active = pathname === dest || (to !== '/' && pathname.startsWith('/dashboard'))
          return (
            <Link
              key={to}
              to={dest}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 ${
                active
                  ? 'bg-brand-600/20 text-brand-300 border border-brand-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <span className="text-base">{icon}</span>
              {label}
            </Link>
          )
        })}

        {sessionId && (
          <>
            <div className="border-t border-slate-800 my-3" />
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest px-2 mb-2">
              Session
            </p>
            <div className="px-3 py-2 rounded-xl bg-slate-800/40 border border-slate-700/50">
              <p className="text-xs text-slate-500 font-mono break-all">{sessionId}</p>
            </div>
          </>
        )}
      </div>
    </aside>
  )
}
