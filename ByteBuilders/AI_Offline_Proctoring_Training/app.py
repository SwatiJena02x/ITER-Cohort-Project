"""Entry point + login page for the AI proctoring UI.

Belongs at the project root as `app.py`. Run with `streamlit run app.py`.
Streamlit auto-discovers files under `pages/` as additional sidebar pages;
the numeric filename prefixes (1_, 2_, 3_) control their sidebar order.

Auth model: st.session_state["user"] holds the logged-in user's record
for the current browser session. Every other page checks for it at the
top and redirects to this page if missing -- see the top of
pages/2_Upload_Video.py and pages/3_Report.py.

Visuals live in theme.py and are shared across every page -- see that
module's docstring for the design rationale.
"""

import logging

import streamlit as st

from db.auth import verify_user
from db.database import init_db
from theme import inject_css, hero

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

st.set_page_config(page_title="AI Proctoring System", page_icon="\U0001F393", layout="centered")
inject_css()

init_db()

if "user" not in st.session_state:
    st.session_state.user = None


def _login_form() -> None:
    hero(
        eyebrow="SESSION INTEGRITY SCANNER",
        title="AI Proctoring System",
        tagline=(
            "Multi-agent review of exam recordings -- vision, audio and "
            "behavior signals cross-checked against your rubric before a "
            "human ever opens the video."
        ),
        pills=["\U0001F4F9 Video agent", "\U0001F3A4 Audio agent", "\U0001F9ED Behavior agent", "\U0001F4CA Risk scoring"],
    )

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="eyebrow">ACCESS</div>', unsafe_allow_html=True)
        st.markdown("### Log in")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. proctor_jane")
            password = st.text_input("Password", type="password", placeholder="\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022")
            submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Enter both username and password.")
            else:
                with st.spinner("Verifying credentials..."):
                    user = verify_user(username, password)
                if user is None:
                    st.error("Invalid username or password.")
                else:
                    st.session_state.user = user
                    st.toast(f"Welcome back, {user['username']}", icon="\u2705")
                    st.switch_page("pages/2_Upload_Video.py")

        st.markdown(
            '<p class="mono" style="color:var(--text-dim);font-size:0.8rem;margin-top:0.6rem;">'
            "No account yet?</p>",
            unsafe_allow_html=True,
        )
        if st.button("Create an account", use_container_width=True):
            st.switch_page("pages/1_Create_Account.py")

    with right:
        st.markdown('<div class="eyebrow">HOW IT WORKS</div>', unsafe_allow_html=True)
        st.markdown("### The pipeline")
        st.markdown(
            """
            <div class="readout">
1  video     &rarr; object / gaze / presence detection
2  audio     &rarr; speech &amp; ambient-sound transcription
3  behavior  &rarr; posture &amp; interaction pattern checks
4  activity  &rarr; raw signals merged into readable segments
5  risk      &rarr; LOW / MEDIUM / HIGH score against your rules
6  report    &rarr; deterministic report + narrative + human review
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="tip-card">Every session is scored the same way, '
            "every time -- the model never sees who it's grading.</div>",
            unsafe_allow_html=True,
        )


def _logged_in_view() -> None:
    hero(
        eyebrow="SIGNED IN",
        title=f"Welcome back, {st.session_state.user['username']}",
        tagline="Start a new scan or jump back into a report that's already in progress.",
    )

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        with st.container(border=True):
            st.markdown('<div class="eyebrow">START</div>', unsafe_allow_html=True)
            st.markdown("### \U0001F3A5 Upload a video")
            st.caption("Submit an exam recording for a fresh multi-agent scan.")
            if st.button("Upload a video", use_container_width=True, type="primary"):
                st.switch_page("pages/2_Upload_Video.py")
    with col2:
        with st.container(border=True):
            st.markdown('<div class="eyebrow">REVIEW</div>', unsafe_allow_html=True)
            st.markdown("### \U0001F4CB View reports")
            st.caption("Check progress or revisit a completed risk report.")
            if st.button("View reports", use_container_width=True):
                st.switch_page("pages/3_Report.py")

    st.divider()
    if st.button("Log out"):
        st.session_state.user = None
        st.rerun()


if st.session_state.user is None:
    _login_form()
else:
    _logged_in_view()
