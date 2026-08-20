print("🔥 LOADED CODE_PAGE FROM:", __file__)
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.step_evaluator_agent import StepEvaluatorSession


def render_code_page():
    # -----------------------------
    # SESSION STATE
    # -----------------------------

    if "step_session" not in st.session_state:
        st.session_state.step_session = StepEvaluatorSession()

    if "coding_question" not in st.session_state:
        st.session_state.coding_question = None

    if "coding_topic" not in st.session_state:
        st.session_state.coding_topic = "Binary Tree"

    if "coding_difficulty" not in st.session_state:
        st.session_state.coding_difficulty = "easy"

    if "student_code" not in st.session_state:
        st.session_state.student_code = ""

    if "evaluation_result" not in st.session_state:
        st.session_state.evaluation_result = None

    if "hint_result" not in st.session_state:
        st.session_state.hint_result = None


    # -----------------------------
    # SIDEBAR
    # -----------------------------

    with st.sidebar:

        st.markdown("## 🌳 DSA Coach Tree")
        st.caption("Coding Practice")

        st.divider()

        if st.button(
            "💬 Q&A",
            key="code_page_qa_button",
            use_container_width=True,
        ):
            st.session_state.current_page = "chat"
            st.rerun()

        st.button(
            "💻 Code",
            key="code_page_code_button",
            use_container_width=True,
            disabled=True,
        )

        st.divider()

        st.markdown("### 🎯 Practice Settings")

        topic = st.selectbox(
            "Topic",
            [
                "Binary Tree",
                "Binary Search Tree",
                "Tree Traversal",
                "Tree Recursion",
                "AVL Tree",
                "Heap",
                "Any Tree Topic",
            ],
            key="code_topic_selectbox",
        )

        difficulty = st.selectbox(
            "Difficulty",
            [
                "easy",
                "medium",
                "hard",
            ],
            key="code_difficulty_selectbox",
        )

        if st.button(
            "🔄 New Question",
            key="code_new_question_button",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.coding_topic = topic
            st.session_state.coding_difficulty = difficulty

            st.session_state.coding_question = None
            st.session_state.student_code = ""
            st.session_state.evaluation_result = None
            st.session_state.hint_result = None

            with st.spinner(
                "🌳 Generating coding question..."
            ):

                try:
                    question = (st.session_state.step_session.new_question(topic=topic,difficulty=difficulty,))
                    print("=" * 80)
                    print("DEBUG - NEW QUESTION RETURNED TO CODE_PAGE")
                    print("=" * 80)
                    print("QUESTION:", question)
                    print("DEBUG - ABOUT TO RENDER QUESTION")
                    st.session_state.coding_question = question

                except Exception as error:

                    st.error(
                        f"Unable to generate question:\n\n{error}"
                    )

            st.rerun()


    # -----------------------------
    # PAGE HEADER
    # -----------------------------

    st.title("💻 Coding Practice")

    st.caption(
        "Solve Tree problems, submit your code, "
        "and improve your DSA skills."
    )


    # -----------------------------
    # BACKEND SESSION
    # -----------------------------

    step_session = (
        st.session_state.step_session
    )


    # -----------------------------
    # NO QUESTION
    # -----------------------------

    if st.session_state.coding_question is None:

        st.info(
            "🌳 No coding question is active."
        )

        st.markdown(
            """
            ## 🚀 Start Practicing

            Select a topic and difficulty from the
            sidebar and click **🔄 New Question**.
            """
        )

        return


    # -----------------------------
    # QUESTION
    # -----------------------------

    question = (
        st.session_state.coding_question
    )

    if step_session.current_question:

        data = step_session.current_question

        title = data.get(
            "title",
            "Coding Problem",
        )

        statement = data.get(
            "statement",
            question,
        )

        topic_value = data.get(
            "topic",
            st.session_state.coding_topic,
        )

        difficulty_value = data.get(
            "difficulty",
            st.session_state.coding_difficulty,
        )

    else:

        title = "Coding Problem"
        statement = question

        topic_value = (
            st.session_state.coding_topic
        )

        difficulty_value = (
            st.session_state.coding_difficulty
        )


    # -----------------------------
    # QUESTION DISPLAY
    # -----------------------------

    st.divider()

    col1, col2, col3 = st.columns(
        [6, 2, 2]
    )

    with col1:
        st.subheader(
            "📋 " + str(title)
        )

    with col2:
        st.metric(
            "Topic",
            str(topic_value),
        )

    with col3:
        st.metric(
            "Difficulty",
            str(difficulty_value).upper(),
        )


    st.markdown(
        "### 📖 Problem Statement"
    )

    st.markdown(statement)


    # -----------------------------
    # FUNCTION NAME
    # -----------------------------

    if step_session.function_name:

        st.info(
            "💡 Your solution should define "
            f"`{step_session.function_name}()`"
        )


    # -----------------------------
    # RUBRIC
    # -----------------------------

    if step_session.rubric:

        with st.expander(
            "📌 What will be evaluated?"
        ):

            for item in step_session.rubric:
                st.markdown(
                    f"- {item}"
                )


    # ========================================================
    # CODE INPUT
    # ========================================================

    st.markdown("## 🧑‍💻 Your Code")

    st.caption(
        "Write your Python solution below."
    )

    code = st.text_area(
        "Code Editor",
        value=st.session_state.student_code,
        height=550,
        placeholder="""def solution(root):
    # Write your solution here
    pass
""",
        label_visibility="collapsed",
        key="student_code_editor",
    )

    st.session_state.student_code = code


    # ========================================================
    # BUTTONS
    # ========================================================

    col_submit, col_hint, col_space = st.columns(
        [2, 2, 8]
    )


    with col_submit:

        submit_clicked = st.button(
            "▶️ Submit Code",
            key="submit_code_button",
            type="primary",
            use_container_width=True,
        )


    with col_hint:

        hint_clicked = st.button(
            "💡 Hint",
            key="request_hint_button",
            use_container_width=True,
        )


    # ========================================================
    # SUBMIT → BACKEND
    # ========================================================

    if submit_clicked:

        if not code.strip():

            st.warning(
                "⚠️ Please write your solution first."
            )

        else:

            with st.spinner(
                "🧪 Evaluating your solution..."
            ):

                try:

                    result = (
                        step_session
                        .submit_code(code)
                    )

                    st.session_state.evaluation_result = result
                    st.session_state.hint_result = None

                except Exception as error:

                    st.session_state.evaluation_result = (
                        f"⚠️ Evaluation failed:\n\n{error}"
                    )

            st.rerun()


    # ========================================================
    # HINT → BACKEND
    # ========================================================

    if hint_clicked:

        with st.spinner(
            "💡 Generating a hint..."
        ):

            try:

                hint = (
                    step_session
                    .request_hint()
                )

                st.session_state.hint_result = hint

            except Exception as error:

                st.session_state.hint_result = (
                    f"⚠️ Unable to generate hint:\n\n{error}"
                )

        st.rerun()


    # ========================================================
    # SHOW HINT
    # ========================================================

    if st.session_state.hint_result:

        st.divider()

        st.markdown("## 💡 Hint")

        st.info(
            st.session_state.hint_result
        )


    # ========================================================
    # SHOW EVALUATION
    # ========================================================

    if st.session_state.evaluation_result:

        st.divider()

        st.markdown("## 📊 Evaluation")

        evaluation = (
            st.session_state.evaluation_result
        )

        if isinstance(evaluation, str):

            st.markdown(evaluation)

        elif isinstance(evaluation, dict):

            for key, value in evaluation.items():

                st.markdown(
                    f"### {key.replace('_', ' ').title()}"
                )

                st.write(value)

        else:

            st.write(evaluation)


    # ========================================================
    # SOLVED
    # ========================================================

    if step_session.solved:

        st.success(
            "🎉 Excellent! You solved the problem."
        )

        if st.button(
            "➡️ Next Question",
            key="next_question_button",
            type="primary",
        ):

            st.session_state.coding_question = None
            st.session_state.student_code = ""
            st.session_state.evaluation_result = None
            st.session_state.hint_result = None

            with st.spinner(
                "🌳 Generating next question..."
            ):

                try:

                    new_question = (
                        step_session
                        .new_question(
                            topic=st.session_state.coding_topic,
                            difficulty=(
                                st.session_state
                                .coding_difficulty
                            ),
                        )
                    )

                    st.session_state.coding_question = (
                        new_question
                    )

                except Exception as error:

                    st.error(
                        f"Unable to generate next question:\n\n{error}"
                    )

            st.rerun()