from llm import OllamaClient


class AgentReasoner:
    """
    Determines what the agent should do next
    after observing a tool result.
    """

    def __init__(self):

        self.llm = OllamaClient(
            model="qwen2.5-coder:7b"
        )

    def decide_next_action(
        self,
        question: str,
        observation: str
    ) -> str:

        prompt = f"""
You are the reasoning component of a DSA AI Coach.

The student asked:

{question}

The agent has already used a tool and received:

{observation}

Decide whether the agent has enough information
to answer the student.

Return ONLY one of:

ANSWER
RETRIEVE

Use ANSWER if the information is sufficient.

Use RETRIEVE if more knowledge retrieval is required.
"""

        response = self.llm.generate(
            prompt
        )

        decision = (
            response
            .strip()
            .upper()
        )

        if "RETRIEVE" in decision:
            return "RETRIEVE"

        return "ANSWER"