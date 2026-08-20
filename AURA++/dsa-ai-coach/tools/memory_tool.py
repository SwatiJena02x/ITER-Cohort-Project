import os

import psycopg

from dotenv import load_dotenv


load_dotenv()


class MemoryTool:
    """
    Persistent memory for the DSA Coach.

    Stores two types of memory:

    1. Student progress
       - current problem
       - hints used
       - attempts
       - status
       - last action

    2. Conversation history
       - user messages
       - assistant responses
    """

    def __init__(self):

        self.connection = psycopg.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432")
        )

        print(
            "PostgreSQL memory connection established."
        )

    # ==================================================
    # SAVE / UPSERT STUDENT PROGRESS
    # ==================================================

    def save_progress(
        self,
        session_id: str,
        problem_id: str,
        problem_title: str,
        topic: str,
        difficulty: str,
        hints_used: int = 0,
        attempts: int = 0,
        status: str = "in_progress",
        last_action: str = ""
    ):

        query = """
            INSERT INTO student_progress (
                session_id,
                problem_id,
                problem_title,
                topic,
                difficulty,
                hints_used,
                attempts,
                status,
                last_action
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )

            ON CONFLICT (
                session_id,
                problem_id
            )

            DO UPDATE SET

                problem_title = EXCLUDED.problem_title,

                topic = EXCLUDED.topic,

                difficulty = EXCLUDED.difficulty,

                hints_used = EXCLUDED.hints_used,

                attempts = EXCLUDED.attempts,

                status = EXCLUDED.status,

                last_action = EXCLUDED.last_action,

                updated_at = CURRENT_TIMESTAMP
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    session_id,
                    problem_id,
                    problem_title,
                    topic,
                    difficulty,
                    hints_used,
                    attempts,
                    status,
                    last_action
                )
            )

        self.connection.commit()

    # ==================================================
    # GET STUDENT PROGRESS
    # ==================================================

    def get_progress(
        self,
        session_id: str
    ) -> list[dict]:

        query = """
            SELECT
                id,
                session_id,
                problem_id,
                problem_title,
                topic,
                difficulty,
                hints_used,
                attempts,
                status,
                last_action,
                created_at,
                updated_at
            FROM student_progress

            WHERE session_id = %s

            ORDER BY updated_at DESC
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (session_id,)
            )

            rows = cursor.fetchall()

        results = []

        for row in rows:

            results.append(
                {
                    "id": row[0],
                    "session_id": row[1],
                    "problem_id": row[2],
                    "problem_title": row[3],
                    "topic": row[4],
                    "difficulty": row[5],
                    "hints_used": row[6],
                    "attempts": row[7],
                    "status": row[8],
                    "last_action": row[9],
                    "created_at": row[10],
                    "updated_at": row[11]
                }
            )

        return results

    # ==================================================
    # GET CURRENT PROBLEM
    # ==================================================

    def get_current_problem(
        self,
        session_id: str
    ) -> dict | None:

        query = """
            SELECT
                problem_id,
                problem_title,
                topic,
                difficulty,
                hints_used,
                attempts,
                status,
                last_action

            FROM student_progress

            WHERE session_id = %s
              AND status = 'in_progress'

            ORDER BY updated_at DESC

            LIMIT 1
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (session_id,)
            )

            row = cursor.fetchone()

        if row is None:

            return None

        return {
            "problem_id": row[0],
            "problem_title": row[1],
            "topic": row[2],
            "difficulty": row[3],
            "hints_used": row[4],
            "attempts": row[5],
            "status": row[6],
            "last_action": row[7]
        }

    # ==================================================
    # INCREMENT HINTS
    # ==================================================

    def increment_hints(
        self,
        session_id: str,
        problem_id: str
    ):

        query = """
            UPDATE student_progress

            SET
                hints_used = hints_used + 1,
                last_action = 'requested_hint',
                updated_at = CURRENT_TIMESTAMP

            WHERE
                session_id = %s
                AND problem_id = %s
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    session_id,
                    problem_id
                )
            )

        self.connection.commit()

    # ==================================================
    # INCREMENT ATTEMPTS
    # ==================================================

    def increment_attempts(
        self,
        session_id: str,
        problem_id: str
    ):

        query = """
            UPDATE student_progress

            SET
                attempts = attempts + 1,
                last_action = 'submitted_code',
                updated_at = CURRENT_TIMESTAMP

            WHERE
                session_id = %s
                AND problem_id = %s
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    session_id,
                    problem_id
                )
            )

        self.connection.commit()

    # ==================================================
    # UPDATE STATUS
    # ==================================================

    def update_status(
        self,
        session_id: str,
        problem_id: str,
        status: str
    ):

        query = """
            UPDATE student_progress

            SET
                status = %s,
                updated_at = CURRENT_TIMESTAMP

            WHERE
                session_id = %s
                AND problem_id = %s
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    status,
                    session_id,
                    problem_id
                )
            )

        self.connection.commit()

    # ==================================================
    # SAVE CONVERSATION MESSAGE
    # ==================================================

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):

        query = """
            INSERT INTO conversation_messages (
                session_id,
                role,
                content
            )

            VALUES (
                %s,
                %s,
                %s
            )
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    session_id,
                    role,
                    content
                )
            )

        self.connection.commit()

    # ==================================================
    # GET CONVERSATION HISTORY
    # ==================================================

    def get_conversation(
        self,
        session_id: str,
        limit: int = 10
    ) -> list[dict]:

        query = """
            SELECT
                role,
                content,
                created_at

            FROM conversation_messages

            WHERE session_id = %s

            ORDER BY created_at DESC

            LIMIT %s
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    session_id,
                    limit
                )
            )

            rows = cursor.fetchall()

        # Database gives newest first.
        # Reverse so the agent sees
        # chronological conversation.

        rows.reverse()

        return [
            {
                "role": row[0],
                "content": row[1],
                "created_at": row[2]
            }
            for row in rows
        ]

    # ==================================================
    # CLOSE
    # ==================================================

    def close(self):

        if self.connection:

            self.connection.close()

            print(
                "PostgreSQL memory connection closed."
            )