# Offline AI Proctoring System — Documentation

A LangGraph multi-agent pipeline that analyzes exam-session video for
suspicious activity (unauthorized objects, multiple people, speech),
produces a risk-scored report, and routes it to a human reviewer for a
final decision. Runs entirely offline/locally (Whisper for speech,
DETR for object detection, a local Ollama LLM for explanation) with
LangSmith tracing throughout. Includes a Streamlit UI backed by
PostgreSQL for account management, video upload, and report delivery.

---

## 1. Architecture

### 1.1 Pipeline flow

```
START
  │
  ▼
video_agent      — extract frames (1/sec), run DETR object detection
  │
  ▼
audio_agent      — extract audio track (ffmpeg), transcribe (Whisper)
  │
  ▼
behavior_agent   — merge external event log + multi-person detection
  │
  ▼
activity_agent   — collapse raw evidence into readable, merged segments
  │
  ▼
risk_agent       — score the merged activity → risk_score + risk_level
  │
  ├─ LOW ──────────────────────────────┐
  │                                    │
  └─ MEDIUM/HIGH                       │
       │                               │
       ▼                               │
  synthesis_agent  ── hybrid RAG ──    │
  (rule_chunks → FAISS + BM25 index    │
   [built once, cached]; activity      │
   text → dense search + keyword       │
   search → Reciprocal Rank Fusion     │
   → top-5 rules → LLM prompt →        │
   call_llm() → risk_reason;           │
   skipped entirely for LOW)           │
       │      ▲                        │
       │      │ retry (malformed       │
       │      │ response, capped)      │
       │      └────────────┐           │
       │                   │           │
       ▼                   │           ▼
       └──────────► report_agent ◄─────┘
                         │
                         ▼
                  human_review_agent
                         │
                         ▼
                        END
```

The RAG layer (chunking → dense + sparse indexing/retrieval → fusion →
LLM call) lives entirely **inside** the `synthesis_agent` node — it isn't
a separate node in the graph, and only executes for MEDIUM/HIGH sessions
(a LOW-risk session skips this box entirely via the conditional edge).
See Section 6 for the RAG breakdown and Section 7 for the retry loop.

Built and compiled in `graph/workflow.py`; the routing decision
(skip `synthesis` for LOW risk) lives in `_route_after_risk`.

### 1.2 Two entry points, one graph

Both entry points call the exact same compiled graph
(`graph.workflow.app`) — there is no duplicated pipeline logic between
them:

| Entry point | Trigger | Runs on |
|---|---|---|
| `main.py` | `python main.py video.mp4` | Foreground, blocks until done |
| Streamlit UI (`app.py` → `worker.py`) | Upload button click | Background thread (bounded pool, max 2 concurrent) |

The UI never calls the graph directly from a page — `pages/2_Upload_Video.py`
hands the job to `worker.submit_job()`, which runs it on a background
thread so the browser/page isn't blocked for the several minutes a full
analysis can take. The UI and the background thread only communicate
through the `proctoring_jobs` Postgres table (write status from the
worker thread, poll status from the report page) — there is no direct
in-memory link between them.

### 1.3 State

All nodes read from and write to one shared dictionary, typed as
`ProctoringState` (`graph/state.py`). Key groups:

- **Raw evidence** (what actually happened, frame/segment-level):
  `video_evidence`, `audio_evidence`, `behavior_evidence`
- **Activity** (merged, human-readable, what gets displayed and scored):
  `video_activity`, `audio_activity`, `behavior_activity`
- **Risk**: `risk_score`, `risk_level`, `risk_reason`, `retrieved_rules`
- **Synthesis retry loop**: `synthesis_attempts`, `synthesis_valid` (see Section 7)
- **Output**: `final_report`, `human_review`
- **Debug**: `step_history` (list of node names, in execution order)

---

## 2. Project layout

```
proctoring_system/
├── main.py                    CLI entry point
├── app.py                     Streamlit UI entry point (login)
├── worker.py                  Background job runner (ThreadPoolExecutor)
├── requirements.txt
├── .env.example
│
├── agents/                    LangGraph nodes
│   ├── video_agent.py
│   ├── audio_agent.py
│   ├── behavior_agent.py
│   ├── activity_agent.py
│   ├── risk_agent.py
│   ├── synthesis_agent.py
│   ├── report_agent.py
│   └── human_review_agent.py
│
├── graph/
│   ├── state.py                ProctoringState schema
│   └── workflow.py             Graph assembly + routing
│
├── rag/
│   ├── exam_rules.py           EXAM_RULES_TEXT constant + rule splitter
│   ├── chunker.py              Generic word-count chunker (unused currently)
│   ├── embeddings.py           sentence-transformers wrapper
│   ├── retriever.py            FAISS (dense) index build/search
│   ├── bm25_retriever.py       BM25 (sparse/keyword) index build/search
│   └── hybrid.py               Reciprocal Rank Fusion -- merges dense + sparse
│
├── llm/
│   ├── ollama_client.py        Traced call_llm() wrapper
│   └── langsmith_utils.py      tag_current_run() / log_current_run_metadata()
│
├── video_processing/frame_extractor.py
├── vision/object_detector.py
├── audio/audio_extractor.py    Includes has_audio_stream() pre-check
│
├── db/                         Streamlit UI: Postgres access
│   ├── database.py             Connection pool + schema (calls load_dotenv())
│   ├── auth.py                 Signup/login (bcrypt)
│   └── jobs.py                 proctoring_jobs CRUD
├── pages/
│   ├── 1_Create_Account.py
│   ├── 2_Upload_Video.py
│   └── 3_Report.py
│
├── legacy/                     Not wired into the graph -- kept for reference
│   ├── rule_engine.py
│   └── proctoring_llm.py
│
└── data/
    ├── videos/uploads/         UI-uploaded videos land here
    ├── frames/                 Per-run extracted JPEG frames
    ├── audio/                  Per-run extracted .wav files
    └── events/events.json      Optional external event log for behavior_agent
```

---

## 3. Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # fill in your actual values

# Ollama must be running locally with the model pulled:
ollama pull llama3.2

# ffmpeg must be on PATH:
ffmpeg -version
```

### 3.1 Configuration (`.env`)

```ini
# LangSmith tracing (optional -- pipeline runs fine with this unset)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=your_project_name

# Ollama
OLLAMA_HOST=http://127.0.0.1:11434

# Postgres (Streamlit UI only)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=proctoring_db
DB_USER=postgres
DB_PASSWORD=your_password
```

`db/database.py` calls `load_dotenv()` itself, so `.env` is loaded
correctly regardless of whether the CLI (`main.py`) or the UI (`app.py`)
is the entry point.

> **Never commit `.env` or paste its contents anywhere.** If a real
> secret (API key, DB password) is ever exposed, rotate it immediately.

### 3.2 Database (UI only)

```bash
createdb proctoring_db   # or point DB_NAME at an existing database
```

Tables (`users`, `proctoring_jobs`) are created automatically on first
launch via `db.database.init_db()` — no manual migration step needed.

---

## 4. Usage

### 4.1 CLI

```bash
python main.py path/to/exam_video.mp4
```

Prints the final report, human review, step history, and LangSmith run
ID to the console. Exit code `0` on success, `1` on failure.

### 4.2 UI

```bash
streamlit run app.py
```

Flow: create an account (`1_Create_Account.py`) → log in (`app.py`) →
upload a video (`2_Upload_Video.py`) → the pipeline runs in the
background → the report page (`3_Report.py`) polls status every
rerun/5-second auto-refresh and shows the report + a `.txt` download
once `DONE`.

---

## 5. Risk scoring reference

`agents/risk_agent.py` scores off the **merged activity segments**
(`video_activity`, `audio_activity`, `behavior_activity` — produced by
`agents/activity_agent.py`), not raw per-frame/per-segment evidence.
This means the score is always reconstructable by counting exactly what
the report displays — one displayed segment/block/event = one scored
item.

| Evidence type | Points per item | Notes |
|---|---|---|
| Video segment, peak confidence ≥ 0.80 | 4 | One continuous sighting = one item, regardless of duration |
| Video segment, peak confidence 0.50–0.79 | 2 | Below 0.50, the segment doesn't exist at all (filtered by `activity_agent`) |
| Audio block (merged continuous speech) | 2 | One merged block = one item, regardless of how many raw Whisper segments merged into it |
| Behavior event (e.g. multiple people) | 3 | Only counted after passing `behavior_agent`'s 2+ consecutive-frame filter |

**Risk level thresholds** (`risk_agent.py`):

| Score | Level |
|---|---|
| ≥ 10 | HIGH |
| 5–9 | MEDIUM |
| < 5 | LOW |

**Suspicious objects** (`agents/activity_agent.py`'s `SUSPICIOUS_OBJECTS`):
`cell phone`, `phone`, `laptop`, `tablet`, `book`, `remote`, `keyboard`,
`mouse`. **Open question, not yet resolved**: if the exam is taken on a
laptop, `laptop`/`keyboard`/`mouse` will flag the candidate's own
required device every time it's visible. Removing those three labels
(or making the suspicious-objects list configurable per exam) is a
one-line change in `activity_agent.py`, pending a decision on whether
that's the desired behavior for your use case.

**Multi-person detection filter** (`agents/behavior_agent.py`): a
`multiple_people` event only counts if 2+ people are detected across at
least `MIN_CONSECUTIVE_FRAMES = 2` consecutive sampled frames — a single
isolated frame (motion blur, someone briefly passing a window) does not
trigger a scored event.

---

## 6. RAG component (hybrid rule retrieval + LLM synthesis)

This is the retrieval-augmented generation layer: given a MEDIUM/HIGH
session, find the specific exam rules relevant to what was detected, and
ask a local LLM to explain the risk level grounded in that retrieved
text — not the LLM's own general knowledge of "exam rules" in the
abstract. Retrieval is **hybrid**: dense (semantic) search and sparse
(keyword) search run independently and get merged, rather than relying
on either alone. Seven files are involved, spanning `rag/`, `llm/`, and
`agents/synthesis_agent.py`.

### 6.1 RAG flow

```
rag/exam_rules.py
  EXAM_RULES_TEXT (constant)
        │
        │  split_into_rule_chunks()
        │  -- splits on "RULE N:" markers, NOT word count
        ▼
  rule_chunks: List[str]              (one chunk per rule, currently 8)
        │
        ├──────────────────────────────┬──────────────────────────────┐
        │                              │                              │
        ▼ dense                       ▼ sparse                        │
  rag/embeddings.py:            rag/bm25_retriever.py:                │
  create_embeddings(rule_chunks) build_bm25_index(rule_chunks)        │
  -- sentence-transformers,     -- rank_bm25.BM25Okapi over            │
     model "all-MiniLM-L6-v2"      tokenized chunk text                │
        │                              │                              │
        ▼                              ▼                              │
  rule_embeddings: np.ndarray    BM25Index                             │
  (8 x 384, L2-normalized)                                             │
        │                              │                              │
        ▼                              │                              │
  rag/retriever.py:                    │                              │
  create_index(rule_embeddings)        │                              │
  -- faiss.IndexFlatIP                 │                              │
     (exact search, inner product)     │                              │
        │                              │                              │
        ▼                              ▼                              │
  FAISS index  ─────────────────  BM25Index  ── both cached for the ──┘
                                              process lifetime
        (agents/synthesis_agent.py: _get_rule_indexes(), built once)
        │                              │
        │  at query time, per MEDIUM/HIGH session:
        │
   query text = risk level + score + formatted video/audio/behavior
                activity (from agents/activity_agent.py's format_*
                functions)
        │
        ├──────────────────────────────┐
        ▼ dense                        ▼ sparse
  create_embeddings([query])      bm25_index.search(query, top_k=5)
        │                              │
        ▼                              │
  retrieve_rules(index, ...,           │
    query_embedding, top_k=5)          │
        │                              │
        ▼ top-5 dense results          ▼ top-5 sparse results
        └──────────────┬───────────────┘
                        ▼
         rag/hybrid.py: reciprocal_rank_fusion([dense, sparse], top_k=5)
                        │
                        ▼
              top-5 fused rules, merged by rank position
                        │
                        │  embedded into the LLM prompt as context
                        │  llm/ollama_client.py: call_llm(prompt, model="llama3.2")
                        ▼
              LLM-generated explanation  ──►  state["risk_reason"]
                                               (overwrites risk_agent's
                                               raw mechanical version)
```

### 6.2 Component reference

| File | Role | Key detail |
|---|---|---|
| `rag/exam_rules.py` | Rule source of truth | `EXAM_RULES_TEXT` is a Python constant, not an external file — no filesystem dependency. `split_into_rule_chunks()` splits on `RULE \d+:` markers via regex lookahead, so each chunk is exactly one complete rule with its number intact. Edit rules by editing this constant directly. |
| `rag/chunker.py` | Generic word-count chunker | `chunk_text(text, chunk_size=80, overlap=20)` — sliding window over whitespace-split words. **Not currently used** for the exam rules (word-count chunking on an 8-rule document produced heavily overlapping near-duplicate chunks; rule-boundary splitting replaced it). Kept as a ready utility for a longer, less-structured document. |
| `rag/embeddings.py` | Text → vector (dense) | `create_embeddings(texts)` via `sentence-transformers`, model `all-MiniLM-L6-v2`. Embeddings are L2-normalized (`normalize_embeddings=True`), which is what makes FAISS's inner-product search mathematically equivalent to cosine similarity. The model itself is a cached, process-wide singleton (`get_embedder()`). |
| `rag/retriever.py` | Dense vector index + search | `create_index()` builds a `faiss.IndexFlatIP` — **exact**, brute-force search (not an approximate index), a deliberate choice given the rule set is only ~8 chunks. `retrieve_rules(..., top_k=5)` returns `{chunk_id, text, score}` dicts, ordered by descending similarity. `save_index`/`load_index` exist but are unused — the index is cheap enough to rebuild once per process. |
| `rag/bm25_retriever.py` | Sparse (keyword) index + search | `BM25Index` wraps `rank_bm25.BM25Okapi`. Scores purely on literal term overlap and term rarity — no notion of meaning at all, but catches an exact keyword match dense search alone can under-rank. Returns results in the same `{chunk_id, text, score}` shape as the dense side, so both merge identically. |
| `rag/hybrid.py` | Fusion | `reciprocal_rank_fusion(ranked_lists, top_k=5)` — merges the dense and sparse ranked lists by **rank position**, not raw score (`1/(RRF_K + rank + 1)` per list, summed per item), sidestepping the fact that cosine similarity and BM25 scores are on incomparable scales. `RRF_K = 60` is the standard constant from the original RRF paper. |
| `agents/synthesis_agent.py` | Orchestrates all of the above + calls the LLM | `_get_rule_indexes()` builds and caches **both** indexes for the process lifetime, on first use. Query text is built from `agents/activity_agent.py`'s `format_video_activity`/`format_audio_activity`/`format_behavior_activity` output, **not raw evidence** — so retrieval is grounded in the same merged, readable segments the report displays. |
| `llm/ollama_client.py` | LLM call | `call_llm(prompt, model="llama3.2", options={"temperature": 0.2})` — single traced wrapper around `ollama.chat()`, reused by `synthesis_agent`, `report_agent`, and `human_review_agent`. Low temperature (0.2) favors consistent, factual output over creative variation. |

### 6.3 Why hybrid, not dense-only

Dense (embedding) search matches on *meaning* — it can find a rule about
"secondary computing devices" from a query saying "unauthorized laptop",
even with zero word overlap. What it can under-rank is an exact,
distinctive keyword: a query mentioning "keyboard" specifically can rank
a generically-similar "electronic devices" rule above the one rule that
actually says "keyboard" verbatim, because embedding similarity is about
overall meaning, not exact terms. BM25 has no notion of meaning at all,
but is very good at exactly this case. Fusing both means a session gets
the better of two different failure modes, not just one method's blind
spots.

### 6.4 When RAG runs, and the fallback if it fails

`synthesis_agent` only executes for MEDIUM/HIGH sessions — routed via
`graph/workflow.py`'s conditional edge after `risk_agent` (Section 1.1).
A LOW-risk session skips the entire RAG pipeline: no embedding pass, no
BM25 search, no LLM call, since there's nothing suspicious to explain
against the rules.

If the LLM call itself fails (Ollama unreachable, model not pulled,
etc.), `synthesis_agent` catches the exception and falls back to
`risk_agent`'s original deterministic `risk_reason` text, with a note
appended that AI synthesis was unavailable — and does **not** trigger
the retry loop (Section 7); a connection failure isn't something retrying
will fix. Retrieval itself (embedding + FAISS + BM25 + fusion) is not
wrapped in that same fallback — it has no external network dependency,
unlike the LLM call, so it's treated as unlikely to fail and always runs.

---

## 7. The retry loop

`synthesis_agent` is wired into `graph/workflow.py` with the one genuine
loop in an otherwise straight-line graph: a conditional edge that can
route back to `synthesis_agent` itself, not just forward.

**Why**: an LLM occasionally returns a response missing one or more
required section headers (`RISK LEVEL:`, `ACTIVITY:`, `RULES:`,
`EXPLANATION:`) — not a call failure, just a malformed-but-successful
response. That's specifically worth retrying (with a corrective note
added to the prompt on the second attempt), where a genuine connection
failure is not.

```python
# graph/workflow.py
def _route_after_synthesis(state):
    if state.get("synthesis_valid", True):
        return "report"
    return "retry"

graph.add_conditional_edges(
    "synthesis",
    _route_after_synthesis,
    {"retry": "synthesis", "report": "report"},   # "retry" -> itself
)
```

`agents/synthesis_agent.py` tracks this via two state fields:
`synthesis_attempts` (incremented each run) and `synthesis_valid` (set
`True` once the response is well-formed **or** the attempt cap
`MAX_SYNTHESIS_ATTEMPTS = 2` is reached — either way, the loop exits and
routes to `report_agent`). A genuine LLM call failure sets
`synthesis_valid = True` immediately, regardless of attempt count, so a
connection outage never triggers a retry.

---

## 8. Observability (LangSmith)

Every node (`video`, `audio`, `behavior`, `activity`, `risk`,
`synthesis`, `report`, `human_review`) is individually traced via
`@traceable`, plus the embedding/retrieval/LLM calls inside them. Two
tagging mechanisms work together to make HIGH-risk sessions
filterable/alertable in the LangSmith UI:

- **Node-level**: `risk_agent` tags its own span (`risk-{LEVEL}`, plus
  `HIGH-RISK-ALERT` for HIGH) the instant the score is computed
  (`llm/langsmith_utils.py`'s `tag_current_run`).
- **Root-run level**: `main.py` (CLI) and `worker.py` (UI) both tag the
  entire run with the same scheme once the graph finishes.

Both tagging calls are best-effort and never raise — tracing failures
never affect pipeline correctness.

---

## 9. Known limitations / open items

- **Laptop/keyboard/mouse as suspicious objects** — see Section 5. Not
  yet resolved; pending a decision on whether to exclude the candidate's
  own required exam device.
- **`SUSPICIOUS_OBJECTS`-adjacent duplication**: `report_agent.py`'s
  `_format_rules` and `human_review_agent.py`'s `_format_rules` are
  near-identical (one joins with `"\n\n"`, the other `"\n"`) — a minor,
  cosmetic drift from not sharing one implementation.
- **`main.py`/`worker.py` initial-state duplication**: both files
  independently build the same "fresh state" dictionary. Adding a new
  `ProctoringState` field requires updating both by hand.
- **`data/events/events.json` is a single shared path**, not per-session
  — fine for the current design (no code currently writes to it), but
  would need to become per-job if a live external event feed is ever
  added.
- **`rag/chunker.py`'s generic word-count chunker** and
  **`rag/retriever.py`'s `save_index`/`load_index`** are currently
  unused (kept as ready-to-use utilities for a larger, less-structured
  rules document than the current 8-rule set).
- **`vision/object_detector.py`'s `detect_objects_batch`** is
  implemented but not called — `video_agent.py` currently detects one
  frame at a time; batching would likely improve throughput on a GPU for
  longer videos.
- **Docker packaging**: not yet built. If/when containerized,
  `DB_HOST=postgres` (a Docker Compose service name) is correct *only*
  when the app itself also runs inside the same Compose network — it
  will fail with a DNS resolution error if the app is run locally
  outside Docker while `.env` still points at that hostname.

---

## 10. Troubleshooting quick reference

| Symptom | Likely cause | Where to look |
|---|---|---|
| `could not translate host name "postgres"` | `.env` `DB_HOST` set to a Docker service name, but the app isn't running inside that Docker network | `.env` → set `DB_HOST=localhost` for local runs |
| `password authentication failed for user "postgres"` | `.env` not being loaded (missing `load_dotenv()`), wrong variable names, or an actual wrong password | Confirm `db/database.py` calls `load_dotenv()`; verify `.env` variable names match exactly what `database.py` reads |
| `0 speech segments transcribed` | Three distinct causes, now individually logged by `audio_agent.py`: no audio track in source video / extraction-transcription failure (check the `ERROR` log line) / audio present but genuinely silent | Console output now states which of the three it is directly |
| Risk score doesn't match what the report visually shows | Should no longer happen after the Section 5 scoring change — score is now computed from the same merged segments displayed | If it still happens, check whether the item in question ever became an `activity` segment at all (confidence may be below `LOW_CONFIDENCE_THRESHOLD = 0.50`) |
| Duplicate rule text / `RULE 0` in synthesis output | Fixed — rules are chunked one-per-`RULE N:` marker, not by word count, and no longer re-labeled with a fake chunk index | N/A, already resolved |

---

For a full line-by-line walkthrough of every file (concepts, alternatives
considered, and why each design choice was made), see the separate
7-part beginner's guide delivered earlier in this conversation.
