# ============================================================
# DSA COACH AI - POSTGRESQL DATABASE
# ============================================================
#
# Purpose:
# Store structured DSA information in PostgreSQL.
#
# Task 3:
# 1. Store DSA metadata
# 2. Store FAISS chunk IDs
# 3. Link PostgreSQL records with FAISS records
#
# Shared key:
#     chunk_id
#
# ============================================================


# ------------------------------------------------------------
# Standard Library Imports
# ------------------------------------------------------------

import os


# ------------------------------------------------------------
# PostgreSQL Driver
# ------------------------------------------------------------

import psycopg2

from psycopg2.extras import RealDictCursor


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = os.getenv(
    "POSTGRES_HOST",
    "localhost"
)

DB_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

DB_NAME = os.getenv(
    "POSTGRES_DB",
    "dsa_coach"
)

DB_USER = os.getenv(
    "POSTGRES_USER",
    "postgres"
)

DB_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
    "postgres"
)


# ============================================================
# CREATE DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a PostgreSQL database connection.
    """

    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    return connection


# ============================================================
# CREATE TABLE
# ============================================================

def create_tables():
    """
    Create the DSA problems table.

    The chunk_id column is used as the shared ID
    between PostgreSQL and FAISS.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Create DSA problems table
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dsa_problems (

                problem_id SERIAL PRIMARY KEY,

                title TEXT NOT NULL,

                description TEXT,

                difficulty VARCHAR(30),

                topic VARCHAR(100),

                tags TEXT[],

                source_file TEXT,

                line_reference TEXT,

                chunk_id UUID UNIQUE,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            );
            """
        )

        # Save changes
        connection.commit()

        print(
            "PostgreSQL table created successfully."
        )

    finally:

        cursor.close()

        connection.close()


# ============================================================
# INSERT DSA PROBLEM
# ============================================================

def insert_problem(
    title,
    description=None,
    difficulty=None,
    topic=None,
    tags=None,
    source_file=None,
    line_reference=None,
    chunk_id=None
):
    """
    Insert one DSA problem into PostgreSQL.

    chunk_id is the shared identifier between
    PostgreSQL and FAISS.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO dsa_problems
            (
                title,
                description,
                difficulty,
                topic,
                tags,
                source_file,
                line_reference,
                chunk_id
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            ON CONFLICT (chunk_id)
            DO NOTHING
            RETURNING problem_id;
            """,
            (
                title,
                description,
                difficulty,
                topic,
                tags,
                source_file,
                line_reference,
                chunk_id
            )
        )

        result = cursor.fetchone()

        connection.commit()

        if result:
            return result[0]

        return None

    finally:

        cursor.close()

        connection.close()


# ============================================================
# STORE FAISS CHUNKS IN POSTGRESQL
# ============================================================

def store_chunks_in_postgres(chunks):
    """
    Store metadata of FAISS chunks in PostgreSQL.

    IMPORTANT:
    The chunk_id stored here must be the SAME chunk_id
    stored inside FAISS document metadata.

    This creates the FAISS ↔ PostgreSQL relationship.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        inserted_count = 0

        # ----------------------------------------------------
        # Process every chunk
        # ----------------------------------------------------

        for chunk in chunks:

            metadata = chunk.metadata

            # Get shared chunk ID
            chunk_id = metadata.get("chunk_id")

            # Skip chunks without an ID
            if not chunk_id:
                continue

            # ------------------------------------------------
            # Extract metadata
            # ------------------------------------------------

            source_file = metadata.get(
                "source_file",
                "unknown"
            )

            difficulty = metadata.get(
                "difficulty"
            )

            topic = metadata.get(
                "topic"
            )

            tags = metadata.get(
                "tags",
                []
            )

            line_reference = metadata.get(
                "line_reference"
            )

            # ------------------------------------------------
            # Use first line as title when no title exists
            # ------------------------------------------------

            title = metadata.get(
                "title",
                "DSA Knowledge Chunk"
            )

            # ------------------------------------------------
            # Insert into PostgreSQL
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO dsa_problems
                (
                    title,
                    description,
                    difficulty,
                    topic,
                    tags,
                    source_file,
                    line_reference,
                    chunk_id
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                ON CONFLICT (chunk_id)
                DO NOTHING;
                """,
                (
                    title,
                    chunk.page_content,
                    difficulty,
                    topic,
                    tags,
                    source_file,
                    line_reference,
                    chunk_id
                )
            )

            inserted_count += 1

        # ----------------------------------------------------
        # Save all records
        # ----------------------------------------------------

        connection.commit()

        print(
            f"{inserted_count} FAISS chunks linked to PostgreSQL."
        )

        return inserted_count

    finally:

        cursor.close()

        connection.close()


# ============================================================
# GET ALL PROBLEMS
# ============================================================

def get_all_problems():
    """
    Retrieve all DSA records from PostgreSQL.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            """
            SELECT *
            FROM dsa_problems
            ORDER BY problem_id;
            """
        )

        results = cursor.fetchall()

        return results

    finally:

        cursor.close()

        connection.close()


# ============================================================
# GET PROBLEM BY CHUNK ID
# ============================================================

def get_problem_by_chunk_id(chunk_id):
    """
    Retrieve PostgreSQL information using the shared
    FAISS chunk_id.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            """
            SELECT *
            FROM dsa_problems
            WHERE chunk_id = %s;
            """,
            (chunk_id,)
        )

        result = cursor.fetchone()

        return result

    finally:

        cursor.close()

        connection.close()


# ============================================================
# TEST POSTGRESQL
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 60)
    print("DSA COACH AI - POSTGRESQL TEST")
    print("=" * 60)

    try:

        # ----------------------------------------------------
        # Test connection
        # ----------------------------------------------------

        connection = get_connection()

        print(
            "\nPostgreSQL connection successful!"
        )

        connection.close()

        # ----------------------------------------------------
        # Create required tables
        # ----------------------------------------------------

        create_tables()

        print("\n")
        print("=" * 60)
        print("POSTGRESQL SETUP COMPLETED")
        print("=" * 60)

    except Exception as error:

        print(
            "\nPostgreSQL connection failed."
        )

        print(
            "\nError:"
        )

        print(error)