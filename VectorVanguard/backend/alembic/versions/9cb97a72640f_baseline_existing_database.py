"""baseline existing database

Revision ID: 9cb97a72640f
Revises:
Create Date: 2026-08-18 01:06:42.424580

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9cb97a72640f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial database schema."""

    op.create_table(
        "students",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_id",
            name="uq_students_student_id",
        ),
    )

    op.create_index(
        "ix_students_id",
        "students",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_students_student_id",
        "students",
        ["student_id"],
        unique=True,
    )

    op.create_table(
        "exam_sessions",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "exam_name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "ended_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_exam_sessions_id",
        "exam_sessions",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_exam_sessions_student_id",
        "exam_sessions",
        ["student_id"],
        unique=False,
    )

    op.create_table(
        "evidence_records",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "evidence_id",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "image_path",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "ocr_text",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["exam_sessions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "evidence_id",
            name="uq_evidence_id",
        ),
    )

    op.create_index(
        "ix_evidence_records_id",
        "evidence_records",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_evidence_records_evidence_id",
        "evidence_records",
        ["evidence_id"],
        unique=True,
    )

    op.create_index(
        "ix_evidence_records_session_id",
        "evidence_records",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the initial database schema."""

    op.drop_index(
        "ix_evidence_records_session_id",
        table_name="evidence_records",
    )

    op.drop_index(
        "ix_evidence_records_evidence_id",
        table_name="evidence_records",
    )

    op.drop_index(
        "ix_evidence_records_id",
        table_name="evidence_records",
    )

    op.drop_table("evidence_records")

    op.drop_index(
        "ix_exam_sessions_student_id",
        table_name="exam_sessions",
    )

    op.drop_index(
        "ix_exam_sessions_id",
        table_name="exam_sessions",
    )

    op.drop_table("exam_sessions")

    op.drop_index(
        "ix_students_student_id",
        table_name="students",
    )

    op.drop_index(
        "ix_students_id",
        table_name="students",
    )

    op.drop_table("students")