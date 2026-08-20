from llm import OllamaClient


class AgentRouter:
    """
    LLM-based router for the DSA Coach Agent.

    Available routes:

        RAG
        PROBLEM
        HINT
        CODE
        DIRECT
    """

    def __init__(self):

        self.llm = OllamaClient(
            model="qwen2.5-coder:7b"
        )

    def classify(
        self,
        question: str
    ) -> str:

        prompt = f"""
You are the routing system for a DSA AI Coach.

Determine what the student wants.

Available routes:

RAG

Use RAG when the student wants:
- Explanation of a DSA concept
- Algorithm explanation
- Solution explanation
- Complexity explanation
- Conceptual DSA knowledge

Examples:

"What is dynamic programming?"
RAG

"Explain House Robber."
RAG


PROBLEM

Use PROBLEM when the student wants:
- A DSA problem
- A coding problem
- A practice question
- A problem with a specific difficulty
- A problem from a specific topic

Examples:

"Give me a DP problem."
PROBLEM

"Give me a medium array problem."
PROBLEM


HINT

Use HINT when the student wants:
- A hint
- A clue
- Help without the complete solution
- Help because they are stuck

Examples:

"Give me a hint."
HINT

"I'm stuck on House Robber."
HINT


CODE

Use CODE when the student:
- Submits code for review
- Asks why their code is wrong
- Asks why their code gives TLE
- Asks about bugs in their code
- Asks for time complexity of their code
- Asks for space complexity of their code
- Wants their solution analyzed

Examples:

"Why is my code giving TLE?"
CODE

"Analyze this solution."
CODE

"What's wrong with my code?"
CODE

"What is the time complexity of my code?"
CODE


DIRECT

Use DIRECT when:
- Greeting
- Casual conversation
- Unrelated question

Examples:

"Hello"
DIRECT


IMPORTANT:

Return ONLY one of:

RAG
PROBLEM
HINT
CODE
DIRECT


Student question:

{question}
"""

        response = self.llm.generate(
            prompt
        )

        decision = (
            response
            .strip()
            .upper()
        )

        if "CODE" in decision:
            return "CODE"

        if "HINT" in decision:
            return "HINT"

        if "PROBLEM" in decision:
            return "PROBLEM"

        if "RAG" in decision:
            return "RAG"

        return "DIRECT"