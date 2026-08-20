from agents import DSACoachAgent


def main():

    print("\n" + "=" * 70)
    print("CONVERSATION MEMORY TEST")
    print("=" * 70)

    agent = DSACoachAgent()

    session_id = "conversation_test_001"

    try:

        # ==========================================
        # MESSAGE 1
        # ==========================================

        print("\nUSER:")
        print("Give me a medium DP problem.")

        result = agent.ask(
            "Give me a medium DP problem.",
            session_id=session_id
        )

        print("\nASSISTANT:")
        print(result["answer"])

        # ==========================================
        # MESSAGE 2
        # ==========================================

        print("\nUSER:")
        print("Give me a hint.")

        result = agent.ask(
            "Give me a hint.",
            session_id=session_id
        )

        print("\nASSISTANT:")
        print(result["answer"])

        # ==========================================
        # MESSAGE 3
        # ==========================================

        print("\nUSER:")
        print("Why?")

        result = agent.ask(
            "Why?",
            session_id=session_id
        )

        print("\nASSISTANT:")
        print(result["answer"])

        # ==========================================
        # SHOW HISTORY
        # ==========================================

        print("\n" + "=" * 70)
        print("STORED CONVERSATION")
        print("=" * 70)

        history = (
            agent.memory_tool.get_conversation(
                session_id=session_id,
                limit=20
            )
        )

        for message in history:

            print(
                f"\n{message['role'].upper()}:"
            )

            print(
                message["content"]
            )

    finally:

        agent.close()


if __name__ == "__main__":
    main()