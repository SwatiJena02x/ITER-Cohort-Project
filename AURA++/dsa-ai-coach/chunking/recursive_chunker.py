from langchain_text_splitters import RecursiveCharacterTextSplitter

from document_loader.document import Document
from .chunk import Chunk


class RecursiveChunker:
    """
    Splits documents using recursive character-based splitting.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,

            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def chunk_document(
        self,
        document: Document,
        document_index: int = 0
    ) -> list[Chunk]:

        texts = self.splitter.split_text(
            document.text
        )

        chunks = []

        for index, text in enumerate(
            texts
        ):

            chunk_id = (
                f"doc_{document_index:03d}"
                f"_chunk_{index:03d}"
            )

            metadata = {
                **document.metadata,

                "chunk_index": index,

                "chunk_size": len(text)
            }

            chunk = Chunk(
                chunk_id=chunk_id,
                text=text,
                metadata=metadata
            )

            chunks.append(chunk)

        return chunks

    def chunk_documents(
        self,
        documents: list[Document]
    ) -> list[Chunk]:

        all_chunks = []

        for document_index, document in enumerate(
            documents
        ):

            chunks = self.chunk_document(
                document,
                document_index
            )

            all_chunks.extend(chunks)

        return all_chunks