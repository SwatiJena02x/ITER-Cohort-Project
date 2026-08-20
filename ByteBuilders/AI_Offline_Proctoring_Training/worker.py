"""Background execution of the proctoring pipeline for the Streamlit UI.

Belongs at the project root as `worker.py`.

Streamlit is request/rerun-driven, not built for long-running work in the
same script execution -- a pipeline run (Whisper + DETR + Ollama) can take
minutes, and blocking the Streamlit script for that long would freeze the
page and risk the browser connection timing out. Instead,
pages/2_Upload_Video.py submits a job to this module's thread pool and
returns immediately; pages/3_Report.py polls proctoring_jobs.status in
Postgres to show progress.

MAX_CONCURRENT_JOBS is deliberately small (not "one thread per upload").
Whisper and the DETR object detector are both loaded as process-wide
singleton models on the GPU (see agents/audio_agent.py:get_model and
vision/object_detector.py:_get_detector) -- running too many pipeline
instances at once risks GPU out-of-memory, not just slower throughput.
Threads (not separate processes) are used because those singletons are
already designed to be loaded once per process and reused; a
ProcessPoolExecutor would instead reload both models per worker process.
"""

import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from db import jobs
from graph.workflow import app as proctoring_app

logger = logging.getLogger(__name__)

MAX_CONCURRENT_JOBS = 2
_executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_JOBS, thread_name_prefix="proctoring-job")


def _build_initial_state(video_path: str) -> dict:
    """Same shape as main.py's build_initial_state -- kept in sync manually
    since the UI and the CLI entry point are two separate invocation paths
    into the same graph.
    """
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


def _run_job(job_id: str, video_path: str) -> None:
    """Runs on a worker thread. Never raises -- all failure paths write a
    FAILED status + error message to the job row instead, since there's no
    caller left to catch an exception from a background thread.
    """
    jobs.mark_running(job_id)
    run_id = str(uuid.uuid4())

    try:
        result = proctoring_app.invoke(
            _build_initial_state(video_path),
            config={
                "run_id": run_id,
                "run_name": f"proctoring-{Path(video_path).stem}",
                "tags": ["proctoring", "streamlit-ui"],
                "metadata": {"video_path": video_path, "job_id": job_id},
            },
        )
        jobs.mark_done(
            job_id,
            risk_level=result.get("risk_level", "UNKNOWN"),
            risk_score=result.get("risk_score", 0.0),
            final_report=result.get("final_report", ""),
            human_review=result.get("human_review", ""),
            langsmith_run_id=run_id,
        )
        logger.info("Job %s completed: risk_level=%s", job_id, result.get("risk_level"))
    except Exception as exc:
        logger.error("Job %s failed: %s", job_id, exc, exc_info=True)
        jobs.mark_failed(job_id, str(exc))


def submit_job(job_id: str, video_path: str) -> None:
    """Fire-and-forget: submit the pipeline run to the background pool and
    return immediately. Progress is tracked via the job row in Postgres,
    not via this function's return value.
    """
    _executor.submit(_run_job, job_id, video_path)
