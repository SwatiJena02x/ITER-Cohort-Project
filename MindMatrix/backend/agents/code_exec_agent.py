# ============================================================
# FILE: backend/agents/code_exec_agent.py
#
# DSA COACH AI - CODE EXECUTION AGENT
#
# ARCHITECTURE
# ------------------------------------------------------------
#
# React Frontend
#       |
#       | problem + language + approach + code
#       v
# FastAPI
#       |
#       v
# LangGraph
#       |
#       v
# code_exec_node()
#       |
#       +----------------------+
#       |                      |
#       v                      v
# Execute Python Code      CrewAI Agent
#       |                      |
#       | execution result     | DSA analysis
#       +----------+-----------+
#                  |
#                  v
#             Final Feedback
#                  |
#                  v
#              LangGraph
#                  |
#                  v
#              FastAPI
#                  |
#                  v
#             React Result Page
#
# IMPORTANT:
# - Python code is executed locally in a subprocess.
# - CrewAI analyzes the REAL execution result.
# - code_exec_node() is exported for workflow.py.
# ============================================================


import json
import os
import subprocess
import sys
import tempfile
from typing import Any

from crewai import Agent, Task, Crew, Process, LLM

from config.settings import settings
from graph.state import DSAAgentState


# ============================================================
# SECTION 1 - EXECUTE PYTHON CODE
# ============================================================

def execute_python_code(
    code: str,
    language: str = "python"
) -> dict:
    """
    Execute the candidate's submitted code.

    Currently Python is supported.
    """

    # --------------------------------------------------------
    # Validate language
    # --------------------------------------------------------

    language = (language or "python").lower().strip()

    if language not in ["python", "py"]:
        return {
            "status": "unsupported",
            "output": "",
            "error": f"{language} execution is not supported yet.",
        }

    temp_file = None

    try:

        # ----------------------------------------------------
        # Create temporary Python file
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as file:

            file.write(code)
            temp_file = file.name

        # ----------------------------------------------------
        # Execute candidate code
        # ----------------------------------------------------

        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=5,
            encoding="utf-8",
            errors="replace",
        )

        # ----------------------------------------------------
        # Successful execution
        # ----------------------------------------------------

        if result.returncode == 0:

            return {
                "status": "passed",
                "output": result.stdout.strip(),
                "error": "",
            }

        # ----------------------------------------------------
        # Runtime / syntax error
        # ----------------------------------------------------

        return {
            "status": "failed",
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
        }

    # --------------------------------------------------------
    # Timeout
    # --------------------------------------------------------

    except subprocess.TimeoutExpired:

        return {
            "status": "timeout",
            "output": "",
            "error": "Code execution exceeded the 5 second limit.",
        }

    # --------------------------------------------------------
    # Unexpected execution error
    # --------------------------------------------------------

    except Exception as exc:

        return {
            "status": "error",
            "output": "",
            "error": str(exc),
        }

    # --------------------------------------------------------
    # Delete temporary file
    # --------------------------------------------------------

    finally:

        if temp_file and os.path.exists(temp_file):

            try:
                os.remove(temp_file)
            except OSError:
                pass


# ============================================================
# SECTION 2 - GET GROQ MODEL
# ============================================================

def create_llm():
    """
    Create the CrewAI LLM.

    Model comes from .env through settings.MODEL.
    """

    model_name = settings.MODEL

    # --------------------------------------------------------
    # Avoid double "groq/" prefix
    # --------------------------------------------------------

    if not model_name.startswith("groq/"):
        model_name = f"groq/{model_name}"

    return LLM(
        model=model_name,
        api_key=settings.GROQ_API_KEY,
        temperature=0,
    )


# ============================================================
# SECTION 3 - CREWAI AGENT
# ============================================================

llm = create_llm()


code_exec_coach = Agent(
    role="Senior DSA Interview Coach",

    goal=(
        "Analyze a candidate's DSA solution using the actual "
        "execution result and provide concise, useful interview "
        "feedback."
    ),

    backstory=(
        "You are an experienced DSA interviewer and coding coach. "
        "You carefully evaluate correctness, code quality, "
        "complexity, edge cases and interview readiness. "
        "You never claim that code passed unless the execution "
        "result confirms it."
    ),

    llm=llm,

    verbose=False,

    allow_delegation=False,
)


# ============================================================
# SECTION 4 - CREWAI TASK
# ============================================================

code_exec_task = Task(

    description="""
You are evaluating a candidate's DSA solution.

PROBLEM:
{problem}

LANGUAGE:
{language}

CANDIDATE APPROACH:
{approach}

CANDIDATE CODE:
{code}

ACTUAL EXECUTION STATUS:
{execution_status}

ACTUAL PROGRAM OUTPUT:
{execution_output}

ACTUAL ERROR:
{execution_error}


Your job is to analyze the solution using the REAL execution
information above.

Return ONLY valid JSON.

Use exactly this structure:

{
    "overall_score": 0,
    "correctness": "",
    "time_complexity": "",
    "space_complexity": "",
    "strengths": [],
    "weaknesses": [],
    "suggestions": [],
    "interview_result": "",
    "learning_plan": []
}

Rules:

1. overall_score must be between 0 and 100.

2. If execution_status is "passed":
   - Do not say the code failed.
   - Evaluate the algorithm and approach.
   - Mention correctness based on the submitted solution.

3. If execution_status is "failed":
   - Clearly mention that execution failed.
   - Use the actual error.
   - Do not pretend the solution passed.

4. If execution_status is "timeout":
   - Explain that execution exceeded the time limit.

5. Analyze time complexity.

6. Analyze space complexity.

7. Give 2-4 strengths.

8. Give 2-4 weaknesses.

9. Give 2-4 concrete suggestions.

10. Give 2-5 learning-plan items.

11. Keep all feedback concise and useful for a DSA learner.

12. Return JSON only. No markdown. No ```json.
""",

    expected_output=(
        "A valid JSON object containing overall_score, correctness, "
        "time_complexity, space_complexity, strengths, weaknesses, "
        "suggestions, interview_result and learning_plan."
    ),

    agent=code_exec_coach,
)


# ============================================================
# SECTION 5 - CREW
# ============================================================

code_exec_crew = Crew(

    agents=[
        code_exec_coach
    ],

    tasks=[
        code_exec_task
    ],

    process=Process.sequential,

    verbose=False,
)


# ============================================================
# SECTION 6 - SAFE JSON PARSER
# ============================================================

def parse_ai_feedback(raw_output: Any) -> dict:
    """
    Convert CrewAI output into a Python dictionary.

    Handles:
    - normal JSON
    - JSON surrounded by text
    - markdown JSON blocks
    """

    if raw_output is None:
        return {}

    text = str(raw_output).strip()

    # --------------------------------------------------------
    # Remove markdown fences
    # --------------------------------------------------------

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    # --------------------------------------------------------
    # Try direct JSON
    # --------------------------------------------------------

    try:

        parsed = json.loads(text)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Try extracting JSON object
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_text = text[start:end + 1]

        try:

            parsed = json.loads(json_text)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

    return {}


# ============================================================
# SECTION 7 - FALLBACK FEEDBACK
# ============================================================

def fallback_feedback(
    execution_result: dict,
    problem: str,
    approach: str,
    code: str,
) -> dict:
    """
    Fallback response if the AI cannot produce valid JSON.
    """

    status = execution_result.get("status", "error")
    output = execution_result.get("output", "")
    error = execution_result.get("error", "")

    if status == "passed":

        return {
            "overall_score": 75,
            "correctness": (
                "The submitted code executed successfully. "
                "Review the algorithm against all possible edge cases."
            ),
            "time_complexity": "Analyze based on the submitted loops and data structures.",
            "space_complexity": "Analyze based on the additional data structures used.",
            "strengths": [
                "Code executed successfully.",
                "The solution has a working implementation.",
            ],
            "weaknesses": [
                "More edge-case validation may be needed.",
            ],
            "suggestions": [
                "Test the solution with boundary cases.",
                "Explain the time and space complexity clearly.",
            ],
            "interview_result": (
                "The solution runs successfully but needs further "
                "algorithmic validation."
            ),
            "learning_plan": [
                "Practice edge-case analysis.",
                "Practice explaining complexity.",
                "Solve more problems using the same pattern.",
            ],
        }

    if status == "timeout":

        return {
            "overall_score": 30,
            "correctness": "The program did not finish within the execution limit.",
            "time_complexity": "Likely inefficient or contains a non-terminating operation.",
            "space_complexity": "Could not be fully evaluated because execution timed out.",
            "strengths": [],
            "weaknesses": [
                "Execution exceeded the time limit.",
            ],
            "suggestions": [
                "Check for infinite loops.",
                "Improve the algorithmic complexity.",
            ],
            "interview_result": "Needs optimization before being interview-ready.",
            "learning_plan": [
                "Practice Big-O analysis.",
                "Practice optimizing nested loops.",
            ],
        }

    return {
        "overall_score": 0,
        "correctness": "The submitted code failed during execution.",
        "time_complexity": "Not determined because execution failed.",
        "space_complexity": "Not determined because execution failed.",
        "strengths": [],
        "weaknesses": [
            "The submitted code did not execute successfully.",
            error[:500] if error else "Unknown execution error.",
        ],
        "suggestions": [
            "Fix the execution error first.",
            "Run the solution again after correcting the code.",
        ],
        "interview_result": "Not interview-ready until the execution error is fixed.",
        "learning_plan": [
            "Practice debugging Python errors.",
            "Test solutions with small examples.",
        ],
    }


# ============================================================
# SECTION 8 - LANGGRAPH NODE
#
# IMPORTANT:
# This function MUST exist because workflow.py imports:
#
# from agents.code_exec_agent import code_exec_node
# ============================================================

def code_exec_node(state: DSAAgentState) -> DSAAgentState:

    """
    LangGraph node.

    Flow:

        LangGraph
             |
             v
        code_exec_node
             |
             +----> Execute Python
             |
             +----> CrewAI DSA Coach
             |
             v
        execution_result
    """

    # --------------------------------------------------------
    # Get data from LangGraph state
    # --------------------------------------------------------

    problem = state.get("problem", "")
    language = state.get("language", "python")
    code = state.get("code", "")
    approach = state.get("approach", "")

    # --------------------------------------------------------
    # STEP 1 - Actually execute candidate code
    # --------------------------------------------------------

    execution = execute_python_code(
        code=code,
        language=language,
    )

    # --------------------------------------------------------
    # STEP 2 - Run CrewAI analysis
    #
    # CrewAI receives the REAL execution result.
    # --------------------------------------------------------

    try:

        crew_result = code_exec_crew.kickoff(

            inputs={
                "problem": problem,
                "language": language,
                "code": code,
                "approach": approach,

                "execution_status": execution.get(
                    "status",
                    "error"
                ),

                "execution_output": execution.get(
                    "output",
                    ""
                ),

                "execution_error": execution.get(
                    "error",
                    ""
                ),
            }
        )

        # ----------------------------------------------------
        # Get raw CrewAI output
        # ----------------------------------------------------

        raw_output = getattr(
            crew_result,
            "raw",
            str(crew_result)
        )

        # ----------------------------------------------------
        # Parse AI JSON
        # ----------------------------------------------------

        feedback = parse_ai_feedback(raw_output)

        # ----------------------------------------------------
        # If AI JSON is invalid, use fallback
        # ----------------------------------------------------

        if not feedback:

            feedback = fallback_feedback(
                execution_result=execution,
                problem=problem,
                approach=approach,
                code=code,
            )

    except Exception as exc:

        # ----------------------------------------------------
        # If CrewAI fails, DO NOT crash the API.
        # Return useful fallback feedback.
        # ----------------------------------------------------

        feedback = fallback_feedback(
            execution_result=execution,
            problem=problem,
            approach=approach,
            code=code,
        )

        feedback["weaknesses"].append(
            f"AI analysis error: {str(exc)[:300]}"
        )

    # --------------------------------------------------------
    # STEP 3 - Add actual execution information
    # --------------------------------------------------------

    feedback["execution_status"] = execution.get(
        "status",
        "error"
    )

    feedback["execution_output"] = execution.get(
        "output",
        ""
    )

    feedback["execution_error"] = execution.get(
        "error",
        ""
    )

    # --------------------------------------------------------
    # STEP 4 - Store result in LangGraph state
    # --------------------------------------------------------

    state["execution_result"] = feedback

    # --------------------------------------------------------
    # STEP 5 - Return state to LangGraph
    # --------------------------------------------------------

    return state


# ============================================================
# END OF code_exec_agent.py
# ============================================================