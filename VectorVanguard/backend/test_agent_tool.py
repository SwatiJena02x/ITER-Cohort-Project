from app.services.agent_tools import retrieve_evidence


def run_test():
    print("[*] Testing retrieval tool...")

    result = retrieve_evidence.invoke(
        {
            "query": "mobile phone near examination desk"
        }
    )

    print("\n[SUCCESS] Tool executed.")
    print("\nRetrieved evidence:")
    print(result)


if __name__ == "__main__":
    run_test()