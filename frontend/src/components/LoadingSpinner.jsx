export default function LoadingSpinner({ message = 'Loading…', fullscreen = false }) {
  const content = (
    <div className="flex flex-col items-center justify-center gap-4 text-center animate-fade-in">
      {/* Animated ring */}
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 rounded-full border-4 border-brand-900" />
        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-brand-400 animate-spin-slow" />
        <div className="absolute inset-2 rounded-full border-2 border-transparent border-t-purple-400 animate-spin" style={{ animationDirection: 'reverse' }} />
      </div>
      <div>
        <p className="text-base font-semibold text-slate-200">{message}</p>
        <p className="text-sm text-slate-500 mt-1">This may take up to 90 seconds</p>
      </div>
    </div>
  )

  if (fullscreen) {
    return (
      <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center">
        <div className="card p-12">{content}</div>
      </div>
    )
  }

  return <div className="flex items-center justify-center py-20">{content}</div>
}
