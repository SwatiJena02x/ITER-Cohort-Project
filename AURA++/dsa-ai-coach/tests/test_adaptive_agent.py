from agents import DSACoachAgent


def main():

    print("\n" + "=" * 70)
    print("ADAPTIVE DSA AGENT TEST")
    print("=" * 70)

    agent = DSACoachAgent()

    session_id = "adaptive_test_001"

    try:

        # ==========================================
        # STEP 1
        # ==========================================

        print("\nSTEP 1")
        print(
            "Student: "
            "Give me a medium DP problem."
        )

        result = agent.ask(
            "Give me a medium DP problem.",
            session_id=session_id
        )

        print("\nAgent:")
        print(result["answer"])

        # ==========================================
        # STEP 2
        # ==========================================

        print("\nSTEP 2")
        print(
            "Student: "
            "Give me a hint."
        )

        result = agent.ask(
            "Give me a hint.",
            session_id=session_id
        )

        print("\nAgent:")
        print(result["answer"])

        # ==========================================
        # STEP 3
        # ==========================================

        print("\nSTEP 3")
        print(
            "Student: "
            "Give me another hint."
        )

        result = agent.ask(
            "Give me another hint.",
            session_id=session_id
        )

        print("\nAgent:")
        print(result["answer"])

        # ==========================================
        # MEMORY
        # ==========================================

        print("\n" + "=" * 70)
        print("FINAL STUDENT MEMORY")
        print("=" * 70)

        progress = (
            agent.memory_tool.get_progress(
                session_id
            )
        )

        for item in progress:

            print(
                f"\nProblem: "
                f"{item['problem_title']}"
            )

            print(
                f"Hints: "
                f"{item['hints_used']}"
            )

            print(
                f"Attempts: "
                f"{item['attempts']}"
            )

            print(
                f"Status: "
                f"{item['status']}"
            )

            print(
                f"Last Action: "
                f"{item['last_action']}"
            )

    finally:

        agent.close()


if __name__ == "__main__":
    main()