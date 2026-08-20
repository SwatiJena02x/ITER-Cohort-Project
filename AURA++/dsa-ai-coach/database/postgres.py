import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector


# Find project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")


class PostgreSQLConnection:
    """
    Handles connection between Python and PostgreSQL.
    """

    def __init__(self):

        self.connection = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        # Register pgvector support
        register_vector(self.connection)

        print("PostgreSQL connection established.")

    def get_connection(self):
        return self.connection

    def close(self):

        self.connection.close()

        print("PostgreSQL connection closed.")