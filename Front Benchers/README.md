# DSA Coach

**AI-Powered DSA Coaching with Character Personas**

Solve LeetCode-style problems in a Monaco code editor while an AI coach (Walter White, Kratos, or Thanos) reacts to your approach in real time. It detects inefficient patterns using AST analysis, comments in character, and changes expression. Hints are tiered so it nudges rather than spoils. Code executes against real test cases.

---

## Features

- **5 Classic LeetCode Problems**: Two Sum, Valid Parentheses, Best Time to Buy/Sell Stock, Contains Duplicate, Valid Anagram
- **3 Selectable Personas**: Walter White (chemistry metaphors), Kratos (battle metaphors), Thanos (cosmic balance metaphors)
- **Real-time Code Analysis**: AST-based anti-pattern detection triggers in-character AI commentary
- **Tiered Hint System**: 3 levels per problem (nudge → technique → near-pseudocode), delivered in persona voice
- **In-character Chat**: Ask the coach anything about the problem
- **Code Execution**: Run your solution against test cases with pass/fail results
- **Premium Dark Theme**: Cold blue undertone, ember/signal/alert feedback colors, animated glow ring

## Tech Stack

| Piece | Tool |
|---|---|
| Frontend | React + Vite + TailwindCSS |
| Code Editor | Monaco Editor |
| Backend | FastAPI (Python) |
| Pattern Detection | Python `ast` module (deterministic) |
| LLM | Groq API (llama-3.3-70b-versatile) |
| Code Execution | Local subprocess (sandboxed) |
| Styling | Custom design tokens + Tailwind |

## Setup & Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- A Groq API key (free at [console.groq.com](https://console.groq.com))

### Backend

```bash
cd backend
# Create and activate virtual env (or use the project-root venv)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Set your Groq API key
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=your_key_here

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — pick a problem, choose a persona, and start coding!

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/problems` | GET | List all 5 problems |
| `/problems/{id}` | GET | Get problem detail (public fields only) |
| `/analyze` | POST | Analyze code for anti-patterns, get AI comment |
| `/hint` | POST | Get a tiered hint in persona's voice |
| `/chat` | POST | Chat with the persona about the problem |
| `/execute` | POST | Run code against test cases |

## Design System

| Token | Color | Use |
|---|---|---|
| `--ink` | `#0A0C10` | App background |
| `--panel` | `#14171F` | Raised surfaces |
| `--ember` | `#FF8A3D` | Primary accent, thinking state |
| `--signal` | `#4FD8B5` | Success, impressed/celebrating |
| `--alert` | `#FF5C5C` | Warning, anti-pattern detected |
| `--fog` | `#E7E9EE` | Primary text |

Typography: Space Grotesk (display), JetBrains Mono (code/comments), Inter (UI)

## License

Prototype — built for the GenAI Cohort Project.
