import os

from dotenv import load_dotenv
import psycopg
from pgvector.psycopg import register_vector

from sentence_transformers import SentenceTransformer

from rag.ingest import build_documents


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "dsa_coach_tree")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# EMBEDDING MODEL
# ============================================================

_model = None


def get_model():

    global _model

    if _model is None:

        print(
            f"Loading embedding model: {MODEL_NAME}"
        )

        _model = SentenceTransformer(
            MODEL_NAME
        )

    return _model


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    if not DB_PASSWORD:
        raise ValueError(
            "DB_PASSWORD is not set in the .env file."
        )

    connection = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    register_vector(connection)

    return connection


# ============================================================
# CREATE TABLE
# ============================================================

def create_table():

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tree_documents (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    source TEXT,
                    chunk_index INTEGER,
                    embedding vector(384)
                );
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                tree_documents_embedding_hnsw
                ON tree_documents
                USING hnsw (embedding vector_cosine_ops);
                """
            )

        connection.commit()

        print(
            "PostgreSQL pgvector table is ready."
        )

    finally:

        connection.close()


# ============================================================
# EMBEDDING
# ============================================================

def embed_texts(texts):

    model = get_model()

    vectors = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    return vectors


# ============================================================
# BUILD PGVECTOR DATABASE
# ============================================================

def build_and_save_index(
    kb_root="knowledge_base"
):

    print()
    print("=" * 70)
    print("BUILDING PGVECTOR RAG DATABASE")
    print("=" * 70)

    # --------------------------------------------------------
    # Create database table
    # --------------------------------------------------------

    create_table()

    # --------------------------------------------------------
    # Ingest documents
    # --------------------------------------------------------

    print()
    print("STEP 1: Ingesting and chunking...")

    documents = build_documents(
        kb_root
    )

    print(
        f"Chunks created: {len(documents)}"
    )

    if not documents:

        print(
            "No documents found."
        )

        return

    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    print()
    print(
        "STEP 2: Generating embeddings..."
    )

    texts = [
        document["text"]
        for document in documents
    ]

    vectors = embed_texts(
        texts
    )

    print(
        "Embedding shape:",
        vectors.shape
    )

    # --------------------------------------------------------
    # Insert into PostgreSQL
    # --------------------------------------------------------

    print()
    print(
        "STEP 3: Storing embeddings in PostgreSQL..."
    )

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            # Remove old RAG documents
            cursor.execute(
                "DELETE FROM tree_documents"
            )

            for document, vector in zip(
                documents,
                vectors
            ):

                cursor.execute(
                    """
                    INSERT INTO tree_documents
                    (
                        id,
                        content,
                        source,
                        chunk_index,
                        embedding
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id)
                    DO UPDATE SET
                        content = EXCLUDED.content,
                        source = EXCLUDED.source,
                        chunk_index = EXCLUDED.chunk_index,
                        embedding = EXCLUDED.embedding;
                    """,
                    (
                        document["id"],
                        document["text"],
                        document["source"],
                        document["chunk_index"],
                        vector
                    )
                )

        connection.commit()

    finally:

        connection.close()

    print()
    print("=" * 70)
    print("PGVECTOR RAG DATABASE CREATED SUCCESSFULLY")
    print("=" * 70)

    print(
        f"Total chunks stored: {len(documents)}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    build_and_save_index()