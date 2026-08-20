from typing import TypedDict


class AgentState(TypedDict):

    question: str

    session_id: str

    conversation_history: list[dict]

    problem_id: str

    problem: str

    code: str

    language: str

    context: str

    answer: str

    route: str

    next_action: str

    tool_result: str

    observation: str

    iteration: int

    max_iterations: int

    final: bool