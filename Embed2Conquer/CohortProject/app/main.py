"""
DSA Coach Tree - Main Streamlit Application
============================================

Project structure:

    app/
        main.py
        code_page.py

Normal DSA conversation:

    Streamlit
        ↓
    DSATreeOrchestrator
        ↓
    RAG Agent

Coding practice:

    Sidebar
        ↓
    💻 Code
        ↓
    code_page.py
        ↓
    StepEvaluatorSession
        ↓
    step_evaluator_agent.py
"""

import sys
from pathlib import Path

import streamlit as st


# ============================================================
# 1. PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# 2. IMPORT RAG ORCHESTRATOR
# ============================================================

from agent.supervisor import DSATreeOrchestrator
from app.code_page import render_code_page

# ============================================================
# 3. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DSA Coach Tree",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 4. IMPORT CODE PAGE RENDER FUNCTION
# ============================================================

# from app.code_page import render_code_page


# ============================================================
# 5. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       WELCOME SCREEN
       ====================================================== */

    .welcome-title {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }

    .welcome-subtitle {
        margin-top: -5px !important;
        padding-top: 0px !important;
        font-size: 18px;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {
        padding-top: 1rem;
    }


    /* ======================================================
       FILE UPLOADER
       ====================================================== */

    .upload-box {
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 8px;
    }


    /* ======================================================
       CHAT INPUT
       ====================================================== */

    div[data-testid="stChatInput"] {
        margin-top: 0px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 6. SESSION STATE
# ============================================================

if "orchestrator" not in st.session_state:

    st.session_state.orchestrator = (
        DSATreeOrchestrator()
    )


if "messages" not in st.session_state:

    st.session_state.messages = []


if "chat_sessions" not in st.session_state:

    st.session_state.chat_sessions = {}


if "current_chat" not in st.session_state:

    st.session_state.current_chat = None


if "new_chat_mode" not in st.session_state:

    st.session_state.new_chat_mode = True


if "show_file_uploader" not in st.session_state:

    st.session_state.show_file_uploader = False


if "uploaded_files" not in st.session_state:

    st.session_state.uploaded_files = []


# ============================================================
# 7. CURRENT PAGE
# ============================================================

if "current_page" not in st.session_state:

    st.session_state.current_page = "chat"


# ============================================================
# 8. SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # Logo
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            padding: 5px 0 10px 0;
        ">
            <h2 style="
                margin: 0;
                padding: 0;
            ">
                🌳 DSA Coach Tree
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()


    # ========================================================
    # Q&A
    # ========================================================

    if st.button(
        "💬 Q&A",
        use_container_width=True,
        key="sidebar_qa",
    ):

        st.session_state.current_page = "chat"

        st.rerun()


    # ========================================================
    # CODE
    # ========================================================

    if st.button(
        "💻 Code",
        use_container_width=True,
        key="sidebar_code",
    ):

        st.session_state.current_page = "code"

        st.rerun()


    # ========================================================
    # PROFILE
    # ========================================================

    st.button(
        "👤 Profile",
        use_container_width=True,
        key="sidebar_profile",
    )


    # ========================================================
    # NEW CHAT
    # ========================================================

    if st.button(
        "➕ New Chat",
        use_container_width=True,
        key="sidebar_new_chat",
    ):

        st.session_state.messages = []

        st.session_state.current_chat = None

        st.session_state.new_chat_mode = True

        # Fresh RAG conversation
        st.session_state.orchestrator = (
            DSATreeOrchestrator()
        )

        st.session_state.current_page = "chat"

        st.rerun()


    # ========================================================
    # SETTINGS
    # ========================================================

    st.button(
        "⚙️ Settings",
        use_container_width=True,
        key="sidebar_settings",
    )


    # ========================================================
    # LOGOUT
    # ========================================================

    st.button(
        "🚪 Logout",
        use_container_width=True,
        key="sidebar_logout",
    )


    st.divider()


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    with st.expander(
        "📜 Chat History",
        expanded=True,
    ):

        search_text = st.text_input(
            "Search history",
            placeholder="Search history...",
            label_visibility="collapsed",
            key="history_search",
        )


        filtered_titles = []

        for title in st.session_state.chat_sessions:

            if search_text.lower() in title.lower():

                filtered_titles.append(title)


        if not filtered_titles:

            st.caption(
                "No chats yet."
            )

        else:

            for index, title in enumerate(
                filtered_titles
            ):

                display_title = (
                    title[:35] + "..."
                    if len(title) > 35
                    else title
                )


                if st.button(
                    display_title,
                    key=f"history_{index}_{title}",
                    use_container_width=True,
                ):

                    st.session_state.current_chat = title

                    st.session_state.messages = (
                        st.session_state
                        .chat_sessions[title]
                    )

                    st.session_state.new_chat_mode = False

                    st.session_state.current_page = "chat"

                    st.rerun()


# ============================================================
# 9. PAGE ROUTING
# ============================================================
if st.session_state.current_page == "code":
    render_code_page()
    st.stop()
# ============================================================
# 10. MAIN CHAT PAGE
# ============================================================


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <h1 class="welcome-title">
            💬 DSA Coach Tree
        </h1>

        <div class="welcome-subtitle">
            Ask me anything about Trees and Data Structures.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 11. DISPLAY CONVERSATION
# ============================================================

else:

    for message in st.session_state.messages:

        role = message["role"]

        content = message["content"]


        if role == "user":

            with st.chat_message("user"):

                st.markdown(content)


        elif role == "assistant":

            with st.chat_message("assistant"):

                st.markdown(content)


# ============================================================
# 12. FILE UPLOAD
# ============================================================

if st.session_state.show_file_uploader:

    st.markdown(
        '<div class="upload-box">',
        unsafe_allow_html=True,
    )


    uploaded_files = st.file_uploader(
        "Select files",
        type=[
            "pdf",
            "md",
            "txt",
            "csv",
            "json",
            "py",
            "ipynb",
            "docx",
        ],
        accept_multiple_files=True,
        label_visibility="visible",
        key="chat_file_uploader",
    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


    if uploaded_files:

        st.session_state.uploaded_files = uploaded_files

        st.success(
            f"{len(uploaded_files)} file(s) selected."
        )

        for file in uploaded_files:

            st.caption(
                f"📄 {file.name}"
            )


# ============================================================
# 13. INPUT CONTROL
# ============================================================

col_plus, col_input, col_voice = st.columns(
    [1, 12, 1],
    vertical_alignment="bottom",
)


# ============================================================
# 14. PLUS BUTTON
# ============================================================

with col_plus:

    if st.button(
        "＋",
        help="Attach files",
        use_container_width=True,
        key="chat_plus_button",
    ):

        st.session_state.show_file_uploader = (
            not st.session_state.show_file_uploader
        )

        st.rerun()


# ============================================================
# 15. CHAT INPUT
# ============================================================

with col_input:

    prompt = st.chat_input(
        "Ask your DSA question..."
    )


# ============================================================
# 16. VOICE BUTTON
# ============================================================

with col_voice:

    voice_clicked = st.button(
        "🎤",
        help="Voice input",
        use_container_width=True,
        key="chat_voice_button",
    )


if voice_clicked:

    st.info(
        "🎤 Voice input is not connected yet."
    )


# ============================================================
# 17. SEND MESSAGE
# ============================================================

if prompt:

    # --------------------------------------------------------
    # Create new chat
    # --------------------------------------------------------

    if st.session_state.new_chat_mode:

        title = prompt.strip()

        if len(title) > 45:

            title = title[:45] + "..."

        st.session_state.current_chat = title

        st.session_state.chat_sessions[
            title
        ] = []

        st.session_state.new_chat_mode = False


    # --------------------------------------------------------
    # User message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )


    # --------------------------------------------------------
    # RAG Agent
    # --------------------------------------------------------

    with st.spinner(
        "🌳 Searching your Tree knowledge base..."
    ):

        try:

            reply = (
                st.session_state
                .orchestrator
                .send_message(prompt)
            )

        except Exception as error:

            reply = (
                "⚠️ I couldn't process your question.\n\n"
                f"Error: `{error}`"
            )


    # --------------------------------------------------------
    # Assistant response
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply,
        }
    )


    # --------------------------------------------------------
    # Save history
    # --------------------------------------------------------

    st.session_state.chat_sessions[
        st.session_state.current_chat
    ] = st.session_state.messages


    # --------------------------------------------------------
    # Rerun
    # --------------------------------------------------------

    st.rerun()