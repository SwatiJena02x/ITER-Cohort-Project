from agents import DSACoachAgent


def main():

    agent = DSACoachAgent()

    try:

        result = agent.ask(
            "What is dynamic programming?",
            session_id="react_test_001"
        )

        print("\nFINAL ANSWER:")
        print(result["answer"])

    finally:

        agent.close()


if __name__ == "__main__":
    main()