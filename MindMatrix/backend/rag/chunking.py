# ============================================================
# DSA COACH AI - DOCUMENT CHUNKING MODULE
# ============================================================
#
# Purpose:
#   Split large LangChain Documents into smaller chunks before
#   generating embeddings.
#
# Why chunking is required:
#   Large documents cannot always be passed directly to an
#   embedding model or LLM. Chunking breaks the documents into
#   smaller, searchable pieces.
#
# Chunking methods implemented:
#
#   1. Recursive Character Text Splitting
#   2. Character Text Splitting
#   3. Token-Based Text Splitting
#
# The project will compare these methods and select the most
# suitable strategy for the DSA Coach RAG pipeline.
# ============================================================


# ------------------------------------------------------------
# Standard Library Imports
# ------------------------------------------------------------

from pathlib import Path
from typing import Dict, List


# ------------------------------------------------------------
# LangChain Imports
# ------------------------------------------------------------

from langchain_core.documents import Document

from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)


# ============================================================
# 1. RECURSIVE CHARACTER CHUNKING
# ============================================================

def recursive_chunking(
    documents: List[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> List[Document]:
    """
    Split documents using RecursiveCharacterTextSplitter.

    Recursive splitting tries several separators in order:

        1. Paragraph
        2. Line
        3. Space
        4. Character

    This helps preserve meaningful sections of text.

    Args:
        documents:
            List of LangChain Document objects.

        chunk_size:
            Maximum approximate number of characters in a chunk.

        chunk_overlap:
            Number of characters shared between neighboring
            chunks.

    Returns:
        List of smaller LangChain Document chunks.
    """

    # Create the recursive text splitter.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,

        # Try to split at meaningful boundaries first.
        separators=[
            "\n\n",  # Paragraph boundary
            "\n",    # Line boundary
            " ",     # Word boundary
            "",      # Character boundary
        ],
    )

    # Split all documents into smaller chunks.
    chunks = splitter.split_documents(documents)

    return chunks


# ============================================================
# 2. CHARACTER-BASED CHUNKING
# ============================================================

def character_chunking(
    documents: List[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> List[Document]:
    """
    Split documents using CharacterTextSplitter.

    This method uses a fixed separator and character length.

    Args:
        documents:
            List of LangChain Document objects.

        chunk_size:
            Maximum size of each chunk.

        chunk_overlap:
            Number of overlapping characters.

    Returns:
        List of character-based document chunks.
    """

    # Create a character-based splitter.
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    # Split the documents.
    chunks = splitter.split_documents(documents)

    return chunks


# ============================================================
# 3. TOKEN-BASED CHUNKING
# ============================================================

def token_chunking(
    documents: List[Document],
    chunk_size: int = 300,
    chunk_overlap: int = 50,
) -> List[Document]:
    """
    Split documents approximately according to token count.

    Token-based chunking is useful when the final LLM has
    token-based context limitations.

    We use the cl100k_base tokenizer when tiktoken is available.

    Args:
        documents:
            List of LangChain Document objects.

        chunk_size:
            Approximate maximum number of tokens per chunk.

        chunk_overlap:
            Approximate token overlap.

    Returns:
        List of token-based chunks.
    """

    try:

        # Create a tokenizer-aware recursive splitter.
        splitter = (
            RecursiveCharacterTextSplitter
            .from_tiktoken_encoder(
                encoding_name="cl100k_base",
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        )

    except Exception as error:

        # If tiktoken is unavailable, use a character-based
        # fallback instead of stopping the entire pipeline.
        print(
            "\nWarning: Tokenizer unavailable."
        )

        print(
            f"Reason: {error}"
        )

        print(
            "Using character-based fallback."
        )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size * 4,
            chunk_overlap=chunk_overlap * 4,
        )

    # Split documents.
    chunks = splitter.split_documents(documents)

    return chunks


# ============================================================
# 4. COMPARE ALL CHUNKING METHODS
# ============================================================

def compare_chunking_methods(
    documents: List[Document],
) -> Dict[str, List[Document]]:
    """
    Run all three chunking strategies.

    This function is useful for comparing the number and size
    of generated chunks.

    Args:
        documents:
            Original LangChain Documents.

    Returns:
        Dictionary containing chunks generated by each method.
    """

    # Run recursive character chunking.
    recursive_chunks = recursive_chunking(
        documents
    )

    # Run normal character chunking.
    character_chunks = character_chunking(
        documents
    )

    # Run token-based chunking.
    token_chunks = token_chunking(
        documents
    )

    # Return all results.
    return {
        "recursive": recursive_chunks,
        "character": character_chunks,
        "token": token_chunks,
    }


# ============================================================
# 5. PRINT CHUNK STATISTICS
# ============================================================

def print_chunk_statistics(
    method_name: str,
    chunks: List[Document],
) -> None:
    """
    Display statistics for a chunking strategy.

    Statistics include:
        - Number of chunks
        - Total characters
        - Average chunk size
        - Sample chunks
    """

    # Handle an empty chunk list.
    if not chunks:

        print(
            f"\n{method_name}: No chunks generated."
        )

        return

    # Calculate total characters.
    total_characters = sum(
        len(chunk.page_content)
        for chunk in chunks
    )

    # Calculate average chunk size.
    average_size = (
        total_characters / len(chunks)
    )

    # Print statistics.
    print("\n")
    print("=" * 60)
    print(f"CHUNKING METHOD: {method_name}")
    print("=" * 60)

    print(
        f"Number of chunks      : {len(chunks)}"
    )

    print(
        f"Total characters      : {total_characters}"
    )

    print(
        f"Average chunk size    : "
        f"{average_size:.2f} characters"
    )

    # Display a few sample chunks.
    print("\nSample chunks:")

    for index, chunk in enumerate(
        chunks[:3],
        start=1,
    ):

        print("\n" + "-" * 50)

        print(
            f"Chunk {index}"
        )

        print("-" * 50)

        print(
            chunk.page_content[:300]
        )

        # Display source metadata.
        print(
            "\nSource:",
            chunk.metadata.get(
                "source",
                "Unknown",
            ),
        )


# ============================================================
# 6. MAIN TEST PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("DSA COACH AI - CHUNKING TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Find the backend directory automatically.
    #
    # Current file:
    #
    # backend/
    #     rag/
    #         chunking.py
    #
    # parents[0] = rag
    # parents[1] = backend
    # --------------------------------------------------------

    backend_directory = (
        Path(__file__).resolve().parents[1]
    )

    # --------------------------------------------------------
    # Locate the documents directory.
    # --------------------------------------------------------

    documents_directory = (
        backend_directory
        / "rag"
        / "documents"
    )

    print("\nDocuments directory:")
    print(documents_directory)

    # --------------------------------------------------------
    # Import the unified document loader.
    # --------------------------------------------------------

    from rag.loaders.document_loader import (
        load_all_documents,
    )

    # --------------------------------------------------------
    # Load all supported documents.
    # --------------------------------------------------------

    print("\n")
    print("Loading documents...")

    documents = load_all_documents(
        str(documents_directory)
    )

    print(
        f"\nOriginal documents loaded: "
        f"{len(documents)}"
    )

    # --------------------------------------------------------
    # Run Recursive Character Chunking.
    # --------------------------------------------------------

    recursive_chunks = recursive_chunking(
        documents,
        chunk_size=800,
        chunk_overlap=100,
    )

    print_chunk_statistics(
        "Recursive Character",
        recursive_chunks,
    )

    # --------------------------------------------------------
    # Run Character Chunking.
    # --------------------------------------------------------

    character_chunks = character_chunking(
        documents,
        chunk_size=800,
        chunk_overlap=100,
    )

    print_chunk_statistics(
        "Character",
        character_chunks,
    )

    # --------------------------------------------------------
    # Run Token-Based Chunking.
    # --------------------------------------------------------

    token_chunks = token_chunking(
        documents,
        chunk_size=300,
        chunk_overlap=50,
    )

    print_chunk_statistics(
        "Token Based",
        token_chunks,
    )

    # ========================================================
    # FINAL COMPARISON
    # ========================================================

    print("\n")
    print("=" * 60)
    print("CHUNKING METHOD COMPARISON")
    print("=" * 60)

    print(
        f"\nRecursive Character : "
        f"{len(recursive_chunks)} chunks"
    )

    print(
        f"Character           : "
        f"{len(character_chunks)} chunks"
    )

    print(
        f"Token Based         : "
        f"{len(token_chunks)} chunks"
    )

    print("\n")
    print("=" * 60)
    print("CHUNKING TEST COMPLETED")
    print("=" * 60)