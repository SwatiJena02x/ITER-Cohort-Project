# 🧠⚡ DSA AI Coach

> 🚀 **An Agentic AI DSA Mentor — Problem Solving • Progressive Hints • RAG • Code Analysis • Memory**


An 🤖 AI-powered Data Structures and Algorithms coaching platform that combines **LangGraph orchestration, specialized AI tools, Retrieval-Augmented Generation (RAG), persistent student memory, code analysis, and a Streamlit interface**.

The project is designed to behave like an interactive DSA mentor rather than a simple question-answer chatbot. It can provide problems, progressive hints, explain concepts from a curated knowledge base, analyze student code, and maintain learning progress across a session.

---


<div align="center">

## 🧰 Technology Stack

**🐍 Python** • **🧠 Qwen 2.5 Coder** • **🦙 Ollama** • **🔗 LangGraph** • **🤖 ReAct** • **📚 RAG** • **🔎 BM25** • **🧬 Semantic Search** • **🔀 RRF** • **⚡ FastAPI** • **🎈 Streamlit** • **🐘 PostgreSQL** • **🧩 pgvector** • **🐳 Docker Compose** • **🎨 Custom CSS** • **🐙 Git / GitHub**

| Technology | Role |
|---|---|
| 🐍 **Python** | Core application and AI engineering language |
| 🔗 **LangGraph** | Agent workflow, state, routing & orchestration |
| 🧠 **Qwen 2.5 Coder** | Local reasoning, generation & code analysis |
| 🦙 **Ollama** | Local LLM runtime |
| 📚 **RAG** | Grounded DSA knowledge retrieval |
| 🔎 **BM25** | Keyword / lexical retrieval |
| 🧬 **Sentence Transformers** | Semantic embeddings with `all-MiniLM-L6-v2` |
| 🔀 **RRF** | Hybrid retrieval ranking |
| ⚡ **FastAPI** | Backend API layer |
| 🎈 **Streamlit** | Interactive frontend / dashboard |
| 🐘 **PostgreSQL** | Persistent application & student memory |
| 🧩 **pgvector** | Vector similarity search |
| 🐳 **Docker Compose** | Containerized deployment |
| 🎨 **Custom CSS** | Professional AI-product UI styling |
| 🐙 **Git / GitHub** | Version control & collaboration |

</div>

---


## 1. Project Overview

### Problem

Traditional DSA practice platforms generally separate:

- Problem solving
- Hints
- Explanations
- Code debugging
- Progress tracking

The DSA AI Coach brings these capabilities together into a single AI-driven workflow.

### Solution

The system uses a **LangGraph-based agent workflow** to understand a student's request and route it to the appropriate specialized tool.

The major capabilities are:

1. Generate/select DSA problems
2. Provide progressive hints
3. Explain DSA concepts using RAG
4. Analyze submitted code
5. Track student progress and conversation memory
6. Orchestrate multi-step interactions using ReAct-style planning
7. Expose the backend through FastAPI
8. Provide an interactive frontend through Streamlit

---

# 🚀 2. Key Features

## 🧩 Problem Generation

The Problem Tool selects problems according to:

- Topic
- Difficulty
- Previous problems
- Session history

The current problem bank contains problems across:

- Dynamic Programming
- Arrays
- Strings

The Dynamic Programming section includes 20 problems.

---

## 💡 Progressive Hint System

Each supported problem can contain three levels of hints:

### Hint 1

Conceptual direction.

### Hint 2

More specific algorithmic guidance.

### Hint 3

Near-solution guidance without immediately giving the complete solution.

The student's hint usage is recorded in memory.

---

## 🔍 Code Analysis

Students can submit their DSA solutions for analysis.

The Code Analysis Tool can be used to identify:

- Syntax issues
- Logical errors
- Incorrect algorithmic assumptions
- Edge cases
- Time complexity
- Space complexity
- Possible improvements

The goal is to guide the student rather than simply replace their solution.

---

## 📚 Retrieval-Augmented Generation

The RAG system provides grounded explanations from the project's DSA knowledge base.

The pipeline contains:

```
Documents
    ↓
Document Loader
    ↓
Recursive Chunking
    ↓
Embeddings / Semantic Retrieval
    +
BM25 Keyword Retrieval
    ↓
Hybrid Retrieval / RRF
    ↓
Context Builder
    ↓
Qwen
    ↓
Grounded Explanation

```

The knowledge base contains structured explanations for DSA concepts and problems.

The current DP knowledge set contains 20 problem-specific documents.

---

## 🧠 Persistent Student Memory

The Memory Tool stores learning progress such as:

- Current problem
- Topic
- Difficulty
- Hints used
- Attempts
- Status
- Last action
- Conversation history

PostgreSQL is used as the persistent database.

The project also uses `pgvector` for vector-based retrieval where configured.

---

# 🏗️ 3. High-Level Architecture

```
                         ┌─────────────────────┐
                         │      Student        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Streamlit UI      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI         │
                         │      Backend        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    DSA Coach Agent  │
                         │      LangGraph      │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
              Problem Tool      Hint Tool        RAG Tool
                    │               │                │
                    │               │         ┌──────┴──────┐
                    │               │         │             │
                    │               │      Retrieval      Qwen
                    │               │         │
                    │               │    Knowledge Base
                    │               │
                    └───────────────┼────────────────┐
                                    │                │
                                    ▼                ▼
                              Code Analysis      Memory Tool
                                  Tool                │
                                    │                 ▼
                                    │             PostgreSQL
                                    │
                                    ▼
                                  Qwen

```

---

# 🤖 4. Agent Architecture

The central agent is implemented using **LangGraph**.

The agent maintains a state containing information such as:

- User question
- Session ID
- Current problem
- Problem ID
- Route
- Tool result
- Observation
- Conversation history
- Next action
- Iteration count
- Final answer

### Simplified flow

```
START
  ↓
Router
  ↓
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ PROBLEM  │   HINT   │   CODE   │   RAG    │  DIRECT  │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘
     │          │          │          │            │
     └──────────┴──────────┴──────────┴────────────┘
                         ↓
                       Memory
                         ↓
                ReAct decision gate
                    /           \
                 FINAL         PLANNER
                                  ↓
                             Next Tool
                                  ↓
                                FINAL

```

The ReAct planner is used when a request requires multiple reasoning/tool steps.

Simple requests can terminate directly after their relevant tool completes. This avoids unnecessary local LLM calls and improves response latency.

---

# 🛠️ 5. Five Core Tools

## 5.1 Problem Tool

Responsible for selecting DSA problems.

Inputs can include:

```
topic
difficulty
exclude_ids

```

Example:

```
Give me a medium DP problem.

```

The tool selects an appropriate problem while avoiding previously used problems when session information is available.

---

## 5.2 Hint Tool

Responsible for progressive hints.

Example:

```
Give me a hint.

```

The tool resolves the current problem ID and returns:

```
Hint 1
Hint 2
Hint 3

```

Hints are stored alongside the problem definitions in the problem bank.

---

## 5.3 RAG Tool

Responsible for concept and problem explanations.

Example:

```
Explain Coin Change.

```

The RAG tool retrieves relevant knowledge and sends the retrieved context to the configured Qwen model.

---

## 5.4 Code Analysis Tool

Responsible for evaluating student code.

Example:

```
Analyze my solution for Partition Equal Subset Sum.

```

The tool can provide feedback about correctness, complexity, bugs, edge cases, and improvements.

---

## 5.5 Memory Tool

Responsible for persistent learning state.

Example stored information:

```
Problem: House Robber
Topic: dynamic_programming
Difficulty: medium
Hints Used: 2
Attempts: 1
Status: in_progress
Last Action: requested_hint

```

This enables the coach to maintain continuity between interactions.

---

# 📚 6. RAG Architecture

The RAG implementation is separated into several components.

```
knowledge_base/documents
        ↓
DocumentLoader
        ↓
RecursiveChunker
        ↓
HybridRetriever
        ↓
ContextBuilder
        ↓
RAGPrompt
        ↓
OllamaClient
        ↓
Qwen

```

## Document Loader

Loads knowledge documents from:

```
knowledge_base/documents/

```

## Recursive Chunker

Breaks larger documents into smaller overlapping chunks.

The current pipeline uses:

```
chunk_size = 500
chunk_overlap = 100

```

## Hybrid Retriever

Combines:

- Semantic search
- 🔎 BM25 keyword search
- 🔀 Reciprocal Rank Fusion (RRF)

This gives the system both semantic and lexical retrieval capabilities.

## Context Builder

Combines the highest-ranked retrieved chunks into the context supplied to the LLM.

## RAG Prompt

Constrains the generation process around retrieved knowledge.

## Ollama Client

Provides the local LLM interface.

The project has used Qwen 2.5 Coder models through Ollama.

---

# 📖 7. Knowledge Base

The knowledge base is stored under:

```
knowledge_base/
└── documents/

```

The current DP knowledge coverage includes:

1. House Robber
2. Climbing Stairs
3. Coin Change
4. Longest Increasing Subsequence
5. Partition Equal Subset Sum
6. 0/1 Knapsack
7. Unbounded Knapsack
8. House Robber II
9. Decode Ways
10. Unique Paths
11. Minimum Path Sum
12. Word Break
13. Longest Common Subsequence
14. Edit Distance
15. Maximum Subarray
16. Target Sum
17. Interleaving String
18. Distinct Subsequences
19. Palindromic Substrings
20. Matrix Chain Multiplication

Each knowledge document is structured around:

- Problem statement
- Core idea
- DP state
- Base case
- Transition
- Example
- Complexity
- Common mistakes
- Key takeaway

---

# 🧩 8. Problem Bank

Problems are maintained in:

```
problems/problem_bank.py

```

Each problem follows a structure similar to:

```
{
    "id": "dp_003",
    "title": "Coin Change",
    "topic": "dynamic_programming",
    "difficulty": "medium",
    "description": "...",
    "hints": [
        "...",
        "...",
        "..."
    ]
}
```

This creates a single source of truth for the Problem Tool and Hint Tool.

---

# 🧠 9. Memory Architecture

The Memory Tool uses PostgreSQL to maintain persistent student state.

The system tracks:

```
session_id
problem_id
problem_title
topic
difficulty
hints_used
attempts
status
last_action

```

Conversation messages can also be persisted.

### Example

```
Student:
Give me a medium DP problem.

Coach:
Coin Change

Memory:
problem_id = dp_003
status = in_progress
hints_used = 0
attempts = 0
last_action = requested_problem

```

After requesting a hint:

```
hints_used = 1
last_action = requested_hint

```

After submitting code:

```
attempts = 1

```

---

# 🗄️ 10. Database

The project uses **PostgreSQL** for persistent application data.

`pgvector` can be used for vector similarity search.

The database layer supports the project's:

- Student progress
- Session information
- Conversation memory
- Vector retrieval components where configured

---

# ⚡ 11. API Layer

The backend is exposed through **FastAPI**.

Example server command:

```
uvicorn api.main:app --reload
```

The API exposes health and chat functionality.

### Health Check

```
GET /health

```

### Chat

```
POST /chat

```

The Streamlit frontend communicates with the FastAPI backend.

---

# 🎨 12. Frontend

The UI is implemented using **Streamlit**.

The frontend is responsible for:

- Chat interface
- Student interaction
- Problem display
- Hint interaction
- Code submission
- Coach responses

The UI communicates with the FastAPI backend instead of directly managing agent orchestration.

---

# 🧰 13. Technology Stack

## Programming Language

- 🐍 Python

## AI / LLM

- 🧠 Qwen 2.5 Coder
- 🦙 Ollama

## Agent Orchestration

- 🔗 LangGraph
- 🧠 ReAct-style planning

## RAG

- 🧬 Semantic embeddings
- BM25
- 🔀 Hybrid retrieval
- Reciprocal Rank Fusion (RRF)
- 🧩 Vector search / pgvector where configured

## Backend

- ⚡ FastAPI
- 🚀 Uvicorn

## Frontend

- 🎈 Streamlit

## Database

- 🐘 PostgreSQL
- 🧩 pgvector

## Embeddings

The project uses:

```
all-MiniLM-L6-v2

```

for semantic embeddings.

## Development Environment

- 🐍 Python virtual environment
- 🪟 Windows development environment
- 🐙 Git / GitHub

---

# 📁 14. Project Structure

A simplified project structure is:

```
dsa-ai-coach/
│
├── agents/
│   ├── dsa_agent.py
│   ├── planner.py
│   ├── router.py
│   └── state.py
│
├── api/
│   └── main.py
│
├── chunking/
│   └── recursive_chunker.py
│
├── dashboard/
│   └── app.py
│
├── document_loader/
│   └── ...
│
├── embedding/
│   └── ...
│
├── knowledge_base/
│   ├── documents/
│   └── generate_dp_knowledge.py
│
├── llm/
│   └── ...
│
├── problems/
│   └── problem_bank.py
│
├── rag/
│   ├── __init__.py
│   ├── context_builder.py
│   ├── rag_pipeline.py
│   └── rag_prompt.py
│
├── retrieval/
│   └── ...
│
├── tools/
│   ├── code_analysis_tool.py
│   ├── hint_tool.py
│   ├── memory_tool.py
│   ├── problem_tool.py
│   └── rag_tool.py
│
├── tests/
│   └── ...
│
├── ingest.py
├── requirements.txt
├── .env
└── README.md

```

> File names can vary slightly depending on the final local project structure.

---

# 🔄 15. End-to-End Example

Consider a student starting a session.

### Step 1 --- Problem

```
Student:
Give me a medium DP problem.

```

Router:

```
PROBLEM

```

Problem Tool:

```
Coin Change

```

Memory:

```
problem_id = dp_003
status = in_progress

```

---

### Step 2 --- Hint

```
Student:
Give me a hint.

```

Router:

```
HINT

```

Hint Tool:

```
Hint 1:
Think about solving smaller amounts before solving the target amount.

```

Memory:

```
hints_used = 1

```

---

### Step 3 --- Explanation

```
Student:
Explain this problem.

```

Router:

```
RAG

```

RAG:

```
Retrieve Coin Change knowledge
        ↓
Build context
        ↓
Qwen
        ↓
Generate explanation

```

---

### Step 4 --- Code Analysis

Student submits:

```
def coinChange(coins, amount):
    ...
```

Router:

```
CODE

```

Code Analysis Tool evaluates the solution and returns feedback.

---

### Step 5 --- Progress

Memory records:

```
Problem: Coin Change
Hints Used: 1
Attempts: 1
Status: in_progress

```

This allows the next interaction to continue from the student's current state.

---

# 🔗 16. LangGraph Role

LangGraph is responsible for **workflow orchestration**, not for being the LLM itself.

The distinction is:

```
Qwen
    = reasoning / generation

LangGraph
    = workflow / state / routing / control flow

Tools
    = specialized capabilities

PostgreSQL
    = persistent memory

RAG
    = external knowledge retrieval

```

This separation makes the architecture modular.

---

# 🧠 17. ReAct Orchestration

The project includes a ReAct-style planner for requests that genuinely require multiple steps.

For a simple request:

```
Explain dynamic programming.

```

the workflow can be:

```
Router
  ↓
RAG
  ↓
Memory
  ↓
Final

```

For a multi-step request:

```
Analyze my code and then explain the optimal approach.

```

the workflow can become:

```
Router
  ↓
Code Analysis
  ↓
Memory
  ↓
ReAct Planner
  ↓
RAG / another tool
  ↓
Final

```

This prevents unnecessary planner calls for every simple request and is especially useful when running local LLMs.

---

# 🦙 18. Local LLM Architecture

Ollama is used to run the LLM locally.

This provides:

- Local inference
- No mandatory external model API
- Full control over the model runtime
- Ability to switch between model sizes

The project has used:

```
qwen2.5-coder:1.5b
qwen2.5-coder:7b

```

A smaller model can be used for latency-sensitive operations, while a larger model can be used for heavier reasoning/code analysis depending on available hardware.

---

# ⚙️ 19. Setup

## Clone the repository

```
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd dsa-ai-coach
```

## Create virtual environment

Windows:

```
python -m venv .venv
```

Activate:

```
.venv\Scripts\activate
```

## Install dependencies

```
pip install -r requirements.txt
```

## Configure environment variables

Create:

```
.env

```

and configure the required PostgreSQL/database settings used by the project.

Do not commit secrets.

---

# 🦙 20. Ollama Setup

Install Ollama and pull the required model.

Example:

```
ollama pull qwen2.5-coder:1.5b
```

For heavier local inference:

```
ollama pull qwen2.5-coder:7b
```

Verify Ollama:

```
ollama list
```

---

# ⚡ 21. Run the Backend

From the project root:

```
uvicorn api.main:app --reload
```

The API will normally be available at:

```
http://127.0.0.1:8000

```

Health check:

```
http://127.0.0.1:8000/health

```

---

# 🎈 22. Run Streamlit

Start the frontend using:

```
streamlit run dashboard/app.py
```

The Streamlit application will provide the user-facing DSA Coach interface.

---

# 🧪 23. Testing

The project contains component-level tests for important parts of the system.

Useful tests include:

### 🔍 Code Analysis

```
python test_code_analysis.py
```

### Memory

```
python test_memory_tool.py
```

### Hint data

```
python test_hint_data.py
```

Testing should verify:

- Tool behavior
- Database connectivity
- Agent routing
- Memory updates
- RAG retrieval
- Code analysis
- Hint progression
- End-to-end agent behavior

---

# 💬 24. Example Supported Interactions

### Problem generation

```
Give me a medium DP problem.

```

### Different problem

```
Give me another DP problem.

```

### Hint

```
Give me a hint.

```

### More guidance

```
Give me another hint.

```

### Concept explanation

```
Explain dynamic programming.

```

### Problem explanation

```
Explain Coin Change.

```

### Code analysis

```
Analyze my solution for Partition Equal Subset Sum.

```

### Complexity

```
What is the time complexity of my solution?

```

### Learning progress

```
What problem am I currently solving?

```

---

# 🎯 25. Design Principles

The project follows several design principles.

### Separation of Responsibilities

Each tool has a specific responsibility.

### Stateful Agent

Student progress is persisted instead of treating every request as independent.

### Grounded Generation

RAG answers are based on retrieved project knowledge.

### Modular Architecture

Individual tools can be replaced or improved without rebuilding the entire system.

### Efficient Orchestration

Simple requests avoid unnecessary ReAct iterations.

### Progressive Learning

Hints provide guidance incrementally instead of immediately exposing the solution.

---

# 🔮 26. Future Improvements

Potential future improvements include:

- Authentication and student accounts
- More DSA topics
- Larger problem bank
- More comprehensive hint datasets
- Automated code execution and test cases
- Unit-test generation
- Difficulty adaptation based on student performance
- Learning analytics dashboard
- Topic-wise mastery scoring
- Spaced repetition
- Personalized problem recommendations
- Streaming responses
- Production database configuration
- Docker deployment
- Cloud deployment
- CI/CD
- Observability and logging
- Rate limiting
- Production-grade authentication

---

# 📦 27. Current Scope

The current implementation focuses on building a functional AI DSA coaching backend with:

```
Python
+
LangGraph
+
Specialized Tools
+
RAG
+
Qwen / Ollama
+
PostgreSQL
+
pgvector
+
FastAPI
+
Streamlit

```

The system is intended as an educational AI assistant and is not a replacement for formal evaluation or human instruction.

---

# 🏆 28. Summary

DSA AI Coach combines traditional DSA practice with an agentic AI architecture.

The core architecture is:

```
                 DSA AI COACH
                      │
             ┌────────┴────────┐
             │   LangGraph     │
             │ Agent Workflow  │
             └────────┬────────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
   Problem          Hint           RAG
    Tool            Tool           Tool
       │              │              │
       └──────────────┼──────────────┘
                      │
                Code Analysis
                      │
                      ▼
                   Memory
                      │
                      ▼
                 PostgreSQL
                      │
                      ▼
              FastAPI Backend
                      │
                      ▼
               Streamlit UI

```

The result is a modular, stateful, RAG-enabled DSA coaching system capable of guiding students from **problem selection → hints → explan**

---

# 🐳 29. Final Docker Deployment Architecture

The production-style local deployment uses two application containers:

```text
                    Host Machine
                         |
                  http://localhost:8501
                         |
                         v
              +-----------------------+
              |   dsa_frontend        |
              |   Streamlit :8501     |
              +-----------+-----------+
                          |
                          | Docker network
                          | http://backend:2024
                          v
              +-----------------------+
              |   dsa_backend         |
              |   LangGraph :2024     |
              +-----+------------+----+
                    |            |
                    v            v
              PostgreSQL       Ollama
              + pgvector       Qwen 2.5 Coder
```

The browser only needs access to the frontend.

The frontend container communicates with the backend using the Docker Compose service name:

```text
http://backend:2024
```

This makes the application portable across machines without hard-coding one developer's localhost address.

---

# 🎨 30. Frontend Design System

The Streamlit dashboard was customized to present the application as an AI engineering product rather than the default Streamlit page.

## Visual hierarchy

The interface is organized into:

```text
Application Branding
        ↓
Hero / Introduction
        ↓
Capability Cards
        ↓
Conversation Area
        ↓
Agent / Backend Status
        ↓
Session / Thread Context
        ↓
Chat Input
```

## UI components

The application includes visual components for:

- Problem Engine
- Hint Engine
- RAG Knowledge
- Memory
- Conversation
- Agent status
- Backend status
- Session ID
- Action buttons
- Chat messages
- User input

## Styling

The UI uses custom CSS styling around Streamlit components for:

- Dark developer-style presentation
- Gradient backgrounds
- Rounded cards
- Borders and shadows
- Spacing and layout
- Status indicators
- Chat containers
- Interactive states
- Responsive presentation

The exact font family and CSS values should be treated as implementation details in `dashboard/app.py`; this README intentionally does not invent a font name that is not guaranteed by the source.

## Animation philosophy

Where CSS animation/transition styling is used, it is deliberately lightweight.

Animations are presentation-only and are not part of the AI reasoning loop.

They are intended to:

```text
Highlight state
    ↓
Improve visual feedback
    ↓
Make interaction feel responsive
```

The AI workflow remains independent of the visual animation layer.

---

# 🔁 31. ReAct Loop — Detailed Explanation

The ReAct-style planner is used only when the request benefits from multiple tool calls.

A conceptual execution is:

```text
User Request
     |
     v
   Router
     |
     v
  Agent State
     |
     v
   Planner
     |
     v
 Select Action
     |
     +----------------------+
     |                      |
     v                      v
  Call Tool              Finish
     |
     v
Tool Result / Observation
     |
     v
Update State
     |
     v
Decision Gate
     |
     +------------+
     |            |
     v            v
  FINAL       PLAN AGAIN
                  |
                  v
              Next Tool
                  |
                  +---------> Observation
```

The important design decision is that **not every request enters a long ReAct cycle**.

For a simple request:

```text
"Give me a medium DP problem."
```

the path can be:

```text
Router → Problem Tool → Memory → Final
```

For a multi-step request:

```text
"Analyze my code and explain the optimal approach."
```

the path can be:

```text
Router
  ↓
Code Analysis
  ↓
Observation
  ↓
Memory
  ↓
Planner
  ↓
RAG
  ↓
Final
```

This conditional planning approach reduces unnecessary local LLM calls.

---

# 🔄 32. State Flow

The LangGraph state acts as the shared context between nodes.

A simplified state lifecycle is:

```text
Incoming Request
      ↓
question
      ↓
session_id
      ↓
route
      ↓
tool execution
      ↓
tool_result
      ↓
observation
      ↓
memory update
      ↓
next_action
      ↓
iteration_count
      ↓
final_answer
```

The state allows different nodes to cooperate without each node independently reconstructing the whole conversation.

---

# 🔗 33. RAG + Agent Integration

RAG is not simply a separate search page.

It is a tool that the agent can invoke when external project knowledge is needed.

```text
User
 ↓
Router
 ↓
RAG Tool
 ↓
Retriever
 ├── Semantic Retrieval
 └── BM25
 ↓
Hybrid / RRF Ranking
 ↓
Context Builder
 ↓
RAG Prompt
 ↓
Ollama Client
 ↓
Qwen
 ↓
Grounded Response
 ↓
Agent State
```

This separates:

```text
Retrieval
```

from:

```text
Generation
```

and makes the response more grounded in the project's DSA knowledge base.

---

# 🧠 34. Memory + Agent Integration

Memory is also exposed through a specialized tool.

```text
User
 ↓
Agent
 ↓
Memory Tool
 ↓
PostgreSQL
 ↓
Student State
 ↓
Agent State
```

For example, after the user receives a hint:

```text
problem_id   = dp_003
hints_used   = 1
last_action  = requested_hint
status       = in_progress
```

The next request can therefore be interpreted in context.

---

# 🐘 35. Why PostgreSQL and pgvector?

PostgreSQL provides durable structured storage for application state.

pgvector extends PostgreSQL with vector similarity capabilities.

This allows the architecture to keep structured state and vector retrieval in the same database technology where configured:

```text
PostgreSQL
 ├── Student/session data
 ├── Conversation state
 └── Vector data
       ↓
    pgvector
```

---

# 🔎 36. Why BM25 + Semantic Retrieval?

Semantic retrieval is useful when two queries have similar meaning but different wording.

BM25 is useful for exact terms, names, and technical keywords.

The project combines both:

```text
                 Query
                   |
          +--------+--------+
          |                 |
          v                 v
   Semantic Search       BM25 Search
          |                 |
          +--------+--------+
                   |
                   v
            Hybrid Ranking
                   |
                   v
                  RRF
                   |
                   v
             Top Context
```

This improves retrieval robustness compared with relying on only one retrieval method.

---

# 🔗 37. Why LangGraph?

LangGraph is used for **workflow orchestration and stateful control flow**.

It is not the language model.

The architecture separates:

```text
LangGraph → decides workflow
Qwen      → generates/reasons
Tools     → perform specialized actions
RAG       → retrieves knowledge
Postgres  → persists state
Streamlit → presents the interface
```

This separation makes individual components easier to replace and test.

---

# 🦙 38. Why Ollama?

Ollama provides the local model runtime.

The project has used:

```text
qwen2.5-coder:1.5b
qwen2.5-coder:7b
```

The model files remain outside the application Docker image.

That means:

```text
Application Image
    ≠
Large LLM Model Image
```

The Docker image contains application dependencies, while Ollama manages the model runtime separately.

This keeps the application image more manageable and allows the model to be changed independently.

---

# 🌍 39. Portability

The project was prepared so another machine can run it without depending on the original developer's local paths.

Avoided machine-specific assumptions include:

```text
C:\Users\...
127.0.0.1
developer-specific virtual environments
developer-specific secrets
```

For Docker networking, service discovery is used:

```text
backend:2024
```

Configuration is provided through:

```text
.env.example
```

The actual:

```text
.env
```

is intentionally excluded from Git.

---

# ♻️ 40. Reproducible Setup

The intended machine-independent setup is:

```text
Clone repository
       ↓
Create .env from .env.example
       ↓
Install/start Ollama
       ↓
Pull Qwen model
       ↓
Verify PostgreSQL/pgvector
       ↓
docker compose up -d
       ↓
docker compose ps
       ↓
Open localhost:8501
```

This is the recommended presentation/evaluation path.

---

# ✅ 41. Evaluation Checklist

Before presenting on another machine, verify:

```text
[ ] Docker Desktop is running
[ ] Docker Compose is available
[ ] PostgreSQL is available
[ ] pgvector is available/configured
[ ] Ollama is running
[ ] qwen2.5-coder:7b is installed
[ ] .env has been created locally
[ ] docker compose up -d succeeds
[ ] dsa_backend is Up
[ ] dsa_frontend is Up
[ ] localhost:8501 opens
[ ] localhost:2024/docs opens
[ ] frontend can reach backend
[ ] problem generation works
[ ] hint flow works
[ ] RAG explanation works
[ ] memory/session flow works
[ ] code analysis works
```

---

# 🎬 42. Recommended Demonstration

A complete live demonstration can follow this sequence:

### A. Open the dashboard

```text
http://localhost:8501
```

Explain the UI:

```text
Hero
→ Capability Cards
→ Conversation
→ Agent Status
→ Session Context
```

### B. Generate a problem

```text
Give me a medium dynamic programming problem.
```

Explain:

```text
Router → Problem Tool → Memory → Final
```

### C. Ask for a hint

```text
Give me a hint.
```

Explain:

```text
Router → Hint Tool → Memory → Final
```

### D. Ask for an explanation

```text
Explain this problem.
```

Explain:

```text
RAG → Hybrid Retrieval → Context → Qwen
```

### E. Submit code

Explain:

```text
Code Analysis Tool
```

### F. Ask a multi-step question

Explain the ReAct-style loop.

### G. Show Docker

```powershell
docker compose ps
```

Explain:

```text
dsa_backend  :2024
dsa_frontend :8501
```

### H. Show networking

Explain why:

```text
http://backend:2024
```

is used from inside the frontend container.

---

# 🎓 43. Viva — Architecture Questions

## What makes this an agentic application?

Because the system has:

```text
State
+
Routing
+
Specialized Tools
+
Tool Results / Observations
+
Conditional Planning
+
Memory
```

It is not simply:

```text
Prompt → LLM → Answer
```

---

## What is LangGraph doing?

LangGraph manages the workflow graph, state transitions, routing, and conditional execution.

---

## What is ReAct?

ReAct is a reasoning/action pattern in which an agent can reason about what to do, call a tool, observe the result, update state, and decide whether another action is required.

---

## Why not use ReAct for every request?

Because simple requests do not require multi-step planning.

Avoiding unnecessary planning reduces latency and local LLM usage.

---

## What is RAG?

Retrieval-Augmented Generation retrieves relevant project knowledge and supplies it to the LLM as context before generation.

---

## Why hybrid retrieval?

BM25 handles lexical matching while semantic retrieval handles meaning similarity. Combining both improves retrieval robustness.

---

## Why pgvector?

It enables vector similarity search while using PostgreSQL as the persistence layer.

---

## Why Ollama?

It provides local LLM inference and allows Qwen models to run without making the core application dependent on a hosted LLM API.

---

## Why Dockerize frontend and backend separately?

Separation provides:

- Independent service boundaries
- Clear networking
- Easier deployment
- Easier debugging
- Independent rebuilds
- Better portability

---

## Why does the frontend use `backend:2024`?

Because containers communicate using Docker Compose service names.

Inside the frontend container:

```text
localhost
```

means the frontend container itself, not the backend.

Therefore:

```text
backend:2024
```

is required.

---

# 🔐 44. Important Security Note

The repository should contain:

```text
.env.example
```

but must not contain:

```text
.env
```

The `.env` file may contain:

```text
Database password
API keys
LangSmith credentials
```

These must remain local and should never be committed.

---

# 🏁 45. Final System Summary

The final system can be represented as:

```text
                         ┌───────────────────┐
                         │      STUDENT      │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │   STREAMLIT UI    │
                         │ Custom CSS / UX   │
                         │   Port 8501       │
                         └─────────┬─────────┘
                                   │
                          Docker Network
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    LANGGRAPH      │
                         │ Agent Orchestrator│
                         │   Port 2024       │
                         └─────────┬─────────┘
                                   │
                  ┌────────────────┼─────────────────┐
                  │                │                 │
                  ▼                ▼                 ▼
              PROBLEM            HINT              RAG
                TOOL              TOOL              TOOL
                  │                │                 │
                  │                │          ┌──────┴──────┐
                  │                │          │             │
                  │                │       BM25       Semantic
                  │                │          │             │
                  │                │          └──────┬──────┘
                  │                │                 ▼
                  │                │              RRF
                  │                │                 │
                  │                │                 ▼
                  │                │          Context Builder
                  │                │                 │
                  └────────────────┼─────────────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
                     ▼                           ▼
              CODE ANALYSIS                    MEMORY
                     │                           │
                     │                           ▼
                     │                      PostgreSQL
                     │                      + pgvector
                     │                           │
                     └──────────────┬────────────┘
                                    ▼
                              ReAct Decision
                              /           \
                             ▼             ▼
                          FINAL        NEXT TOOL
                             │             │
                             └──────┬──────┘
                                    ▼
                                  Qwen
                               via Ollama
                                    │
                                    ▼
                              Final Response
                                    │
                                    ▼
                              Streamlit UI
```

**DSA AI Coach combines:**

```text
DSA Practice
     +
Agentic Workflow
     +
LangGraph
     +
ReAct-style Planning
     +
Specialized Tools
     +
RAG
     +
Hybrid Retrieval
     +
Persistent Memory
     +
PostgreSQL / pgvector
     +
Qwen / Ollama
     +
FastAPI
     +
Streamlit
     +
Custom CSS UI
     +
Docker Compose
     =
Complete AI DSA Coaching Platform
```
