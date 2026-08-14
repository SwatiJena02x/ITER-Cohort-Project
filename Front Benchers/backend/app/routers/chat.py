"""POST /chat endpoint.

Free-text chat with the persona about the current problem.
Uses RAG to retrieve relevant DSA knowledge for informed responses.
Retrieval is strictly filtered for relevance, and the LLM is instructed to ignore irrelevant context.
History is maintained client-side and sent with each request.
"""
from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse
from app.services.llm_client import generate_chat_reply
from app.services.rag_service import hybrid_search

router = APIRouter()


def _get_stores():
    from app.main import problems_store, personas_store
    return problems_store, personas_store


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Generate an in-character chat reply about the problem.
    
    Flow:
    1. Build RAG query using problem title + user message
    2. Perform hybrid search (ChromaDB + BM25) with relevance filtering
    3. Inject source-labeled context into LLM prompt
    4. LLM evaluates relevance and answers in character
    """
    problems_store, personas_store = _get_stores()

    problem = problems_store.get(req.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{req.problem_id}' not found")

    persona = personas_store.get(req.persona)
    if not persona:
        raise HTTPException(status_code=400, detail=f"Persona '{req.persona}' not found")

    # RAG retrieval — use the problem title + user's message for better context
    rag_query = f"{problem['title']} {req.message}"
    rag_context = hybrid_search(rag_query, top_k=3)

    reply = generate_chat_reply(
        persona_voice=persona["voice"],
        problem_description=problem["description"],
        problem_title=problem["title"],
        message=req.message,
        history=[msg.model_dump() for msg in req.history],
        rag_context=rag_context,
    )

    return ChatResponse(reply=reply)
