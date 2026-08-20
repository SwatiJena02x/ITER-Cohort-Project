class ContextBuilder:
    """
    Builds clean context from retrieved chunks
    for the LLM.
    """

    def __init__(
        self,
        max_chunks: int = 3
    ):

        self.max_chunks = max_chunks

    def build(
        self,
        results: list[dict]
    ) -> str:
        """
        Convert retrieved search results into
        formatted context.
        """

        if not results:
            return ""

        selected_results = results[
            :self.max_chunks
        ]

        context_parts = []

        for index, result in enumerate(
            selected_results,
            start=1
        ):

            source = result.get(
                "source",
                "unknown"
            )

            chunk_id = result.get(
                "chunk_id",
                "unknown"
            )

            content = result.get(
                "content",
                ""
            )

            similarity = result.get(
                "similarity",
                0.0
            )

            context = f"""
--- Context {index} ---
Source: {source}
Chunk ID: {chunk_id}
Similarity: {similarity:.4f}

{content}
"""

            context_parts.append(
                context.strip()
            )

        return "\n\n".join(
            context_parts
        )