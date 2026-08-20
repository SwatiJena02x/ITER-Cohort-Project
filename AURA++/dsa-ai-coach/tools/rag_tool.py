from rag import RAGPipeline


class RAGTool:
    """
    Tool that allows the agent to access
    the DSA knowledge base.
    """

    def __init__(self):

        self.rag = RAGPipeline(
            model="qwen2.5-coder:7b",
            top_k=3
        )

    def execute(
        self,
        question: str
    ) -> dict:
        """
        Retrieve relevant knowledge and
        generate a RAG-based answer.
        """

        result = self.rag.ask(
            question
        )

        return result

    def close(self):

        self.rag.close()