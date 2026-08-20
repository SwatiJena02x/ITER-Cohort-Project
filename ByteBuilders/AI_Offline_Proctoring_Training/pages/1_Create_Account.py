"""Signup page.

Belongs in `pages/1_Create_Account.py`. Streamlit auto-discovers files
under pages/ as sidebar entries; the "1_" prefix just controls ordering
and is stripped from the displayed page title.

On a successful create_user() call this page no longer waits for the
user to click anything -- it shows a brief confirmation animation and
then calls st.switch_page("app.py") itself, landing them straight on the
login form with their new username ready to type in.
"""

import time

import streamlit as st

from db.auth import SignupError, create_user
from db.database import init_db
from theme import inject_css, hero

st.set_page_config(page_title="Create Account", page_icon="\U0001F4DD")
inject_css()
init_db()

hero(
    eyebrow="NEW OPERATOR",
    title="Create an account",
    tagline="One account gets you upload access and every report you've ever run, in one place.",
)


def _password_strength(pw: str) -> tuple[int, str, str]:
    """Cheap heuristic strength meter -- purely a UI nudge, the real rule
    enforced server-side is still just MIN_PASSWORD_LENGTH in db/auth.py.
    """
    if not pw:
        return 0, "", "var(--border)"
    score = 0
    score += min(len(pw), 16) / 16 * 2
    score += any(c.islower() for c in pw)
    score += any(c.isupper() for c in pw)
    score += any(c.isdigit() for c in pw)
    score += any(not c.isalnum() for c in pw)
    pct = min(int(score / 6 * 100), 100)
    if pct < 35:
        return pct, "WEAK", "var(--high)"
    if pct < 70:
        return pct, "OKAY", "var(--medium)"
    return pct, "STRONG", "var(--low)"


left, right = st.columns([1.1, 0.9], gap="large")

with left:
    with st.form("signup_form"):
        username = st.text_input("Username", help="3-32 characters: letters, numbers, ., _, -")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password", help="At least 8 characters")
        confirm_password = st.text_input("Confirm password", type="password")

        pct, label, color = _password_strength(password)
        st.markdown(
            f"""
            <div style="margin:-0.4rem 0 0.9rem 0;">
              <div style="height:6px;border-radius:3px;background:var(--border);overflow:hidden;">
                <div style="height:100%;width:{pct}%;background:{color};transition:width 0.2s;"></div>
              </div>
              <div class="mono" style="font-size:0.72rem;color:{color};margin-top:0.25rem;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)

    if submitted:
        if password != confirm_password:
            st.error("Passwords do not match.")
        else:
            try:
                with st.spinner("Provisioning your account..."):
                    user = create_user(username, email, password)

                success_box = st.empty()
                success_box.success(
                    f"Account created for **{user['username']}**. Redirecting you to log in..."
                )
                st.balloons()
                time.sleep(1.4)
                st.switch_page("app.py")
            except SignupError as exc:
                # SignupError messages are written to be shown directly to the
                # user -- see db/auth.py for what's covered (bad format,
                # duplicate username/email, weak password).
                st.error(str(exc))

    st.markdown(
        '<p class="mono" style="color:var(--text-dim);font-size:0.8rem;margin-top:0.4rem;">'
        "Already registered?</p>",
        unsafe_allow_html=True,
    )
    if st.button("Back to log in", use_container_width=True):
        st.switch_page("app.py")

with right:
    st.markdown('<div class="eyebrow">ACCOUNT RULES</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="readout">
username   3-32 chars  [a-zA-Z0-9 . _ -]
email      must contain @ and a domain
password   8+ characters minimum
storage    bcrypt hash only -- raw password
           is never written to disk or logs
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tip-card">Usernames and emails must be unique -- '
        "you'll get a clear message if either is already taken.</div>",
        unsafe_allow_html=True,
    )
