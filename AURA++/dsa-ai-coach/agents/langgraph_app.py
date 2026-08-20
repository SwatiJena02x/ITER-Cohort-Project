"""
LangGraph entry point for LangSmith deployment.

This file exposes the compiled DSA Coach graph
as a module-level variable named `graph`.
"""

from agents.dsa_agent import DSACoachAgent


# Create the DSA Coach
coach = DSACoachAgent(
    planner_model="qwen2.5-coder:1.5b"
)


# Expose the compiled LangGraph
graph = coach.graph