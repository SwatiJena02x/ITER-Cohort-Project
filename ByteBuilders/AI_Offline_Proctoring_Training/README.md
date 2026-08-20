# Offline AI Proctoring System

A LangGraph multi-agent pipeline that analyzes exam-session video for
suspicious activity — unauthorized objects, multiple people, speech —
scores the risk, explains it with a locally-run LLM grounded in your
exam rules (RAG), and routes it to a human reviewer. Runs fully offline
(Whisper, DETR, a local Ollama model). Includes a Streamlit UI backed by
PostgreSQL for accounts, upload, and report delivery.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally
- `ffmpeg` on your PATH
- PostgreSQL (only needed for the web UI, not the CLI)

## Quick start

```bash
git clone <your-repo-url>
cd <your-repo-folder>

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# open .env and fill in your actual values (see below)

ollama pull llama3.2
ffmpeg -version                    # confirm it's installed
```

### Run the CLI (no database needed)

```bash
python main.py path/to/exam_video.mp4
```

### Run the web UI

```bash
createdb proctoring_db             # or point .env at an existing database
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).
Tables are created automatically on first launch — no manual migration
step.

## Configuration

Copy `.env.example` to `.env` and fill in:

```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=proctoring_db
DB_USER=postgres
DB_PASSWORD=your_local_postgres_password

LANGSMITH_TRACING=true             # optional, tracing works without it
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=your_project_name

OLLAMA_HOST=http://127.0.0.1:11434
```

**`.env` is gitignored on purpose — never commit it.** If a real secret
ever ends up in a commit or a chat, rotate it immediately rather than
trying to remove it after the fact (git history keeps old commits around
even after a file is deleted in a later commit).

## Project structure

See [`DOCUMENTATION.md`](./DOCUMENTATION.md) for the full architecture
breakdown, module-by-module reference, risk-scoring formula, and RAG
pipeline detail.

