# ============================================================
# DSA COACH AI - DSA FEEDBACK AGENT
# ============================================================
#
# File:
#     dsa_agent.py
#
# Purpose:
#     Orchestrates the complete DSA feedback workflow.
#
# Agent:
#     LangGraph
#
# LLM:
#     Groq
#
# RAG:
#     FAISS + PostgreSQL
#
# ============================================================


# ============================================================
# STANDARD LIBRARY
# ============================================================

from typing import TypedDict


# ============================================================
# LANGGRAPH
# ============================================================

from langgraph.graph import (
    StateGraph,
    START,
    END,
)


# ============================================================
# RAG RETRIEVER
# ============================================================

from rag.retriever import retrieve_context


# ============================================================
# GROQ AI SERVICE
# ============================================================

from services.ai_service import get_ai_feedback


# ============================================================
# AGENT STATE
# ============================================================

class DSAAgentState(TypedDict, total=False):
    """
    State shared between all nodes of the DSA agent.
    """

    # DSA problem statement
    problem: str

    # Programming language
    language: str

    # Student's code
    code: str

    # Student's explanation
    approach: str

    # Retrieved RAG context
    rag_context: str

    # Prompt sent to Groq
    prompt: str

    # Final AI feedback
    feedback: str


# ============================================================
# NODE 1 - RETRIEVE DSA KNOWLEDGE
# ============================================================

def retrieve_knowledge(
    state: DSAAgentState,
) -> DSAAgentState:
    """
    Retrieve relevant DSA knowledge from FAISS.

    The retrieved chunks provide context to the LLM.
    """

    # --------------------------------------------------------
    # Build the retrieval query
    # --------------------------------------------------------

    query = f"""
Problem:
{state["problem"]}

Student Approach:
{state.get("approach", "")}

Student Code:
{state["code"]}
"""

    # --------------------------------------------------------
    # Search the RAG knowledge base
    # --------------------------------------------------------

    context = retrieve_context(
        query
    )

    # --------------------------------------------------------
    # Store retrieved context
    # --------------------------------------------------------

    return {
        **state,
        "rag_context": context,
    }


# ============================================================
# NODE 2 - BUILD LLM PROMPT
# ============================================================

def build_prompt(
    state: DSAAgentState,
) -> DSAAgentState:
    """
    Build the prompt that will be sent to Groq.
    """

    prompt = f"""
You are an expert DSA Coach AI.

Your task is to evaluate a student's DSA solution
and provide useful, educational feedback.

============================================================
DSA PROBLEM
============================================================

{state["problem"]}


============================================================
PROGRAMMING LANGUAGE
============================================================

{state["language"]}


============================================================
STUDENT APPROACH
============================================================

{state.get("approach", "Not provided")}


============================================================
STUDENT CODE
============================================================

{state["code"]}


============================================================
RELEVANT KNOWLEDGE FROM RAG
============================================================

{state.get("rag_context", "No relevant knowledge found.")}


============================================================
YOUR TASK
============================================================

Analyze the student's solution and provide feedback.

Your response MUST include:

1. Correctness
   - Is the solution logically correct?
   - Identify any bugs or edge cases.

2. Approach
   - Explain the algorithm used by the student.

3. Time Complexity
   - Give Big-O time complexity.
   - Explain why.

4. Space Complexity
   - Give Big-O space complexity.
   - Explain why.

5. Optimization
   - Explain whether a better approach exists.
   - If yes, explain it clearly.

6. Code Quality
   - Comment on readability and maintainability.

7. DSA Concepts
   - Identify the important DSA concepts involved.

8. Improvement Suggestions
   - Give specific suggestions the student can apply.

9. Final Verdict
   - Give a short overall assessment.

IMPORTANT RULES:

- Do not blindly assume the student's code is correct.
- Do not invent information that is not supported by the code
  or retrieved knowledge.
- Explain technical concepts clearly.
- Prefer practical feedback suitable for a student preparing
  for coding interviews.
- Use the retrieved RAG knowledge as supporting context.
"""

    # --------------------------------------------------------
    # Store prompt in agent state
    # --------------------------------------------------------

    return {
        **state,
        "prompt": prompt,
    }


# ============================================================
# NODE 3 - CALL GROQ LLM
# ============================================================

def generate_feedback(
    state: DSAAgentState,
) -> DSAAgentState:
    """
    Send the generated prompt to Groq and obtain
    the final DSA feedback.
    """

    # --------------------------------------------------------
    # Get prompt
    # --------------------------------------------------------

    prompt = state["prompt"]

    # --------------------------------------------------------
    # Call Groq through ai_service.py
    # --------------------------------------------------------

    feedback = get_ai_feedback(
        prompt
    )

    # --------------------------------------------------------
    # Store final response
    # --------------------------------------------------------

    return {
        **state,
        "feedback": feedback,
    }


# ============================================================
# BUILD LANGGRAPH AGENT
# ============================================================

def build_dsa_agent():
    """
    Build and compile the DSA Feedback Agent.
    """

    # --------------------------------------------------------
    # Create state graph
    # --------------------------------------------------------

    graph = StateGraph(
        DSAAgentState
    )


    # --------------------------------------------------------
    # Add nodes
    # --------------------------------------------------------

    graph.add_node(
        "retrieve",
        retrieve_knowledge,
    )

    graph.add_node(
        "prompt",
        build_prompt,
    )

    graph.add_node(
        "generate",
        generate_feedback,
    )


    # --------------------------------------------------------
    # Define agent workflow
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "retrieve",
    )

    graph.add_edge(
        "retrieve",
        "prompt",
    )

    graph.add_edge(
        "prompt",
        "generate",
    )

    graph.add_edge(
        "generate",
        END,
    )


    # --------------------------------------------------------
    # Compile graph
    # --------------------------------------------------------

    return graph.compile()


# ============================================================
# CREATE AGENT
# ============================================================

dsa_agent = build_dsa_agent()


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def run_dsa_agent(
    problem: str,
    language: str,
    code: str,
    approach: str = "",
) -> str:
    """
    Run the complete DSA Feedback Agent.

    Flow:

        Problem
            ↓
        RAG Retrieval
            ↓
        Prompt
            ↓
        Groq
            ↓
        Feedback
    """

    # --------------------------------------------------------
    # Create initial state
    # --------------------------------------------------------

    initial_state: DSAAgentState = {

        "problem": problem,

        "language": language,

        "code": code,

        "approach": approach,

    }


    # --------------------------------------------------------
    # Execute LangGraph
    # --------------------------------------------------------

    result = dsa_agent.invoke(
        initial_state
    )


    # --------------------------------------------------------
    # Return final feedback
    # --------------------------------------------------------

    return result["feedback"]


# ============================================================
# TEST THE AGENT
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("DSA COACH AI - GROQ AGENT TEST")
    print("=" * 60)


    # --------------------------------------------------------
    # Test DSA problem
    # --------------------------------------------------------

    test_problem = """
Given an array of integers and a target,
return indices of two numbers that add up to the target.
"""


    # --------------------------------------------------------
    # Test code
    # --------------------------------------------------------

    test_code = """
def twoSum(nums, target):

    seen = {}

    for i, num in enumerate(nums):

        complement = target - num

        if complement in seen:

            return [
                seen[complement],
                i
            ]

        seen[num] = i
"""


    # --------------------------------------------------------
    # Test approach
    # --------------------------------------------------------

    test_approach = """
I use a HashMap to store previously visited numbers.
This allows complement lookup in O(1) average time.
"""


    try:

        # ----------------------------------------------------
        # Run DSA Agent
        # ----------------------------------------------------

        result = run_dsa_agent(

            problem=test_problem,

            language="Python",

            code=test_code,

            approach=test_approach,

        )


        # ----------------------------------------------------
        # Display final feedback
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("FINAL AI FEEDBACK")
        print("=" * 60)

        print(result)


        # ----------------------------------------------------
        # Success message
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("DSA GROQ AGENT TEST COMPLETED")
        print("=" * 60)


    except Exception as error:

        print()
        print("Agent execution failed.")

        print()
        print("Error:")

        print(error)