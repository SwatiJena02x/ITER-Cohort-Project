# AI Exam Proctoring Assistant 🚀

A **Privacy-First**, **Human-in-the-Loop** examination evidence analysis system powered by a novel **Few-Shot Visual RAG Architecture**. 

Instead of relying on rigid heuristics or streaming private student video to external APIs, this system builds a searchable, semantic timeline of an exam entirely on local hardware, enabling human investigators to query exam evidence using natural language.

---

## 🏆 Hackathon Pitch: The Problem & The Solution

**The Problem:**
Traditional online proctoring is broken. It relies on arbitrary flags (which cause massive anxiety and false positives for students) or it requires human proctors to manually scrub through hours of video. Furthermore, streaming private bedrooms to the cloud raises massive ethical and privacy concerns.

**Our Solution:**
We built a locally-run AI assistant that **never automatically fails a student**. Instead, it acts as a semantic search engine for the investigator. 

### How it Works (The Visual RAG Architecture)
Our architecture is split into two innovative pipelines:

#### 1. The Reference Database (Data Ingestion)
Instead of hardcoding rules like *"if motion > X then cheat"*, we seeded a **ChromaDB Vector Database** with descriptions of known cheating behaviors (e.g., *"Student is looking away from the screen"*, *"A mobile phone is visible"*). These textual descriptions are converted into embeddings, forming our semantic baseline for malpractice.

#### 2. The Video Retrieval Pipeline
1. When a student's exam video is uploaded, the system extracts frames periodically.
2. It uses local computer vision (OpenCV) and OCR (Tesseract) to generate a **raw textual description** of what is happening in that specific frame.
3. This generated description is embedded and run through a **Cosine Similarity Search** against our Reference Database.
4. If the frame's description is highly similar to a known cheating embedding, the timestamp is flagged.

#### 3. Agentic Investigation
The human investigator can type natural language queries like:
> *"Show me where the student looked at a phone."*

The system searches the flagged evidence, retrieves the exact timestamps, and passes the context to a **Local LLM (Ollama - Llama 3.1)** to generate a grounded, natural-language incident report.

---

## 🛠️ Tech Stack
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Frontend / Dashboard**: Streamlit
- **AI & RAG Orchestration**: LangChain, LangGraph
- **Vector Database**: ChromaDB (Semantic Search)
- **Relational Database**: SQLite / SQLAlchemy (Structured Search)
- **Local LLM**: Ollama (Llama 3)
- **Computer Vision & OCR**: OpenCV, PyTesseract

---

## 💻 How to Run Locally

### Prerequisites
1. Python 3.11+
2. Tesseract-OCR installed on your system (and added to your PATH).
3. [Optional but recommended] Ollama installed locally with the `llama3.1` model downloaded (`ollama run llama3.1`).

### Setup Instructions
1. Navigate to the project directory:
   ```bash
   cd "d:/GenAI TP/proto"
   ```
2. Activate the virtual environment:
   ```bash
   .\.venv\Scripts\activate
   ```
3. Start the Backend API:
   ```bash
   python -m uvicorn proctoring_assistant.api:app --host 127.0.0.1 --port 8000
   ```
4. Open a second terminal and start the Investigator UI:
   ```bash
   python -m streamlit run streamlit_app.py
   ```
5. Navigate to `http://localhost:8501` in your browser!

---

## 🔍 Demo Guide for Judges
1. **Load Data:** Click the `Load demo evidence` button in the UI, or upload a 30-second video of yourself simulating a test.
2. **Timeline Review:** Show the **Evidence Timeline** tab where the AI has automatically plotted a risk graph based on its visual description matching. Expand the flagged chunks to see the exact *Reference Pattern* it matched!
3. **Agentic Investigation:** Switch to the **Investigation** tab. Type a query like `"Find phone-related suspicious evidence"`.
4. **Local LLM Generation:** The system will dynamically route the query (Semantic vs. SQL), retrieve the chunks, and generate a final human-readable report summarizing the incident.

---

*Built for privacy. Built for fairness. Built to assist humans, not replace them.*
