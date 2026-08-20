from tools import MemoryTool


def main():

    print("\n" + "=" * 60)
    print("MEMORY TOOL TEST")
    print("=" * 60)

    memory = MemoryTool()

    session_id = "test_session_001"

    # ------------------------------------------
    # Save progress
    # ------------------------------------------

    memory.save_progress(
        session_id=session_id,
        problem_id="dp_001",
        problem_title="House Robber",
        topic="dynamic_programming",
        difficulty="medium",
        hints_used=2,
        attempts=1,
        status="in_progress",
        last_action="requested_hint"
    )

    print(
        "\nProgress saved successfully."
    )

    # ------------------------------------------
    # Retrieve progress
    # ------------------------------------------

    progress = memory.get_progress(
        session_id
    )

    print("\nStored Progress:")

    for item in progress:

        print(
            f"\nProblem: "
            f"{item['problem_title']}"
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

    memory.close()


if __name__ == "__main__":
    main()