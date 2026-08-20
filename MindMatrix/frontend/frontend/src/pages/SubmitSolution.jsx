import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import CodeEditor from '../components/CodeEditor.jsx'

import {
  analyzeSolution,
  getErrorMessage,
} from '../services/api.js'

const LOADING_STEPS = [
  'Reviewing your code…',
  'Checking complexity…',
  'Looking for a better approach…',
  'Judging interview readiness…',
  'Building your study plan…',
]

export default function SubmitSolution() {

  const navigate = useNavigate()

  // ==========================================================
  // FORM STATE
  // ==========================================================

  const [problem, setProblem] = useState('')
  const [language, setLanguage] = useState('Python')
  const [code, setCode] = useState('')
  const [approach, setApproach] = useState('')

  // ==========================================================
  // REQUEST STATE
  // ==========================================================

  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')
  const [stepIndex, setStepIndex] = useState(0)

  // ==========================================================
  // VALIDATION
  // ==========================================================

  const isValid =
    problem.trim() &&
    code.trim() &&
    approach.trim()

  // ==========================================================
  // SUBMIT
  // ==========================================================

  async function handleSubmit(e) {

    e.preventDefault()

    if (!isValid || status === 'loading') {
      return
    }

    setStatus('loading')
    setError('')
    setStepIndex(0)

    const ticker = setInterval(() => {

      setStepIndex((i) =>
        Math.min(
          i + 1,
          LOADING_STEPS.length - 1
        )
      )

    }, 2200)

    try {

      // ======================================================
      // CALL BACKEND
      // ======================================================

      const feedback = await analyzeSolution({

        problem,
        language,
        code,
        approach,

      })

      clearInterval(ticker)

      // ======================================================
      // SAVE FEEDBACK
      // ======================================================
      //
      // This is the important fix.
      //
      // Feedback will remain available even after:
      //
      // - refresh
      // - direct /feedback navigation
      // - router state disappearing
      //
      // ======================================================

      const feedbackData = {

        feedback,

        problem,

        language,

        code,

        approach,

      }

      localStorage.setItem(
        'dsa_feedback',
        JSON.stringify(feedbackData)
      )

      // ======================================================
      // NAVIGATE TO FEEDBACK
      // ======================================================

      navigate('/feedback', {

        state: feedbackData,

      })

    } catch (err) {

      clearInterval(ticker)

      console.error(
        'Feedback generation failed:',
        err
      )

      setStatus('error')

      setError(
        getErrorMessage(err)
      )

    }

  }

  // ==========================================================
  // UI
  // ==========================================================

  return (

    <div className="max-w-5xl mx-auto px-6 py-12">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <p className="font-hand text-xl text-marker-blue -rotate-1">
        Step up to the board
      </p>

      <h1 className="font-display text-3xl font-bold tracking-tight mt-1">
        Submit a solution
      </h1>

      <p className="text-board-faint text-sm mt-2 max-w-xl">

        Tell us the problem, explain your thinking, and paste
        your code — the same way you'd talk through it in a
        real interview.

      </p>

      {/* =====================================================
          FORM
          ===================================================== */}

      <form
        onSubmit={handleSubmit}
        className="mt-8 grid lg:grid-cols-5 gap-8"
      >

        {/* ===================================================
            LEFT
            =================================================== */}

        <div className="lg:col-span-2 space-y-5">

          {/* =================================================
              PROBLEM
              ================================================= */}

          <div>

            <label
              htmlFor="problem"
              className="block text-xs font-semibold uppercase tracking-wide text-board-faint mb-1.5"
            >
              Problem
            </label>

            <input
              id="problem"
              type="text"
              value={problem}
              onChange={(e) =>
                setProblem(e.target.value)
              }
              placeholder="e.g. Two Sum"
              className="w-full bg-board-panel border border-board-grid rounded-md px-3 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-marker-blue"
              required
            />

          </div>

          {/* =================================================
              APPROACH
              ================================================= */}

          <div>

            <label
              htmlFor="approach"
              className="block text-xs font-semibold uppercase tracking-wide text-board-faint mb-1.5"
            >
              Your approach
            </label>

            <textarea
              id="approach"
              value={approach}
              onChange={(e) =>
                setApproach(e.target.value)
              }
              placeholder="Explain your reasoning — what data structure you chose, why, and the complexity you're aiming for."
              rows={9}
              className="w-full bg-board-panel border border-board-grid rounded-md px-3 py-2.5 text-sm leading-relaxed resize-y focus:outline-none focus:ring-1 focus:ring-marker-blue"
              required
            />

          </div>

        </div>

        {/* ===================================================
            RIGHT
            =================================================== */}

        <div className="lg:col-span-3 space-y-5">

          {/* =================================================
              CODE
              ================================================= */}

          <div>

            <span className="block text-xs font-semibold uppercase tracking-wide text-board-faint mb-1.5">
              Your code
            </span>

            <CodeEditor
              code={code}
              onCodeChange={setCode}
              language={language}
              onLanguageChange={setLanguage}
            />

          </div>

          {/* =================================================
              ERROR
              ================================================= */}

          {status === 'error' && (

            <div className="border border-marker-red/30 bg-marker-red/5 text-marker-red text-sm rounded-md px-4 py-3">

              {error}

            </div>

          )}

          {/* =================================================
              BUTTON
              ================================================= */}

          <div className="flex items-center gap-4">

            <button
              type="submit"
              disabled={
                !isValid ||
                status === 'loading'
              }
              className="bg-board-ink text-board-bg font-medium text-sm px-5 py-3 rounded-md hover:bg-board-ink/85 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >

              {status === 'loading'
                ? 'Grading…'
                : 'Get feedback'
              }

            </button>

            {/* =================================================
                LOADING
                ================================================= */}

            {status === 'loading' && (

              <span className="text-sm text-board-faint">

                {LOADING_STEPS[stepIndex]}

              </span>

            )}

          </div>

        </div>

      </form>

    </div>

  )

}