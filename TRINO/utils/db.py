from __future__ import annotations

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from .schema import EvidenceRecord


class StructuredEvidenceDB:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or os.getenv("PROCTOR_DB_PATH", "data/proctoring.db"))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id TEXT PRIMARY KEY,
                    student_id TEXT,
                    session_id TEXT,
                    timestamp TEXT,
                    camera TEXT,
                    resolution TEXT,
                    category TEXT,
                    source_path TEXT,
                    ocr_text TEXT,
                    vision_description TEXT,
                    metadata TEXT,
                    suspicious INTEGER,
                    risk_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_evidence_student_session ON evidence(student_id, session_id)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evidence_category ON evidence(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evidence_timestamp ON evidence(timestamp)")
            conn.commit()

    def insert_records(self, records: List[EvidenceRecord]) -> int:
        saved = 0
        with self._connect() as conn:
            for record in records:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO evidence (
                        evidence_id, student_id, session_id, timestamp, camera, resolution, category,
                        source_path, ocr_text, vision_description, metadata, suspicious, risk_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.evidence_id,
                        record.student_id,
                        record.session_id,
                        record.timestamp,
                        record.camera,
                        record.resolution,
                        record.category,
                        record.source_path,
                        record.ocr_text,
                        record.vision_description,
                        json.dumps(record.metadata, default=str),
                        int(bool(record.suspicious)),
                        float(record.risk_score),
                    ),
                )
                saved += 1
            conn.commit()
        return saved

    def list_records(self, student_id: Optional[str] = None, session_id: Optional[str] = None, category: Optional[str] = None) -> List[EvidenceRecord]:
        query = "SELECT * FROM evidence WHERE 1=1"
        params: List[str] = []
        if student_id:
            query += " AND student_id = ?"
            params.append(student_id)
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY timestamp DESC"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        return [
            EvidenceRecord(
                evidence_id=row["evidence_id"],
                student_id=row["student_id"],
                session_id=row["session_id"],
                timestamp=row["timestamp"],
                camera=row["camera"],
                resolution=row["resolution"],
                category=row["category"],
                source_path=row["source_path"],
                ocr_text=row["ocr_text"],
                vision_description=row["vision_description"],
                metadata=json.loads(row["metadata"] or "{}"),
                suspicious=bool(row["suspicious"]),
                risk_score=float(row["risk_score"] or 0.0),
            )
            for row in rows
        ]

    def search_by_text(self, text: str) -> List[EvidenceRecord]:
        tokens = re.findall(r"[A-Za-z0-9]+", text)
        clauses = []
        params: List[str] = []
        for token in tokens:
            clauses.append("(student_id LIKE ? OR session_id LIKE ? OR category LIKE ? OR ocr_text LIKE ? OR vision_description LIKE ?)")
            pattern = f"%{token}%"
            params.extend([pattern, pattern, pattern, pattern, pattern])
        if not clauses:
            return self.list_records()
        query = "SELECT * FROM evidence WHERE " + " OR ".join(clauses) + " ORDER BY timestamp DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            EvidenceRecord(
                evidence_id=row["evidence_id"],
                student_id=row["student_id"],
                session_id=row["session_id"],
                timestamp=row["timestamp"],
                camera=row["camera"],
                resolution=row["resolution"],
                category=row["category"],
                source_path=row["source_path"],
                ocr_text=row["ocr_text"],
                vision_description=row["vision_description"],
                metadata=json.loads(row["metadata"] or "{}"),
                suspicious=bool(row["suspicious"]),
                risk_score=float(row["risk_score"] or 0.0),
            )
            for row in rows
        ]
