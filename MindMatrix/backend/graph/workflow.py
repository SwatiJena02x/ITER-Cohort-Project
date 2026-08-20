# ============================================================
# FILE: backend/graph/workflow.py
#
# LANGGRAPH ARCHITECTURE
#
# START
#   |
#   v
# code_exec
#   |
#   v
# code_exec_node()
#   |
#   +--> Execute Python
#   |
#   +--> CrewAI DSA Coach
#   |
#   v
# execution_result
#   |
#   v
# END
# ============================================================

from langgraph.graph import StateGraph, END

from graph.state import DSAAgentState
from agents.code_exec_agent import code_exec_node


# ============================================================
# Create LangGraph
# ============================================================

workflow = StateGraph(DSAAgentState)


# ============================================================
# Add Code Execution + AI Feedback Node
# ============================================================

workflow.add_node(
    "code_exec",
    code_exec_node
)


# ============================================================
# START -> code_exec
# ============================================================

workflow.set_entry_point("code_exec")


# ============================================================
# code_exec -> END
# ============================================================

workflow.add_edge(
    "code_exec",
    END
)


# ============================================================
# Compile
# ============================================================

agent_graph = workflow.compile()