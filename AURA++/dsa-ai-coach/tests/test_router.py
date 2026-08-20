from agents.router import AgentRouter


def main():

    router = AgentRouter()

    questions = [
        "What is the DP state in House Robber?",
        "I'm stuck on my dynamic programming solution.",
        "Explain time complexity of binary search.",
        "Hello, how are you?"
    ]

    for question in questions:

        print("\n" + "=" * 60)

        print(
            "Question:",
            question
        )

        decision = router.classify(
            question
        )

        print(
            "Decision:",
            decision
        )


if __name__ == "__main__":
    main()