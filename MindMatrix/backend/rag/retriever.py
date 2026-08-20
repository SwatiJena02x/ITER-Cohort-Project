# ============================================================
# DSA COACH AI - RETRIEVER
# ============================================================
#
# File Name:
#     retriever.py
#
# Purpose:
#     Retrieve relevant DSA knowledge from the existing
#     FAISS vector database.
#
# Task 4:
#     Retrieve relevant chunks using semantic similarity.
#
# Workflow:
#
#     User Problem
#          |
#          v
#     Question Embedding
#          |
#          v
#     FAISS Similarity Search
#          |
#          v
#     Relevant Chunks
#          |
#          v
#     chunk_id
#          |
#          v
#     PostgreSQL Metadata
#
# ============================================================


# ------------------------------------------------------------
# Standard Library Imports
# ------------------------------------------------------------

import os


# ------------------------------------------------------------
# FAISS Vector Store
# ------------------------------------------------------------

from langchain_community.vectorstores import FAISS


# ------------------------------------------------------------
# Embedding Model
# ------------------------------------------------------------

from rag.embeddings import get_embeddings


# ------------------------------------------------------------
# PostgreSQL Helper
# ------------------------------------------------------------

from rag.postgres_db import get_problem_by_chunk_id


# ============================================================
# FAISS DATABASE LOCATION
# ============================================================

# Current directory:
# backend/rag

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# FAISS index directory:
# backend/rag/faiss_index

FAISS_FOLDER = os.path.join(
    CURRENT_DIR,
    "faiss_index"
)


# ============================================================
# GLOBAL VECTOR DATABASE
# ============================================================

# Initially None.
#
# The FAISS database will be loaded only once.
# This prevents loading the vector database for every query.

vector_db = None


# ============================================================
# FUNCTION: get_vector_database()
# ============================================================

def get_vector_database():
    """
    Load the existing FAISS vector database.

    The database is loaded only once and then reused.
    """

    global vector_db

    # --------------------------------------------------------
    # Check whether FAISS is already loaded
    # --------------------------------------------------------

    if vector_db is None:

        # Check whether FAISS folder exists
        if not os.path.exists(FAISS_FOLDER):

            raise FileNotFoundError(
                f"FAISS index not found: {FAISS_FOLDER}"
            )

        print(
            "Loading existing FAISS vector database..."
        )

        # ----------------------------------------------------
        # Load embedding model
        # ----------------------------------------------------

        embeddings = get_embeddings()

        # ----------------------------------------------------
        # Load existing FAISS index
        #
        # allow_dangerous_deserialization=True is required
        # because FAISS stores serialized index data.
        #
        # Only load indexes created by this application.
        # ----------------------------------------------------

        vector_db = FAISS.load_local(

            FAISS_FOLDER,

            embeddings,

            allow_dangerous_deserialization=True

        )

        print(
            "FAISS vector database loaded successfully."
        )

    # Return the loaded database
    return vector_db


# ============================================================
# FUNCTION: retrieve_documents()
# ============================================================

def retrieve_documents(
    problem,
    k=4
):
    """
    Retrieve the most relevant documents from FAISS.

    Args:
        problem:
            User's DSA problem/question.

        k:
            Number of relevant chunks to retrieve.

    Returns:
        List of LangChain Document objects.
    """

    # --------------------------------------------------------
    # Load FAISS database
    # --------------------------------------------------------

    db = get_vector_database()

    # --------------------------------------------------------
    # Perform similarity search
    #
    # FAISS compares the embedding of the user question
    # with the embeddings stored in the vector database.
    # --------------------------------------------------------

    results = db.similarity_search(

        problem,

        k=k

    )

    return results


# ============================================================
# FUNCTION: retrieve_context()
# ============================================================

def retrieve_context(
    problem,
    k=4
):
    """
    Retrieve relevant DSA knowledge and combine it
    into a single context string.

    This context can later be passed to an AI agent/LLM.
    """

    # --------------------------------------------------------
    # Retrieve relevant documents
    # --------------------------------------------------------

    results = retrieve_documents(
        problem,
        k
    )

    # --------------------------------------------------------
    # Combine document contents
    # --------------------------------------------------------

    context_parts = []

    for document in results:

        context_parts.append(
            document.page_content
        )

    # Join all chunks
    context = "\n\n".join(
        context_parts
    )

    return context


# ============================================================
# FUNCTION: retrieve_with_metadata()
# ============================================================

def retrieve_with_metadata(
    problem,
    k=4
):
    """
    Retrieve FAISS chunks and then use the shared chunk_id
    to retrieve structured information from PostgreSQL.

    This demonstrates the FAISS <-> PostgreSQL connection.
    """

    # --------------------------------------------------------
    # Retrieve relevant FAISS documents
    # --------------------------------------------------------

    results = retrieve_documents(
        problem,
        k
    )

    retrieved_data = []

    # --------------------------------------------------------
    # Process each retrieved chunk
    # --------------------------------------------------------

    for document in results:

        # Get metadata stored during Task 3
        metadata = document.metadata

        # Get shared FAISS/PostgreSQL ID
        chunk_id = metadata.get(
            "chunk_id"
        )

        # ----------------------------------------------------
        # Retrieve PostgreSQL record
        # ----------------------------------------------------

        postgres_data = None

        if chunk_id:

            postgres_data = get_problem_by_chunk_id(
                chunk_id
            )

        # ----------------------------------------------------
        # Store combined result
        # ----------------------------------------------------

        retrieved_data.append({

            "chunk_id": chunk_id,

            "content": document.page_content,

            "metadata": metadata,

            "postgres_data": postgres_data

        })

    return retrieved_data


# ============================================================
# TEST RETRIEVER
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("DSA COACH AI - RETRIEVER TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Example DSA question
    # --------------------------------------------------------

    test_problem = (
        "Given an array of integers and a target, "
        "find two numbers that add up to the target."
    )

    print("\nQuery:")
    print(test_problem)

    try:

        # ----------------------------------------------------
        # Retrieve relevant chunks
        # ----------------------------------------------------

        results = retrieve_with_metadata(
            test_problem,
            k=4
        )

        # ----------------------------------------------------
        # Display results
        # ----------------------------------------------------

        print("\n")
        print("=" * 60)
        print("RETRIEVED RESULTS")
        print("=" * 60)

        for index, result in enumerate(
            results,
            start=1
        ):

            print(
                f"\nRESULT {index}"
            )

            print(
                "-" * 60
            )

            # Display chunk ID
            print(
                f"Chunk ID: {result['chunk_id']}"
            )

            # Display source
            print(
                f"Source: "
                f"{result['metadata'].get('source_file')}"
            )

            # Display chunking method
            print(
                f"Chunking method: "
                f"{result['metadata'].get('chunking_method')}"
            )

            # Display content
            print("\nContent:")

            print(
                result["content"]
            )

            # ------------------------------------------------
            # PostgreSQL information
            # ------------------------------------------------

            postgres_data = result[
                "postgres_data"
            ]

            if postgres_data:

                print("\nPostgreSQL:")

                print(
                    f"Problem ID: "
                    f"{postgres_data['problem_id']}"
                )

                print(
                    f"Title: "
                    f"{postgres_data['title']}"
                )

                print(
                    f"Topic: "
                    f"{postgres_data['topic']}"
                )

                print(
                    f"Difficulty: "
                    f"{postgres_data['difficulty']}"
                )

        # ----------------------------------------------------
        # Final success message
        # ----------------------------------------------------

        print("\n")
        print("=" * 60)
        print("RETRIEVER TEST COMPLETED")
        print("=" * 60)

    except Exception as error:

        print("\nRetriever test failed.")

        print("\nError:")

        print(error)