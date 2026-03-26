export default function PlanCard({ company, role, timelineDays, htmlOutput }) {
  return (
    <div className="card overflow-hidden animate-slide-up">
      {/* Header */}
      <div className="px-6 py-5 border-b border-slate-800 bg-gradient-to-r from-brand-900/40 to-purple-900/20">
        <div className="flex flex-wrap items-center gap-3 mb-3">
          <span className="badge bg-brand-900/60 text-brand-300 border border-brand-700/50">
            🏢 {company || 'Company'}
          </span>
          <span className="badge bg-purple-900/60 text-purple-300 border border-purple-700/50">
            💼 {role || 'Role'}
          </span>
          {timelineDays && (
            <span className="badge bg-emerald-900/50 text-emerald-300 border border-emerald-700/50">
              📅 {timelineDays} days
            </span>
          )}
        </div>
        <h2 className="text-xl font-bold text-white">Your Preparation Plan</h2>
        <p className="text-sm text-slate-400 mt-1">AI-generated personalised study roadmap</p>
      </div>

      {/* Plan content */}
      <div className="px-6 py-6 overflow-x-auto">
        {htmlOutput ? (
          <iframe
            title="Prep Tracker"
            srcDoc={htmlOutput}
            className="w-full min-h-[800px] border-0 rounded-lg bg-[#0f0f0f]"
            sandbox="allow-scripts allow-same-origin"
          />
        ) : (
          <p className="text-slate-500 italic">No plan content available.</p>
        )}
      </div>
    </div>
  )
}
