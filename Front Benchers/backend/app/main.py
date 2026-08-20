"""DSA Coach — FastAPI Backend with LangChain/LangGraph.

Loads problem data and personas at startup, builds RAG index,
and mounts all routers. Uses LangChain for LLM calls and
LangGraph for the chat pipeline.
"""
import json
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="DSA Coach API",
    description="AI-powered DSA coaching with selectable personas",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Data stores (loaded at startup) ────────────────────────────────────
problems_store: dict = {}  # problem_id → full problem dict
personas_store: dict = {}  # persona_key → persona dict


def _load_problems():
    """Load all problem JSON files from data/problems/."""
    global problems_store
    problems_dir = Path(__file__).parent / "data" / "problems"
    if not problems_dir.exists():
        print(f"[WARN] Problems directory not found: {problems_dir}")
        return

    for json_file in problems_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            problem = json.load(f)
            problems_store[problem["id"]] = problem
            print(f"  [OK] Loaded problem: {problem['title']}")

    print(f"[INFO] {len(problems_store)} problems loaded")


def _load_personas():
    """Load persona definitions from personas/personas.json."""
    global personas_store
    personas_file = Path(__file__).parent / "personas" / "personas.json"
    if not personas_file.exists():
        print(f"[WARN] Personas file not found: {personas_file}")
        return

    with open(personas_file, "r", encoding="utf-8") as f:
        personas_store = json.load(f)

    print(f"[INFO] {len(personas_store)} personas loaded: {', '.join(personas_store.keys())}")


@app.on_event("startup")
async def startup():
    """Load data stores and build RAG index on startup."""
    print("[START] Starting DSA Coach API...")
    _load_problems()
    _load_personas()

    # Build RAG hybrid search index
    from app.services.rag_service import build_index
    print("[RAG] Building hybrid search index...")
    build_index()

    # Verify Groq API key is set (used by LangChain ChatGroq)
    if not os.getenv("GROQ_API_KEY"):
        print("[WARN] GROQ_API_KEY not set! LangChain + Groq LLM features will fail.")
    else:
        print("[OK] LangChain + Groq API key configured")

    print("[READY] DSA Coach API ready (LangChain + LangGraph)!")


# ─── Mount routers ──────────────────────────────────────────────────────
from app.routers import problems, analyze, hint, chat, execute

app.include_router(problems.router, tags=["Problems"])
app.include_router(analyze.router, tags=["Analysis"])
app.include_router(hint.router, tags=["Hints"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(execute.router, tags=["Execution"])


@app.get("/")
async def root():
    return {
        "app": "DSA Coach API",
        "version": "1.0.0",
        "problems_loaded": len(problems_store),
        "personas_loaded": len(personas_store),
    }


@app.get("/personas/{persona_id}")
async def get_persona(persona_id: str):
    """Return persona data including pass/fail quotes."""
    from fastapi import HTTPException
    persona = personas_store.get(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")
    return {
        "id": persona_id,
        "display_name": persona.get("display_name", persona_id),
        "pass_quotes": persona.get("pass_quotes", []),
        "fail_quotes": persona.get("fail_quotes", []),
    }


@app.get("/rag/search")
async def rag_search(query: str, top_k: int = 3):
    """Debug endpoint: test hybrid RAG search directly.
    
    Example: /rag/search?query=nested+loop+brute+force&top_k=3
    """
    from app.services.rag_service import hybrid_search, is_ready
    if not is_ready():
        return {"error": "RAG index not built yet", "chunks": []}
    
    context = hybrid_search(query, top_k=top_k)
    chunks = context.split("\n\n---\n\n") if context else []
    return {
        "query": query,
        "top_k": top_k,
        "num_results": len(chunks),
        "chunks": chunks,
    }
