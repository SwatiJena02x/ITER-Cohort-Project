# VectorVanguard

VectorVanguard is an offline, privacy-first system for investigating exam evidence after an exam has taken place. It ingests evidence images, extracts text and visual observations locally, stores them in PostgreSQL and ChromaDB, and lets an investigator ask natural-language questions answered by a LangGraph agent that is grounded strictly in retrieved evidence — no cloud AI API is required.

## Features

- Evidence ingestion: OpenCV preprocessing → Tesseract OCR + local vision model, run independently and merged before storage
- Structured visual observations (objects, electronic devices, seat number, environment) stored as JSONB alongside raw OCR text
- Hybrid retrieval: PostgreSQL full-text search + ChromaDB semantic search, fused with Reciprocal Rank Fusion
- LangGraph investigation agent that must call a retrieval tool before answering, and is instructed to only state what the evidence supports
- All AI inference (vision, embeddings, LLM reasoning) runs locally through Ollama

## Architecture

**Ingestion:**
```
Evidence Image → FastAPI (/upload-evidence) → OpenCV Preprocessing
   → Tesseract OCR  +  gemma3:4b Vision (run independently)
   → PostgreSQL (EvidenceRecord) + ChromaDB (nomic-embed-text embedding)
```

**Investigation:**
```
Question → FastAPI (/investigate) → LangGraph Agent (llama3.1:8b)
   → Hybrid Retrieval (PostgreSQL full-text + ChromaDB semantic, fused with RRF)
   → PostgreSQL Hydration → Grounded Investigation Answer
```

## Requirements

- Python 3.12
- Node.js (for the Vite/React frontend)
- PostgreSQL
- [Ollama](https://ollama.com)
- Tesseract OCR

---

## 1. Installation

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

*(macOS/Linux: `source .venv/bin/activate` instead of the `Activate.ps1` line.)*

### Frontend

```powershell
cd frontend
npm install
```

### Tesseract OCR

Install Tesseract for your OS. The app looks for it in this order:

1. `TESSERACT_PATH` in `backend/.env`, if set
2. `tesseract` resolved from your system `PATH`

### Ollama

```powershell
ollama pull nomic-embed-text
ollama pull gemma3:4b
ollama pull llama3.1:8b
```

---

## 2. Configuration

Create a PostgreSQL database matching `DB_NAME` in your `.env` (default `vectorvanguard_db`) using `psql` or pgAdmin.

```powershell
cd backend
Copy-Item .env.example .env
```

*(Equivalent to manually duplicating `.env.example` as `.env` and editing it.)*

| Variable | Required | Default | Notes |
|---|---|---|---|
| `DB_USER` | No | `postgres` | |
| `DB_PASSWORD` | **Yes** | — | No default; app fails to start without it |
| `DB_HOST` | No | `localhost` | |
| `DB_PORT` | No | `5432` | |
| `DB_NAME` | No | `vectorvanguard_db` | |
| `CHROMA_PERSIST_DIRECTORY` | No | `./storage/chroma` | Resolved relative to `backend/` |
| `CHROMA_COLLECTION_NAME` | No | `exam_evidence_vectors` | |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | |
| `OLLAMA_LLM_MODEL` | No | `llama3.1:8b` | Used by the investigation agent |
| `OLLAMA_EMBED_MODEL` | No | `nomic-embed-text:latest` | Used for ChromaDB embeddings |
| `OLLAMA_VISION_MODEL` | No | `gemma3:4b` | Used for image analysis during ingestion |
| `TESSERACT_PATH` | No | *(auto-detected)* | Set explicitly if `tesseract` isn't on PATH |

Frontend: copy `frontend/.env.example` to `frontend/.env`:

```
VITE_API_URL=http://127.0.0.1:8000
```

---

## 3. Database Setup

Schema is managed by Alembic:

```powershell
cd backend
alembic upgrade head
```

---

## 4. Running the Application

**Backend** (from `backend/`, app defined in `main.py`):

```powershell
uvicorn main:app --reload --port 8000
```

**Frontend** (from `frontend/`):

```powershell
npm run dev
```

**Health check:**

```
GET http://127.0.0.1:8000/health
```

**Environment diagnostic** (checks PostgreSQL connectivity, Alembic migration state, required Ollama models, Tesseract, and ChromaDB — see `backend/app/core/diagnostics.py`):

```powershell
python -m app.core.diagnostics
```

---

## 5. Testing

```powershell
cd backend
python -m pytest -v
```

Verified result: **2 passed, 4 warnings**, covering:
- `test_db_connection.py`
- `test_evidence_bridge.py`

---

## Using the System

1. Start PostgreSQL and Ollama.
2. Start the backend (`uvicorn main:app --reload --port 8000`).
3. Start the frontend (`npm run dev`).
4. Upload evidence for an exam session.
5. Ask an investigation question and review the evidence-grounded answer.

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | App + PostgreSQL connectivity check |
| `POST` | `/upload-evidence` | Upload an evidence image (`session_id` + `file`, jpg/png/webp, max 10MB) |
| `POST` | `/investigate` | `{"query": "..."}` → `{"answer": "..."}` |
| `GET` | `/students` | List students |
| `GET` | `/sessions` | List exam sessions |

## Troubleshooting

- **CORS errors from the frontend** — `main.py` allows only `http://localhost:5173` (Vite's default); update it if your frontend runs elsewhere.
- **Backend won't start** — `DB_PASSWORD` has no default; confirm it's set in `backend/.env`.
- **Ollama errors during ingestion or investigation** — confirm the models in `.env` are actually pulled (`ollama list`).

## Project Structure

```
backend/
├── .env.example
├── requirements.txt
├── alembic.ini
├── alembic/env.py
├── main.py
└── app/
    ├── api/routes.py
    ├── core/  (config, database, seed, diagnostics, vector_store)
    ├── models/ (student, exam_session, evidence)
    └── services/ (ingestion, retrieval, agent, agent_tools, llm, evidence_store)

frontend/
├── package.json
├── .env.example
└── src/            # React app (Vite dev server on :5173)
```

## Privacy / Offline Operation

All AI inference — vision analysis, embeddings, and the investigation agent's reasoning — runs locally through Ollama. No cloud AI API is called anywhere in this pipeline. PostgreSQL and ChromaDB both run locally as well, so evidence data does not need to leave the machine it's processed on.
