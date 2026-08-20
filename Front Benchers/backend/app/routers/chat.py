"""POST /chat endpoint — powered by LangGraph.

Uses a LangGraph StateGraph to orchestrate the RAG-augmented chat flow:
  START -> retrieve (hybrid search) -> generate (LLM reply) -> END

The graph retrieves relevant DSA knowledge via hybrid search (ChromaDB + BM25),
then generates an in-character response using the LangChain ChatGroq LLM.
History is maintained client-side and sent with each request.
"""
from typing import TypedDict, Optional
from fastapi import APIRouter, HTTPException
from langgraph.graph import StateGraph, START, END

from app.models import ChatRequest, ChatResponse
from app.services.llm_client import generate_chat_reply
from app.services.rag_service import hybrid_search

router = APIRouter()


def _get_stores():
    from app.main import problems_store, personas_store
    return problems_store, personas_store


# ─── LangGraph State Schema ────────────────────────────────────────────

class ChatGraphState(TypedDict):
    """State that flows through the LangGraph chat pipeline."""
    # Inputs
    persona_voice: str
    problem_description: str
    problem_title: str
    message: str
    history: list[dict]
    # Intermediate
    rag_context: str
    # Output
    reply: str


# ─── LangGraph Node Functions ──────────────────────────────────────────

def retrieve_node(state: ChatGraphState) -> dict:
    """Node 1: Retrieve relevant DSA knowledge via hybrid search.
    
    Uses LangChain EnsembleRetriever (ChromaDB + BM25) with RRF fusion
    and relevance-floor filtering.
    """
    rag_query = f"{state['problem_title']} {state['message']}"
    rag_context = hybrid_search(rag_query, top_k=3)
    return {"rag_context": rag_context}


def generate_node(state: ChatGraphState) -> dict:
    """Node 2: Generate an in-character chat reply using LangChain ChatGroq.
    
    Injects the retrieved RAG context into the LLM prompt.
    The LLM is instructed to ignore irrelevant context.
    """
    reply = generate_chat_reply(
        persona_voice=state["persona_voice"],
        problem_description=state["problem_description"],
        problem_title=state["problem_title"],
        message=state["message"],
        history=state["history"],
        rag_context=state.get("rag_context", ""),
    )
    return {"reply": reply}


# ─── Build the LangGraph ───────────────────────────────────────────────

def _build_chat_graph() -> StateGraph:
    """Build and compile the LangGraph StateGraph for chat.
    
    Graph topology:
        START -> retrieve -> generate -> END
    """
    builder = StateGraph(ChatGraphState)

    # Add nodes
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)

    # Add edges: linear flow
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)

    return builder.compile()


# Compile the graph once at module load
_chat_graph = _build_chat_graph()


# ─── FastAPI Endpoint ──────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Generate an in-character chat reply about the problem.
    
    Powered by LangGraph StateGraph:
    1. retrieve node: Hybrid search (ChromaDB + BM25) with relevance filtering
    2. generate node: LangChain ChatGroq LLM call with RAG context injection
    """
    problems_store, personas_store = _get_stores()

    problem = problems_store.get(req.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{req.problem_id}' not found")

    persona = personas_store.get(req.persona)
    if not persona:
        raise HTTPException(status_code=400, detail=f"Persona '{req.persona}' not found")

    # Run the LangGraph chat pipeline
    initial_state: ChatGraphState = {
        "persona_voice": persona["voice"],
        "problem_description": problem["description"],
        "problem_title": problem["title"],
        "message": req.message,
        "history": [msg.model_dump() for msg in req.history],
        "rag_context": "",
        "reply": "",
    }

    result = _chat_graph.invoke(initial_state)

    return ChatResponse(reply=result["reply"])
