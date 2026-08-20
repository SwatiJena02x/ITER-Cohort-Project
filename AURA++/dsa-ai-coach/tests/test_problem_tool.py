from tools import ProblemTool


def main():

    tool = ProblemTool()

    print("\n" + "=" * 60)
    print("PROBLEM TOOL TEST")
    print("=" * 60)

    # -------------------------------
    # Test 1: DP + Medium
    # -------------------------------

    results = tool.execute(
        topic="dynamic_programming",
        difficulty="medium"
    )

    print("\nDP + Medium Problems:")

    for problem in results:

        print(
            f"\n{problem['id']} - "
            f"{problem['title']}"
        )

        print(
            f"Difficulty: "
            f"{problem['difficulty']}"
        )

        print(
            f"Description: "
            f"{problem['description']}"
        )

    # -------------------------------
    # Test 2: All easy problems
    # -------------------------------

    results = tool.execute(
        difficulty="easy"
    )

    print("\n" + "=" * 60)
    print("EASY PROBLEMS")
    print("=" * 60)

    for problem in results:

        print(
            f"{problem['title']} "
            f"({problem['topic']})"
        )


if __name__ == "__main__":
    main()