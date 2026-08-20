"""
DSA Coach Tree - Orchestrator
==============================
This is the top-level Supervisor that ties rag_agent.py and
step_evaluator_agent.py together into one system, matching the
Supervisor-routed pattern from your architecture reference diagram.

    Learner message
          |
          v
      Supervisor (rule-based, no LLM - decides intent)
          |
          +---- new_question / submit_code / hint --> Step Evaluator Agent
          |
          +---- everything else (general chat) -------> RAG Agent
          |
          v
      Reply to learner

Two ways to drive this, both provided below - use whichever fits your UI:

  1. TEXT ROUTING (send_message)
     For a single chat box where the student just types. The Supervisor
     reads the text and decides which specialist agent should handle it.

  2. DIRECT ACTIONS (click_new_question / submit_code / click_hint)
     For a real UI with separate buttons/inputs (a "New Question" button,
     a code editor with a "Submit" button, a "Hint" button). These BYPASS
     the Supervisor entirely and call the right specialist directly -
     which is more correct anyway, since a button click is already an
     unambiguous signal and doesn't need text-based intent guessing.

Both paths ultimately go through the SAME underlying rag_agent graph and
the SAME StepEvaluatorSession, so memory/context stays consistent no
matter which one you use.
"""

import uuid

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState, StateGraph, END

# Adjust these two import paths to match your real folder structure.
from agent.tree_agent import graph as rag_graph
from agent.step_evaluator_agent import StepEvaluatorSession


# ============================================================
# 1. KEYWORDS THE SUPERVISOR USES FOR TEXT-BASED ROUTING
# (only used by send_message() - the direct action methods below don't
# need any of this, since a button click is already unambiguous)
# ============================================================
NEW_QUESTION_KEYWORDS = [
    "give me a question", "new question", "next question",
    "quiz me", "practice question", "another question",
]
HINT_KEYWORDS = [
    "hint", "i'm stuck", "im stuck", "stuck", "help me with this",
]


# ============================================================
# 2. ORCHESTRATOR STATE
# ============================================================
class OrchestratorState(MessagesState):
    mode: str   # "new_question" | "submit_code" | "hint" | "chat"


# ============================================================
# 3. THE ORCHESTRATOR
# ============================================================
class DSATreeOrchestrator:
    """
    One instance of this = one learner's session. It owns:
      - a StepEvaluatorSession (its own memory/thread for the practice flow)
      - a thread_id for the RAG agent's own conversational memory
      - the compiled Supervisor graph that routes between the two
    """

    def __init__(self):
        self.step_session = StepEvaluatorSession()

        self.rag_thread_id = str(uuid.uuid4())
        self.rag_config = {"configurable": {"thread_id": self.rag_thread_id}}

        self.graph = self._build_graph()

    # --------------------------------------------------------
    # Graph construction
    # --------------------------------------------------------
    def _build_graph(self):
        builder = StateGraph(OrchestratorState)

        builder.add_node("supervisor", self.supervisor_node)
        builder.add_node("rag_agent", self.call_rag_agent_node)
        builder.add_node("step_evaluator", self.call_step_evaluator_node)

        builder.set_entry_point("supervisor")
        builder.add_conditional_edges("supervisor", self.route_from_supervisor, {
            "rag_agent": "rag_agent",
            "step_evaluator": "step_evaluator",
        })
        builder.add_edge("rag_agent", END)
        builder.add_edge("step_evaluator", END)

        # No checkpointer needed at THIS level - each specialist already
        # keeps its own memory internally (rag_thread_id / step_session).
        # The orchestrator itself is stateless per call.
        return builder.compile()

    def show_graph(self):
        """Print a Mermaid representation of the orchestrator graph."""
        print(self.graph.get_graph().draw_mermaid())

    # --------------------------------------------------------
    # Supervisor node - rule-based, no LLM call, decides intent
    # --------------------------------------------------------
    def supervisor_node(self, state: OrchestratorState) -> dict:
        text = state["messages"][-1].content.lower().strip()

        if any(kw in text for kw in NEW_QUESTION_KEYWORDS):
            intent = "new_question"
        elif any(kw in text for kw in HINT_KEYWORDS):
            intent = "hint"
        elif self.step_session.current_question is not None:
            # a question is already active and this doesn't look like a
            # new-question or hint request -> treat it as an answer
            intent = "submit_code"
        else:
            intent = "chat"

        print(f"[Supervisor] routing intent -> {intent}")
        return {"mode": intent}

    def route_from_supervisor(self, state: OrchestratorState) -> str:
        return "step_evaluator" if state["mode"] in ("new_question", "submit_code", "hint") else "rag_agent"

    # --------------------------------------------------------
    # Specialist call nodes
    # --------------------------------------------------------
    def call_rag_agent_node(self, state: OrchestratorState) -> dict:
        user_text = state["messages"][-1].content
        result = rag_graph.invoke(
            {"messages": [HumanMessage(content=user_text)]},
            config=self.rag_config,
        )
        answer = result["messages"][-1].content
        return {"messages": [AIMessage(content=answer)]}

    def call_step_evaluator_node(self, state: OrchestratorState) -> dict:
        mode = state["mode"]
        user_text = state["messages"][-1].content

        if mode == "new_question":
            answer = self.step_session.new_question()
        elif mode == "hint":
            answer = self.step_session.request_hint()
        else:  # submit_code
            answer = self.step_session.submit_code(user_text)

        return {"messages": [AIMessage(content=answer)]}

    # --------------------------------------------------------
    # PUBLIC API #1 - text routing, for a single chat box
    # --------------------------------------------------------
    def send_message(self, user_text: str) -> str:
        """
        Send free-text input and let the Supervisor decide what to do
        with it. Use this when your UI is just one chat box.
        """
        result = self.graph.invoke({"messages": [HumanMessage(content=user_text)]})
        return result["messages"][-1].content

    # --------------------------------------------------------
    # PUBLIC API #2 - direct actions, for a real UI with buttons
    # --------------------------------------------------------
    def click_new_question(self, topic: str = "any tree topic", difficulty: str = "easy") -> str:
        """Wire this to your 'New Question' button."""
        return self.step_session.new_question(topic=topic, difficulty=difficulty)

    def submit_code(self, code: str) -> str:
        """Wire this to your code editor's 'Submit' button."""
        return self.step_session.submit_code(code)

    def click_hint(self) -> str:
        """Wire this to your 'Hint' button."""
        return self.step_session.request_hint()

    def ask_general_question(self, question_text: str) -> str:
        """Wire this to a separate 'Ask a concept question' input, if you have one."""
        result = rag_graph.invoke(
            {"messages": [HumanMessage(content=question_text)]},
            config=self.rag_config,
        )
        return result["messages"][-1].content


# ============================================================
# 4. QUICK MANUAL TEST
# Run with: python -m agent.orchestrator
# (requires Ollama running locally + your pgvector RAG DB populated)
# ============================================================
if __name__ == "__main__":
    orchestrator = DSATreeOrchestrator()

    print("=" * 70)
    print("1) General concept question (should route to rag_agent)")
    print("=" * 70)
    print(orchestrator.send_message("What is a self-balancing binary tree?"))

    print("\n" + "=" * 70)
    print("2) 'New Question' button click (direct action, bypasses Supervisor)")
    print("=" * 70)
    print(orchestrator.click_new_question(topic="binary tree traversal", difficulty="easy"))

    print("\n" + "=" * 70)
    print("3) Student pastes code into the chat box (text routing via Supervisor)")
    print("=" * 70)
    print(orchestrator.send_message("def solution(root):\n    pass\n"))

    print("\n" + "=" * 70)
    print("4) 'Hint' button click (direct action, bypasses Supervisor)")
    print("=" * 70)
    print(orchestrator.click_hint())

