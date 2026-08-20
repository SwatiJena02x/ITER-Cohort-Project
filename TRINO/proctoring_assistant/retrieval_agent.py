from __future__ import annotations

import re
from typing import Any, Dict, List

SEMANTIC_KEYWORDS = ["phone", "mobile", "device", "screen", "notes", "cheat", "suspicious", "person", "multiple"]
SQL_KEYWORDS = ["student", "session", "stu", "camera", "category", "timestamp"]


def route_query(question: str) -> str:
    lowered = question.lower()
    has_semantic = any(keyword in lowered for keyword in SEMANTIC_KEYWORDS)
    has_sql = any(keyword in lowered for keyword in SQL_KEYWORDS) or bool(
        re.search(r"\b(?:stu|student|session)[-_ ]?[a-z0-9]+\b", lowered)
    )
    if has_semantic and has_sql:
        return "hybrid"
    if has_semantic:
        return "semantic"
    if has_sql:
        return "sql"
    return "hybrid"


def analyze_query(question: str) -> Dict[str, Any]:
    lowered = question.lower()
    filters: Dict[str, Any] = {}
    student_match = re.search(r"\b(stu[0-9a-z-]+)\b", lowered)
    session_match = re.search(r"\b(session[0-9a-z-]+)\b", lowered)
    if student_match:
        filters["student_id"] = student_match.group(1).upper()
    if session_match:
        filters["session_id"] = session_match.group(1).upper()
    if any(term in lowered for term in ("suspicious", "flagged")):
        filters["suspicious"] = True
        time_range = re.search(r"between\s+(\d{1,2}:\d{2})\s+and\s+(\d{1,2}:\d{2})", lowered)
        if time_range:
            filters["start_time"] = time_range.group(1)
            filters["end_time"] = time_range.group(2)
    return {
        "query_type": route_query(question).upper(),
        "filters": filters,
    }


def decide_retrieval(question: str) -> Dict[str, List[str]]:
    route = route_query(question)
    if route == "semantic":
        return {"route": ["semantic"], "reason": ["query mentions suspicious visual evidence"]}
    if route == "sql":
        return {"route": ["sql"], "reason": ["query references structured fields such as student or session"]}
    return {"route": ["semantic", "sql"], "reason": ["query needs both interpretation and metadata filtering"]}
