from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class EvidenceRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "data/evidence.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

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
            conn.execute("CREATE INDEX IF NOT EXISTS idx_student_session ON evidence(student_id, session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON evidence(category)")
            conn.commit()

    def insert_record(self, record: Dict[str, Any]) -> str:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO evidence (
                    evidence_id, student_id, session_id, timestamp, camera, resolution, category,
                    source_path, ocr_text, vision_description, metadata, suspicious, risk_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["evidence_id"],
                    record.get("student_id", ""),
                    record.get("session_id", ""),
                    record.get("timestamp", ""),
                    record.get("camera", ""),
                    record.get("resolution", ""),
                    record.get("category", ""),
                    record.get("source_path", ""),
                    record.get("ocr_text", ""),
                    record.get("vision_description", ""),
                    json.dumps(record.get("metadata", {}), default=str),
                    int(bool(record.get("suspicious", 0))),
                    float(record.get("risk_score", 0.0)),
                ),
            )
            conn.commit()
        return record["evidence_id"]

    def fetch_by_student_session(self, student_id: str, session_id: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM evidence WHERE student_id = ? AND session_id = ? ORDER BY timestamp DESC",
                (student_id, session_id),
            ).fetchall()
        return [
            {
                "evidence_id": row["evidence_id"],
                "student_id": row["student_id"],
                "session_id": row["session_id"],
                "timestamp": row["timestamp"],
                "camera": row["camera"],
                "resolution": row["resolution"],
                "category": row["category"],
                "source_path": row["source_path"],
                "ocr_text": row["ocr_text"],
                "vision_description": row["vision_description"],
                "metadata": json.loads(row["metadata"] or "{}"),
                "suspicious": bool(row["suspicious"]),
                "risk_score": float(row["risk_score"] or 0.0),
            }
            for row in rows
        ]

    def fetch_by_query(self, query: str) -> List[Dict[str, Any]]:
        query_text = f"%{query}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM evidence
                WHERE student_id LIKE ? OR session_id LIKE ? OR category LIKE ? OR ocr_text LIKE ? OR vision_description LIKE ?
                ORDER BY timestamp DESC
                """,
                (query_text, query_text, query_text, query_text, query_text),
            ).fetchall()
        return [
            {
                "evidence_id": row["evidence_id"],
                "student_id": row["student_id"],
                "session_id": row["session_id"],
                "timestamp": row["timestamp"],
                "camera": row["camera"],
                "resolution": row["resolution"],
                "category": row["category"],
                "source_path": row["source_path"],
                "ocr_text": row["ocr_text"],
                "vision_description": row["vision_description"],
                "metadata": json.loads(row["metadata"] or "{}"),
                "suspicious": bool(row["suspicious"]),
                "risk_score": float(row["risk_score"] or 0.0),
            }
            for row in rows
        ]
