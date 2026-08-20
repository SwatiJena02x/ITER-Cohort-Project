"""Entry point for the offline AI proctoring workflow."""

import argparse
import logging
import sys
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # loads LANGSMITH_*, OLLAMA_HOST, etc. from .env if present

from graph.workflow import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

BANNER = (
    "\n========================================\n"
    "     OFFLINE AI PROCTORING SYSTEM\n"
    "     LANGGRAPH MULTI-AGENT WORKFLOW\n"
    "========================================\n"
)

DEFAULT_VIDEO_PATH = "data/videos/input_video.mp4"


def build_initial_state(video_path: str) -> dict:
    """Construct a fresh initial state dict for a workflow run."""
    return {
        "video_path": video_path,
        "frames": [],
        "video_evidence": [],
        "audio_evidence": [],
        "behavior_evidence": [],
        "video_activity": [],
        "audio_activity": [],
        "behavior_activity": [],
        "retrieved_rules": [],
        "synthesis_attempts": 0,
        "synthesis_valid": True,
        "risk_score": 0.0,
        "risk_level": "",
        "risk_reason": "",
        "final_report": "",
        "human_review": "",
        "step_history": [],
    }


def build_run_config(video_path: Path) -> tuple[dict, str]:
    """Build the LangGraph/LangSmith run config for one workflow invocation.

    Generates the run_id up front (instead of letting LangSmith assign one)
    so it can be handed to downstream review tooling -- e.g. so a human
    reviewer's later decision can be logged as feedback against this exact
    run via langsmith_feedback.log_reviewer_feedback(run_id, ...).

    Picked up by LangSmith tracing (when LANGSMITH_TRACING=true) so
    individual exam sessions are easy to find/filter in the LangSmith UI.
    Harmless no-ops when tracing is disabled.

    Every node (video, audio, behavior, activity, risk, synthesis, report,
    human_review) is now individually traced (see each agent module's
    @traceable decorator), plus the embedding/retrieval/LLM calls inside
    them, so a single run's trace tree shows the full pipeline, not just
    one opaque top-level span. risk_agent also tags its own span with
    "risk-<LEVEL>" and, for HIGH sessions, "HIGH-RISK-ALERT" the moment
    the score is computed (see llm/langsmith_utils.py) -- combined with the
    root-run tag below, that makes HIGH sessions filterable/alertable on
    in the LangSmith UI at both the whole-run and single-node level.
    """
    run_id = str(uuid.uuid4())
    run_config = {
        "run_id": run_id,
        "run_name": f"proctoring-{video_path.stem}",
        "tags": ["proctoring", "offline"],
        "metadata": {"video_path": str(video_path)},
    }
    return run_config, run_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the offline AI proctoring workflow.")
    parser.add_argument(
        "video_path",
        nargs="?",
        default=DEFAULT_VIDEO_PATH,
        help=f"Path to the input video (default: {DEFAULT_VIDEO_PATH})",
    )
    return parser.parse_args()


def print_section(title: str, body: str) -> None:
    print(f"\n{title}:\n")
    print(body)


def _tag_run_with_risk_level(run_id: str, risk_level: str) -> None:
    """Best-effort: tag the root LangSmith run with its final risk_level so
    alerts/filters in the UI can scope to e.g. tag=HIGH. Never raises --
    tagging failures shouldn't affect the exit code of a completed run.

    This complements risk_agent's own node-level tagging (see
    llm/langsmith_utils.py): that tags risk_agent's span as soon as the
    score is known; this tags the *root* run once the whole graph has
    finished, so the entire session is filterable by risk_level in the
    LangSmith UI, not just the risk_agent span within it.
    """
    if not risk_level:
        return
    try:
        from langsmith import Client

        tags = ["proctoring", "offline", risk_level]
        if risk_level == "HIGH":
            tags.append("HIGH-RISK-ALERT")
        Client().update_run(run_id, tags=tags)
    except Exception:
        logger.debug("Skipping LangSmith run tagging (tracing likely disabled)", exc_info=True)


def main() -> int:
    args = parse_args()

    video_path = Path(args.video_path)
    if not video_path.is_file():
        logger.error("Video file not found: %s", video_path)
        return 1

    print(BANNER)

    initial_state = build_initial_state(str(video_path))
    run_config, run_id = build_run_config(video_path)

    start = time.monotonic()
    try:
        result = app.invoke(initial_state, config=run_config)
    except Exception:
        logger.exception("Workflow failed to complete")
        return 1
    elapsed = time.monotonic() - start

    _tag_run_with_risk_level(run_id, result.get("risk_level", ""))

    print("\n========================================")
    print("             FINAL OUTPUT")
    print("========================================")

    print_section("FINAL REPORT", result.get("final_report", "No report generated."))
    print_section("HUMAN REVIEW", result.get("human_review", "No human review generated."))
    print_section("STEP HISTORY", " → ".join(result.get("step_history", [])))

    # Downstream review tooling needs this to later call
    # langsmith_feedback.log_reviewer_feedback(run_id, model_risk_level, human_decision).
    print_section("LANGSMITH RUN ID", run_id)

    logger.info("Workflow completed in %.2fs", elapsed)

    return 0


if __name__ == "__main__":
    sys.exit(main())
