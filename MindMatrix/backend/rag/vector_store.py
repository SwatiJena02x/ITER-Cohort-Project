# ============================================================
# File Name:
# vector_store.py
#
# Purpose:
# ------------------------------------------------------------
# Creates a FAISS Vector Database for the DSA Coach RAG system.
#
# Knowledge Sources:
#   1. DSA Knowledge
#   2. DSA Patterns
#   3. Interview Rules
#   4. LeetCode Notes
#
# Task 3:
#   1. Generate embeddings
#   2. Store documents + embeddings in FAISS
#   3. Store structured DSA data in PostgreSQL
#   4. Link FAISS chunks with PostgreSQL using chunk_id
#
# Flow:
#
# Text Files
#     |
#     v
# Document Loader
#     |
#     v
# Text Splitter
#     |
#     v
# Metadata + Chunk ID
#     |
#     v
# Embeddings
#     |
#     v
# FAISS Vector Store
#     |
#     v
# PostgreSQL
#
# ============================================================


# ============================================================
# STANDARD LIBRARY IMPORTS
# ============================================================

import os
import uuid


# ============================================================
# LANGCHAIN IMPORTS
# ============================================================

# FAISS vector database
from langchain_community.vectorstores import FAISS

# Text loader
from langchain_community.document_loaders import TextLoader

# Text splitter
from langchain_text_splitters import CharacterTextSplitter


# ============================================================
# PROJECT IMPORTS
# ============================================================

# Embedding model
from rag.embeddings import get_embeddings

# PostgreSQL functions
from rag.postgres_db import (
    create_tables,
    insert_problem
)


# ============================================================
# CURRENT DIRECTORY
# ============================================================

# Current directory:
# backend/rag

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# DOCUMENT DIRECTORY
# ============================================================

# Documents are stored inside:
#
# backend/rag/documents

DOCUMENT_FOLDER = os.path.join(
    CURRENT_DIR,
    "documents"
)


# ============================================================
# FAISS STORAGE DIRECTORY
# ============================================================

# The FAISS index will be stored here:
#
# backend/rag/faiss_index

FAISS_FOLDER = os.path.join(
    CURRENT_DIR,
    "faiss_index"
)


# ============================================================
# KNOWLEDGE FILES
# ============================================================

# Add new knowledge files here when required.

KNOWLEDGE_FILES = [

    "dsa_knowledge.txt",

    "dsa_patterns.txt",

    "interview_rules.txt",

    "leetcode_notes.txt"

]


# ============================================================
# EXTRACT DSA METADATA
# ============================================================

def extract_metadata(chunk):
    """
    Extract useful DSA metadata from a document chunk.

    Metadata:
        title
        topic
        difficulty
        tags
    """

    # --------------------------------------------------------
    # Get chunk text
    # --------------------------------------------------------

    text = chunk.page_content

    text_lower = text.lower()


    # --------------------------------------------------------
    # Default values
    # --------------------------------------------------------

    title = "DSA Knowledge Chunk"

    topic = None

    difficulty = None

    tags = []


    # ========================================================
    # DETECT DIFFICULTY
    # ========================================================

    if "easy" in text_lower:

        difficulty = "Easy"

    elif "medium" in text_lower:

        difficulty = "Medium"

    elif "hard" in text_lower:

        difficulty = "Hard"


    # ========================================================
    # DSA TOPIC KEYWORDS
    # ========================================================

    topic_keywords = {

        "Array": [
            "array",
            "arrays"
        ],

        "Hash Map": [
            "hashmap",
            "hash map",
            "dictionary"
        ],

        "String": [
            "string",
            "strings"
        ],

        "Linked List": [
            "linked list"
        ],

        "Tree": [
            "tree",
            "binary tree"
        ],

        "Graph": [
            "graph",
            "graphs"
        ],

        "Dynamic Programming": [
            "dynamic programming",
            "dp"
        ],

        "Stack": [
            "stack"
        ],

        "Queue": [
            "queue"
        ],

        "Recursion": [
            "recursion",
            "recursive"
        ],

        "Sorting": [
            "sorting",
            "sort"
        ],

        "Binary Search": [
            "binary search"
        ],

        "Heap": [
            "heap",
            "priority queue"
        ],

        "Greedy": [
            "greedy"
        ],

        "Backtracking": [
            "backtracking"
        ]

    }


    # ========================================================
    # FIND MATCHING TOPICS
    # ========================================================

    for topic_name, keywords in topic_keywords.items():

        for keyword in keywords:

            if keyword in text_lower:

                # Add topic to tags
                if topic_name not in tags:

                    tags.append(topic_name)


                # Use first detected topic as main topic
                if topic is None:

                    topic = topic_name


                break


    # ========================================================
    # DETECT TITLE
    # ========================================================

    lines = [

        line.strip()

        for line in text.splitlines()

        if line.strip()

    ]


    if lines:

        first_line = lines[0]


        # Avoid using very long lines as titles
        if len(first_line) <= 100:

            title = first_line


    # ========================================================
    # RETURN METADATA
    # ========================================================

    return {

        "title": title,

        "topic": topic,

        "difficulty": difficulty,

        "tags": tags

    }


# ============================================================
# CREATE FAISS VECTOR STORE
# ============================================================

def create_vector_store():

    """
    Create FAISS vector database from DSA knowledge files.

    Steps:

        1. Load documents
        2. Split documents into chunks
        3. Generate unique chunk IDs
        4. Extract metadata
        5. Generate embeddings
        6. Create FAISS vector store
        7. Store structured data in PostgreSQL
        8. Link FAISS and PostgreSQL using chunk_id
    """


    # ========================================================
    # STEP 1 - LOAD DOCUMENTS
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 1 - LOADING DSA DOCUMENTS")
    print("=" * 60)


    documents = []


    # --------------------------------------------------------
    # Load every knowledge file
    # --------------------------------------------------------

    for file_name in KNOWLEDGE_FILES:


        # Complete file path

        file_path = os.path.join(

            DOCUMENT_FOLDER,

            file_name

        )


        # ----------------------------------------------------
        # Check file existence
        # ----------------------------------------------------

        if not os.path.exists(file_path):

            raise FileNotFoundError(

                f"Missing RAG file: {file_path}"

            )


        print(
            f"Loading: {file_name}"
        )


        # ----------------------------------------------------
        # Create text loader
        # ----------------------------------------------------

        loader = TextLoader(

            file_path,

            encoding="utf-8"

        )


        # ----------------------------------------------------
        # Load document
        # ----------------------------------------------------

        loaded_documents = loader.load()


        # ----------------------------------------------------
        # Add documents to main list
        # ----------------------------------------------------

        documents.extend(
            loaded_documents
        )


    print(
        f"\nTotal documents loaded: {len(documents)}"
    )


    # ========================================================
    # STEP 2 - CHUNKING
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 2 - CHUNKING DOCUMENTS")
    print("=" * 60)


    # --------------------------------------------------------
    # Character based chunking
    # --------------------------------------------------------

    splitter = CharacterTextSplitter(

        # Maximum characters per chunk
        chunk_size=700,

        # Preserve context between chunks
        chunk_overlap=100

    )


    # --------------------------------------------------------
    # Create chunks
    # --------------------------------------------------------

    chunks = splitter.split_documents(

        documents

    )


    print(
        f"Total chunks created: {len(chunks)}"
    )


    # ========================================================
    # STEP 3 - CREATE CHUNK IDs + METADATA
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 3 - GENERATING CHUNK METADATA")
    print("=" * 60)


    for chunk in chunks:


        # ----------------------------------------------------
        # Generate unique UUID
        # ----------------------------------------------------

        chunk_id = str(
            uuid.uuid4()
        )


        # ----------------------------------------------------
        # Store chunk ID
        #
        # This ID will be shared between:
        #
        # FAISS
        # PostgreSQL
        #
        # ----------------------------------------------------

        chunk.metadata[
            "chunk_id"
        ] = chunk_id


        # ----------------------------------------------------
        # Store chunking method
        # ----------------------------------------------------

        chunk.metadata[
            "chunking_method"
        ] = "character"


        # ----------------------------------------------------
        # Extract DSA metadata
        # ----------------------------------------------------

        metadata = extract_metadata(
            chunk
        )


        # ----------------------------------------------------
        # Add extracted metadata
        # ----------------------------------------------------

        chunk.metadata.update(
            metadata
        )


        # ----------------------------------------------------
        # Store source file
        # ----------------------------------------------------

        source_path = chunk.metadata.get(
            "source",
            ""
        )


        chunk.metadata[
            "source_file"
        ] = os.path.basename(
            source_path
        )


    print(
        "Chunk metadata generated successfully."
    )


    # ========================================================
    # STEP 4 - CREATE EMBEDDINGS
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 4 - GENERATING EMBEDDINGS")
    print("=" * 60)


    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    embeddings = get_embeddings()


    print(
        "Embedding model loaded successfully."
    )


    # ========================================================
    # STEP 5 - CREATE FAISS VECTOR STORE
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 5 - CREATING FAISS VECTOR STORE")
    print("=" * 60)


    # --------------------------------------------------------
    # Convert documents into vectors
    # --------------------------------------------------------

    vector_store = FAISS.from_documents(

        chunks,

        embeddings

    )


    print(
        "FAISS vector store created successfully."
    )


    # ========================================================
    # STEP 6 - SAVE FAISS INDEX
    # ========================================================

    # --------------------------------------------------------
    # Create FAISS directory
    # --------------------------------------------------------

    os.makedirs(

        FAISS_FOLDER,

        exist_ok=True

    )


    # --------------------------------------------------------
    # Save FAISS index locally
    # --------------------------------------------------------

    vector_store.save_local(

        FAISS_FOLDER

    )


    print(
        f"FAISS index saved to: {FAISS_FOLDER}"
    )


    # ========================================================
    # STEP 7 - CREATE POSTGRESQL TABLE
    # ========================================================

    print()
    print("=" * 60)
    print("STEP 6 - POSTGRESQL STORAGE")
    print("=" * 60)


    # --------------------------------------------------------
    # Make sure PostgreSQL table exists
    # --------------------------------------------------------

    create_tables()


    # ========================================================
    # STEP 8 - INSERT CHUNKS INTO POSTGRESQL
    # ========================================================

    linked_count = 0


    for chunk in chunks:


        # ----------------------------------------------------
        # Read metadata
        # ----------------------------------------------------

        chunk_id = chunk.metadata.get(
            "chunk_id"
        )


        title = chunk.metadata.get(

            "title",

            "DSA Knowledge Chunk"

        )


        topic = chunk.metadata.get(
            "topic"
        )


        difficulty = chunk.metadata.get(
            "difficulty"
        )


        tags = chunk.metadata.get(

            "tags",

            []

        )


        source_file = chunk.metadata.get(

            "source_file"

        )


        # ----------------------------------------------------
        # Insert into PostgreSQL
        # ----------------------------------------------------

        insert_problem(

            title=title,

            description=chunk.page_content,

            difficulty=difficulty,

            topic=topic,

            tags=tags,

            source_file=source_file,

            line_reference=None,

            chunk_id=chunk_id

        )


        linked_count += 1


    # ========================================================
    # STEP 9 - DISPLAY LINKING RESULT
    # ========================================================

    print()

    print(
        f"{linked_count} FAISS chunks linked to PostgreSQL."
    )


    print()

    print(
        "FAISS ↔ PostgreSQL linking completed."
    )


    print(
        f"Total chunks: {len(chunks)}"
    )


    # ========================================================
    # RETURN VECTOR DATABASE
    # ========================================================

    return vector_store


# ============================================================
# TEST VECTOR STORE
# ============================================================

if __name__ == "__main__":


    print()

    print("=" * 60)

    print(
        "DSA COACH AI - VECTOR STORAGE TEST"
    )

    print("=" * 60)


    try:


        # ----------------------------------------------------
        # Create FAISS vector database
        # ----------------------------------------------------

        db = create_vector_store()


        # ----------------------------------------------------
        # Test similarity search
        # ----------------------------------------------------

        test_query = (
            "Find two numbers that add up to a target"
        )


        print()

        print(
            "Testing similarity search..."
        )


        results = db.similarity_search(

            test_query,

            k=3

        )


        # ----------------------------------------------------
        # Display search results
        # ----------------------------------------------------

        for index, document in enumerate(

            results,

            start=1

        ):


            print()

            print(
                "=" * 60
            )

            print(
                f"RESULT {index}"
            )

            print(
                "=" * 60
            )


            print(
                f"Source: "
                f"{document.metadata.get('source_file')}"
            )


            print(
                f"Chunk ID: "
                f"{document.metadata.get('chunk_id')}"
            )


            print(
                f"Chunking method: "
                f"{document.metadata.get('chunking_method')}"
            )


            print(
                f"Title: "
                f"{document.metadata.get('title')}"
            )


            print(
                f"Topic: "
                f"{document.metadata.get('topic')}"
            )


            print(
                f"Difficulty: "
                f"{document.metadata.get('difficulty')}"
            )


            print(
                f"Tags: "
                f"{document.metadata.get('tags')}"
            )


            print()

            print(
                "Content:"
            )

            print(
                document.page_content
            )


        # ====================================================
        # FINAL SUCCESS MESSAGE
        # ====================================================

        print()

        print(
            "=" * 60
        )

        print(
            "VECTOR STORAGE TEST COMPLETED"
        )

        print(
            "=" * 60
        )


    except Exception as error:


        # ----------------------------------------------------
        # Display error
        # ----------------------------------------------------

        print()

        print(
            "Vector storage failed."
        )


        print()

        print(
            "Error:"
        )


        print(
            error
        )