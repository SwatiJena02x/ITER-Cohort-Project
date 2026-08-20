from typing import TypedDict, NotRequired

from langgraph.graph import StateGraph, START, END

from agents.state import AgentState
from agents.router import AgentRouter
from agents.planner import ReActPlanner

from tools.rag_tool import RAGTool
from tools.problem_tool import ProblemTool
from tools.hint_tool import HintTool
from tools.code_analysis_tool import CodeAnalysisTool
from tools.memory_tool import MemoryTool


# ============================================================
# PUBLIC INPUT SCHEMA
# ============================================================

class DSAInput(TypedDict):
    """
    Public input schema exposed to LangGraph Studio.

    Only question is required.
    Session ID is optional.
    """

    question: str
    session_id: NotRequired[str]


# ============================================================
# DSA COACH AGENT
# ============================================================

class DSACoachAgent:

    def __init__(
        self,
        planner_model="qwen2.5-coder:7b"
    ):

        # ==================================================
        # COMPONENTS
        # ==================================================

        self.router = AgentRouter()

        self.planner = ReActPlanner(
            model=planner_model
        )

        # ==================================================
        # TOOLS
        # ==================================================

        self.rag_tool = RAGTool()

        self.problem_tool = ProblemTool()

        self.hint_tool = HintTool()

        self.code_tool = CodeAnalysisTool()

        self.memory_tool = MemoryTool()

        # ==================================================
        # LANGGRAPH
        # ==================================================

        graph = StateGraph(
            AgentState,
            input_schema=DSAInput
        )

        # ==================================================
        # NODES
        # ==================================================

        graph.add_node(
            "initialize",
            self.initialize_state
        )

        graph.add_node(
            "router",
            self.route
        )

        graph.add_node(
            "problem",
            self.call_problem
        )

        graph.add_node(
            "hint",
            self.call_hint
        )

        graph.add_node(
            "code",
            self.call_code_analysis
        )

        graph.add_node(
            "rag",
            self.call_rag
        )

        graph.add_node(
            "memory",
            self.update_memory
        )

        graph.add_node(
            "planner",
            self.call_planner
        )

        graph.add_node(
            "answer",
            self.generate_final_answer
        )

        graph.add_node(
            "direct",
            self.direct_answer
        )

        # ==================================================
        # START
        # ==================================================

        graph.add_edge(
            START,
            "initialize"
        )

        graph.add_edge(
            "initialize",
            "router"
        )

        # ==================================================
        # ROUTER
        # ==================================================

        graph.add_conditional_edges(
            "router",
            self.route_decision,
            {
                "PROBLEM": "problem",
                "HINT": "hint",
                "CODE": "code",
                "RAG": "rag",
                "DIRECT": "direct"
            }
        )

        # ==================================================
        # TOOLS → MEMORY
        # ==================================================

        graph.add_edge(
            "problem",
            "memory"
        )

        graph.add_edge(
            "hint",
            "memory"
        )

        graph.add_edge(
            "code",
            "memory"
        )

        graph.add_edge(
            "rag",
            "memory"
        )

        # ==================================================
        # MEMORY → FINAL / PLANNER
        # ==================================================

        graph.add_conditional_edges(
            "memory",
            self.after_memory_decision,
            {
                "PLANNER": "planner",
                "FINAL": "answer"
            }
        )

        # ==================================================
        # PLANNER → NEXT ACTION
        # ==================================================

        graph.add_conditional_edges(
            "planner",
            self.planner_decision,
            {
                "PROBLEM": "problem",
                "HINT": "hint",
                "CODE": "code",
                "RAG": "rag",
                "FINAL": "answer"
            }
        )

        # ==================================================
        # FINAL
        # ==================================================

        graph.add_edge(
            "answer",
            END
        )

        graph.add_edge(
            "direct",
            END
        )

        # ==================================================
        # COMPILE
        # ==================================================

        self.graph = graph.compile()


    # ======================================================
    # INITIALIZE STATE
    # ======================================================

    def initialize_state(
        self,
        state: AgentState
    ) -> AgentState:

        question = state["question"]

        session_id = state.get(
            "session_id",
            "default_session"
        )

        # --------------------------------------------------
        # GET PREVIOUS CONVERSATION
        # --------------------------------------------------

        conversation_history = (
            self.memory_tool.get_conversation(
                session_id=session_id,
                limit=10
            )
        )

        # --------------------------------------------------
        # SAVE USER MESSAGE
        # --------------------------------------------------

        self.memory_tool.save_message(
            session_id=session_id,
            role="user",
            content=question
        )

        # --------------------------------------------------
        # COMPLETE INTERNAL STATE
        # --------------------------------------------------

        return {

            "question":
                question,

            "session_id":
                session_id,

            "conversation_history":
                conversation_history,

            "problem_id":
                "",

            "problem":
                "",

            "code":
                "",

            "language":
                "python",

            "context":
                "",

            "answer":
                "",

            "route":
                "",

            "next_action":
                "",

            "tool_result":
                "",

            "observation":
                "",

            "iteration":
                0,

            "max_iterations":
                5,

            "final":
                False
        }


    # ======================================================
    # ROUTER
    # ======================================================

    def route(
        self,
        state: AgentState
    ) -> AgentState:

        print(
            "\n[AGENT] Understanding intent..."
        )

        decision = self.router.classify(
            state["question"]
        )

        print(
            f"[AGENT] Initial route: {decision}"
        )

        return {
            **state,
            "route": decision
        }


    # ======================================================
    # ROUTER DECISION
    # ======================================================

    def route_decision(
        self,
        state: AgentState
    ) -> str:

        return state["route"]


    # ======================================================
    # PROBLEM TOOL
    # ======================================================

    def call_problem(
        self,
        state: AgentState
    ) -> AgentState:

        print(
            "\n[TOOL] PROBLEM"
        )

        question = (
            state["question"]
            .lower()
            .strip()
        )

        # ==================================================
        # DIFFICULTY
        # ==================================================

        difficulty = None

        if "easy" in question:

            difficulty = "easy"

        elif "medium" in question:

            difficulty = "medium"

        elif "hard" in question:

            difficulty = "hard"


        # ==================================================
        # TOPIC
        # ==================================================

        topic = None

        topic_mapping = {

            "dynamic programming":
                "dynamic_programming",

            "dynamic_programming":
                "dynamic_programming",

            "dp":
                "dynamic_programming",

            "array":
                "arrays",

            "arrays":
                "arrays",

            "string":
                "strings",

            "strings":
                "strings",

            "linked list":
                "linked_list",

            "linked_list":
                "linked_list",

            "tree":
                "trees",

            "trees":
                "trees",

            "graph":
                "graphs",

            "graphs":
                "graphs",

            "stack":
                "stacks",

            "stacks":
                "stacks",

            "queue":
                "queues",

            "queues":
                "queues",

            "binary search":
                "binary_search",

            "greedy":
                "greedy",

            "backtracking":
                "backtracking"
        }

        for keyword, mapped_topic in topic_mapping.items():

            if keyword in question:

                topic = mapped_topic

                break


        # ==================================================
        # PREVIOUS PROGRESS
        # ==================================================

        previous_progress = (
            self.memory_tool.get_progress(
                state["session_id"]
            )
        )

        exclude_ids = {

            progress["problem_id"]

            for progress in previous_progress

            if progress.get("problem_id")
        }


        # ==================================================
        # ANOTHER / DIFFERENT PROBLEM
        # ==================================================

        another_phrases = [

            "another",

            "another question",

            "another problem",

            "different problem",

            "different question",

            "new problem",

            "new question",

            "next problem",

            "next question",

            "give me another",

            "give another",

            "one more"
        ]

        is_another_request = any(

            phrase in question

            for phrase in another_phrases
        )


        print(
            f"[PROBLEM] Topic: {topic}"
        )

        print(
            f"[PROBLEM] Difficulty: {difficulty}"
        )

        print(
            f"[PROBLEM] Previous problems: "
            f"{exclude_ids}"
        )

        print(
            f"[PROBLEM] Another request: "
            f"{is_another_request}"
        )


        # ==================================================
        # FETCH PROBLEMS
        # ==================================================

        if is_another_request:

            problems = self.problem_tool.execute(

                topic=topic,

                difficulty=difficulty,

                exclude_ids=exclude_ids
            )

        else:

            problems = self.problem_tool.execute(

                topic=topic,

                difficulty=difficulty
            )


        # ==================================================
        # FALLBACK
        # ==================================================

        if not problems and is_another_request:

            print(
                "[PROBLEM] No unseen matching "
                "problem found."
            )

            problems = self.problem_tool.execute(

                topic=topic,

                difficulty=difficulty
            )


        # ==================================================
        # NO PROBLEM
        # ==================================================

        if not problems:

            result = (
                "I couldn't find a matching "
                "DSA problem."
            )

            return {

                **state,

                "tool_result":
                    result,

                "observation":
                    result,

                "iteration":
                    state["iteration"] + 1
            }


        # ==================================================
        # SELECT PROBLEM
        # ==================================================

        import random

        selected = random.choice(
            problems
        )

        problem_id = selected["id"]

        problem = selected["description"]

        result = "\n".join(
            [

                "Here is your problem:",

                "",

                f"Title: {selected['title']}",

                f"Topic: {selected['topic']}",

                f"Difficulty: {selected['difficulty']}",

                "",

                selected["description"]
            ]
        )

        print(
            f"[PROBLEM] Selected: "
            f"{selected['title']} "
            f"({problem_id})"
        )

        return {

            **state,

            "problem_id":
                problem_id,

            "problem":
                problem,

            "tool_result":
                result,

            "observation":
                result,

            "iteration":
                state["iteration"] + 1
        }


    # ======================================================
    # HINT TOOL
    # ======================================================

    def call_hint(
        self,
        state: AgentState
    ) -> AgentState:

        print(
            "\n[TOOL] HINT"
        )

        question = (
            state["question"]
            .lower()
        )

        problem_id = (
            state.get(
                "problem_id",
                ""
            )
        )


        # ==================================================
        # GET CURRENT PROBLEM FROM MEMORY
        # ==================================================

        if not problem_id:

            current = (
                self.memory_tool
                .get_current_problem(
                    state["session_id"]
                )
            )

            if current:

                problem_id = (
                    current["problem_id"]
                )


        # ==================================================
        # FALLBACK DETECTION
        # ==================================================

        if not problem_id:

            if "house robber" in question:

                problem_id = "dp_001"

            elif "climbing stairs" in question:

                problem_id = "dp_002"

            elif "coin change" in question:

                problem_id = "dp_003"

            elif "two sum" in question:

                problem_id = "arr_001"

            elif "longest substring" in question:

                problem_id = "str_001"


        # ==================================================
        # HINT LEVEL
        # ==================================================

        hint_level = 1

        if (
            "another hint" in question
            or "second hint" in question
            or "hint 2" in question
        ):

            hint_level = 2

        elif (
            "one more hint" in question
            or "third hint" in question
            or "hint 3" in question
        ):

            hint_level = 3


        # ==================================================
        # NO PROBLEM
        # ==================================================

        if not problem_id:

            result = (
                "I need to know which problem "
                "you are working on before "
                "I can give you a hint."
            )

            return {

                **state,

                "tool_result":
                    result,

                "observation":
                    result,

                "iteration":
                    state["iteration"] + 1
            }


        # ==================================================
        # GET HINT
        # ==================================================

        result = self.hint_tool.execute(

            problem_id=problem_id,

            hint_level=hint_level
        )

        return {

            **state,

            "problem_id":
                problem_id,

            "tool_result":
                result,

            "observation":
                result,

            "iteration":
                state["iteration"] + 1
        }


    # ======================================================
    # CODE ANALYSIS
    # ======================================================

    def call_code_analysis(
        self,
        state: AgentState
    ) -> AgentState:

        print(
            "\n[TOOL] CODE ANALYSIS"
        )

        problem = state.get(
            "problem",
            ""
        )


        # ==================================================
        # GET CURRENT PROBLEM
        # ==================================================

        if not problem:

            current = (
                self.memory_tool
                .get_current_problem(
                    state["session_id"]
                )
            )

            if current:

                problem = current.get(
                    "problem_title",
                    ""
                )


        # ==================================================
        # ANALYZE
        # ==================================================

        result = self.code_tool.execute(

            code=state["question"],

            problem=problem
        )

        return {

            **state,

            "tool_result":
                result,

            "observation":
                result,

            "iteration":
                state["iteration"] + 1
        }


    # ======================================================
    # RAG
    # ======================================================

    def call_rag(
        self,
        state: AgentState
    ) -> AgentState:

        print(
            "\n[TOOL] RAG"
        )

        result = self.rag_tool.execute(
            state["question"]
        )

        return {

            **state,

            "context":
                result.get(
                    "context",
                    ""
                ),

            "tool_result":
                result.get(
                    "answer",
                    ""
                ),

            "observation":
                result.get(
                    "answer",
                    ""
                ),

            "iteration":
                state["iteration"] + 1
        }


    # ======================================================
    # MEMORY
    # ======================================================

    def update_memory(
        self,
        state: AgentState
    ) -> AgentState:

        print(
            "\n[MEMORY] Updating..."
        )

        session_id = (
            state["session_id"]
        )

        problem_id = (
            state.get(
                "problem_id",
                ""
            )
        )


        # ==================================================
        # NO PROBLEM
        # ==================================================

        if not problem_id:

            return state


        # ==================================================
        # PROBLEM REQUEST
        # ==================================================

        if state["route"] == "PROBLEM":

            problem_title = ""

            topic = ""

            difficulty = ""

            for problem in self.problem_tool.problems:

                if problem["id"] == problem_id:

                    problem_title = (
                        problem["title"]
                    )

                    topic = (
                        problem["topic"]
                    )

                    difficulty = (
                        problem["difficulty"]
                    )

                    break


            self.memory_tool.save_progress(

                session_id=session_id,

                problem_id=problem_id,

                problem_title=problem_title,

                topic=topic,

                difficulty=difficulty,

                hints_used=0,

                attempts=0,

                status="in_progress",

                last_action="requested_problem"
            )


        # ==================================================
        # HINT
        # ==================================================

        elif state["route"] == "HINT":

            self.memory_tool.increment_hints(

                session_id=session_id,

                problem_id=problem_id
            )


        # ==================================================
        # CODE
        # ==================================================

        elif state["route"] == "CODE":

            self.memory_tool.increment_attempts(

                session_id=session_id,

                problem_id=problem_id
            )


        return {

            **state,

            "observation":
                state["tool_result"]
        }


    # ======================================================
    # REACT GATE
    # ======================================================

    def after_memory_decision(
        self,
        state: AgentState
    ) -> str:

        """
        Decide whether ReAct planner is required.

        Simple requests terminate immediately.
        Multi-step requests use the planner.
        """

        question = (
            state["question"]
            .lower()
            .strip()
        )

        route = state["route"]


        # ==================================================
        # CODE
        # ==================================================

        if route == "CODE":

            multi_step_phrases = [

                "then explain",

                "then compare",

                "then teach",

                "also explain",

                "also compare",

                "after that explain",

                "after analyzing",

                "using rag",

                "look up and explain",

                "compare with",

                "compare it with"
            ]

            if any(

                phrase in question

                for phrase in multi_step_phrases
            ):

                print(
                    "[REACT GATE] "
                    "Multi-step code request "
                    "detected."
                )

                return "PLANNER"


            print(
                "[REACT GATE] "
                "Code analysis complete "
                "→ FINAL"
            )

            return "FINAL"


        # ==================================================
        # HINT
        # ==================================================

        if route == "HINT":

            print(
                "[REACT GATE] "
                "Hint complete → FINAL"
            )

            return "FINAL"


        # ==================================================
        # PROBLEM
        # ==================================================

        if route == "PROBLEM":

            print(
                "[REACT GATE] "
                "Problem provided → FINAL"
            )

            return "FINAL"


        # ==================================================
        # RAG
        # ==================================================

        if route == "RAG":

            print(
                "[REACT GATE] "
                "RAG answer generated → FINAL"
            )

            return "FINAL"


        # ==================================================
        # DEFAULT
        # ==================================================

        print(
            "[REACT GATE] "
            "Default → FINAL"
        )

        return "FINAL"


    # ======================================================
    # REACT PLANNER
    # ======================================================

    def call_planner(
        self,
        state: AgentState
    ) -> AgentState:

        print(
            "\n[REACT] "
            "Qwen is deciding next action..."
        )


        # ==================================================
        # STUDENT MEMORY
        # ==================================================

        memory = {}

        current = (
            self.memory_tool
            .get_current_problem(
                state["session_id"]
            )
        )

        if current:

            memory = current

            print(
                "\n[REACT] Student Memory:"
            )

            print(
                f"Problem: "
                f"{current['problem_title']}"
            )

            print(
                f"Topic: "
                f"{current['topic']}"
            )

            print(
                f"Difficulty: "
                f"{current['difficulty']}"
            )

            print(
                f"Hints: "
                f"{current['hints_used']}"
            )

            print(
                f"Attempts: "
                f"{current['attempts']}"
            )

            print(
                f"Status: "
                f"{current['status']}"
            )

            print(
                f"Last Action: "
                f"{current['last_action']}"
            )

        else:

            print(
                "\n[REACT] "
                "No existing student memory."
            )


        # ==================================================
        # CONVERSATION
        # ==================================================

        conversation_history = (
            state["conversation_history"]
        )

        print(
            f"[REACT] Conversation messages: "
            f"{len(conversation_history)}"
        )


        # ==================================================
        # PLANNER
        # ==================================================

        result = self.planner.plan(

            question=state["question"],

            problem=state["problem"],

            observation=state["observation"],

            route=state["route"],

            iteration=state["iteration"],

            max_iterations=state["max_iterations"],

            memory=memory,

            conversation_history=conversation_history
        )

        action = result["action"]

        reason = result["reason"]

        print(
            f"[REACT] Qwen decision: "
            f"{action}"
        )

        print(
            f"[REACT] Reason: "
            f"{reason}"
        )

        return {

            **state,

            "next_action":
                action
        }


    # ======================================================
    # PLANNER DECISION
    # ======================================================

    def planner_decision(
        self,
        state: AgentState
    ) -> str:

        action = state.get(
            "next_action",
            "FINAL"
        )

        allowed_actions = {

            "PROBLEM",

            "HINT",

            "CODE",

            "RAG",

            "FINAL"
        }

        if action not in allowed_actions:

            print(
                f"[REACT] Invalid action "
                f"'{action}' → FINAL"
            )

            return "FINAL"

        return action


    # ======================================================
    # FINAL ANSWER
    # ======================================================

    def generate_final_answer(
        self,
        state: AgentState
    ) -> AgentState:

        print(
            "\n[AGENT] FINAL ANSWER"
        )

        answer = state.get(
            "tool_result",
            ""
        )

        if not answer:

            answer = (
                "I couldn't generate an answer."
            )

        return {

            **state,

            "answer":
                answer,

            "final":
                True
        }


    # ======================================================
    # DIRECT ANSWER
    # ======================================================

    def direct_answer(
        self,
        state: AgentState
    ) -> AgentState:

        answer = (
            "I'm your DSA Coach. "
            "Ask me about Data Structures "
            "and Algorithms."
        )

        return {

            **state,

            "answer":
                answer,

            "final":
                True
        }


    # ======================================================
    # ASK
    # ======================================================

    def ask(
        self,
        question: str,
        session_id: str = "default_session"
    ) -> AgentState:

        result = self.graph.invoke(
            {
                "question": question,

                "session_id": session_id
            }
        )

        # ==================================================
        # SAVE ASSISTANT MESSAGE
        # ==================================================

        answer = result.get(
            "answer",
            ""
        )

        if answer:

            self.memory_tool.save_message(

                session_id=session_id,

                role="assistant",

                content=answer
            )

        return result


    # ======================================================
    # CLOSE
    # ======================================================

    def close(self):

        try:

            self.rag_tool.close()

        except Exception:

            pass


        try:

            self.memory_tool.close()

        except Exception:

            pass