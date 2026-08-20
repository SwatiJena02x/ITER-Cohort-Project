from chunking.chunk import Chunk
from database import PostgreSQLConnection


class PostgreSQLVectorStore:
    """
    Stores chunks and embeddings in PostgreSQL
    using pgvector.
    """

    def __init__(self):

        self.db = PostgreSQLConnection()

        self.connection = (
            self.db.get_connection()
        )

    def add_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]]
    ):
        """
        Insert or update document chunks and their
        embeddings in PostgreSQL.
        """

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings "
                "must be equal."
            )

        query = """
            INSERT INTO document_chunks (
                chunk_id,
                content,
                source,
                file_type,
                chunk_index,
                embedding
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            ON CONFLICT (chunk_id)
            DO UPDATE SET
                content = EXCLUDED.content,
                source = EXCLUDED.source,
                file_type = EXCLUDED.file_type,
                chunk_index = EXCLUDED.chunk_index,
                embedding = EXCLUDED.embedding;
        """

        data = []

        for chunk, embedding in zip(
            chunks,
            embeddings
        ):

            data.append(
                (
                    chunk.chunk_id,
                    chunk.text,
                    chunk.metadata.get("source"),
                    chunk.metadata.get("file_type"),
                    chunk.metadata.get("chunk_index"),
                    embedding
                )
            )

        with self.connection.cursor() as cursor:

            cursor.executemany(
                query,
                data
            )

        self.connection.commit()

        print(
            f"Inserted/updated "
            f"{len(chunks)} chunks."
        )

    def count(self) -> int:
        """
        Return the total number of chunks
        stored in PostgreSQL.
        """

        result = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM document_chunks;
            """
        ).fetchone()

        return result[0]

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 3
    ) -> list[dict]:
        """
        Search for the most semantically similar chunks
        using cosine distance through pgvector.
        """

        query = """
            SELECT
                chunk_id,
                content,
                source,
                file_type,
                chunk_index,
                1 - (embedding <=> %s::vector) AS similarity
            FROM document_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    query_embedding,
                    query_embedding,
                    top_k
                )
            )

            rows = cursor.fetchall()

        results = []

        for row in rows:

            results.append(
                {
                    "chunk_id": row[0],
                    "content": row[1],
                    "source": row[2],
                    "file_type": row[3],
                    "chunk_index": row[4],
                    "similarity": float(row[5])
                }
            )

        return results

    def close(self):
        """
        Close the PostgreSQL connection.
        """

        self.db.close()