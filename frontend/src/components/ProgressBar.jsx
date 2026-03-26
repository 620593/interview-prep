export default function ProgressBar({ progress = {} }) {
  const total = Object.keys(progress).length
  const done  = Object.values(progress).filter(Boolean).length
  const pct   = total === 0 ? 0 : Math.round((done / total) * 100)

  const color = pct >= 80 ? 'from-emerald-500 to-teal-400'
              : pct >= 50 ? 'from-brand-500 to-purple-500'
              :              'from-brand-600 to-brand-400'

  return (
    <div className="space-y-2 animate-fade-in">
      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-400 font-medium">Overall Progress</span>
        <span className="font-bold text-white">{pct}%</span>
      </div>

      <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${color} transition-all duration-700 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>

      <p className="text-xs text-slate-500 text-right">
        {done} / {total} topics completed
      </p>
    </div>
  )
}
