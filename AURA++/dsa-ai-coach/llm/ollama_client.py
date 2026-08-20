import os
import ollama


class OllamaClient:
    """
    Handles communication with Ollama.

    Local:
        http://localhost:11434

    Docker:
        http://host.docker.internal:11434
    """

    def __init__(
        self,
        model: str = "qwen2.5-coder:7b"
    ):
        self.model = model

        # Allows us to use the same code locally and inside Docker.
        self.ollama_host = os.getenv(
            "OLLAMA_HOST",
            "http://localhost:11434"
        )

        self.client = ollama.Client(
            host=self.ollama_host
        )

    def generate(
        self,
        prompt: str
    ) -> str:

        print("\n" + "=" * 80)
        print("RAG PROMPT SENT TO OLLAMA")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response["message"]["content"]

        print("\nOLLAMA ANSWER")
        print("=" * 80)
        print(answer)
        print("=" * 80)

        return answer