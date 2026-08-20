import uuid
import streamlit as st
from langgraph_sdk import get_sync_client
from datetime import datetime
import time
import urllib.request

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Algorithm Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# LANGGRAPH CONFIG
# ============================================================

import os

LANGGRAPH_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:2024"
)
GRAPH_ID = "dsa_coach"

# ============================================================
# LANGGRAPH CLIENT
# ============================================================

client = get_sync_client(url=LANGGRAPH_URL)

def check_langgraph_backend():
    try:
        _ = client.assistants.search()
        return True
    except Exception:
        return False

client_available = check_langgraph_backend()

# ============================================================
# SESSION STATE
# ============================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_input_key" not in st.session_state:
    st.session_state.chat_input_key = 0

# ============================================================
# CUSTOM CSS - MINIMAL AESTHETIC & ANIMATIONS
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    * {
        box-sizing: border-box;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre, .stCodeBlock * {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stApp {
        background: #090a0f;
        color: #f1f5f9;
        overflow-x: hidden;
    }

    /* Ambient Background Mesh */
    .stApp::before {
        content: '';
        position: fixed;
        top: -40%;
        left: -20%;
        width: 140vw;
        height: 140vh;
        background: 
            radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 80% 30%, rgba(56, 189, 248, 0.06) 0%, transparent 45%),
            radial-gradient(circle at 50% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 50%);
        animation: aurora-drift 22s ease-in-out infinite alternate;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes aurora-drift {
        0% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.08) rotate(2deg); }
        100% { transform: scale(1) rotate(-1deg); }
    }

    .block-container {
        position: relative;
        z-index: 1;
        padding: 2rem 2.5rem 5rem;
        max-width: 1500px;
    }

    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 99px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.24);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: rgba(11, 13, 20, 0.85);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(28px);
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 20px;
        padding: 2rem 2.2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(12px);
    }

    .hero-container::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 10%;
        width: 80%;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), rgba(56, 189, 248, 0.3), transparent);
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #ffffff 40%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-tagline {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-top: 0.35rem;
        font-weight: 400;
    }

    /* Cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        backdrop-filter: blur(8px);
    }

    .feature-card:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(255, 255, 255, 0.12);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }

    .feature-card .icon {
        font-size: 1.15rem;
        margin-bottom: 0.4rem;
        display: inline-block;
    }

    .feature-card .title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #f1f5f9;
    }

    .feature-card .desc {
        font-size: 0.72rem;
        color: #64748b;
        margin-top: 0.2rem;
    }

    /* Chat Messages */
    div[data-testid="stChatMessage"] {
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.04);
        background: rgba(255, 255, 255, 0.015);
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.75rem;
        animation: fadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    div[data-testid="stChatMessage"][data-testid="stChatMessageUser"] {
        background: rgba(99, 102, 241, 0.05);
        border-color: rgba(99, 102, 241, 0.15);
    }

    /* Shimmer Thinking Indicator */
    .thinking-shimmer {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: #94a3b8;
        background: linear-gradient(90deg, #64748b 0%, #cbd5e1 50%, #64748b 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 1.8s linear infinite;
    }

    @keyframes shimmer {
        0% { background-position: 200% center; }
        100% { background-position: -200% center; }
    }

    /* Button Aesthetic */
    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.03);
        color: #e2e8f0;
        font-size: 0.82rem;
        font-weight: 500;
        padding: 0.45rem 1rem;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.07);
        border-color: rgba(255, 255, 255, 0.2);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Chat Input Bar */
    div[data-testid="stChatInput"] {
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(15, 18, 28, 0.6);
        backdrop-filter: blur(14px);
        transition: all 0.25s ease;
    }

    div[data-testid="stChatInput"]:focus-within {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0;">
        <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff; letter-spacing: -0.02em;">✨ Core Engine</div>
        <div style="font-size: 0.72rem; color: #64748b;">LangGraph Orchestrator</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Session Handling
    st.caption("THREAD CONTEXT")
    col_sid, col_new = st.columns([2, 1])
    with col_sid:
        st.code(st.session_state.session_id, language="text")
    with col_new:
        if st.button("Reset", use_container_width=True):
            st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
            st.session_state.thread_id = None
            st.session_state.messages = []
            st.session_state.chat_input_key += 1
            st.rerun()

    st.divider()

    # Status
    st.caption("BACKEND STATUS")
    if client_available:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #34d399; font-size: 0.8rem; font-weight: 500;">
            <span style="width: 7px; height: 7px; background: #34d399; border-radius: 50%; box-shadow: 0 0 8px #34d399;"></span> Operational
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; color: #f87171; font-size: 0.8rem; font-weight: 500;">
            <span style="width: 7px; height: 7px; background: #f87171; border-radius: 50%; box-shadow: 0 0 8px #f87171;"></span> Disconnected
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.caption("ENGINES")
    engines = ["Adaptive Problem Engine", "Stepwise Guidance", "Indexed Retrieval", "Syntax & Logic Analyzer"]
    for eng in engines:
        st.markdown(f"<div style='font-size: 0.78rem; color: #94a3b8; padding: 0.15rem 0;'>• {eng}</div>", unsafe_allow_html=True)

# ============================================================
# HERO & OVERVIEW
# ============================================================

st.markdown("""
<div class="hero-container">
    <div class="hero-title">Interactive Problem Workspace</div>
    <div class="hero-tagline">Analyze algorithms, debug complex edge cases, and work through problems interactively.</div>
</div>
""", unsafe_allow_html=True)

# Cards Row
cols = st.columns(4)
cards_data = [
    ("⚡", "Dynamic Generation", "Tailored algorithmic challenges"),
    ("🔍", "Context Retrieval", "Semantic search across reference texts"),
    ("💡", "Hint Guidance", "Step-by-step progressive clues"),
    ("⚡", "State Continuity", "Persisted run execution thread"),
]
for col, (icon, title, desc) in zip(cols, cards_data):
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <span class="icon">{icon}</span>
            <div class="title">{title}</div>
            <div class="desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ============================================================
# WORKSPACE LAYOUT
# ============================================================

chat_col, quick_action_col = st.columns([3.2, 1], gap="large")

with quick_action_col:
    st.markdown("##### Quick Actions")
    prompts = [
        ("✨ Medium DP Challenge", "Give me a medium dynamic programming problem with arrays"),
        ("✨ Progressive Hint", "Give me a hint for the current problem"),
        ("✨ Complexity Check", "Analyze the time and space complexity of my approach"),
        ("✨ Edge Cases", "What are the most common edge cases for this pattern?"),
    ]

    with st.form("prompt_launcher"):
        for label, text in prompts:
            if st.form_submit_button(label, use_container_width=True):
                st.session_state.quick_prompt = text
                st.session_state.chat_input_key += 1
                st.rerun()

with chat_col:
    st.markdown("##### Workspace Stream")

    if not st.session_state.messages:
        st.markdown("""
        <div style="border: 1px dashed rgba(255,255,255,0.08); border-radius: 12px; padding: 2rem; text-align: center;">
            <div style="font-size: 0.9rem; color: #94a3b8;">Workspace initialized. Start by submitting a prompt or picking an action.</div>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "✨"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "metadata" in message:
                meta = message["metadata"]
                with st.expander("Execution Trace", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.caption("ROUTE")
                        st.code(meta.get("route", "DIRECT"))
                    with c2:
                        st.caption("PROBLEM")
                        st.code(meta.get("problem_id", "-"))
                    with c3:
                        st.caption("ITERATION")
                        st.code(str(meta.get("iteration", 0)))

# ============================================================
# INPUT & EXECUTION
# ============================================================

input_key = f"chat_input_{st.session_state.chat_input_key}"
quick_prompt = st.session_state.get("quick_prompt", "")

if quick_prompt:
    user_message = quick_prompt
    st.session_state.quick_prompt = ""
else:
    user_message = st.chat_input("Enter your algorithm prompt or code snippet...", key=input_key)

if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})

    with chat_col:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_message)

        with st.chat_message("assistant", avatar="✨"):
            placeholder = st.empty()
            placeholder.markdown('<div class="thinking-shimmer">✨ Processing workspace graph...</div>', unsafe_allow_html=True)

            try:
                if st.session_state.thread_id is None and client_available:
                    try:
                        thread = client.threads.create()
                        st.session_state.thread_id = thread["thread_id"]
                    except Exception as e:
                        st.error("Failed to initialize execution thread.")
                        st.code(str(e))
                        client_available = False

                if client_available and st.session_state.thread_id:
                    graph_input = {
                        "question": user_message,
                        "session_id": st.session_state.session_id,
                        "conversation_history": [m["content"] for m in st.session_state.messages[-6:]],
                        "problem_id": "",
                        "problem": "",
                        "code": "",
                    }

                    try:
                        result = client.runs.wait(
                            st.session_state.thread_id,
                            GRAPH_ID,
                            input=graph_input
                        )

                        answer = result.get("answer", "")
                        if not answer:
                            answer = result.get("observation", "No response generated.")

                        route = result.get("route", "DIRECT")
                        problem_id = result.get("problem_id", "")
                        iteration = result.get("iteration", 0)

                        placeholder.markdown(answer)

                        with st.expander("Execution Trace", expanded=False):
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.caption("ROUTE")
                                st.code(route or "DIRECT")
                            with c2:
                                st.caption("PROBLEM")
                                st.code(problem_id or "-")
                            with c3:
                                st.caption("ITERATION")
                                st.code(str(iteration))

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "metadata": {
                                "route": route,
                                "problem_id": problem_id,
                                "iteration": iteration,
                            },
                        })

                    except Exception as e:
                        placeholder.error("Graph run execution failed.")
                        st.code(str(e))
                else:
                    placeholder.error("LangGraph backend unavailable.")
            except Exception as e:
                placeholder.error("Unexpected execution error.")
                st.code(str(e))