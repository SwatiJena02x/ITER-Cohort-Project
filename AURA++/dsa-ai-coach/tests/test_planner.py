from agents.planner import ReActPlanner


def main():

    print("\n" + "=" * 60)
    print("REACT PLANNER TEST")
    print("=" * 60)

    planner = ReActPlanner()

    # ==========================================
    # Test 1
    # ==========================================

    result = planner.plan(

        question=(
            "Give me a medium DP problem."
        ),

        problem="",

        observation="",

        route="PROBLEM",

        iteration=0,

        max_iterations=5
    )

    print("\nTest 1")
    print(result)

    # ==========================================
    # Test 2
    # ==========================================

    result = planner.plan(

        question=(
            "I'm stuck. Give me a hint."
        ),

        problem="House Robber",

        observation=(
            "Student is currently "
            "working on House Robber."
        ),

        route="HINT",

        iteration=1,

        max_iterations=5
    )

    print("\nTest 2")
    print(result)

    # ==========================================
    # Test 3
    # ==========================================

    result = planner.plan(

        question=(
            "Analyze my Python solution."
        ),

        problem="House Robber",

        observation=(
            "Student submitted Python code."
        ),

        route="CODE",

        iteration=1,

        max_iterations=5
    )

    print("\nTest 3")
    print(result)

    # ==========================================
    # Test 4
    # ==========================================

    result = planner.plan(

        question=(
            "What is dynamic programming?"
        ),

        problem="",

        observation="",

        route="RAG",

        iteration=0,

        max_iterations=5
    )

    print("\nTest 4")
    print(result)


if __name__ == "__main__":
    main()