const LANGUAGES = ['Python', 'JavaScript', 'Java', 'C++', 'C', 'Go', 'TypeScript']

export default function CodeEditor({ code, onCodeChange, language, onLanguageChange }) {
  const lineCount = Math.max(code.split('\n').length, 14)
  const gutter = Array.from({ length: lineCount }, (_, i) => i + 1)

  return (
    <div className="rounded-lg overflow-hidden border border-board-ink/15 shadow-board bg-[#1C2321]">
      {/* window chrome */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#22282A] border-b border-white/5">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-marker-red/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-marker-amber/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-marker-green/70" />
        </div>
        <label className="flex items-center gap-2 text-xs text-white/50">
          <span>Language</span>
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="bg-white/5 text-white/90 text-xs font-mono rounded px-2 py-1 border border-white/10 focus:outline-none focus:ring-1 focus:ring-marker-blue"
          >
            {LANGUAGES.map((lang) => (
              <option key={lang} value={lang} className="text-board-ink">
                {lang}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* editor body */}
      <div className="flex font-mono text-[13px] leading-6">
        <div
          aria-hidden="true"
          className="select-none text-white/25 text-right px-3 py-4 bg-white/[0.02] border-r border-white/5"
        >
          {gutter.map((n) => (
            <div key={n}>{n}</div>
          ))}
        </div>
        <textarea
          value={code}
          onChange={(e) => onCodeChange(e.target.value)}
          spellCheck={false}
          placeholder={'def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i'}
          className="flex-1 min-h-[320px] py-4 pl-3 pr-4 bg-transparent text-[#E8ECE9] placeholder-white/20 resize-y focus:outline-none"
        />
      </div>
    </div>
  )
}
