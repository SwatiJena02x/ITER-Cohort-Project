# AI Exam Proctoring Assistant
### Scope and Implementation Plan

**Team Name:** Trino

**Submitted by:** Ayush Sinha, Sai Kiran Mohanty, Aditya Kumar Das

**Project Type:** RAG-based Examination Evidence Analysis System

---

## 1. Project Overview

Exams conducted online or in a computer-based setting generate a huge amount of visual evidence — webcam frames, hall snapshots, screen recordings, ID cards, and incident screenshots. Going through all of this manually to catch malpractice is slow and doesn't scale well, especially for large batches of students.

This project builds an **AI Exam Proctoring Assistant** — a Retrieval-Augmented Generation (RAG) system that takes image-based exam evidence, processes it using OCR and (optionally) vision-based captioning, and stores the extracted information so an investigator can search it using plain natural language instead of digging through folders of images or writing SQL by hand.

The goal isn't to build a system that decides "this student cheated." It's to build something that surfaces the *right* evidence quickly, with timestamps and context, so a human examiner can make the final call.

---

## 2. Scope of the Project

### 2.1 What the system will do

- Ingest image evidence (JPEG/JPG/PNG/GIF) — webcam captures, hall snapshots, screen-recording frames, ID documents, incident screenshots
- Monitor running processes on the exam machine and flag unauthorized or suspicious applications
- Detect whether the exam is being taken inside a virtual machine (VM detection), since VMs are a common way to bypass proctoring controls
- Extract embedded text using OCR (Tesseract)
- Optionally generate a semantic description of the image using a vision/captioning model, since OCR alone can't describe objects, posture, or activity
- Attach metadata to every piece of evidence — student ID, session ID, timestamp, camera source, resolution, category
- Represent each processed image as a LangChain `Document` (text + description + metadata)
- Split the extracted content into chunks and generate embeddings
- Store semantic data in a vector database (Chroma / PGVector) and structured data in PostgreSQL, linked by a common `evidence_id`
- Let a LangChain agent decide, per query, whether to run semantic search, SQL search, or a hybrid of both
- Apply Top-K retrieval followed by reranking to surface the most relevant evidence
- Feed the reranked evidence into an LLM through a RAG pipeline to generate a grounded, evidence-backed answer for the investigator
- Store every processed result — including exam progress like questions attempted, answers given, and questions remaining, each tagged with a timestamp — in encrypted form in a local cache DB as full-snapshot chunks, and sync that cache to the server periodically, with an offline queue so nothing is lost if the internet drops

### 2.2 What's in scope for this phase

| Included | Not included (this phase) |
|---|---|
| Static image evidence (frames, screenshots, ID docs) | Live video stream processing |
| OCR + optional captioning | Full object/pose detection models |
| Semantic + structured + hybrid retrieval | Full real-time video monitoring during the exam |
| Process monitoring + VM detection | Kernel-level anti-cheat / rootkit-style monitoring |
| Human-reviewed recommendations | Automated disciplinary decisions |
| Single vector DB + PostgreSQL | Multi-modal embeddings (image+text jointly) |

### 2.3 Target users

Examination investigators / proctoring staff who need to review flagged sessions after the fact and ask questions like "show me anything involving a phone for STU102 during SESSION004" instead of scrolling through hundreds of screenshots.

---

## 3. System Design (High Level)

```
Exam Images → OCR + Vision Captioning → Metadata Extraction
     → Process Monitoring + VM Detection
     → LangChain Document → Chunking → Embeddings
     → [Vector DB]  +  [PostgreSQL]  (linked by evidence_id)
     → Encrypted Local Cache (full snapshot chunks)
     → Internet available? → Yes: Sync to Server (periodic)
                            → No: Hold in Offline Queue → Sequential Upload once online
     → User Query → Agent picks strategy (semantic / SQL / hybrid)
     → Top-K → Reranker → RAG context → LLM → Grounded response
```

Two databases are used on purpose:
- **Vector DB** is good at "what's semantically similar to this?" — e.g. finding a phone even if the word "phone" was never typed anywhere.
- **PostgreSQL** is good at "give me exact records matching these conditions" — e.g. all incidents for STU102 in SESSION004.

The agent's job is to figure out which one (or both) a given question actually needs.

---

## 4. Implementation Plan

I'm breaking this into phases so I can build and test incrementally rather than trying to wire everything together at once.

### Phase 1 — Setup & Image Ingestion
- Set up Python environment, repo structure, `.env` config with `python-dotenv`
- Build the image loader for JPEG/JPG/PNG/GIF using Pillow/OpenCV
- Wrap loading into a LangChain-compatible loader
- Test with a small sample batch of dummy exam images

### Phase 2 — OCR & Vision Processing
- Integrate Tesseract OCR to pull text (student ID, session ID, timestamp) off images
- Add an optional vision/captioning step for images with no embedded text
- Compare OCR output quality across a few sample images and note failure cases (blurry frames, bad lighting)

### Phase 3 — Process Monitoring & VM Detection
- Build a lightweight process monitor that logs running applications during the exam session
- Flag known unauthorized applications (e.g. screen-sharing tools, messaging apps, remote-access software) against a configurable watchlist
- Add VM/sandbox detection checks to flag if the exam is being attempted inside a virtual machine
- Feed these flags into the evidence pipeline as their own incident category, alongside image-based evidence

### Phase 4 — Document & Metadata Layer
- Define the metadata schema (evidence_id, student_id, session_id, timestamp, camera, resolution, category)
- Combine OCR text + vision description + metadata into LangChain `Document` objects
- Write a small script to validate that every document has the required metadata fields before it moves further down the pipeline

### Phase 5 — Chunking Experiments
- Try three different chunking strategies (e.g. fixed-size, recursive character split, semantic/sentence-based split)
- Compare them on: number of chunks produced, whether context stays intact, and retrieval relevance
- Pick the best-performing one for the actual pipeline and document why

### Phase 6 — Embeddings & Storage
- Generate embeddings for the chunks using a LangChain embedding wrapper
- Set up Chroma (or PGVector) for vector storage
- Set up the PostgreSQL schema for structured evidence records
- Link both stores using `evidence_id` as the shared key

### Phase 7 — Retrieval & Agent Routing
- Implement semantic search (vector DB), SQL search (PostgreSQL), and hybrid search
- Build the LangChain agent that reads a user's query and decides which retrieval path to use
- Test with a mix of semantic, structured, and hybrid example queries to check routing accuracy

### Phase 8 — Top-K, Reranking & RAG
- Add Top-K limiting on retrieved results
- Add a reranking step (cross-encoder or similar) to reorder by actual relevance
- Wire the reranked evidence into the RAG prompt and connect it to the LLM
- Check that generated answers actually reference the retrieved evidence and don't make things up

### Phase 9 — Encrypted Caching & Offline Sync
- Store every processed evidence result (OCR text, vision description, metadata, RAG-ready chunks) as a full-snapshot chunk in a local cache DB, encrypted at rest
- Each snapshot also captures exam progress at that point in time — questions attempted, answers given so far, and questions remaining — tagged with a timestamp
- Build a background sync job that periodically pushes cached snapshots to the server
- Add a queue data structure to hold snapshots locally when there's no internet connection, so nothing gets lost
- When connectivity comes back, drain the queue and upload the pending snapshots to the server sequentially (FIFO), then clear them from the local queue once confirmed

### Phase 10 — Interface & Testing
- Build a basic Streamlit (or React) front end so an investigator can type a query and see results with evidence, timestamps, and metadata
- Backend via FastAPI
- Run end-to-end tests: ingest sample images → query → verify the right evidence comes back
- Document known limitations (OCR errors, false positives, retrieval misses)

### Phase 11 — Report & Submission
- Write up evaluation results (OCR accuracy, chunking comparison, retrieval Top-K performance, reranking impact)
- Final cleanup, README, demo screenshots

---

## 5. Tech Stack

| Component | Tool |
|---|---|
| Language | Python |
| RAG Framework | LangChain |
| Image Processing | Pillow / OpenCV |
| OCR | Tesseract |
| Vector DB | Chroma / PGVector |
| Relational DB | PostgreSQL |
| Backend | FastAPI |
| Frontend | Streamlit / React |
| Reranking | Cross-encoder model |
| Local Cache / Offline Queue | Encrypted local DB (e.g. SQLite with encryption) + queue data structure for offline sync |

---

## 6. Evaluation Plan

- **OCR accuracy** — check if student ID / session ID / timestamp come out correctly on a sample set
- **Chunking comparison** — measure chunk count, coherence, and retrieval quality across the three strategies tried
- **Retrieval quality** — check if relevant evidence shows up in Top-1 / Top-3 / Top-5
- **Reranking impact** — compare rankings before vs. after reranking
- **RAG output quality** — check that generated answers are grounded in retrieved evidence and don't hallucinate

---

## 7. Limitations to Keep in Mind

- OCR can fail on blurry or low-quality images
- The vision model can misread objects/activities — this is why the system only *recommends review*, it doesn't auto-flag someone as guilty
- Retrieval quality depends heavily on chunking and embedding choices
- Exam footage is sensitive personal data, so storage and access need to be handled carefully (local processing where possible, restricted DB access, env vars for credentials)

---

## 8. Future Work

- Extend to video by extracting frames instead of relying only on static images
- Add proper object/person/pose detection instead of relying on vision captioning alone
- Move toward multimodal embeddings instead of converting everything to text first
- Adapt the pipeline for near real-time monitoring
- Build a proper investigator dashboard with timeline view and review status tracking
