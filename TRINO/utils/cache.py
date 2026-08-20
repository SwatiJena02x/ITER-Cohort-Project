from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet

from .schema import EvidenceRecord


class LocalEvidenceCache:
    def __init__(self, db_path: str = "local_cache.db", key: str = "exam-proctoring-local-key"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        raw_key = hashlib.sha256(key.encode("utf-8")).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(raw_key[:32]))
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evidence_id TEXT UNIQUE,
                    student_id TEXT,
                    session_id TEXT,
                    timestamp TEXT,
                    payload TEXT,
                    encrypted_payload TEXT,
                    created_at TEXT,
                    synced INTEGER DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS offline_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evidence_id TEXT UNIQUE,
                    queued_at TEXT,
                    payload TEXT,
                    synced INTEGER DEFAULT 0
                )
                """
            )
            conn.commit()

    def _serialize_record(self, record: EvidenceRecord) -> Dict[str, Any]:
        return {
            "evidence_id": record.evidence_id,
            "student_id": record.student_id,
            "session_id": record.session_id,
            "timestamp": record.timestamp,
            "camera": record.camera,
            "resolution": record.resolution,
            "category": record.category,
            "source_path": record.source_path,
            "ocr_text": record.ocr_text,
            "vision_description": record.vision_description,
            "metadata": record.metadata,
            "suspicious": record.suspicious,
            "risk_score": record.risk_score,
        }

    def store_snapshot(self, record: EvidenceRecord) -> bool:
        payload = self._serialize_record(record)
        encrypted_payload = self.cipher.encrypt(json.dumps(payload, default=str).encode("utf-8"))
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO snapshots (
                    evidence_id, student_id, session_id, timestamp, payload, encrypted_payload, created_at, synced
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    record.evidence_id,
                    record.student_id,
                    record.session_id,
                    record.timestamp,
                    json.dumps(payload, default=str),
                    encrypted_payload.decode("utf-8"),
                    created_at,
                ),
            )
            conn.commit()
        return True

    def enqueue_for_offline_sync(self, record: EvidenceRecord) -> bool:
        payload = json.dumps(self._serialize_record(record), default=str)
        queued_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO offline_queue (evidence_id, queued_at, payload, synced) VALUES (?, ?, ?, 0)",
                (record.evidence_id, queued_at, payload),
            )
            conn.commit()
        return True

    def get_pending_queue(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT evidence_id, queued_at, payload FROM offline_queue WHERE synced = 0 ORDER BY id ASC"
            ).fetchall()
        return [
            {"evidence_id": evidence_id, "queued_at": queued_at, "payload": json.loads(payload)}
            for evidence_id, queued_at, payload in rows
        ]

    def get_latest_snapshot(self, student_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload FROM snapshots WHERE student_id = ? ORDER BY id DESC LIMIT 1",
                (student_id,),
            ).fetchone()
        if not row:
            return None
        return json.loads(row[0])

    def mark_synced(self, evidence_id: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE snapshots SET synced = 1 WHERE evidence_id = ?", (evidence_id,))
            conn.execute("UPDATE offline_queue SET synced = 1 WHERE evidence_id = ?", (evidence_id,))
            conn.commit()
