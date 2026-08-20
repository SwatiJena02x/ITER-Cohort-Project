from __future__ import annotations

import argparse

from utils.db import StructuredEvidenceDB
from utils.ingestion import demo_evidence_records


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Exam Proctoring Assistant CLI")
    parser.add_argument("--student-id", default="STU102")
    parser.add_argument("--session-id", default="SESSION004")
    parser.add_argument("--category", default="incident")
    args = parser.parse_args()

    db = StructuredEvidenceDB()
    records = demo_evidence_records()
    inserted = db.insert_records(records)
    print(f"Inserted {inserted} evidence records for student {args.student_id} / session {args.session_id}.")


if __name__ == "__main__":
    main()
