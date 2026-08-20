// A hand-circled score, like a mentor grading a whiteboard session.
// The ellipse path is deliberately imperfect (a closed, slightly
// irregular loop) rather than a clean SVG <circle>, to read as a
// marker stroke rather than UI chrome.

function toneFor(score) {
  if (score >= 80) return { ring: '#1E8E5A', label: 'Strong' }
  if (score >= 55) return { ring: '#DE9A1F', label: 'Developing' }
  return { ring: '#D63B3B', label: 'Needs work' }
}

export default function ScoreDial({ score = 0 }) {
  const { ring, label } = toneFor(score)

  return (
    <div className="relative w-32 h-32 shrink-0 flex items-center justify-center">
      <svg viewBox="0 0 140 140" className="absolute inset-0 w-full h-full overflow-visible">
        <path
          d="M 70 12
             C 108 10, 130 34, 128 70
             C 126 108, 100 130, 68 128
             C 32 126, 10 102, 12 68
             C 14 32, 36 14, 70 12 Z"
          fill="none"
          stroke={ring}
          strokeWidth="4.5"
          strokeLinecap="round"
        />
      </svg>
      <div className="flex flex-col items-center">
        <span className="font-hand text-4xl font-bold leading-none" style={{ color: ring }}>
          {score}
        </span>
        <span className="text-[11px] uppercase tracking-wide text-board-faint mt-1">{label}</span>
      </div>
    </div>
  )
}
