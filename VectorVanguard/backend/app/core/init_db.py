from app.core.database import engine
from app.models.base import Base

# Import all models so SQLAlchemy registers their tables.
from app.models import Student, ExamSession, EvidenceRecord


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")