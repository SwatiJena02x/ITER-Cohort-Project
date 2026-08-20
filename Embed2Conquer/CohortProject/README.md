# 🌳 DSA Coach Tree

> An AI-powered Tree Data Structures learning assistant built with **RAG, PostgreSQL + pgvector, hybrid retrieval, LangGraph agents, Ollama, and Streamlit**.

The project helps students learn and practice Tree Data Structures through two main experiences:

1. **Ask & Learn** – Ask questions about Trees and receive answers grounded in the project knowledge base using Retrieval-Augmented Generation (RAG).
2. **Coding Practice** – Generate Tree coding questions by topic and difficulty, submit Python solutions, run them against generated test cases, receive evaluation, and request hints.

---

## 📌 Why this project exists

The project was built to demonstrate an end-to-end AI application rather than only a chatbot. It includes:

- multi-format document ingestion
- chunking
- embedding generation
- persistent vector storage
- semantic retrieval
- BM25 keyword retrieval
- hybrid retrieval
- RAG tool calling
- LangGraph-based agent workflows
- short-term conversation memory
- coding-question generation
- executable code evaluation
- hint generation
- a Streamlit user interface

The intended knowledge domain is **Tree Data Structures and Algorithms**, including Binary Trees, BSTs, traversals, recursion, AVL Trees, Heaps, and Tree interview/practice problems.

---

# 🏗️ System Architecture

## 1. RAG pipeline

```text
Knowledge Base
(PDF / MD / TXT / PY / CSV / JSON / IPYNB)
        |
        v
Data Ingestion
rag/ingest.py
        |
        v
Text Extraction
        |
        v
Chunking
200 words, 40-word overlap
        |
        v
SentenceTransformer Embeddings
all-MiniLM-L6-v2
384 dimensions
        |
        v
PostgreSQL + pgvector
(tree_documents table)
        |
        +-------------------------+
        |                         |
        v                         v
Semantic Search              BM25 Search
pgvector cosine similarity   In-memory lexical index
        |                         |
        +-----------+-------------+
                    |
                    v
              Hybrid Retrieval
               alpha = 0.5
                    |
                    v
              Top Retrieved Chunks
                    |
                    v
                 RAG Agent
                    |
                    v
              Grounded AI Answer
```

## 2. Agent architecture

```text
                         User
                          |
                          v
                   Streamlit Application
                          |
                          v
                 DSATreeOrchestrator
                    (Supervisor)
                          |
          +---------------+---------------+
          |                               |
          v                               v
      RAG Agent                   Step Evaluator Agent
          |                               |
          v                               +---------------------------+
  search_tree_knowledge                      |             |           |
          |                                  v             v           v
          v                            New Question    Submit Code    Hint
   Hybrid Retrieval                         |             |           |
   Semantic + BM25                         LLM       run_code tool    LLM
          |                                  |             |           |
          +------------------+---------------+-------------+-----------+
                             |
                             v
                        Final Response
```

---

# ✨ Features

## 📚 RAG-based learning

The assistant searches the Tree knowledge base before answering Tree-related questions. Retrieval combines:

- **Semantic search** using `all-MiniLM-L6-v2` embeddings stored in pgvector.
- **Keyword search** using BM25.
- **Hybrid ranking** with both retrieval scores combined using `alpha=0.5`.

This allows the project to retrieve information based on both meaning and exact terminology.

## 📄 Multi-format ingestion

`rag/ingest.py` currently supports:

| Extension | Handling |
|---|---|
| `.pdf` | Text extraction with `pypdf` |
| `.md` | Plain-text reader |
| `.txt` | Plain-text reader |
| `.py` | Plain-text reader |
| `.csv` | CSV rows converted into readable text |
| `.json` | JSON converted to formatted text |
| `.ipynb` | Markdown and code cells extracted |

Unsupported files are skipped and reported in the terminal.

## 🧠 Persistent vector database

Embeddings are stored in PostgreSQL instead of only in memory or local files.

The project creates:

```text
tree_documents
├── id             TEXT PRIMARY KEY
├── content        TEXT
├── source         TEXT
├── chunk_index    INTEGER
└── embedding      vector(384)
```

An HNSW index is created for vector search:

```sql
CREATE INDEX tree_documents_embedding_hnsw
ON tree_documents
USING hnsw (embedding vector_cosine_ops);
```

## 🤖 LangGraph agents

The project uses LangGraph to structure agent behavior.

### RAG Agent

`agent/tree_agent.py`

- receives Tree-related questions
- decides when to use `search_tree_knowledge`
- retrieves relevant knowledge-base chunks
- uses the retrieved context to generate an educational answer
- uses `InMemorySaver` for short-term checkpoint memory while the application runs

### Step Evaluator Agent

`agent/step_evaluator_agent.py`

Responsible for:

- generating coding questions
- storing hidden question metadata
- maintaining the current question, rubric, test cases, and required function name
- executing submitted Python code against test cases
- asking the LLM to explain the actual execution result
- generating Socratic hints

### Supervisor / Orchestrator

`agent/supervisor.py`

Routes requests between the RAG Agent and Step Evaluator Agent. The current implementation uses rule-based intent detection for actions such as:

- new question
- hint request
- code submission
- general Tree question

---

# 📁 Project Structure

```text
DSA_COACH_TREE/
│
├── agent/
│   ├── __init__.py
│   ├── run_agent.py
│   ├── step_evaluator_agent.py
│   ├── supervisor.py
│   └── tree_agent.py
│
├── app/
│   ├── main.py
│   └── code_page.py
│
├── knowledge_base/
│   ├── notes/
│   │   └── tree_data_structure_types.md
│   │
│   ├── pdfs/
│   │   └── Trees_Zero_to_FAANG.pdf
│   │
│   └── questions/
│       ├── DSA_Trees_Complete_Problems_Set_1.pdf
│       ├── DSA_Trees_Complete_Problems_Set_2 (8).pdf
│       └── Tree_Interview_Question_Bank_60Q.pdf
│
├── memory/
│   ├── memory_manager.py
│   └── student_memory.json
│
├── rag/
│   ├── embeddings.py
│   ├── ingest.py
│   └── retriever.py
│
├── requirements.txt
└── README.md
```

The following should **not** be committed or included in a project submission archive:

```text
.venv/
.env
__pycache__/
*.pyc
```

Each machine should create its own `.venv` in the project root.

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| LLM runtime | Ollama |
| LLM integration | LangChain / `langchain-ollama` |
| Agent workflow | LangGraph |
| Embeddings | SentenceTransformers |
| Embedding model | `all-MiniLM-L6-v2` |
| Vector database | PostgreSQL + pgvector |
| Semantic search | pgvector cosine distance |
| Keyword search | BM25 (`rank-bm25`) |
| Hybrid retrieval | Weighted score fusion |
| PDF ingestion | pypdf |
| Database driver | psycopg |
| Configuration | python-dotenv |
| Language | Python 3.12 recommended |

---

# 🚀 Complete Setup on Another Machine

Follow these steps **in order**. This is the recommended procedure for presentation, evaluation, or running the project on a new machine.

## Step 1: Extract / clone the project

If using the ZIP submitted with the project:

1. Extract the ZIP.
2. Open a terminal in the project root.
3. Confirm that folders such as `agent`, `app`, `rag`, and `knowledge_base` are directly inside the root.

Example:

```powershell
cd C:\path\to\DSA_COACH_TREE
```

> Do not run the application from inside `app/`. Run commands from the project root.

---

## Step 2: Install Python

Use Python **3.12** if possible, matching the development environment.

Verify:

```powershell
python --version
```

Expected example:

```text
Python 3.12.x
```

If `python` is not recognized, install Python and enable **Add Python to PATH** during installation.

---

## Step 3: Create `.venv` in the project root

From the project root:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the terminal should look similar to:

```text
(.venv) PS C:\path\to\DSA_COACH_TREE>
```

### If PowerShell blocks activation

Run PowerShell as the current user and execute:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## Step 4: Upgrade pip and install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Installation may take several minutes because the project uses ML/NLP packages.

### Important dependency note

Before final submission, verify that `requirements.txt` is the cleaned project dependency list rather than an entire `pip freeze` from the developer machine. A dependency list generated from the actual project imports is preferable for reproducible setup.

The core packages used directly by this source code include:

```text
streamlit
langchain-core
langchain-ollama
langgraph
sentence-transformers
rank-bm25
pypdf
python-dotenv
psycopg-binary
pgvector
numpy
```

If the supplied `requirements.txt` has already been cleaned with `pipreqs`, keep the project-tested versions from that file. Do not blindly downgrade packages during presentation unless installation fails.

---

# 🐘 Step 5: Install PostgreSQL and pgvector

The RAG database uses PostgreSQL with the pgvector extension.

You need:

- PostgreSQL
- pgvector available to that PostgreSQL installation
- optionally pgAdmin 4 for visual database inspection

After PostgreSQL is running, connect using pgAdmin or `psql` and create the database:

```sql
CREATE DATABASE dsa_coach_tree;
```

Then connect to `dsa_coach_tree` and enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Verify:

```sql
SELECT extname
FROM pg_extension
WHERE extname = 'vector';
```

Expected result:

```text
vector
```

> The project requires the PostgreSQL server to have the pgvector extension installed. If `CREATE EXTENSION vector` reports that the extension is unavailable, pgvector must be installed for that PostgreSQL server before continuing.

---

# 🔐 Step 6: Create the `.env` file

Create a file named exactly:

```text
.env
```

in the **project root**, next to `README.md` and `requirements.txt`.

Example:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=dsa_coach_tree
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD

OLLAMA_MODEL=llama3.2:latest
```

Replace:

```text
YOUR_POSTGRES_PASSWORD
```

with the password for the local PostgreSQL user.

### Port note

This project currently defaults to:

```text
DB_PORT=5433
```

If PostgreSQL on the new machine uses the more common default port `5432`, either:

```env
DB_PORT=5432
```

or configure PostgreSQL to use the port expected by the project.

### Security

Never commit `.env` to GitHub because it contains database credentials.

---

# 🦙 Step 7: Install and start Ollama

Install Ollama for the operating system being used.

After installation, verify:

```powershell
ollama --version
```

The project defaults to:

```text
llama3.2:latest
```

Pull the model:

```powershell
ollama pull llama3.2:latest
```

Verify that it exists:

```powershell
ollama list
```

If Ollama is not already running automatically, start the local server:

```powershell
ollama serve
```

Keep that terminal open, or ensure the Ollama service is running.

### Using a different model

The project reads:

```env
OLLAMA_MODEL=...
```

Therefore, if a different compatible local model is preferred, pull it first and update the `.env` value accordingly.

Example:

```powershell
ollama pull qwen2.5:7b
```

Then:

```env
OLLAMA_MODEL=qwen2.5:7b
```

Use the same model name that is actually installed locally.

---

# 🧮 Step 8: Build the RAG database

This is an essential first-run step on a new machine.

From the project root, with `.venv` activated and `.env` configured:

```powershell
python -m rag.embeddings
```

The script performs:

```text
1. Creates the tree_documents table if needed
2. Creates the HNSW vector index if needed
3. Reads supported files from knowledge_base/
4. Splits content into chunks
5. Generates 384-dimensional embeddings
6. Deletes old documents from tree_documents
7. Stores the newly generated chunks and vectors in PostgreSQL
```

Expected terminal messages include something similar to:

```text
BUILDING PGVECTOR RAG DATABASE
STEP 1: Ingesting and chunking...
Chunks created: ...
STEP 2: Generating embeddings...
Embedding shape: (..., 384)
STEP 3: Storing embeddings in PostgreSQL...
PGVECTOR RAG DATABASE CREATED SUCCESSFULLY
Total chunks stored: ...
```

The first embedding-model download may take time and requires internet access. After the model is cached locally, later runs are generally faster.

---

# 🔍 Step 9: Verify that vectors were stored

Open pgAdmin 4, select the `dsa_coach_tree` database, open **Query Tool**, and run:

```sql
SELECT COUNT(*)
FROM tree_documents;
```

To count vectors specifically:

```sql
SELECT COUNT(*)
FROM tree_documents
WHERE embedding IS NOT NULL;
```

To inspect stored chunks:

```sql
SELECT
    id,
    source,
    chunk_index,
    LEFT(content, 200) AS content_preview
FROM tree_documents
LIMIT 10;
```

To inspect the table structure:

```sql
SELECT column_name, data_type, udt_name
FROM information_schema.columns
WHERE table_name = 'tree_documents';
```

The `embedding` column is a pgvector value and is intentionally high-dimensional. pgAdmin may not be convenient for manually reading the complete vector, but its presence can be verified with:

```sql
SELECT id, embedding IS NOT NULL AS has_embedding
FROM tree_documents
LIMIT 10;
```

---

# ▶️ Step 10: Run the Streamlit application

From the project root:

```powershell
streamlit run app/main.py
```

Expected output resembles:

```text
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

Open the displayed local URL in a browser.

---

# 🧪 Suggested Presentation Test Sequence

For a reliable live demonstration, use this order.

## Test 1: Verify RAG startup

When the app starts, confirm terminal messages similar to:

```text
Loading embedding model...
Loading documents from PostgreSQL...
Loaded ... documents.
BM25 keyword index ready.
```

This demonstrates that:

- the embedding model loaded
- PostgreSQL was reachable
- stored chunks were loaded
- BM25 was built from the loaded documents

## Test 2: Ask a Tree concept question

Example:

```text
What is the difference between a Binary Tree and a Binary Search Tree?
```

Explain during the presentation:

```text
User question
   -> RAG Agent
   -> search_tree_knowledge tool
   -> Semantic search + BM25
   -> Hybrid ranking
   -> Retrieved context
   -> Ollama
   -> Final answer
```

## Test 3: Open Coding Practice

1. Open **💻 Code**.
2. Select a topic, for example `Tree Traversal`.
3. Select a difficulty.
4. Click **🔄 New Question**.

The Step Evaluator Agent generates a coding problem and stores metadata including:

- title
- statement
- topic
- difficulty
- required function name
- evaluation rubric
- test cases

## Test 4: Submit Python code

Write a solution with the requested function name and click:

```text
▶️ Submit Code
```

The backend:

```text
Student Code
    |
    v
run_code tool
    |
    v
Execute against generated test cases
    |
    v
Actual pass/fail result
    |
    v
LLM evaluation explanation
    |
    v
CORRECT / PARTIAL / INCORRECT
```

## Test 5: Request a hint

Click:

```text
💡 Hint
```

The agent uses the current question and returns a coaching-oriented hint instead of a full solution.

---

# 🧩 How the RAG Components Work

## Data ingestion — `rag/ingest.py`

The ingestion module walks through `knowledge_base/` recursively. Every supported file is read and converted into text.

The project then performs word-based chunking:

```text
Chunk size: 200 words
Overlap: 40 words
```

The overlap helps preserve context between consecutive chunks.

## Embedding generation — `rag/embeddings.py`

The project uses:

```text
all-MiniLM-L6-v2
```

Each chunk is converted into a vector with:

```text
384 dimensions
```

The vectors are inserted into PostgreSQL through psycopg and pgvector.

## Semantic search — `rag/retriever.py`

For a user query:

1. the query is embedded using the same embedding model
2. PostgreSQL performs vector similarity search
3. cosine distance is used through pgvector's `<=>` operator
4. the top matching chunks are returned

## Keyword search

All loaded document content is tokenized and indexed using `BM25Okapi`.

The query is tokenized and ranked according to BM25 lexical relevance.

## Hybrid retrieval

The retriever obtains both result sets and combines their scores:

```text
final_score =
    alpha * semantic_score
    +
    (1 - alpha) * normalized_keyword_score
```

Current default:

```text
alpha = 0.5
```

This gives equal weight to semantic and keyword relevance.

---

# 🤖 How the Agents Work

## Tree RAG Agent — `agent/tree_agent.py`

The Tree Agent exposes the tool:

```text
search_tree_knowledge(query)
```

The tool runs hybrid retrieval and returns the retrieved source, chunk information, score, and text to the LLM.

LangGraph controls the tool loop:

```text
START
  |
  v
Agent
  |
  +-- tool needed --> ToolNode --> Agent
  |
  +-- no tool needed ----------------> END
```

An `InMemorySaver` checkpointer provides short-term memory while the application process is running.

## Step Evaluator Agent — `agent/step_evaluator_agent.py`

The coding-practice workflow is:

```text
New Question
     |
     v
Question LLM
     |
     v
QUESTION_DATA metadata extracted
     |
     +--> current_question
     +--> rubric
     +--> test_cases
     +--> function_name
     |
     v
Student writes Python code
     |
     v
run_code
     |
     v
Actual test execution
     |
     v
LLM explains result
     |
     v
CORRECT / PARTIAL / INCORRECT
```

The generated `QUESTION_DATA` is parsed internally so the UI can show the problem while the backend keeps the metadata needed for evaluation.

---

# 🧠 Memory

The project uses `InMemorySaver` in the LangGraph agents for short-term runtime memory/checkpointing.

Important behavior:

```text
Application running -> memory available
Application stopped -> in-memory checkpoint state is not persistent
```

The repository also contains:

```text
memory/memory_manager.py
memory/student_memory.json
```

These files are part of the project structure, while the currently visible agent workflow primarily uses LangGraph's in-memory checkpoint mechanism for short-term agent state.

---

# 🗄️ Database Schema

The RAG storage table is created automatically by:

```powershell
python -m rag.embeddings
```

Equivalent schema:

```sql
CREATE TABLE IF NOT EXISTS tree_documents (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    source TEXT,
    chunk_index INTEGER,
    embedding vector(384)
);
```

Vector index:

```sql
CREATE INDEX IF NOT EXISTS tree_documents_embedding_hnsw
ON tree_documents
USING hnsw (embedding vector_cosine_ops);
```

---

# 🔧 Useful Commands

## Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

## Install dependencies

```powershell
pip install -r requirements.txt
```

## Build / rebuild vector database

```powershell
python -m rag.embeddings
```

## Run Streamlit

```powershell
streamlit run app/main.py
```

## Check PostgreSQL data from Python

```powershell
python
```

Then:

```python
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)

cur = conn.cursor()

cur.execute("""
SELECT COUNT(*)
FROM tree_documents
WHERE embedding IS NOT NULL;
""")

print("Vectors stored:", cur.fetchone()[0])

cur.close()
conn.close()
```

---

# 🐛 Troubleshooting

## Error: `DB_PASSWORD is not set`

Cause: `.env` is missing, is in the wrong folder, or does not contain `DB_PASSWORD`.

Fix:

```env
DB_PASSWORD=your_password
```

Place `.env` in the project root.

---

## Error: connection refused / PostgreSQL connection failure

Check:

1. PostgreSQL service is running.
2. `DB_PORT` matches the actual PostgreSQL port.
3. Database `dsa_coach_tree` exists.
4. Username and password are correct.

Try:

```env
DB_PORT=5432
```

if the local server uses the default PostgreSQL port instead of `5433`.

---

## Error: `extension "vector" is not available`

The PostgreSQL server does not currently have pgvector installed.

Install pgvector for that PostgreSQL installation, restart PostgreSQL if required, then run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## `Loaded 0 documents`

Most likely causes:

- the vector database has not been built
- the wrong database is configured in `.env`
- the table is empty

Fix:

```powershell
python -m rag.embeddings
```

Then verify:

```sql
SELECT COUNT(*) FROM tree_documents;
```

---

## First startup is slow

The first run may need to download/cache:

- the SentenceTransformer embedding model
- the Ollama LLM model, if not already pulled

After models are locally available, later runs should not need to download them again.

---

## Hugging Face unauthenticated warning

A warning about unauthenticated Hugging Face Hub requests does not necessarily stop the application. The embedding model can still download anonymously, subject to public rate limits.

A Hugging Face token is optional unless higher limits or authenticated access are required.

---

## Question generation is slow

Question generation depends mainly on the local Ollama model and available hardware. Check:

```powershell
ollama list
```

and make sure the configured model matches the value of `OLLAMA_MODEL`.

A smaller or more efficient local model may respond faster, but model changes should be tested because question formatting depends on structured `QUESTION_DATA` output.

---

# ⚠️ Implementation Notes

## Semantic storage is pgvector

Some comments/docstrings in the project may refer to FAISS. The current source code in this project stores and queries embeddings using:

```text
PostgreSQL + pgvector
```

The active semantic retrieval implementation is therefore pgvector-based, not FAISS-based.

## Code execution

The coding evaluator executes submitted Python code to test the student's solution. This is appropriate for the controlled local project demonstration, but a production deployment should use a sandboxed execution environment with resource and security restrictions.

## Rebuilding the knowledge base

When files inside `knowledge_base/` are added, removed, or significantly changed, rebuild the database:

```powershell
python -m rag.embeddings
```

The current build script removes old rows and repopulates `tree_documents` from the available knowledge base.

---

# 📋 Presentation Checklist

Before presenting from another machine, verify every item below.

- [ ] Python is installed.
- [ ] Project ZIP has been extracted.
- [ ] `.venv` has been created in the project root.
- [ ] `.venv` is activated.
- [ ] Dependencies are installed.
- [ ] PostgreSQL is running.
- [ ] pgvector is installed and enabled.
- [ ] `dsa_coach_tree` database exists.
- [ ] `.env` is configured with the correct database credentials and port.
- [ ] Ollama is installed.
- [ ] The configured Ollama model has been pulled.
- [ ] `python -m rag.embeddings` completes successfully.
- [ ] `tree_documents` contains chunks/vectors.
- [ ] `streamlit run app/main.py` starts successfully.
- [ ] A general Tree question retrieves an answer.
- [ ] A new coding question can be generated.
- [ ] A code submission can be evaluated.
- [ ] A hint can be generated.

---

# 🎯 Trainer Requirement Coverage

The project workflow addresses the requested RAG and agent components as follows:

| Requirement | Implementation |
|---|---|
| Data ingestion | `rag/ingest.py` walks the knowledge base recursively |
| Multiple file extensions | PDF, MD, TXT, PY, CSV, JSON, IPYNB are supported |
| Chunking | 200-word chunks with 40-word overlap |
| Embeddings | `all-MiniLM-L6-v2` |
| Persistent vector storage | PostgreSQL + pgvector |
| Semantic retrieval | pgvector cosine similarity search |
| Keyword retrieval | BM25 using `rank-bm25` |
| Hybrid retrieval | Weighted combination of semantic and BM25 scores |
| RAG agent | `agent/tree_agent.py` |
| Agent workflow | LangGraph |
| Memory/checkpointing | `InMemorySaver` |
| Coding agent | `agent/step_evaluator_agent.py` |
| Supervisor | `agent/supervisor.py` |
| User interface | Streamlit |

---

# 🔮 Future Improvements

Potential next steps include:

- persistent long-term student memory in PostgreSQL or another durable store
- authenticated user profiles
- isolated sandbox/container execution for submitted code
- automated test-case validation before exposing questions
- source citations in the Streamlit UI
- retrieval quality evaluation
- reranking after hybrid retrieval
- conversation history per student
- support for additional DSA topics beyond Trees
- automated unit and integration tests

---

# 👥 Project Team

Add the team member names and responsibilities here before final submission.

Example:

| Member | Responsibility |
|---|---|
| Member 1 | Team Lead / Integration |
| Member 2 | RAG Pipeline |
| Member 3 | Agent Development |
| Member 4 | UI / Testing |

---

# 🏁 Quick Start Summary

For someone who already has Python, PostgreSQL + pgvector, and Ollama installed:

```powershell
# 1. Open the project root
cd C:\path\to\DSA_COACH_TREE

# 2. Create and activate environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env with DB credentials and OLLAMA_MODEL

# 5. Ensure PostgreSQL database + pgvector are ready

# 6. Pull/start Ollama model
ollama pull llama3.2:latest

# 7. Build the RAG vector database
python -m rag.embeddings

# 8. Run the application
streamlit run app/main.py
```

---

## Final Demonstration Flow

```text
Start PostgreSQL
      +
Start Ollama
      +
Activate .venv
      |
      v
python -m rag.embeddings
      |
      v
Vectors stored in PostgreSQL + pgvector
      |
      v
streamlit run app/main.py
      |
      +-------------------------------+
      |                               |
      v                               v
Ask Tree Question               Coding Practice
      |                               |
      v                               v
Hybrid RAG                     Generate Question
      |                               |
      v                               v
Grounded Answer                 Submit / Evaluate / Hint
```

---

**DSA Coach Tree** demonstrates a complete local AI application pipeline: **Knowledge Base → Ingestion → Chunking → Embeddings → PostgreSQL/pgvector → Semantic + BM25 Hybrid Retrieval → LangGraph Agents → Ollama → Streamlit UI**.
