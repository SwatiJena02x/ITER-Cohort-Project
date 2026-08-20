from app.services.agent import agent


def run_test():
    print("[*] Testing LangGraph agent...")

    question = (
        "Investigate whether a mobile phone was visible "
        "near an examination desk. Search the available "
        "evidence and answer based only on retrieved evidence."
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    print("\n[SUCCESS] Agent execution completed.")

    print("\nAgent messages:")

    for message in result["messages"]:
        print(f"\n--- {message.type} ---")
        print(message.content)


if __name__ == "__main__":
    run_test()
    