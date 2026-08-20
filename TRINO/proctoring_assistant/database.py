from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, List, Optional

from sqlalchemy import Boolean, Column, Float, MetaData, String, Table, Text, create_engine, desc, or_, select
from sqlalchemy import Boolean, Column, Float, MetaData, String, Table, Text, create_engine, desc, func, inspect, or_, select, text

from utils.schema import EvidenceRecord


class EvidenceDatabase:
    """SQLAlchemy evidence repository with SQLite fallback and PostgreSQL support."""

    def __init__(self, database_url: Optional[str] = None):
        resolved_url = database_url or "sqlite:///data/proctoring.db"
        if resolved_url.startswith("sqlite:///"):
            Path(resolved_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(resolved_url, future=True)
        self.metadata = MetaData()
        self.evidence = Table(
            "evidence",
            self.metadata,
            Column("evidence_id", String(255), primary_key=True),
            Column("student_id", String(255), nullable=False, index=True),
            Column("session_id", String(255), nullable=False, index=True),
            Column("timestamp", String(64), nullable=False, index=True),
            Column("camera", String(255), nullable=False),
            Column("resolution", String(64), nullable=False),
            Column("category", String(255), nullable=False, index=True),
            Column("incident_type", String(255), nullable=False, default=""),
            Column("source_path", Text, nullable=False),
            Column("ocr_text", Text, nullable=False),
            Column("vision_description", Text, nullable=False),
            Column("metadata", Text, nullable=False),
            Column("suspicious", Boolean, nullable=False, default=False),
            Column("risk_score", Float, nullable=False, default=0.0),
        )
        self.metadata.create_all(self.engine)
        self._migrate_existing_schema()

    def _migrate_existing_schema(self) -> None:
        columns = {column["name"] for column in inspect(self.engine).get_columns("evidence")}
        if "incident_type" not in columns:
            with self.engine.begin() as connection:
                connection.execute(text("ALTER TABLE evidence ADD COLUMN incident_type VARCHAR(255) DEFAULT ''"))

    def upsert_records(self, records: Iterable[EvidenceRecord]) -> int:
        count = 0
        with self.engine.begin() as connection:
            for record in records:
                values = self._to_row(record)
                existing = connection.execute(
                    select(self.evidence.c.evidence_id).where(self.evidence.c.evidence_id == record.evidence_id)
                ).first()
                if existing:
                    connection.execute(
                        self.evidence.update()
                        .where(self.evidence.c.evidence_id == record.evidence_id)
                        .values(**values)
                    )
                else:
                    connection.execute(self.evidence.insert().values(**values))
                count += 1
        return count

    def query_records(
        self,
        *,
        student_id: Optional[str] = None,
        session_id: Optional[str] = None,
        category: Optional[str] = None,
        incident_type: Optional[str] = None,
        suspicious: Optional[bool] = None,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
        text_query: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[EvidenceRecord]:
        conditions = []
        if student_id:
            conditions.append(self.evidence.c.student_id == student_id)
        if session_id:
            conditions.append(self.evidence.c.session_id == session_id)
        if category:
            conditions.append(self.evidence.c.category == category)
        if incident_type:
            conditions.append(self.evidence.c.incident_type == incident_type)
        if suspicious is not None:
            conditions.append(self.evidence.c.suspicious == suspicious)
        if start_timestamp:
            conditions.append(self.evidence.c.timestamp >= start_timestamp)
        if end_timestamp:
            conditions.append(self.evidence.c.timestamp <= end_timestamp)
        if start_time:
            conditions.append(func.substr(self.evidence.c.timestamp, 12, 5) >= start_time)
        if end_time:
            conditions.append(func.substr(self.evidence.c.timestamp, 12, 5) <= end_time)
        if text_query:
            pattern = f"%{text_query}%"
            conditions.append(
                or_(
                    self.evidence.c.ocr_text.ilike(pattern),
                    self.evidence.c.vision_description.ilike(pattern),
                    self.evidence.c.category.ilike(pattern),
                    self.evidence.c.incident_type.ilike(pattern),
                )
            )

        statement = select(self.evidence).order_by(desc(self.evidence.c.timestamp))
        if conditions:
            statement = statement.where(*conditions)
        with self.engine.connect() as connection:
            rows = connection.execute(statement).mappings().all()
        return [self._from_row(row) for row in rows]

    def _to_row(self, record: EvidenceRecord) -> dict[str, Any]:
        incident_type = record.incident_type or str(record.metadata.get("incident_type", ""))
        return {
            "evidence_id": record.evidence_id,
            "student_id": record.student_id,
            "session_id": record.session_id,
            "timestamp": record.timestamp,
            "camera": record.camera,
            "resolution": record.resolution,
            "category": record.category,
            "incident_type": incident_type,
            "source_path": record.source_path,
            "ocr_text": record.ocr_text,
            "vision_description": record.vision_description,
            "metadata": json.dumps(record.metadata, default=str),
            "suspicious": bool(record.suspicious),
            "risk_score": float(record.risk_score),
        }

    @staticmethod
    def _from_row(row: Any) -> EvidenceRecord:
        return EvidenceRecord(
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
            incident_type=row["incident_type"] or "",
        )
