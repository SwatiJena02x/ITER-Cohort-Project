from fastapi import FastAPI
from pydantic import BaseModel

from agents.dsa_agent import DSACoachAgent


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="DSA AI Coach API",
    description="AI-powered DSA coaching backend",
    version="1.0.0"
)


# ==================================================
# AGENT
# ==================================================

agent = DSACoachAgent()


# ==================================================
# REQUEST MODEL
# ==================================================

class ChatRequest(BaseModel):

    message: str

    session_id: str = "default_session"


# ==================================================
# RESPONSE MODEL
# ==================================================

class ChatResponse(BaseModel):

    answer: str

    session_id: str

    route: str

    problem_id: str

    iteration: int


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "DSA AI Coach",
        "version": "1.0.0"
    }


# ==================================================
# HEALTH
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==================================================
# CHAT
# ==================================================

@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest
):

    result = agent.ask(
        question=request.message,
        session_id=request.session_id
    )

    return ChatResponse(

        answer=result.get(
            "answer",
            ""
        ),

        session_id=request.session_id,

        route=result.get(
            "route",
            ""
        ),

        problem_id=result.get(
            "problem_id",
            ""
        ),

        iteration=result.get(
            "iteration",
            0
        )
    )