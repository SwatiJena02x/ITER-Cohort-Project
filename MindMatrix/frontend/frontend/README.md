# DSA Coach AI — Frontend

React + Vite + Tailwind frontend for the DSA Coach AI backend (FastAPI +
LangGraph multi-agent feedback pipeline).

## Setup

```bash
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if your backend isn't on :8000
npm run dev
```

The app runs at `http://localhost:5173` and expects the backend at
`http://127.0.0.1:8000` by default (matches `main.py`'s `uvicorn.run`
config). Make sure the backend's CORS middleware allows this origin —
it currently allows `*`, so no changes are needed in dev.

## Pages

- **`/`** — Home: explains the six-agent grading pipeline.
- **`/submit`** — Submission form: problem, approach, and a code editor.
  Calls `POST /feedback/analyze` and routes to `/feedback` with the result.
- **`/feedback`** — Displays the graded `FinalFeedback` response: score,
  correctness, complexity, strengths/weaknesses/suggestions, interview
  verdict, and learning plan. Reads from router state, so it only shows
  data after a submission (refreshing this page directly shows an empty
  state with a link back to `/submit`).

## Structure

```
src/
  components/   Navbar, CodeEditor, FeedbackCard, ScoreDial
  pages/        Home, SubmitSolution, Feedback
  services/     api.js — axios client wired to the backend
```

## Notes

- The backend's `FinalFeedback` schema is the single source of truth for
  the feedback shape (see `schemas/response.py`). If you add fields there,
  add a matching `FeedbackCard` in `Feedback.jsx`.
- `services/api.js` exports `getErrorMessage()` which unwraps FastAPI's
  `{ detail }` error shape for display.
