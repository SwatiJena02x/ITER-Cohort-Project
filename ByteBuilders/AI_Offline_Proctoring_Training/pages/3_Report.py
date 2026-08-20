"""Report / status page.

Belongs in `pages/3_Report.py`. Shows a session picker (the user's past
jobs, newest first, defaulting to whichever job the upload page just
started), then renders that job's current state:

  PENDING/RUNNING -> an animated status readout (pipeline stage chips +
                     a rotating tip) with manual + optional auto-refresh
  FAILED          -> the recorded error message
  DONE            -> risk badge, a gauge chart of the score, a trend
                     chart across the user's past sessions, the final
                     report, human review notes, and a download button

Polling works by literally re-running this Streamlit script (st.rerun())
and re-reading the job row from Postgres each time -- there's no
persistent connection between the background worker thread and this page,
so Postgres is the only shared state between them.

The pipeline-stage chips shown while PENDING/RUNNING are a cosmetic
approximation (elapsed time since created_at bucketed into rough stages)
-- proctoring_jobs only stores PENDING/RUNNING/DONE/FAILED, not a
per-agent status, so this is not a literal readout of which LangGraph
node is currently executing.
"""

import time
from datetime import datetime, timezone

import streamlit as st

from db import jobs
from theme import inject_css, hero, risk_badge_html, RISK_COLORS

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

st.set_page_config(page_title="Proctoring Report", page_icon="\U0001F4CB", layout="centered")
inject_css()

if not st.session_state.get("user"):
    st.warning("Please log in first.")
    st.page_link("app.py", label="Go to login")
    st.stop()

user = st.session_state.user

hero(
    eyebrow=f"OPERATOR: {user['username']}",
    title="Proctoring report",
    tagline="Live status while a session is being scanned, and the full risk breakdown once it's done.",
)

user_jobs = jobs.get_user_jobs(user["id"])

if not user_jobs:
    st.info("No videos uploaded yet.")
    if st.button("Upload a video", type="primary"):
        st.switch_page("pages/2_Upload_Video.py")
    st.stop()

job_ids = [j["id"] for j in user_jobs]
active_job_id = st.session_state.get("active_job_id")
default_index = job_ids.index(active_job_id) if active_job_id in job_ids else 0


def _format_option(job_id: str) -> str:
    j = next(item for item in user_jobs if item["id"] == job_id)
    timestamp = j["created_at"].strftime("%Y-%m-%d %H:%M")
    return f"{j['video_filename']} -- {j['status']} ({timestamp})"


selected_id = st.selectbox(
    "Select a session",
    options=job_ids,
    index=default_index,
    format_func=_format_option,
)

job = jobs.get_job(selected_id)
status = job["status"]

# ---------------------------------------------------------------------------
# PENDING / RUNNING -- animated waiting state
# ---------------------------------------------------------------------------
PIPELINE_STAGES = ["Video", "Audio", "Behavior", "Activity", "Risk scoring", "Report"]

TIPS = [
    "The risk score never factors in who the student is -- only what the agents observed.",
    "MEDIUM and HIGH risk sessions get an extra pass: retrieved rubric rules explain *why*.",
    "The video, audio and behavior agents run independently, then get merged before scoring.",
    "A human review step always runs last, even on a LOW risk session.",
    "Longer recordings take longer mainly because of the audio transcription pass.",
    "You can leave this tab -- refresh the report page any time to see the latest status.",
]

if status in (jobs.STATUS_PENDING, jobs.STATUS_RUNNING):
    created = job["created_at"]
    if created.tzinfo is not None:
        elapsed = (datetime.now(timezone.utc) - created).total_seconds()
    else:
        elapsed = (datetime.now() - created).total_seconds()

    if status == jobs.STATUS_PENDING:
        active_stage = -1
    else:
        # Rough cosmetic bucketing -- see module docstring.
        bucket_seconds = 25
        active_stage = min(int(elapsed // bucket_seconds), len(PIPELINE_STAGES) - 1)

    chips = '<div class="step-row">'
    for i, name in enumerate(PIPELINE_STAGES):
        cls = "done" if i < active_stage else ("active" if i == active_stage else "")
        chips += f'<span class="step-chip {cls}">{name}</span>'
    chips += "</div>"
    st.markdown(chips, unsafe_allow_html=True)

    st.markdown(
        f'<div class="readout">STATUS: {status}\n'
        f"ELAPSED: {int(elapsed)}s\n"
        f"This can take a few minutes for longer videos.</div>",
        unsafe_allow_html=True,
    )

    tip = TIPS[int(time.time() // 6) % len(TIPS)]
    st.markdown(f'<div class="tip-card">\U0001F4A1 {tip}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Refresh status", use_container_width=True):
            st.rerun()
    with col2:
        auto_refresh = st.toggle("Auto-refresh every 5s", value=True)

    if auto_refresh:
        time.sleep(5)
        st.rerun()

# ---------------------------------------------------------------------------
# FAILED
# ---------------------------------------------------------------------------
elif status == jobs.STATUS_FAILED:
    st.markdown(
        f'<div class="risk-badge" style="--c:{RISK_COLORS["HIGH"]}">'
        f'<span class="dot" style="--c:{RISK_COLORS["HIGH"]}"></span>ANALYSIS FAILED</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">ERROR DETAIL</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="readout">{job.get("error_message") or "No error details recorded."}</div>',
        unsafe_allow_html=True,
    )
    if st.button("Try another video", type="primary"):
        st.switch_page("pages/2_Upload_Video.py")

# ---------------------------------------------------------------------------
# DONE
# ---------------------------------------------------------------------------
elif status == jobs.STATUS_DONE:
    risk_level = job.get("risk_level") or "UNKNOWN"
    risk_score = job.get("risk_score") or 0.0
    color = RISK_COLORS.get(risk_level, RISK_COLORS["UNKNOWN"])

    top_left, top_right = st.columns([1, 1])
    with top_left:
        st.markdown(risk_badge_html(risk_level), unsafe_allow_html=True)
        st.markdown(
            f'<p class="mono" style="color:var(--text-dim);margin-top:0.6rem;">'
            f'SESSION {job["id"][:8]}  \u2022  {job["video_filename"]}</p>',
            unsafe_allow_html=True,
        )

    gauge_col, trend_col = st.columns([1, 1], gap="large")

    with gauge_col:
        st.markdown('<div class="eyebrow">RISK SCORE</div>', unsafe_allow_html=True)
        if HAS_PLOTLY:
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=risk_score,
                    number={"suffix": "", "font": {"color": color, "family": "Space Grotesk"}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#8CA0C2"},
                        "bar": {"color": color},
                        "bgcolor": "rgba(0,0,0,0)",
                        "borderwidth": 0,
                        "steps": [
                            {"range": [0, 34], "color": "rgba(52,211,153,0.18)"},
                            {"range": [34, 67], "color": "rgba(245,185,66,0.18)"},
                            {"range": [67, 100], "color": "rgba(240,71,92,0.18)"},
                        ],
                    },
                )
            )
            fig.update_layout(
                height=240, margin=dict(l=20, r=20, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", font={"color": "#E8EDF4"},
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.metric("Risk score", f"{risk_score:.0f}")

    with trend_col:
        st.markdown('<div class="eyebrow">YOUR RECENT SESSIONS</div>', unsafe_allow_html=True)
        history = [j for j in reversed(user_jobs) if j["status"] == jobs.STATUS_DONE][-10:]
        if HAS_PLOTLY and len(history) >= 1:
            fig2 = go.Figure(
                go.Bar(
                    x=[j["created_at"].strftime("%m/%d") for j in history],
                    y=[j.get("risk_score") or 0 for j in history],
                    marker_color=[RISK_COLORS.get(j.get("risk_level"), RISK_COLORS["UNKNOWN"]) for j in history],
                )
            )
            fig2.update_layout(
                height=240, margin=dict(l=20, r=20, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#E8EDF4"},
                yaxis=dict(range=[0, 100], gridcolor="rgba(255,255,255,0.06)"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            )
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.caption("Not enough completed sessions yet to chart a trend.")

    st.divider()

    tab1, tab2 = st.tabs(["\U0001F4C4 Final report", "\U0001F9D1\u200D\u2696\uFE0F Human review notes"])
    with tab1:
        st.markdown(
            f'<div class="readout">{job.get("final_report") or "No report generated."}</div>',
            unsafe_allow_html=True,
        )
    with tab2:
        st.markdown(
            f'<div class="readout">{job.get("human_review") or "No human review generated."}</div>',
            unsafe_allow_html=True,
        )

    report_text = (
        f"{job.get('final_report', '')}\n\nHUMAN REVIEW:\n{job.get('human_review', '')}\n"
    )
    st.download_button(
        "\u2B07\uFE0F Download full report (.txt)",
        data=report_text,
        file_name=f"proctoring_report_{job['video_filename']}.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.divider()
if st.button("Upload another video"):
    st.switch_page("pages/2_Upload_Video.py")
