from llm import OllamaClient


def main():

    print("\n" + "=" * 60)
    print("LLM TEST")
    print("=" * 60)

    llm = OllamaClient(
        model="qwen2.5-coder:7b"
    )

    prompt = """
You are a DSA tutor.

Explain Dynamic Programming in simple terms
to a beginner.

Keep the explanation under 150 words.
"""

    response = llm.generate(
        prompt
    )

    print("\nLLM RESPONSE:")
    print(response)


if __name__ == "__main__":
    main()