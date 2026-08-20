# 🛡️ ProctorIQ · AI Proctoring System

## 1. Project Overview
**ProctorIQ** is an AI-assisted exam proctoring platform that analyzes examination snapshots to detect academic malpractice (such as unauthorized mobile phones, reference materials, secondary persons, candidate absence, and face mismatches). It calculates a transparent, deterministic **0–100 risk score** and automatically generates plain-language audit reports with downloadable PDF certificates.

---

## 2. Technologies Used

| Technology | Why It Is Used |
|---|---|
| **FastAPI** | High-performance Python async backend framework for all REST API endpoints. |
| **HTML5, CSS3, JavaScript** | Clean, responsive web UI for Student and Admin portals without heavy frontend frameworks. |
| **Nginx** | Fast reverse proxy and static web server to serve the frontend on port `8080` and route `/api/*` requests. |
| **PostgreSQL & SQLAlchemy** | Relational database and ORM to store student profiles, exam events, and risk reports. |
| **Ultralytics YOLOv8** | Pretrained computer vision model to detect unauthorized objects (cell phones, laptops, books) and multiple persons. |
| **face_recognition & dlib** | Extracts 128-dimensional biometric face embeddings to verify student identity against reference photos. |
| **RapidOCR** | Extracts candidate names and roll numbers from student ID cards using ONNX runtime models. |
| **LangGraph & LangChain** | Coordinates the 7-step AI pipeline (detection → verification → scoring → report generation). |
| **Ollama (LLaMA 3)** | Local LLM used to write natural-language executive summaries for proctoring reports. |
| **FPDF2** | Generates formatted, downloadable PDF incident certificates with risk scores and evidence. |
| **Docker & Docker Compose** | Packages backend, frontend, database, and AI services into containers for easy setup. |

---

## 3. How to Run

### Option A: Using Docker (Recommended)

1. **Clone the repository and enter the directory**:
   ```bash
   git clone https://github.com/your-username/ProctorIQ.git
   cd ProctorIQ
   ```

2. **Create your environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Start all services**:
   ```bash
   docker compose up -d --build
   ```

4. **Open in browser**:
   👉 **[http://localhost:8080](http://localhost:8080)**

---

### Option B: Local Setup (Without Docker)

1. **Create and activate a virtual environment**:
   ```powershell
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   ```bash
   # Linux / macOS
   python3.11 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

4. **Ensure PostgreSQL is running locally**, then create the database:
   ```sql
   CREATE DATABASE proctoring_db;
   ```

5. **Start the application**:
   ```bash
   python run.py
   ```

6. **Access URLs**:
   - **Web UI**: [http://localhost:8080](http://localhost:8080)
   - **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 4. Project Structure

```
ProctorIQ/
├── backend/            # FastAPI app, API routers (auth, students, reports), and schemas
├── frontend/           # HTML/CSS/JS student & admin portals, plus nginx.conf
├── agent/              # 7-node LangGraph proctoring workflow and agent state
├── detection/          # YOLOv8 object detection, face recognition, and RapidOCR modules
├── risk_scoring/       # Deterministic rules and 0-100 risk score calculation logic
├── llm/                # LangChain configuration and Ollama prompt templates
├── database/           # PostgreSQL connection, SQLAlchemy ORM models, and CRUD repository
├── tests/              # Automated pytest test suite (22 tests)
├── data/               # Storage for uploaded student photos and ID cards
├── reports/            # Storage for generated PDF incident reports
├── docker-compose.yml  # Multi-container orchestration (Frontend, Backend, Postgres, Ollama)
├── Dockerfile          # Container build file for the backend
├── requirements.txt    # Pinned Python package dependencies
└── run.py              # Single-command local development launcher
```
