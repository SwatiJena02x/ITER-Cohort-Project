"""
backend/main.py
------------------
FastAPI application entry point. Starts the backend and wires up all API
routers (auth, admin, students, malpractice, reports).

Run with:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from backend.api import admin, auth, malpractice, reports, students
from database.connection import init_db

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Proctoring Risk Scoring Agent API v2.0 ...")
    try:
        init_db()
        logger.info("Database tables verified/created.")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not initialise database on startup: %s", exc)
    yield


app = FastAPI(
    title="Proctoring Risk Scoring Agent API",
    description=(
        "Backend for the AI-based exam proctoring system. Provides authentication, "
        "student registration, malpractice image upload, AI-based risk analysis, "
        "and report publishing to the student notice board."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# 1. Configure CORS for the HTML frontend & API clients
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(students.router)
app.include_router(malpractice.router)
app.include_router(reports.router)

# 2. Serve uploaded files (ID Cards, Passport Photos, Reports, Data)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
id_cards_dir = os.path.join(data_dir, "id_cards")
passport_dir = os.path.join(data_dir, "passport_photos")

os.makedirs(id_cards_dir, exist_ok=True)
os.makedirs(passport_dir, exist_ok=True)

app.mount("/uploads/id-cards", StaticFiles(directory=id_cards_dir), name="id-cards")
app.mount("/uploads/passport-photos", StaticFiles(directory=passport_dir), name="passport-photos")
app.mount("/data", StaticFiles(directory=data_dir), name="data")

reports_dir = os.path.join(base_dir, "reports", "generated_reports")
os.makedirs(reports_dir, exist_ok=True)
app.mount("/reports", StaticFiles(directory=os.path.join(base_dir, "reports")), name="reports")

frontend_dir = os.path.join(base_dir, "frontend", "html")
if os.path.exists(frontend_dir):
    app.mount("/app", StaticFiles(directory=frontend_dir, html=True), name="frontend_app")


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "proctoring-risk-scoring-agent", "version": "2.0.0"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", "8000")),
        reload=True,
    )
