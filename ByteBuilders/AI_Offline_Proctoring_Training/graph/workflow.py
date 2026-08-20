"""Builds the proctoring pipeline as a LangGraph graph.

Belongs in the `graph` package (graph/workflow.py).

Pipeline shape:

    video -> audio -> behavior -> activity -> risk -> [synthesis?] -> report -> human_review -> END

`activity` (agents.activity_agent) is new: it collapses the raw, granular
evidence from video/audio/behavior into a handful of human-readable
activity segments (e.g. "phone visible 12.0s-45.0s") before risk_agent
runs. risk_agent still scores off the raw *_evidence fields -- activity
summarization never changes the score -- but everything downstream of
risk_agent (synthesis, report, human_review) is built from the *_activity
fields instead, so reports never dump a full per-second timestamp list.

`synthesis` (rule retrieval + LLM explanation) only runs for MEDIUM/HIGH
risk sessions -- a LOW-risk session has nothing suspicious to explain, so
skipping it saves an embedding pass, a vector search, and an LLM call on
the common case.

`synthesis` has a conditional self-loop: if its LLM response is missing
required section headers, `_route_after_synthesis` routes back to
`synthesis` itself for another attempt (with a corrective prompt), up to
`agents.synthesis_agent.MAX_SYNTHESIS_ATTEMPTS` times, before falling
through to `report` regardless. This is the one genuine loop in an
otherwise straight-line graph -- see agents/synthesis_agent.py's
docstring for why a loop specifically here (a malformed LLM response is
worth retrying; a connection failure is not, and does not trigger the
loop).

Report generation is agents.report_agent.report_agent, which builds a
deterministic decision report (can't fail) plus a best-effort LLM
narrative routed through the traced llm.ollama_client.call_llm wrapper.
(This graph previously wired in a separate llm.proctoring_llm.generate_report
report_node -- that produced a narrative-only report with no deterministic
section and bypassed tracing. Consolidated here so there's a single
report-generation code path.)
"""

import logging

from langgraph.graph import StateGraph, START, END

from graph.state import ProctoringState

from agents.video_agent import video_agent
from agents.audio_agent import audio_agent
from agents.behavior_agent import behavior_agent
from agents.activity_agent import activity_agent
from agents.risk_agent import risk_agent
from agents.synthesis_agent import synthesis_agent
from agents.report_agent import report_agent
from agents.human_review_agent import human_review_agent

logger = logging.getLogger(__name__)


def _route_after_risk(state: ProctoringState) -> str:
    """Decide whether this session needs rule synthesis before reporting.

    MEDIUM/HIGH risk -> synthesis (explain the score against retrieved rules)
    LOW risk -> straight to report (nothing suspicious to explain)
    Unrecognized risk_level -> synthesis, fail safe rather than silently
        skipping an explanation step.
    """
    risk_level = state.get("risk_level", "")

    if risk_level == "LOW":
        return "report"

    if risk_level not in ("MEDIUM", "HIGH"):
        logger.warning(
            "Unrecognized risk_level %r; routing through synthesis to be safe",
            risk_level,
        )

    return "synthesis"


def _route_after_synthesis(state: ProctoringState) -> str:
    """Decide whether synthesis needs to retry itself (loop) or can move on.

    synthesis_agent sets synthesis_valid=True once its response is
    well-formed OR the attempt cap was reached (see agents/synthesis_agent.py)
    -- so this function never needs to know the attempt count or the cap
    itself; it only reads the one flag synthesis_agent already computed.
    """
    if state.get("synthesis_valid", True):
        return "report"
    return "retry"


def build_graph():
    """Assemble and compile the proctoring graph."""
    graph = StateGraph(ProctoringState)

    graph.add_node("video", video_agent)
    graph.add_node("audio", audio_agent)
    graph.add_node("behavior", behavior_agent)
    graph.add_node("activity", activity_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("synthesis", synthesis_agent)
    graph.add_node("report", report_agent)
    graph.add_node("human_review", human_review_agent)

    graph.add_edge(START, "video")
    graph.add_edge("video", "audio")
    graph.add_edge("audio", "behavior")
    graph.add_edge("behavior", "activity")
    graph.add_edge("activity", "risk")

    graph.add_conditional_edges(
        "risk",
        _route_after_risk,
        {"synthesis": "synthesis", "report": "report"},
    )

    # The one genuine loop in this graph: "retry" routes back to
    # "synthesis" itself, not forward. agents.synthesis_agent.
    # MAX_SYNTHESIS_ATTEMPTS bounds how many times this can happen before
    # synthesis_valid is forced True and this always resolves to "report".
    graph.add_conditional_edges(
        "synthesis",
        _route_after_synthesis,
        {"retry": "synthesis", "report": "report"},
    )

    graph.add_edge("report", "human_review")
    graph.add_edge("human_review", END)

    return graph.compile()


app = build_graph()
