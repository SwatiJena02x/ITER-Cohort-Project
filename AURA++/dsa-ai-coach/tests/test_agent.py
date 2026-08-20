from agents import DSACoachAgent


def run_test(
    agent: DSACoachAgent,
    question: str
):
    print("\n" + "=" * 70)

    print("STUDENT:")
    print(question)

    print("-" * 70)

    result = agent.ask(
        question
    )

    print("\nROUTE:")
    print(result["route"])

    print("\nANSWER:")
    print(result["answer"])


def main():

    print("\n" + "=" * 70)
    print("DSA COACH AGENT - COMPLETE TEST")
    print("=" * 70)

    agent = DSACoachAgent()

    try:

        # ==================================================
        # TEST 1 — RAG
        # ==================================================

        run_test(
            agent,
            "What is the DP state in the House Robber problem?"
        )

        # ==================================================
        # TEST 2 — PROBLEM TOOL
        # ==================================================

        run_test(
            agent,
            "Give me a medium DP problem."
        )

        # ==================================================
        # TEST 3 — HINT TOOL
        # ==================================================

        run_test(
            agent,
            "I'm stuck on House Robber. Give me a hint."
        )

        # ==================================================
        # TEST 4 — SECOND HINT
        # ==================================================

        run_test(
            agent,
            "Give me another hint for House Robber."
        )

        # ==================================================
        # TEST 5 — CODE ANALYSIS TOOL
        # ==================================================

        code_question = """
Analyze this code for House Robber:

def rob(nums):
    n = len(nums)

    if n == 0:
        return 0

    dp = [0] * n

    dp[0] = nums[0]

    for i in range(1, n):
        for j in range(i - 1):
            dp[i] = max(
                dp[i],
                dp[j] + nums[i]
            )

    return dp[n - 1]
"""

        run_test(
            agent,
            code_question
        )

        # ==================================================
        # TEST 6 — DIRECT
        # ==================================================

        run_test(
            agent,
            "Hello"
        )

    finally:

        agent.close()


if __name__ == "__main__":
    main()