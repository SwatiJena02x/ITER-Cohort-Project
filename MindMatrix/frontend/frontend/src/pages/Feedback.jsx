import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

import ScoreDial from '../components/ScoreDial.jsx'
import FeedbackCard from '../components/FeedbackCard.jsx'

import {
  getHint,
  getErrorMessage,
} from '../services/api.js'


// ============================================================
// FEEDBACK PAGE
// ============================================================

export default function Feedback() {

  const location = useLocation()

  const routerState = location.state


  // ==========================================================
  // LOAD SAVED FEEDBACK
  // ==========================================================

  const [savedData, setSavedData] = useState(() => {

    try {

      const saved =
        localStorage.getItem('dsa_feedback')

      if (!saved) {
        return null
      }

      return JSON.parse(saved)

    } catch (error) {

      console.error(
        'Could not load saved feedback:',
        error
      )

      return null

    }

  })


  // ==========================================================
  // USE ROUTER STATE FIRST
  // THEN LOCAL STORAGE
  // ==========================================================

  const feedback =
    routerState?.feedback ||
    savedData?.feedback ||
    null

  const problem =
    routerState?.problem ||
    savedData?.problem ||
    ''

  const language =
    routerState?.language ||
    savedData?.language ||
    'Python'

  const code =
    routerState?.code ||
    savedData?.code ||
    ''

  const approach =
    routerState?.approach ||
    savedData?.approach ||
    ''


  // ==========================================================
  // HINT STATE
  // ==========================================================

  const [hint, setHint] = useState('')

  const [hintLevel, setHintLevel] = useState(1)

  const [hintLoading, setHintLoading] = useState(false)

  const [hintError, setHintError] = useState('')


  // ==========================================================
  // UPDATE LOCAL STORAGE IF ROUTER STATE EXISTS
  // ==========================================================

  useEffect(() => {

    if (routerState?.feedback) {

      const newData = {

        feedback: routerState.feedback,

        problem:
          routerState.problem || '',

        language:
          routerState.language || 'Python',

        code:
          routerState.code || '',

        approach:
          routerState.approach || '',

      }

      localStorage.setItem(
        'dsa_feedback',
        JSON.stringify(newData)
      )

      setSavedData(newData)

    }

  }, [routerState])


  // ==========================================================
  // RESET HINT
  // ==========================================================

  useEffect(() => {

    setHint('')
    setHintLevel(1)
    setHintError('')
    setHintLoading(false)

  }, [problem, code])


  // ==========================================================
  // GET HINT
  // ==========================================================

  async function handleGetHint() {

    if (!problem || !code) {

      setHintError(
        'Problem and code are required to generate a hint.'
      )

      return

    }

    if (hintLevel > 3) {
      return
    }

    setHintLoading(true)
    setHintError('')

    try {

      // ======================================================
      // IMPORTANT:
      // api.js expects "hintLevel"
      // NOT "hint_level"
      // ======================================================

      const result = await getHint({

        problem,

        language,

        code,

        approach,

        hintLevel,

      })


      const generatedHint =
        result?.hint ||
        result?.feedback?.hint ||
        result?.message ||
        ''


      if (!generatedHint) {

        throw new Error(
          'The AI did not return a hint.'
        )

      }


      setHint(generatedHint)

    } catch (error) {

      console.error(
        'Hint generation failed:',
        error
      )

      setHintError(
        getErrorMessage(error)
      )

    } finally {

      setHintLoading(false)

    }

  }


  // ==========================================================
  // NO FEEDBACK
  // ==========================================================

  if (!feedback) {

    return (

      <div className="max-w-2xl mx-auto px-6 py-24 text-center">

        <p className="font-hand text-2xl text-marker-amber mb-2">
          nothing on the board yet
        </p>

        <h1 className="font-display text-2xl font-bold">
          No feedback to show
        </h1>

        <p className="text-board-faint text-sm mt-2">

          Submit a solution first and your graded feedback
          will appear here.

        </p>

        <Link
          to="/submit"
          className="inline-flex items-center gap-2 mt-6 bg-board-ink text-board-bg font-medium text-sm px-5 py-3 rounded-md hover:bg-board-ink/85 transition-colors"
        >
          Submit a solution
        </Link>

      </div>

    )

  }


  // ==========================================================
  // BACKEND FEEDBACK ERROR
  // ==========================================================

  if (feedback.error) {

    return (

      <div className="max-w-2xl mx-auto px-6 py-24 text-center">

        <h1 className="font-display text-2xl font-bold text-marker-red">
          Couldn't read the feedback
        </h1>

        <p className="text-board-faint text-sm mt-2">
          {feedback.error}
        </p>

        <Link
          to="/submit"
          className="inline-flex items-center gap-2 mt-6 bg-board-ink text-board-bg font-medium text-sm px-5 py-3 rounded-md hover:bg-board-ink/85 transition-colors"
        >
          Try again
        </Link>

      </div>

    )

  }


  // ==========================================================
  // MAIN FEEDBACK PAGE
  // ==========================================================

  return (

    <div className="max-w-4xl mx-auto px-6 py-12">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <div className="whiteboard border border-board-grid rounded-lg p-6 sm:p-8 flex flex-col sm:flex-row gap-6 sm:items-center">

        <ScoreDial
          score={feedback.overall_score}
        />

        <div className="flex-1 min-w-0">

          {problem && (

            <p className="text-xs font-semibold uppercase tracking-wide text-board-faint mb-1">

              {problem}

            </p>

          )}

          <p className="text-sm leading-relaxed text-board-ink/90">

            {feedback.correctness}

          </p>

          {/* =================================================
              COMPLEXITY
              ================================================= */}

          <div className="flex flex-wrap gap-2 mt-4">

            {feedback.time_complexity && (

              <span className="font-mono text-xs bg-board-ink text-board-bg px-2.5 py-1 rounded">

                time {feedback.time_complexity}

              </span>

            )}

            {feedback.space_complexity && (

              <span className="font-mono text-xs bg-board-ink text-board-bg px-2.5 py-1 rounded">

                space {feedback.space_complexity}

              </span>

            )}

          </div>

        </div>

      </div>


      {/* =====================================================
          INTERVIEW VERDICT
          ===================================================== */}

      {feedback.interview_result && (

        <p className="font-hand text-xl text-marker-blue mt-8 -rotate-1">

          "{feedback.interview_result}"

        </p>

      )}


      {/* =====================================================
          FEEDBACK CARDS
          ===================================================== */}

      <div className="grid sm:grid-cols-2 gap-4 mt-4">

        <FeedbackCard
          title="Strengths"
          items={feedback.strengths}
          tone="green"
          emptyText="No specific strengths called out."
        />

        <FeedbackCard
          title="Weaknesses"
          items={feedback.weaknesses}
          tone="red"
          emptyText="No weaknesses called out."
        />

        <FeedbackCard
          title="Suggestions"
          items={feedback.suggestions}
          tone="amber"
          emptyText="No suggestions given."
        />

        <FeedbackCard
          title="Learning plan"
          items={feedback.learning_plan}
          tone="blue"
          emptyText="No follow-up topics suggested."
        />

      </div>


      {/* =====================================================
          AI DSA COACH HINT
          ===================================================== */}

      <div className="mt-10 rounded-2xl border border-indigo-200 bg-indigo-50 p-6">

        <div className="mb-5">

          <h2 className="text-xl font-bold text-gray-900">
            💡 AI DSA Coach Hint
          </h2>

          <p className="mt-1 text-sm text-gray-600">

            Need help? Get a progressive hint without revealing
            the complete solution.

          </p>

        </div>


        {/* ===================================================
            HINT LEVEL
            =================================================== */}

        <div className="mb-4 flex items-center gap-3">

          <span className="rounded-full bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm">

            Hint Level {hintLevel} / 3

          </span>

          <span className="text-xs text-gray-500">

            {hintLevel === 1
              ? 'Gentle guidance'
              : hintLevel === 2
              ? 'Stronger direction'
              : 'Almost the solution'
            }

          </span>

        </div>


        {/* ===================================================
            HINT BUTTON
            =================================================== */}

        <button
          onClick={handleGetHint}
          disabled={
            hintLoading ||
            hintLevel > 3 ||
            !problem ||
            !code
          }
          className="rounded-xl bg-indigo-600 px-5 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >

          {hintLoading

            ? 'Generating hint...'

            : hintLevel === 1

            ? '💡 Get Hint'

            : hintLevel === 2

            ? '💡 Get Stronger Hint'

            : hintLevel === 3

            ? '💡 Get Final Hint'

            : 'Hints Complete'

          }

        </button>


        {/* ===================================================
            ERROR
            =================================================== */}

        {hintError && (

          <div className="mt-4 rounded-lg bg-red-100 border border-red-200 p-3 text-sm text-red-700">

            {hintError}

          </div>

        )}


        {/* ===================================================
            HINT OUTPUT
            =================================================== */}

        {hint && (

          <div className="mt-5 rounded-xl border border-indigo-200 bg-white p-5">

            <div className="mb-2 font-semibold text-indigo-700">

              💡 Hint {hintLevel}

            </div>

            <p className="leading-7 text-gray-700 whitespace-pre-line">

              {hint}

            </p>


            {/* ===============================================
                STRONGER HINT
                =============================================== */}

            {hintLevel < 3 && (

              <button
                onClick={() => {

                  setHintLevel(
                    (previous) =>
                      previous + 1
                  )

                  setHint('')

                  setHintError('')

                }}
                className="mt-4 rounded-lg border border-indigo-300 px-4 py-2 text-sm font-medium text-indigo-700 hover:bg-indigo-50 transition"
              >

                Get Stronger Hint →

              </button>

            )}


            {/* ===============================================
                FINAL HINT
                =============================================== */}

            {hintLevel === 3 && (

              <div className="mt-4 text-xs font-medium text-gray-500">

                You've reached the final hint. Try implementing
                the idea yourself before checking a full solution.

              </div>

            )}

          </div>

        )}

      </div>


      {/* =====================================================
          SUBMIT ANOTHER
          ===================================================== */}

      <div className="mt-10 flex justify-center">

        <Link
          to="/submit"
          className="text-sm font-medium text-board-faint hover:text-board-ink transition-colors"
        >

          ← Submit another solution

        </Link>

      </div>

    </div>

  )

}