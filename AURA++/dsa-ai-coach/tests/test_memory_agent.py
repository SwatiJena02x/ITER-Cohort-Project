from agents import DSACoachAgent


def main():

    print("\n" + "=" * 70)
    print("DSA COACH - MEMORY AGENT TEST")
    print("=" * 70)

    agent = DSACoachAgent()

    session_id = "memory_test_001"

    try:

        # ==========================================
        # STEP 1 — Get a problem
        # ==========================================

        print("\n\nSTEP 1")
        print("Student: Give me a medium DP problem.")

        result = agent.ask(
            "Give me a medium DP problem.",
            session_id=session_id
        )

        print("\nAgent:")
        print(result["answer"])

        # ==========================================
        # STEP 2 — Ask for first hint
        # ==========================================

        print("\n\nSTEP 2")
        print("Student: I'm stuck. Give me a hint.")

        result = agent.ask(
            "I'm stuck. Give me a hint.",
            session_id=session_id
        )

        print("\nAgent:")
        print(result["answer"])

        # ==========================================
        # STEP 3 — Ask for second hint
        # ==========================================

        print("\n\nSTEP 3")
        print("Student: Give me another hint.")

        result = agent.ask(
            "Give me another hint.",
            session_id=session_id
        )

        print("\nAgent:")
        print(result["answer"])

        # ==========================================
        # STEP 4 — Ask for third hint
        # ==========================================

        print("\n\nSTEP 4")
        print("Student: Give me one more hint.")

        result = agent.ask(
            "Give me one more hint.",
            session_id=session_id
        )

        print("\nAgent:")
        print(result["answer"])

        # ==========================================
        # CHECK MEMORY
        # ==========================================

        print("\n\n" + "=" * 70)
        print("FINAL MEMORY")
        print("=" * 70)

        progress = agent.memory_tool.get_progress(
            session_id
        )

        if not progress:

            print("\nNo progress found.")

        else:

            for item in progress:

                print(
                    f"\nProblem: "
                    f"{item['problem_title']}"
                )

                print(
                    f"Problem ID: "
                    f"{item['problem_id']}"
                )

                print(
                    f"Topic: "
                    f"{item['topic']}"
                )

                print(
                    f"Difficulty: "
                    f"{item['difficulty']}"
                )

                print(
                    f"Hints Used: "
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