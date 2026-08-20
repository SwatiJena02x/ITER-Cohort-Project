const TONES = {
  green: { text: 'text-marker-green', dot: 'bg-marker-green' },
  red: { text: 'text-marker-red', dot: 'bg-marker-red' },
  amber: { text: 'text-marker-amber', dot: 'bg-marker-amber' },
  blue: { text: 'text-marker-blue', dot: 'bg-marker-blue' },
}

/**
 * A single annotated section of feedback (strengths, weaknesses,
 * suggestions, or the learning plan), styled like marginal notes
 * a mentor scribbled next to your whiteboard solution.
 */
export default function FeedbackCard({ title, items, tone = 'blue', emptyText }) {
  const { text, dot } = TONES[tone] ?? TONES.blue
  const hasItems = Array.isArray(items) && items.length > 0

  return (
    <section className="bg-board-panel border border-board-grid rounded-lg p-5">
      <h3 className={`font-display text-sm font-semibold uppercase tracking-wide mb-3 ${text}`}>
        {title}
      </h3>
      {hasItems ? (
        <ul className="space-y-2.5">
          {items.map((item, i) => (
            <li key={i} className="flex gap-2.5 text-sm leading-relaxed text-board-ink/90">
              <span className={`mt-2 w-1.5 h-1.5 rounded-full shrink-0 ${dot}`} />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-board-faint italic">{emptyText || 'Nothing noted here.'}</p>
      )}
    </section>
  )
}
