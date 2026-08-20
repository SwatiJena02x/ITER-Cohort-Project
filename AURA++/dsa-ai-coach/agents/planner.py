import json
import ollama


class ReActPlanner:
    """
    ReAct planner for the DSA Coach.

    The planner decides whether another tool is required.

    Important:
    Simple tool requests should normally finish immediately.

    Supported actions:

        PROBLEM
        HINT
        CODE
        RAG
        FINAL
    """

    def __init__(
        self,
        model: str = "qwen2.5-coder:1.5b"
    ):
        self.model = model

    # ==================================================
    # PLAN
    # ==================================================

    def plan(
        self,
        question: str,
        problem: str,
        observation: str,
        route: str,
        iteration: int,
        max_iterations: int,
        memory: dict | None = None,
        conversation_history: list[dict] | None = None
    ) -> dict:

        question_lower = question.lower().strip()

        route = (route or "").upper()

        # ==================================================
        # IMPORTANT DETERMINISTIC RULES
        # ==================================================
        #
        # If a tool has already answered a simple request,
        # do NOT waste another LLM call.
        #
        # ==================================================

        if route == "PROBLEM":

            return {
                "action": "FINAL",
                "reason": "Problem has already been provided."
            }

        if route == "HINT":

            return {
                "action": "FINAL",
                "reason": "Hint has already been provided."
            }

        if route == "RAG":

            return {
                "action": "FINAL",
                "reason": "RAG has already retrieved and generated the answer."
            }

        # ==================================================
        # CODE ANALYSIS
        # ==================================================

        if route == "CODE":

            # If the user clearly asks for explanation
            # after code analysis, RAG may be useful.

            explanation_words = [
                "explain",
                "why",
                "concept",
                "theory"
            ]

            if any(
                word in question_lower
                for word in explanation_words
            ):

                return {
                    "action": "RAG",
                    "reason": (
                        "The student may need conceptual "
                        "information after code analysis."
                    )
                }

            return {
                "action": "FINAL",
                "reason": (
                    "Code analysis has already produced "
                    "the required feedback."
                )
            }

        # ==================================================
        # SAFETY
        # ==================================================

        if iteration >= max_iterations:

            return {
                "action": "FINAL",
                "reason": "Maximum iterations reached."
            }

        # ==================================================
        # MEMORY DEFAULTS
        # ==================================================

        if memory is None:
            memory = {}

        if conversation_history is None:
            conversation_history = []

        # ==================================================
        # RECENT CONVERSATION
        # ==================================================

        recent_history = conversation_history[-6:]

        conversation_text = "\n".join(
            [
                f"{message['role']}: "
                f"{message['content']}"
                for message in recent_history
            ]
        )

        if not conversation_text:
            conversation_text = "No previous conversation."

        # ==================================================
        # MEMORY
        # ==================================================

        memory_text = f"""
Problem: {memory.get("problem_title", "")}
Problem ID: {memory.get("problem_id", "")}
Topic: {memory.get("topic", "")}
Difficulty: {memory.get("difficulty", "")}
Hints Used: {memory.get("hints_used", 0)}
Attempts: {memory.get("attempts", 0)}
Status: {memory.get("status", "")}
Last Action: {memory.get("last_action", "")}
"""

        # ==================================================
        # LIMIT OBSERVATION
        # ==================================================

        observation = observation or ""

        if len(observation) > 2000:
            observation = observation[:2000]

        # ==================================================
        # QWEN PLANNER PROMPT
        # ==================================================

        prompt = f"""
You are the ReAct planner of a DSA Coach.

Choose exactly ONE action.

Allowed actions:

PROBLEM
HINT
CODE
RAG
FINAL

Rules:

1. Never choose CODE unless the student has actually
   submitted code or explicitly asks for code analysis.

2. Never choose PROBLEM if a problem was already provided.

3. Never choose HINT unless the student is asking for
   a hint.

4. Never choose RAG simply because a problem exists.

5. If the latest observation already answers the request,
   choose FINAL.

6. Use conversation history for follow-up questions.

7. Return ONLY valid JSON.

Student question:
{question}

Initial route:
{route}

Current problem:
{problem}

Latest observation:
{observation}

Student memory:
{memory_text}

Conversation:
{conversation_text}

Return:

{{
    "action": "FINAL",
    "reason": "short reason"
}}
"""

        # ==================================================
        # CALL QWEN
        # ==================================================

        try:

            response = ollama.chat(

                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict JSON planner. "
                            "Return only JSON."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                format="json",

                options={
                    "temperature": 0,
                    "num_predict": 60
                }
            )

            content = (
                response["message"]["content"]
                .strip()
            )

        except Exception as e:

            print(
                f"[PLANNER] Ollama error: {e}"
            )

            return {
                "action": "FINAL",
                "reason": "Planner error; safely finishing."
            }

        # ==================================================
        # PARSE
        # ==================================================

        try:

            decision = json.loads(
                content
            )

        except json.JSONDecodeError:

            print(
                "[PLANNER] Invalid JSON:"
            )

            print(content)

            return {
                "action": "FINAL",
                "reason": "Invalid planner response."
            }

        # ==================================================
        # VALIDATE ACTION
        # ==================================================

        allowed_actions = {
            "PROBLEM",
            "HINT",
            "CODE",
            "RAG",
            "FINAL"
        }

        action = str(
            decision.get(
                "action",
                "FINAL"
            )
        ).upper()

        if action not in allowed_actions:

            action = "FINAL"

        return {
            "action": action,
            "reason": str(
                decision.get(
                    "reason",
                    ""
                )
            )
        }