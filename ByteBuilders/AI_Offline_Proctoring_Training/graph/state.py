"""Shared state schema for the LangGraph proctoring workflow.

Belongs in the `graph` package (graph/state.py).
"""

from typing import Any, Dict, List, TypedDict


class ProctoringState(TypedDict, total=False):
    """State passed between nodes in the proctoring graph.

    total=False because not every field is populated at every point in the
    workflow (e.g. risk_score doesn't exist until the risk node has run,
    retrieved_rules only exists if synthesis ran).
    """

    video_path: str
    frames: List[Any]

    # Raw, per-frame/per-segment evidence. risk_agent scores off these.
    video_evidence: List[Dict[str, Any]]
    audio_evidence: List[Dict[str, Any]]
    behavior_evidence: List[Dict[str, Any]]

    # Human/LLM-facing activity summaries produced by agents.activity_agent:
    # consecutive detections merged into segments, filtered to suspicious/
    # meaningful activity only. synthesis_agent, report_agent, and
    # human_review_agent build their prompts from these, not the raw
    # evidence above, so nothing downstream shows a per-timestamp dump.
    video_activity: List[Dict[str, Any]]
    audio_activity: List[Dict[str, Any]]
    behavior_activity: List[Dict[str, Any]]

    retrieved_rules: List[Dict[str, Any]]

    # Retry-loop bookkeeping for agents.synthesis_agent (see
    # graph/workflow.py's conditional self-loop on the "synthesis" node).
    # synthesis_attempts counts how many times synthesis_agent has run for
    # this session; synthesis_valid is True once a well-formed response
    # was produced OR the attempt cap was reached -- either way, the loop
    # exits and routes to report_agent.
    synthesis_attempts: int
    synthesis_valid: bool

    risk_score: float
    risk_level: str
    risk_reason: str

    final_report: str
    human_review: str

    step_history: List[str]
