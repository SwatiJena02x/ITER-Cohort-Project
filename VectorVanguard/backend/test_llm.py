from app.services.llm import llm


def run_test():
    print("[*] Testing local Ollama LLM...")

    response = llm.invoke(
        "In one short sentence, explain what semantic search means."
    )

    print("\n[SUCCESS] LLM response received:")
    print(response.content)


if __name__ == "__main__":
    run_test()