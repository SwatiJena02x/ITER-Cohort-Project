import { NavLink } from 'react-router-dom'

const linkClass = ({ isActive }) =>
  `text-sm font-medium px-3 py-1.5 rounded-md transition-colors ${
    isActive
      ? 'bg-board-ink text-board-bg'
      : 'text-board-ink/70 hover:text-board-ink hover:bg-board-grid/60'
  }`

export default function Navbar() {
  return (
    <header className="border-b border-board-grid bg-board-bg/95 backdrop-blur sticky top-0 z-20">
      <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
        <NavLink to="/" className="flex items-center gap-2.5 group">
          <svg width="26" height="26" viewBox="0 0 32 32" className="shrink-0">
            <rect width="32" height="32" rx="7" fill="#1C2321" />
            <circle cx="8" cy="10" r="2.6" fill="#FAFAF7" />
            <circle cx="24" cy="10" r="2.6" fill="#FAFAF7" />
            <circle cx="16" cy="22" r="2.6" fill="#DE9A1F" />
            <path d="M8 12.6 L16 19.4 M24 12.6 L16 19.4" stroke="#FAFAF7" strokeWidth="1.4" fill="none" />
          </svg>
          <span className="font-display font-semibold text-lg tracking-tight">
            DSA Coach <span className="text-marker-blue">AI</span>
          </span>
        </NavLink>
        <nav className="flex items-center gap-1.5">
          <NavLink to="/" end className={linkClass}>
            Home
          </NavLink>
          <NavLink to="/submit" className={linkClass}>
            New submission
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
