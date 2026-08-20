"""Video upload page.

Belongs in `pages/2_Upload_Video.py`. Saves the uploaded file to disk,
creates a PENDING job row, and submits it to worker.submit_job() -- which
returns immediately, since the pipeline itself runs on a background
thread. The user is sent to the report page to watch/poll progress.

The launch sequence below (the "LAUNCH_STEPS" loop) is a purely cosmetic
animation -- the real work already happened in the submit_job() call
right before it starts. It exists because otherwise the click just
freezes for a beat and then silently jumps pages; a few seconds of
"here's what's about to happen to your video" keeps that handoff from
feeling broken and previews the pipeline the report page will be polling.
"""

import time
import uuid
from pathlib import Path

import streamlit as st

from db import jobs
from worker import submit_job
from theme import inject_css, hero

st.set_page_config(page_title="Upload Video", page_icon="\U0001F3A5")
inject_css()

if not st.session_state.get("user"):
    st.warning("Please log in first.")
    st.page_link("app.py", label="Go to login")
    st.stop()

UPLOAD_ROOT = Path("data/videos/uploads")
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

hero(
    eyebrow=f"OPERATOR: {st.session_state.user['username']}",
    title="Upload an exam recording",
    tagline="Drop in a video and the video, audio and behavior agents will scan it in the background.",
    pills=["MP4", "MOV", "MKV", "AVI"],
)

LAUNCH_STEPS = [
    ("\U0001F4E4", "Uploading recording", "Streaming the file to local storage"),
    ("\U0001F9FE", "Registering session", "Writing a job record so progress can be tracked"),
    ("\U0001F9E0", "Waking the agents", "Loading vision, audio and behavior models"),
    ("\U0001F680", "Handing off to the worker", "Analysis continues on a background thread"),
]


def _run_launch_animation() -> None:
    chip_row = st.empty()
    status = st.empty()
    bar = st.progress(0)

    n = len(LAUNCH_STEPS)
    for i, (icon, title, detail) in enumerate(LAUNCH_STEPS):
        chips_html = '<div class="step-row">'
        for j, (icon_j, title_j, _) in enumerate(LAUNCH_STEPS):
            cls = "done" if j < i else ("active" if j == i else "")
            chips_html += f'<span class="step-chip {cls}">{icon_j} {title_j}</span>'
        chips_html += "</div>"
        chip_row.markdown(chips_html, unsafe_allow_html=True)

        status.markdown(
            f'<div class="readout">{icon}  {title}\n    {detail}...</div>',
            unsafe_allow_html=True,
        )
        for pct in range(0, 101, 25):
            bar.progress(int((i * 100 + pct) / n))
            time.sleep(0.09)

    chips_html = '<div class="step-row">' + "".join(
        f'<span class="step-chip done">{icon} {title}</span>' for icon, title, _ in LAUNCH_STEPS
    ) + "</div>"
    chip_row.markdown(chips_html, unsafe_allow_html=True)
    status.markdown(
        '<div class="readout">\u2705  Handoff complete -- opening the live report...</div>',
        unsafe_allow_html=True,
    )
    bar.progress(100)
    time.sleep(0.5)


with st.container(border=True):
    st.markdown('<div class="eyebrow">EXAM RECORDING</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop a video here or click to browse",
        type=["mp4", "mov", "mkv", "avi"],
        label_visibility="visible",
    )

    if uploaded_file is not None:
        st.video(uploaded_file)
        st.markdown(
            f'<p class="mono" style="color:var(--text-dim);font-size:0.8rem;">'
            f"{uploaded_file.name}  \u2022  {uploaded_file.size / 1_000_000:.1f} MB</p>",
            unsafe_allow_html=True,
        )

        if st.button("\U0001F680 Run proctoring analysis", type="primary", use_container_width=True):
            safe_name = f"{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
            video_path = UPLOAD_ROOT / safe_name

            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            job_id = jobs.create_job(
                user_id=st.session_state.user["id"],
                video_filename=uploaded_file.name,
                video_path=str(video_path),
            )
            submit_job(job_id, str(video_path))
            st.session_state.active_job_id = job_id

            _run_launch_animation()
            st.switch_page("pages/3_Report.py")

st.divider()
if st.button("View my reports"):
    st.switch_page("pages/3_Report.py")
