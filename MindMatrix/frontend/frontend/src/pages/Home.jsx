import { Link } from 'react-router-dom'

const PIPELINE = [
  { n: '01', name: 'Code Review', desc: 'Reads your submission for correctness, style, and edge cases.' },
  { n: '02', name: 'Complexity', desc: 'Works out the real time and space complexity of your approach.' },
  { n: '03', name: 'Optimization + RAG', desc: 'Pulls relevant DSA patterns and checks for a better approach.' },
  { n: '04', name: 'Interview', desc: 'Judges how your explanation would land in a live interview.' },
  { n: '05', name: 'Learning', desc: 'Builds a short study plan from your specific weak spots.' },
  { n: '06', name: 'Supervisor', desc: 'Combines every agent into one graded verdict.' },
]

export default function Home() {
  return (
    <div>
      {/* hero */}
      <section className="whiteboard border-b border-board-grid">
        <div className="max-w-5xl mx-auto px-6 py-20">
          <p className="font-hand text-2xl text-marker-blue -rotate-1 mb-2">
            "walk me through your approach..."
          </p>
          <h1 className="font-display text-4xl sm:text-5xl font-bold tracking-tight max-w-2xl leading-[1.1]">
            Get graded on your DSA solution like it's a real whiteboard interview.
          </h1>
          <p className="mt-5 text-board-faint max-w-xl text-[15px] leading-relaxed">
            Paste your solution and your reasoning. Six AI agents review it in
            sequence — correctness, complexity, optimization, interview
            readiness, and what to study next — then a supervisor combines it
            into one score.
          </p>
          <Link
            to="/submit"
            className="inline-flex items-center gap-2 mt-8 bg-board-ink text-board-bg font-medium text-sm px-5 py-3 rounded-md hover:bg-board-ink/85 transition-colors"
          >
            Submit a solution
            <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>

      {/* pipeline — a real, ordered sequence, so numbering earns its place */}
      <section className="max-w-5xl mx-auto px-6 py-16">
        <h2 className="font-display text-xs font-semibold uppercase tracking-widest text-board-faint mb-8">
          How a submission gets graded
        </h2>
        <ol className="grid sm:grid-cols-2 lg:grid-cols-3 gap-px bg-board-grid border border-board-grid rounded-lg overflow-hidden">
          {PIPELINE.map((step) => (
            <li key={step.n} className="bg-board-panel p-5 flex flex-col gap-2">
              <span className="font-hand text-2xl text-marker-amber leading-none">{step.n}</span>
              <span className="font-display font-semibold text-sm">{step.name}</span>
              <span className="text-[13px] text-board-faint leading-relaxed">{step.desc}</span>
            </li>
          ))}
        </ol>
      </section>
    </div>
  )
}
