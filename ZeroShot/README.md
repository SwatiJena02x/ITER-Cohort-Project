# Offline Proctoring Behavioral Analysis RAG

**Status: Prototype** — architecture and agents below are tentative design, not a finished build.

## Description

An offline, post test system that processes exam images through a cost-efficient CV pipeline (detection, tracking, clustering) instead of sending every frame to an LLM. The entire ingestion-to-event pipeline runs **fully automatically, with no human step in the loop**. The only human interaction is when it comes to RAG i.e at query time: a user asks a question and gets an answer with linked evidence images.

## Motivation

Sending every proctoring frame to a vision LLM is expensive and slow. Most frames are redundant. A cheap CV pipeline can filter, cluster and pre select the frames worth analyzing, so LLM calls are reserved for query time reasoning and rare escalations so not for touching every image.

## Goals

- Fully automated pipeline: images in, queryable events + evidence out.
- Mostly offline, minimal LLM/API calls and RAG context size.

## Key Features (tentative)

- Automatic batch ingestion, validation, dedup.
- Automatic person/object detection, tracking, pose features.
- Automatic clustering + representative frame selection.
- Automatic temporal event generation.
- Hybrid (keyword + vector + metadata) retrieval.
- Conversational RAG chat with memory.
- Every answer traces back to source evidence images.
- Optional cloud LLM escalation only for ambiguous frames.

## Tentative Architecture

```

TEST IMAGES → INGESTION → Duplicate Filter + Change Detection
   → YOLO (Person / Objects / Pose) → Tracking → Behavior Features
   → Clustering → Temporal Events → [SQLite + FAISS + Image Index]
   → Hybrid Retrieval → Reranking → Llama 3.2:1b → ( Gemini for better result)
   → Answer + Evidence Images (Streamlit)

```

All stages above run automatically end-to-end. The user only enters the picture at "Answer + Evidence Images."

## Tech Stack

| Layer | Tools |
| --- | --- |
| API / UI | FastAPI, Streamlit |
| Detection | YOLO / Ultralytics |
| Pose | YOLO Pose, MediaPipe |
| Tracking | ByteTrack / BoT-SORT |
| Preprocessing | OpenCV |
| Dedup | pHash, SHA256 |
| Embeddings | CLIP/SigLIP-style (image), Sentence Transformers (text) |
| Clustering | KNN |
| Vector Search | FAISS (local), Pinecone (if favours my i3 system speed) |
| Metadata / Events / Memory | SQLite (+ FTS/BM25) |
| Orchestration | LangChain (RAG), CrewAI (agents) |
| Local LLM | Ollama + Llama 3.2:1b |
| Escalation | Gemini API ( ambiguous cases only) |

## RAG / Query Flow

1. User asks a question.
2. Llama 3.2:1b rewrites/routes the query.
3. Hybrid retrieval (keyword + vector + metadata) pulls candidate events.
4. Rerank → Llama 3.2:1b composes the answer.
5. Evidence images for cited events are returned alongside the answer.
6. Gemini escalation for a single ambiguous fram or event, not the default path.

## Agent Architecture (tentative)

CrewAI used only for high level orchestration; agents call deterministic CV/Python tools, not per image LLM calls.

- Ingestion Agent · Vision/Detection Agent · Behavioral/Event Agent · Retrieval Agent · Investigation/Query Agent · Answer Agent

## Example Questions

- Who showed potentially suspicious behavior?
- When did RAM show repeated side-looking?
- What happened around 10:41?
- Show me the evidence for RAM.
- Compare RAM's events with AJCKEY's events.
- Was a phone or paper visible?

## Scope

Batch ingestion · dedup/validation · YOLO detection · basic tracking · pose features · clustering · representative-frame selection · event generation · SQLite storage · FAISS retrieval · hybrid search · conversational RAG with memory · Llama 3.2:1b routing · Streamlit chat UI · optional Gemini fallback.

## Out of Scope

Production deployment · auth · distributed processing · real-time proctoring · perfect face recognition · definitive cheating detection · multi camera sync · production-grade training · full Pinecone dependency.

## Prototype Status

Early stage
