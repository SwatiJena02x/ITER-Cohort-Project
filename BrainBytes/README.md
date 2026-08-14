# 🧠 FatigueSense --- AI-Powered Fatigue Detection System

### Team: BrainBytes

### Gen AI --- ITER Cohort Project

FatigueSense is an AI-powered, agent-based fatigue detection system
designed to analyze fatigue-related visual indicators from uploaded
images and generate a fatigue score, risk level, and grounded
recommendations.

The system combines **Computer Vision, Agentic AI, RAG
(Retrieval-Augmented Generation), Hybrid Search, Vector Embeddings,
Memory, and SQL/NoSQL databases** into an end-to-end application.

------------------------------------------------------------------------

## 🚀 Project Overview

Fatigue can affect concentration, alertness, productivity, and safety.
FatigueSense aims to provide an intelligent system that analyzes visual
fatigue indicators and uses relevant reference knowledge to produce
grounded recommendations.

The system accepts common image formats including:

-   JPG
-   JPEG
-   PNG
-   WebP
-   HEIC
-   Other supported formats

Uploaded images are validated and normalized before Computer Vision
processing.

The system can provide:

-   Fatigue Score
-   Fatigue Risk Level
-   Detected Fatigue Indicators
-   Relevant Retrieved Context
-   AI-generated Recommendations
-   Historical Fatigue Results

> **Testing constraint:** Due to memory limitations, the project uses
> **3--4 test images** to demonstrate and validate the pipeline.

------------------------------------------------------------------------

# 🎯 Objectives

1.  Detect visual indicators associated with fatigue.
2.  Support multiple common image formats.
3.  Normalize different image formats before processing.
4.  Use specialized agents for different tasks.
5.  Build a complete RAG pipeline.
6.  Implement and compare three chunking techniques.
7.  Generate and store document embeddings.
8.  Implement semantic search.
9.  Implement BM25 keyword search.
10. Implement hybrid search.
11. Ground recommendations using retrieved reference knowledge.
12. Store structured and flexible data using MySQL and NoSQL.
13. Maintain short-term and long-term memory.
14. Provide a React-based dashboard.
15. Build an end-to-end agent orchestration workflow.

------------------------------------------------------------------------

# 🏗️ System Architecture

``` text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │ React Frontend  │
                  │    Member C     │
                  └────────┬────────┘
                           │
                     Image Upload
                           │
                 JPG / JPEG / PNG /
                    WebP / HEIC
                           │
                           ▼
                  ┌─────────────────┐
                  │     FastAPI     │
                  │     Backend     │
                  └────────┬────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Agent Orchestrator  │
                │      Member D       │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │ Image Analysis Agent│
                │      Member A       │
                └─────────┬───────────┘
                          │
                     CV Features
                          │
                          ▼
                ┌─────────────────────┐
                │     RAG Pipeline    │
                │      Member B       │
                └─────────┬───────────┘
                          │
                 PDF / JSON / TXT
                          │
                          ▼
                  Document Loading
                          │
                          ▼
                Text Preprocessing
                          │
                          ▼
               ┌────────────────────┐
               │ 3 Chunking Methods │
               │                    │
               │ Fixed-size         │
               │ Recursive          │
               │ Sentence-window    │
               └─────────┬──────────┘
                         │
                  Best Chunking
                         │
                         ▼
                Embedding Generation
                         │
                 ┌───────┴────────┐
                 ▼                ▼
          Semantic Search     BM25 Search
                 │                │
                 └───────┬────────┘
                         ▼
                   Hybrid Search
                         │
                         ▼
                     Re-ranking
                         │
                         ▼
                 Relevant Context
                         │
                         ▼
              Recommendation Agent
                         │
                         ▼
                  Fatigue Result
                         │
                         ▼
                 Memory Management
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
             MySQL              NoSQL
          Structured Data     Flexible Data
               │                   │
               └─────────┬─────────┘
                         ▼
                    FastAPI Response
                         │
                         ▼
                  React Dashboard
```

------------------------------------------------------------------------

# 🤖 Agent Architecture

## 1. Image Analysis Agent --- Member A

Responsible for extracting fatigue-related visual features from uploaded
images.

Possible indicators include:

-   Eye closure
-   Eye aspect ratio
-   Blink-related indicators
-   Yawning indicators
-   Facial landmarks
-   Other facial appearance features

## 2. Fatigue Scoring Agent --- Member A

Uses extracted features to estimate:

``` text
Fatigue Score: 0–100
```

and classify the result into risk levels such as:

``` text
Low
Medium
High
```

## 3. RAG Retrieval Component --- Member B

Retrieves relevant information from the reference knowledge base using:

-   Semantic Search
-   BM25 Keyword Search
-   Hybrid Search
-   Re-ranking

## 4. Recommendation Agent

Uses fatigue analysis and retrieved context to generate grounded
recommendations.

## 5. Agent Orchestrator --- Member D

Coordinates the complete workflow and manages communication between
agents.

------------------------------------------------------------------------

# 📚 RAG Pipeline

The RAG component follows these stages:

``` text
Reference Documents
        │
        ▼
Document Loading
        │
        ▼
Document Parsing
        │
        ▼
Text Preprocessing
        │
        ▼
Chunking
        │
        ▼
Embedding Generation
        │
        ▼
Storage
        │
        ├───────────────┐
        ▼               ▼
Vector Search       Keyword Search
        │               │
        │              BM25
        │               │
        └───────┬───────┘
                ▼
          Hybrid Search
                │
                ▼
            Re-ranking
                │
                ▼
        Relevant Context
                │
                ▼
       Recommendation Agent
```

## Supported Reference Documents

The RAG system is designed to process:

### PDF

-   Fatigue guidelines
-   Sleep research
-   Scientific references
-   Fatigue-related reports

### JSON

-   Behavioral data
-   Fatigue-related structured information
-   Reference datasets

### TXT

-   Fatigue notes
-   Reference information
-   Guidelines

------------------------------------------------------------------------

# ✂️ Chunking Strategies

Three chunking approaches are implemented and compared.

## 1. Fixed-Size Chunking

Documents are divided into chunks using a fixed character/token size.

**Advantages** - Simple - Fast - Easy to implement

**Limitations** - Can break semantic meaning - May split related
information

## 2. Recursive Chunking

Documents are recursively divided using logical separators while
attempting to preserve meaningful sections.

**Advantages** - Better semantic preservation - Suitable for structured
documents - Flexible

## 3. Sentence-Window Chunking

A relevant sentence is retrieved along with surrounding sentences to
preserve context.

**Advantages** - Better contextual understanding - Useful for factual
retrieval - Reduces loss of surrounding information

### Chunking Comparison

The approaches are evaluated using:

-   Retrieval relevance
-   Context preservation
-   Chunk size
-   Search accuracy
-   Processing efficiency
-   Answer quality

The best-performing approach will be selected for the final RAG
pipeline.

------------------------------------------------------------------------

# 🔍 Retrieval System

## Semantic Search

Semantic search uses vector embeddings to find conceptually similar
chunks.

``` text
Query
  ↓
Embedding
  ↓
Vector Similarity
  ↓
Relevant Chunks
```

## BM25 Keyword Search

BM25 retrieves information based on keyword relevance and is useful when
exact terms matter.

## 🔀 Hybrid Search

FatigueSense combines semantic and keyword retrieval:

``` text
Semantic Search
       +
BM25 Keyword Search
       ↓
Hybrid Search
       ↓
Re-ranking
       ↓
Final Relevant Context
```

This combines semantic understanding with exact keyword matching.

------------------------------------------------------------------------

# 🗃️ Data Storage Architecture

The project uses both **MySQL and NoSQL** databases.

## MySQL

Used for structured information such as:

-   User information
-   Analysis records
-   Fatigue scores
-   Risk levels
-   Timestamps
-   Image metadata
-   Historical results

Example entities:

``` text
users
analysis_sessions
analysis_results
fatigue_scores
image_metadata
```

## NoSQL

Used for flexible/semi-structured information such as:

-   Agent outputs
-   CV feature results
-   Recommendations
-   RAG chunks
-   Document metadata
-   Agent logs

## Vector Store

A vector store such as ChromaDB is used for embedding-based retrieval.

``` text
Document
   ↓
Chunk
   ↓
Embedding
   ↓
Vector Store
   ↓
Semantic Search
```

------------------------------------------------------------------------

# 🧠 Memory Management

## Short-Term Memory

Maintains information during the current analysis workflow:

``` text
Uploaded Image
      ↓
CV Features
      ↓
Fatigue Score
      ↓
Retrieved Context
      ↓
Recommendation
```

## Long-Term Memory

Stores historical analysis results to enable:

-   Fatigue history
-   Trend analysis
-   Previous scores
-   Timestamp-based tracking

------------------------------------------------------------------------

# 🖼️ Image Processing

Supported image formats include:

``` text
.jpg
.jpeg
.png
.webp
.heic
```

Processing flow:

``` text
Image Upload
     ↓
Format Detection
     ↓
Validation
     ↓
Format Normalization
     ↓
Standard Image Representation
     ↓
Computer Vision Processing
```

The system is designed to process different image formats consistently.

------------------------------------------------------------------------

# 🧪 Testing Strategy

Because of memory limitations, **3--4 test images** are used for
demonstration and validation.

Example:

``` text
Image 1 → Rested / Low Fatigue
Image 2 → Mild Fatigue
Image 3 → High Fatigue
Image 4 → Edge Case
```

Example formats:

``` text
image_1_rested.jpg
image_2_mild_fatigue.png
image_3_high_fatigue.webp
image_4_edge_case.jpeg
```

The test set demonstrates both fatigue-analysis behavior and
multi-format image handling.

------------------------------------------------------------------------

# 📊 Expected Output

Example system output:

``` text
----------------------------------
        FATIGUESENSE RESULT
----------------------------------

Fatigue Score: 72 / 100

Risk Level: HIGH

Detected Indicators:
✓ Increased eye closure
✓ Possible yawning
✓ Reduced alertness indicators

Retrieved Context:
Relevant fatigue and sleep reference information

Recommendation:
Take an appropriate rest break and avoid activities
requiring sustained attention if fatigue is significant.

----------------------------------
```

> FatigueSense is an educational project and the output is not a medical
> diagnosis.

------------------------------------------------------------------------

# 👥 Team BrainBytes --- Responsibilities

  -----------------------------------------------------------------------
  Member                              Responsibility
  ----------------------------------- -----------------------------------
  **Member A**                        Agent Design, Computer Vision,
                                      Image Processing, Fatigue Scoring

  **Member B**                        RAG Integration, Document Loading,
                                      Chunking, Embeddings, Semantic
                                      Search, Hybrid Search

  **Member C**                        React Frontend, Image Upload,
                                      Dashboard, History and
                                      Visualization

  **Member D**                        Memory, MySQL, NoSQL, FastAPI,
                                      Agent Orchestration, Workflow and
                                      Error Handling
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 🗂️ Project Structure

``` text
FatigueSense/
│
├── README.md
├── .gitignore
├── .env.example
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── cv/
│   │   ├── preprocessing/
│   │   │
│   │   ├── rag/
│   │   │   ├── loaders/
│   │   │   ├── parsers/
│   │   │   ├── preprocessing/
│   │   │   ├── chunking/
│   │   │   ├── embeddings/
│   │   │   ├── vector_store/
│   │   │   ├── retrieval/
│   │   │   └── pipeline.py
│   │   │
│   │   ├── orchestration/
│   │   ├── memory/
│   │   ├── database/
│   │   │   ├── mysql/
│   │   │   └── nosql/
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   │
│   ├── tests/
│   ├── data/
│   │   ├── test_images/
│   │   ├── reference_documents/
│   │   │   ├── pdf/
│   │   │   ├── json/
│   │   │   └── txt/
│   │   ├── chunks/
│   │   └── embeddings/
│   │
│   └── scripts/
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── hooks/
│       └── utils/
│
├── database/
│   ├── mysql/
│   └── nosql/
│
└── docs/
    ├── architecture/
    ├── agents/
    ├── rag/
    ├── database/
    └── frontend/
```

------------------------------------------------------------------------

# 🛠️ Technology Stack

### Frontend

-   React
-   JavaScript
-   HTML
-   CSS
-   Recharts

### Backend

-   Python
-   FastAPI

### AI / Agents

-   CrewAI / LangGraph
-   LLM
-   Computer Vision
-   OpenCV
-   MediaPipe

### RAG

-   Document Loaders
-   Text Chunking
-   Embeddings
-   ChromaDB
-   BM25
-   Hybrid Search
-   Re-ranking

### Databases

-   MySQL
-   NoSQL Database
-   Vector Database / ChromaDB

### Development

-   Git
-   GitHub
-   VS Code
-   Python Virtual Environment

------------------------------------------------------------------------

# 🔄 Complete Workflow

``` text
1. User uploads image
          ↓
2. Validate image format
          ↓
3. Normalize image
          ↓
4. Extract facial/visual features
          ↓
5. Image Analysis Agent
          ↓
6. Fatigue Scoring Agent
          ↓
7. Generate retrieval query
          ↓
8. RAG Pipeline
          ↓
9. Semantic Search + BM25
          ↓
10. Hybrid Search
          ↓
11. Re-rank retrieved context
          ↓
12. Recommendation Agent
          ↓
13. Store analysis and memory
          ↓
14. Return result through FastAPI
          ↓
15. Display result in React
```

------------------------------------------------------------------------

# 🔐 Error Handling

The system should handle:

-   Unsupported image formats
-   Corrupted images
-   Missing facial information
-   Invalid documents
-   Failed document parsing
-   Embedding failures
-   Database connection errors
-   Retrieval failures
-   Agent failures
-   API errors

Retry and fallback mechanisms should be implemented where appropriate.

------------------------------------------------------------------------

# 📈 Future Enhancements

-   Video-based fatigue detection
-   Real-time webcam analysis
-   Larger fatigue datasets
-   Personalized fatigue trends
-   Advanced multimodal RAG
-   Voice-based interaction
-   Advanced re-ranking
-   Additional behavioral signals
-   Cloud deployment
-   Continuous model evaluation

------------------------------------------------------------------------

# ⚠️ Disclaimer

FatigueSense is an educational and research-oriented AI project.

The system provides an estimated fatigue assessment based on available
input signals and reference information. It is **not a medical
diagnostic system** and should not replace professional medical advice
or evaluation.

------------------------------------------------------------------------

# 👨‍💻 Team

## BrainBytes

**Project:** FatigueSense\
**Program:** Gen AI --- ITER Cohort Project

### Contributions

-   **Member A:** Agent Design & Computer Vision
-   **Member B:** RAG Integration & Hybrid Search
-   **Member C:** React Frontend
-   **Member D:** Memory, Database & Agent Orchestration

------------------------------------------------------------------------

## ⭐ Project Vision

> **Detect fatigue. Retrieve knowledge. Reason with agents. Deliver
> grounded insights.**

**FatigueSense --- An intelligent, agentic RAG-powered fatigue detection
system.**
