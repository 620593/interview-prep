export default function TopicCheckbox({ topic, checked, onChange, disabled }) {
  return (
    <label
      className={`flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-150 group
        ${checked
          ? 'bg-emerald-900/20 border border-emerald-700/30'
          : 'hover:bg-slate-800/50 border border-transparent'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <div className={`relative flex-shrink-0 w-5 h-5 rounded-md border-2 transition-all duration-200
        ${checked
          ? 'bg-emerald-500 border-emerald-500'
          : 'border-slate-600 group-hover:border-brand-400'}`}
      >
        {checked && (
          <svg className="absolute inset-0 w-full h-full text-white p-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        )}
        <input
          type="checkbox"
          className="sr-only"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
        />
      </div>
      <span className={`text-sm font-medium transition-colors duration-150 ${checked ? 'text-emerald-300 line-through decoration-emerald-600/60' : 'text-slate-300 group-hover:text-white'}`}>
        {topic}
      </span>
    </label>
  )
}
