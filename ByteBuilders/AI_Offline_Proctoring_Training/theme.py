"""Shared visual identity for the AI Proctoring System UI.

Belongs at the project root as `theme.py`. Imported by app.py and every
page in pages/ so the whole app shares one visual language instead of
each page styling itself ad hoc.

Design language -- "vision system HUD":
  The product's actual job is watching video/audio/behavior and flagging
  what it sees, so the UI borrows from camera viewfinders and scanner
  overlays rather than a generic dashboard look: corner-bracket frames
  (like a viewfinder reticle) on every card, a scanline sweep on hero
  banners, and monospace "readouts" for status/log-like text. Everything
  else is kept quiet so those two motifs stay legible as the signature.

  Palette -- deep ink navy panels, a signal-teal accent (evokes a scope/
  scanner readout, not a brand color), and the three risk colors doubling
  as the only "loud" colors in the system (mint/amber/coral for
  LOW/MEDIUM/HIGH) so risk is the one thing that visually jumps out.

Only inject_css() has side effects (writes a <style> block). Everything
else here returns an HTML string for the caller to hand to
st.markdown(..., unsafe_allow_html=True).
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------

INK = "#080D18"
PANEL = "#101A2E"
PANEL_LIGHT = "#16213A"
BORDER = "#243252"
TEXT = "#E8EDF4"
TEXT_DIM = "#8CA0C2"
ACCENT = "#4FD1C5"          # signal teal
ACCENT_STRONG = "#2BB8AB"
LOW = "#34D399"
MEDIUM = "#F5B942"
HIGH = "#F0475C"

RISK_COLORS = {"LOW": LOW, "MEDIUM": MEDIUM, "HIGH": HIGH, "UNKNOWN": TEXT_DIM}


def inject_css() -> None:
    """Write the global stylesheet. Call once near the top of every page,
    right after st.set_page_config().
    """
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

        :root {{
            --ink: {INK}; --panel: {PANEL}; --panel-light: {PANEL_LIGHT};
            --border: {BORDER}; --text: {TEXT}; --text-dim: {TEXT_DIM};
            --accent: {ACCENT}; --accent-strong: {ACCENT_STRONG};
            --low: {LOW}; --medium: {MEDIUM}; --high: {HIGH};
        }}

        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

        .stApp {{
            background:
                radial-gradient(circle at 12% -10%, rgba(79,209,197,0.16), transparent 42%),
                radial-gradient(circle at 90% 10%, rgba(240,71,92,0.08), transparent 38%),
                repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 34px),
                repeating-linear-gradient(90deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 34px),
                var(--ink);
            color: var(--text);
        }}

        [data-testid="stHeader"] {{ background: transparent; }}
        #MainMenu, footer {{ visibility: hidden; }}

        h1, h2, h3 {{ font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }}

        /* -- eyebrow / monospace utility text ------------------------- */
        .eyebrow {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem; letter-spacing: 0.22em; text-transform: uppercase;
            color: var(--accent); margin-bottom: 0.4rem;
        }}
        .mono {{ font-family: 'JetBrains Mono', monospace; }}

        /* -- viewfinder corner-bracket frame, applied to every bordered
           container and every form so the whole app reads as one system */
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stForm"] {{
            position: relative;
            background: linear-gradient(180deg, var(--panel), var(--panel-light)) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            padding: 0.4rem;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]::before,
        div[data-testid="stForm"]::before {{
            content: ''; position: absolute; top: -1px; left: -1px;
            width: 20px; height: 20px;
            border-top: 2px solid var(--accent); border-left: 2px solid var(--accent);
            border-radius: 6px 0 0 0; pointer-events: none;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]::after,
        div[data-testid="stForm"]::after {{
            content: ''; position: absolute; bottom: -1px; right: -1px;
            width: 20px; height: 20px;
            border-bottom: 2px solid var(--accent); border-right: 2px solid var(--accent);
            border-radius: 0 0 6px 0; pointer-events: none;
        }}

        /* -- hero banner with a sweeping scanline ---------------------- */
        .scan-hero {{
            position: relative; overflow: hidden;
            border: 1px solid var(--border); border-radius: 14px;
            padding: 2.2rem 2rem; margin-bottom: 1.4rem;
            background: linear-gradient(140deg, rgba(79,209,197,0.10), rgba(16,26,46,0.4));
        }}
        .scan-hero::after {{
            content: ''; position: absolute; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            box-shadow: 0 0 18px 2px rgba(79,209,197,0.7);
            animation: sweep 5s linear infinite;
        }}
        @keyframes sweep {{
            0% {{ top: -5%; opacity: 0; }}
            8% {{ opacity: 1; }}
            50% {{ top: 100%; opacity: 1; }}
            58% {{ opacity: 0; }}
            100% {{ top: 100%; opacity: 0; }}
        }}
        .scan-hero h1 {{ margin: 0.2rem 0 0.3rem 0; font-size: 2.1rem; }}
        .scan-hero p.tagline {{ color: var(--text-dim); font-size: 0.98rem; max-width: 640px; }}

        /* -- modality pills (video/audio/behavior) ---------------------- */
        .pill-row {{ display: flex; gap: 0.5rem; margin-top: 1rem; flex-wrap: wrap; }}
        .pill {{
            font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
            border: 1px solid var(--border); border-radius: 999px;
            padding: 0.28rem 0.7rem; color: var(--text-dim); background: rgba(255,255,255,0.02);
        }}

        /* -- status readout block --------------------------------------- */
        .readout {{
            font-family: 'JetBrains Mono', monospace; font-size: 0.86rem;
            background: rgba(0,0,0,0.25); border-left: 3px solid var(--accent);
            border-radius: 4px; padding: 0.85rem 1rem; color: var(--text);
            white-space: pre-wrap; line-height: 1.55;
        }}

        /* -- risk badge --------------------------------------------------- */
        .risk-badge {{
            display: inline-flex; align-items: center; gap: 0.5rem;
            font-family: 'Space Grotesk', sans-serif; font-weight: 700;
            font-size: 1.05rem; padding: 0.45rem 1rem; border-radius: 999px;
            border: 1px solid var(--c); color: var(--c);
            background: color-mix(in srgb, var(--c) 12%, transparent);
        }}
        .dot {{ width: 9px; height: 9px; border-radius: 50%; background: var(--c);
                box-shadow: 0 0 8px 1px var(--c); }}

        /* -- buttons -------------------------------------------------- */
        .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {{
            font-family: 'Space Grotesk', sans-serif; font-weight: 600;
            letter-spacing: 0.02em; border-radius: 8px !important;
            border: 1px solid var(--accent) !important;
            background: linear-gradient(180deg, rgba(79,209,197,0.22), rgba(79,209,197,0.08)) !important;
            color: var(--text) !important; transition: all 0.15s ease;
        }}
        .stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {{
            border-color: var(--accent-strong) !important;
            box-shadow: 0 0 16px rgba(79,209,197,0.35);
            transform: translateY(-1px);
        }}
        button[kind="primary"] {{
            background: linear-gradient(180deg, var(--accent), var(--accent-strong)) !important;
            color: #05130F !important; border: none !important;
        }}

        /* -- inputs ----------------------------------------------------- */
        .stTextInput>div>div, .stSelectbox>div>div, div[data-baseweb="select"]>div {{
            background: rgba(0,0,0,0.25) !important; border: 1px solid var(--border) !important;
            border-radius: 7px !important;
        }}
        .stTextInput>div>div:focus-within {{
            border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent);
        }}
        label {{ font-size: 0.83rem !important; color: var(--text-dim) !important; }}

        /* -- misc --------------------------------------------------------- */
        hr {{ border-color: var(--border) !important; }}
        .tip-card {{
            border: 1px dashed var(--border); border-radius: 10px; padding: 0.9rem 1.1rem;
            color: var(--text-dim); font-size: 0.88rem; margin-top: 0.6rem;
        }}
        .step-row {{ display: flex; gap: 0.4rem; margin: 0.9rem 0; flex-wrap: wrap; }}
        .step-chip {{
            font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
            padding: 0.32rem 0.65rem; border-radius: 6px; border: 1px solid var(--border);
            color: var(--text-dim);
        }}
        .step-chip.active {{
            color: var(--ink); background: var(--accent); border-color: var(--accent);
            box-shadow: 0 0 10px rgba(79,209,197,0.5);
        }}
        .step-chip.done {{ color: var(--accent); border-color: var(--accent); }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(eyebrow: str, title: str, tagline: str, pills=None) -> None:
    """Render the shared scanline hero banner used at the top of every page."""
    pills_html = ""
    if pills:
        pills_html = '<div class="pill-row">' + "".join(
            f'<span class="pill">{p}</span>' for p in pills
        ) + "</div>"
    st.markdown(
        f"""
        <div class="scan-hero">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p class="tagline">{tagline}</p>
            {pills_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge_html(risk_level: str) -> str:
    color = RISK_COLORS.get(risk_level, TEXT_DIM)
    return (
        f'<span class="risk-badge" style="--c:{color}">'
        f'<span class="dot" style="--c:{color}"></span>{risk_level}</span>'
    )


def readout(text: str) -> None:
    st.markdown(f'<div class="readout">{text}</div>', unsafe_allow_html=True)
