# DSA Coach — Full Build Plan & Agent IDE Prompt

## How to use this document

Paste this entire file to your agent IDE (Claude Code, Cursor, Windsurf, etc.) as the first message, along with an instruction like:

> "Build this project following the plan below. Work through the phases in order. After each phase, show me what you built before moving to the next one."

Everything below is written to be directly buildable — schema, personas, API contract, design system, folder structure, and run commands are all spelled out so the agent doesn't have to guess.

---

## 1. Project overview

**DSA Coach** — a web app where you solve LeetCode-style problems in a code editor, and an AI coach (with a selectable personality) reacts to your approach in real time. It notices inefficient patterns (nested loops where a hash map would work, etc.), comments in character, and changes expression. Hints are click-gated and tiered so it nudges rather than spoils. A chat panel lets you ask it anything. Code actually executes against real test cases at the end.

**Scope for v1 (prototype)**: 5 fixed "easy" LeetCode problems, Python only, no accounts/persistence, 3 selectable personas (Walter White, Kratos, Thanos — used as tone/personality references for original commentary, not verbatim quotes or likenesses; images will be added later by the user). This is a prototype — the priority is a tight, working core loop and a frontend that feels genuinely polished, not breadth of content.

---

## 2. Final tech stack

| Piece | Tool | Why |
|---|---|---|
| Frontend | React + Vite | Fast dev loop, standard choice |
| Code editor | Monaco Editor | Free, VS Code's actual editor |
| Backend | FastAPI (Python) | Matches the AST-analysis language, lightweight |
| Problem data | Plain JSON files | 5 fixed problems = direct lookup, no DB needed |
| Pattern detection | Python `ast` module, rule-based | Instant, free, deterministic |
| LLM | Groq API, model `openai/gpt-oss-120b` (`openai/gpt-oss-20b` for even lower latency) | Free tier, no card, very low latency |
| Code execution | Piston public API | Free, no key, sandboxed |
| Styling | Tailwind CSS + custom design tokens (see section 7) | Fast to build, but driven by an intentional dark theme, not defaults |

No vector DB, no multi-agent LLM chains, no paid services anywhere in this stack.

---

## 3. Folder structure

```
dsa-coach/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py                 # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── problems.py           # GET /problems, /problems/{id}
│   │   │   ├── analyze.py            # POST /analyze
│   │   │   ├── hint.py               # POST /hint
│   │   │   ├── chat.py               # POST /chat
│   │   │   └── execute.py            # POST /execute
│   │   ├── services/
│   │   │   ├── ast_analyzer.py       # anti-pattern detection engine
│   │   │   ├── llm_client.py         # Groq API wrapper
│   │   │   └── piston_client.py      # code execution wrapper
│   │   ├── personas/
│   │   │   └── personas.json         # the 3 persona system prompts
│   │   └── data/
│   │       └── problems/             # one JSON file per problem
│   │           ├── two-sum.json
│   │           ├── valid-parentheses.json
│   │           ├── best-time-to-buy-sell-stock.json
│   │           ├── contains-duplicate.json
│   │           └── valid-anagram.json
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProblemSelector.jsx
│   │   │   ├── PersonaSelector.jsx
│   │   │   ├── CodeEditor.jsx
│   │   │   ├── AvatarPanel.jsx
│   │   │   ├── HintPanel.jsx
│   │   │   ├── ChatPanel.jsx
│   │   │   └── ResultsPanel.jsx
│   │   ├── hooks/
│   │   │   └── useDebouncedAnalyze.js
│   │   ├── styles/
│   │   │   └── tokens.css            # design tokens from section 7
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

---

## 4. Problem data schema

Each problem is one JSON file. **Important**: `optimal`, `anti_patterns`, and `hints` are never sent to the frontend directly — only the backend reads them to build LLM context and detect patterns. The frontend only ever gets `id`, `title`, `difficulty`, `description`, `starter_code`, and `test_cases` (inputs/outputs, not the solving logic).

```json
{
  "id": "two-sum",
  "leetcode_id": 1,
  "title": "Two Sum",
  "difficulty": "Easy",
  "description": "Given an array of integers and a target, return indices of the two numbers that add up to target.",
  "function_signature": "def two_sum(nums: list[int], target: int) -> list[int]:",
  "starter_code": "def two_sum(nums, target):\n    pass",
  "test_cases": [
    {"input": {"nums": [2,7,11,15], "target": 9}, "expected": [0,1]},
    {"input": {"nums": [3,2,4], "target": 6}, "expected": [1,2]}
  ],
  "brute_force": {
    "approach": "Nested loop comparing every pair",
    "complexity": "O(n^2) time, O(1) space"
  },
  "optimal": {
    "approach": "Single pass with a hash map storing seen values and their indices",
    "complexity": "O(n) time, O(n) space",
    "key_insight": "For each number, check if (target - number) was already seen instead of scanning ahead"
  },
  "anti_patterns": [
    {
      "rule": "nested_loop_over_same_array",
      "description": "Two nested for-loops both iterating over nums — classic brute force signal",
      "explanation": "This checks every pair, which is O(n^2). You don't need to re-scan the array if you remember what you've already seen."
    }
  ],
  "hints": [
    "What if you didn't need to look ahead at all — only back at what you've already seen?",
    "A hash map storing each number's index as you go lets you check for its complement instantly.",
    "For each num in nums: if target - num is already a key in your map, you're done — return [map[target-num], current_index]. Otherwise add num to the map."
  ]
}
```

Build this same structure for all 5 problems — chosen to cover 5 distinct patterns rather than 5 variations on the same idea:

1. **Two Sum** (LC 1) — brute force nested loop → optimal hash map
2. **Valid Parentheses** (LC 20) — brute force repeated string replacement → optimal stack
3. **Best Time to Buy and Sell Stock** (LC 121) — brute force check every pair of days → optimal single pass tracking min price
4. **Contains Duplicate** (LC 217) — brute force nested loop comparison → optimal set/hash lookup
5. **Valid Anagram** (LC 242) — brute force sorting both strings → optimal character frequency count

For each, write 1 anti-pattern rule (in AST-detectable terms — "nested loops," "no stack/list used for matching," "uses `sorted()` where a single pass suffices," etc.) and 3 tiered hints (vague → names the technique → near-pseudocode), following the Two Sum example above.

*(Once the prototype loop is solid, the same schema extends cleanly to more problems — Maximum Subarray, Climbing Stairs, Binary Search, Reverse Linked List, Merge Two Sorted Lists are natural next additions.)*

---

## 5. Personas

Three selectable personas for v1. These are used as **tone and personality references only** — the LLM should generate original commentary that captures the *energy* of each character, never verbatim lines from any show, game, or film.

```json
{
  "walter_white": {
    "display_name": "Walter White",
    "voice": "Calm, controlled, quietly intimidating. Speaks precisely, like every word is deliberate. Uses chemistry/precision metaphors naturally. Doesn't raise his voice even when the code is bad — the calm is the threat.",
    "tone_examples": ["neutral_thinking", "playful_warning", "disappointed", "impressed", "celebrating", "encouraging"]
  },
  "kratos": {
    "display_name": "Kratos",
    "voice": "Gruff, blunt, permanently intense. Short sentences. Calls out inefficiency like it's a personal insult. Rare, grudging approval when the user does something right. Battle/strength metaphors.",
    "tone_examples": ["neutral_thinking", "playful_warning", "disappointed", "impressed", "celebrating", "encouraging"]
  },
  "thanos": {
    "display_name": "Thanos",
    "voice": "Calm, philosophical, faintly condescending. Talks about efficiency and 'balance' like it's inevitable. Treats bad time complexity as a personal failure of the user to understand necessity.",
    "tone_examples": ["neutral_thinking", "playful_warning", "disappointed", "impressed", "celebrating", "encouraging"]
  }
}
```

The `tone` field returned by the LLM (see API contract below) is what the frontend uses to pick the avatar expression — same 6 states across all 3 personas, so swapping personas doesn't require rebuilding the state machine.

---

## 6. API contract

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/problems` | GET | — | List of `{id, title, difficulty}` for all 5 |
| `/problems/{id}` | GET | — | `{description, starter_code, test_cases}` — no solution data |
| `/analyze` | POST | `{problem_id, code, persona}` | `{triggered: bool, comment, tone, hint_available}` |
| `/hint` | POST | `{problem_id, tier, persona}` | `{hint_text}` |
| `/chat` | POST | `{problem_id, message, history, persona}` | `{reply}` |
| `/execute` | POST | `{problem_id, code}` | `{passed: bool, results: [{input, expected, actual, passed}]}` |

`/analyze` flow inside the backend:
1. Run `ast_analyzer.py` against the code diff — check it against this problem's `anti_patterns` rules.
2. If nothing matches, return `{triggered: false}` immediately (no LLM call — saves latency and quota).
3. If a rule matches, build a prompt from that persona's `voice` + the matched anti-pattern's `explanation`, call Groq, and require a structured JSON response:
   ```json
   {"comment": "...", "tone": "playful_warning", "hint_available": true}
   ```
4. Return that to the frontend.

`tone` must be one of: `neutral_thinking`, `playful_warning`, `disappointed`, `impressed`, `celebrating`, `encouraging`.

Session state (which hint tier is unlocked, chat history) lives in **frontend React state only** — sent back with each request. No backend session storage needed for v1, which keeps the backend fully stateless and easy to host for free.

---

## 7. Design system — dark, distinctive, not a template

The brief is "very attractive, dark-themed, best-looking UI" — that's a real design brief, not just "make it dark." Two clichés to deliberately avoid: the generic near-black-with-acid-green "hacker" look, and a flat, undifferentiated dark grey with no accent identity. Instead, lean into what this product actually is: a late-night debugging session with a character watching over your shoulder.

**Color tokens** (define these as CSS variables in `tokens.css`, reference everywhere — never hardcode hex in components):

| Token | Hex | Use |
|---|---|---|
| `--ink` | `#0A0C10` | App background — near-black with a cold blue undertone, not flat grey |
| `--panel` | `#14171F` | Raised surfaces — editor card, persona card, panels |
| `--panel-line` | `#242836` | Hairline borders between panels |
| `--ember` | `#FF8A3D` | Primary accent — persona attention, active editor glow, "thinking" state |
| `--signal` | `#4FD8B5` | Success/optimal state — passing tests, "impressed"/"celebrating" tones |
| `--alert` | `#FF5C5C` | Roast/anti-pattern flare — "disappointed"/warning tones |
| `--ash` | `#9AA3B2` | Secondary/muted text |
| `--fog` | `#E7E9EE` | Primary text on dark backgrounds |

This gives the tone system a real visual language instead of an arbitrary color swap: amber while it's "thinking," red flare when it roasts a bad pattern, teal glow when you're doing it right. The color *is* the feedback, not just a decoration next to it.

**Typography** — three roles, chosen for the subject instead of generic defaults:
- **Display / persona name plates & headers**: `Space Grotesk` — geometric, a little unusual, used sparingly (problem title, persona name, section labels)
- **Code & data**: `JetBrains Mono` — for the editor itself, and reused deliberately for the comment feed and hint text, so the coach's commentary visually reads like terminal output, not a chat bubble
- **UI / body chrome**: `Inter` — buttons, descriptions, everything else that just needs to be legible

**Layout concept** — split workspace, editor-dominant:

```
┌──────────────────────────────────┬──────────────────┐
│  [ Two Sum ▾ ]         [Walter ▾]│  ┌─────────────┐  │
│ ┌────────────────────────────┐   │  │   PERSONA   │  │
│ │                             │   │  │   PORTRAIT  │  │
│ │   Monaco editor             │   │  │ (glow ring) │  │
│ │   (ember-glow border        │   │  └─────────────┘  │
│ │    while a comment is       │   │  > comment line   │
│ │    being generated)         │   │  > comment line   │
│ │                             │   │  ─────────────────│
│ └────────────────────────────┘   │  [Hint] [Chat][Run]│
└──────────────────────────────────┴──────────────────┘
```

Editor takes ~60% of the width and is the visual anchor — this is a coding tool first. The right column is a fixed-width sidebar: persona portrait card on top, a scrolling terminal-style comment feed below it (each new line prefixed with a `>` prompt glyph, monospace), and a docked control strip (Hint / Chat / Run) at the bottom.

**Signature element**: the persona portrait card has an animated glow ring around its frame, and that ring is the single place all the "reactivity" lives — it pulses slowly in `--ember` while idle/thinking, flashes once in `--alert` when a roast comment fires, and holds a steady `--signal` glow when tests pass. Everything else in the UI stays still. One deliberate, orchestrated motion moment instead of animations scattered across every button and panel — that restraint is what will make it feel premium instead of AI-generated-default.

**Motion rules**: only the glow ring and the comment feed's line-by-line reveal (like text being typed) animate by default. Hover states on buttons should be subtle (border/glow brightening, not scale/bounce). Respect `prefers-reduced-motion` — fall back to a static colored ring instead of pulsing.

**Quality floor**: visible keyboard focus states on every interactive element (a 2px `--ember` outline works well against `--ink`), responsive down to a single-column stacked layout on mobile (editor on top, sidebar below), and sufficient contrast between `--fog` text and `--panel`/`--ink` backgrounds.

---

## 8. Frontend components

- **ProblemSelector** — dropdown/list of the 5 problems, styled with the Space Grotesk display face
- **PersonaSelector** — pick Walter White / Kratos / Thanos before starting
- **CodeEditor** — Monaco instance (dark theme matched to `--ink`/`--panel`), debounces onChange (2-3s pause) and fires `/analyze`; border glows `--ember` while a request is in flight
- **AvatarPanel** — the persona portrait card with the animated glow ring described in section 7; shows the current persona's static image for the current `tone` state (placeholder image per persona/tone until real images are added)
- **CommentFeed** — terminal-style scrolling log of past comments, monospace, `>` prompt prefix, new lines animate in
- **HintPanel** — "Get a hint" button, tracks unlocked tier in local state, calls `/hint`
- **ChatPanel** — free-text input, keeps message history in state, calls `/chat`
- **ResultsPanel** — "Run" button calls `/execute`, shows pass/fail per test case with `--signal`/`--alert` coloring

---

## 9. Step-by-step build phases

**Phase 0 — Scaffolding**
Set up the folder structure above. Initialize FastAPI backend and Vite+React+Tailwind frontend as separate apps. Set up `tokens.css` with the section 7 color/type variables before building any component.

**Phase 1 — Problem data**
Write the 5 problem JSON files following the schema in section 4. Write a small loader in the backend that reads all files from `data/problems/` at startup.

**Phase 2 — Public problem endpoints**
Build `GET /problems` and `GET /problems/{id}`, making sure only the public fields are returned (never leak `optimal`, `anti_patterns`, or `hints` to these endpoints).

**Phase 3 — AST anti-pattern detector**
Build `ast_analyzer.py`: parse submitted code with Python's `ast` module, walk the tree, and check it against the current problem's `anti_patterns` rules (e.g., count nested `For` nodes, check for absence of `Dict`/`Set` usage). Return which rule (if any) matched.

**Phase 4 — Groq LLM client**
Build `llm_client.py`: given a persona + matched anti-pattern explanation (or a chat message), call the Groq API and require structured JSON output (`comment`, `tone`, `hint_available`). Handle malformed JSON gracefully (retry once, then fall back to a generic response).

**Phase 5 — `/analyze`, `/hint`, `/chat` endpoints**
Wire phases 3 and 4 together behind these three routes, following the API contract in section 6.

**Phase 6 — Piston execution**
Build `piston_client.py` to send code + test case inputs to the Piston public API and compare actual vs. expected output. Wire up `/execute`.

**Phase 7 — Frontend shell & design system**
Build the React app skeleton following the layout concept and tokens in section 7 exactly — this phase is where the "attractive, best-looking UI" requirement gets built, not an afterthought bolted on later.

**Phase 8 — Wire up the live loop**
Connect `CodeEditor`'s debounced changes to `/analyze`, update `AvatarPanel`'s glow ring + `CommentFeed` based on returned `tone`/`comment`.

**Phase 9 — Hints and chat**
Wire `HintPanel` to `/hint` (tracking tier client-side), and `ChatPanel` to `/chat` (tracking history client-side).

**Phase 10 — Execution and results**
Wire the "Run" button to `/execute`, display pass/fail per test case in `ResultsPanel`.

**Phase 11 — Polish**
Persona switching mid-session, loading states, error handling if Groq/Piston are briefly unavailable, mobile responsive layout, keyboard focus states, reduced-motion fallback.

---

## 10. Setup & run instructions

**Get a Groq API key** (free, no card): sign up at console.groq.com with email or Google, generate a key from the API Keys page.

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install fastapi uvicorn python-dotenv groq
cp .env.example .env            # add GROQ_API_KEY=your_key_here
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm install @monaco-editor/react
npm run dev
```

Fonts: pull `Space Grotesk`, `JetBrains Mono`, and `Inter` from Google Fonts (all free, no license issues) and load them in `index.html` or via `@font-face` in `tokens.css`.

Open the frontend's local URL (Vite default: `http://localhost:5173`), make sure it's pointed at the backend (`http://localhost:8000`), pick a problem and a persona, and start coding.

---

## 11. Notes for the agent

- Keep the anti-pattern detection fully deterministic (plain `ast` module code) — no LLM call for detection itself, only for phrasing the comment once a rule fires.
- Never expose `optimal`, `anti_patterns`, or `hints` fields to any endpoint the frontend calls directly except through `/hint` (and even then, only the current tier's text, not the whole list).
- Persona commentary must be original text inspired by each character's tone — do not have the LLM reproduce actual quotes from any film, show, or game.
- No vector DB, no multi-step LLM chains — one deterministic check, one LLM call per interaction, by design.
- Follow the design tokens in section 7 exactly rather than defaulting to generic Tailwind dark-mode grays — the color and type choices are deliberate, not placeholders.
- This is a prototype: 5 problems, no accounts. Don't add scope beyond what's specified here without asking first.
