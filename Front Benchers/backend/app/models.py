"""Pydantic request/response schemas for DSA Coach API."""
from pydantic import BaseModel
from typing import Optional


# ─── Problem Models ─────────────────────────────────────────────────────
class ProblemSummary(BaseModel):
    id: str
    title: str
    difficulty: str


class TestCaseInput(BaseModel):
    """Generic test case — input is a dict, expected can be anything."""
    input: dict
    expected: object


class ProblemDetail(BaseModel):
    id: str
    title: str
    difficulty: str
    description: str
    starter_code: str
    test_cases: list[TestCaseInput]


# ─── Analyze ────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    problem_id: str
    code: str
    persona: str  # "walter_white" | "kratos" | "thanos"
    previous_comments: list[str] = []


class AnalyzeResponse(BaseModel):
    triggered: bool
    comment: Optional[str] = None
    tone: Optional[str] = None
    hint_available: bool = False


# ─── Hint ───────────────────────────────────────────────────────────────
class HintRequest(BaseModel):
    problem_id: str
    tier: int  # 0, 1, or 2
    persona: str


class HintResponse(BaseModel):
    hint_text: str


# ─── Chat ───────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    problem_id: str
    message: str
    history: list[ChatMessage] = []
    persona: str


class ChatResponse(BaseModel):
    reply: str


# ─── Execute ────────────────────────────────────────────────────────────
class ExecuteRequest(BaseModel):
    problem_id: str
    code: str


class TestResult(BaseModel):
    input: dict
    expected: object
    actual: object
    passed: bool


class ExecuteResponse(BaseModel):
    passed: bool
    results: list[TestResult]
