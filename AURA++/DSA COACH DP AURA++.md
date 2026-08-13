# DSA AI Coach

An AI-powered Data Structures and Algorithms coaching platform that
combines **LangGraph orchestration, specialized AI tools,
Retrieval-Augmented Generation (RAG), persistent student memory, code
analysis, and a Streamlit interface**.

The project is designed to behave like an interactive DSA mentor rather
than a simple question-answer chatbot. It can provide problems,
progressive hints, explain concepts from a curated knowledge base,
analyze student code, and maintain learning progress across a session.

------------------------------------------------------------------------

## 1. Project Overview

### Problem

Traditional DSA practice platforms generally separate:

-   Problem solving
-   Hints
-   Explanations
-   Code debugging
-   Progress tracking

The DSA AI Coach brings these capabilities together into a single
AI-driven workflow.

### Solution

The system uses a **LangGraph-based agent workflow** to understand a
student's request and route it to the appropriate specialized tool.

The major capabilities are:

1.  Generate/select DSA problems
2.  Provide progressive hints
3.  Explain DSA concepts using RAG
4.  Analyze submitted code
5.  Track student progress and conversation memory
6.  Orchestrate multi-step interactions using ReAct-style planning
7.  Expose the backend through FastAPI
8.  Provide an interactive frontend through Streamlit

------------------------------------------------------------------------

# 2. Key Features

## Problem Generation

The Problem Tool selects problems according to:

-   Topic
-   Difficulty
-   Previous problems
-   Session history

The current problem bank contains problems across:

-   Dynamic Programming
-   Arrays
-   Strings

The Dynamic Programming section includes 20 problems.

------------------------------------------------------------------------

## Progressive Hint System

Each supported problem can contain three levels of hints:

### Hint 1

Conceptual direction.

### Hint 2

More specific algorithmic guidance.

### Hint 3

Near-solution guidance without immediately giving the complete solution.

The student's hint usage is recorded in memory.

------------------------------------------------------------------------

## Code Analysis

Students can submit their DSA solutions for analysis.

The Code Analysis Tool can be used to identify:

-   Syntax issues
-   Logical errors
-   Incorrect algorithmic assumptions
-   Edge cases
-   Time complexity
-   Space complexity
-   Possible improvements

The goal is to guide the student rather than simply replace their
solution.

------------------------------------------------------------------------

## Retrieval-Augmented Generation

The RAG system provides grounded explanations from the project's DSA
knowledge base.

The pipeline contains:

``` text
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

The knowledge base contains structured explanations for DSA concepts and
problems.

The current DP knowledge set contains 20 problem-specific documents.

------------------------------------------------------------------------

## Persistent Student Memory

The Memory Tool stores learning progress such as:

-   Current problem
-   Topic
-   Difficulty
-   Hints used
-   Attempts
-   Status
-   Last action
-   Conversation history

PostgreSQL is used as the persistent database.

The project also uses `pgvector` for vector-based retrieval where
configured.

------------------------------------------------------------------------

# 3. High-Level Architecture

``` text
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

------------------------------------------------------------------------

# 4. Agent Architecture

The central agent is implemented using **LangGraph**.

The agent maintains a state containing information such as:

-   User question
-   Session ID
-   Current problem
-   Problem ID
-   Route
-   Tool result
-   Observation
-   Conversation history
-   Next action
-   Iteration count
-   Final answer

### Simplified flow

``` text
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

The ReAct planner is used when a request requires multiple
reasoning/tool steps.

Simple requests can terminate directly after their relevant tool
completes. This avoids unnecessary local LLM calls and improves response
latency.

------------------------------------------------------------------------

# 5. Five Core Tools

## 5.1 Problem Tool

Responsible for selecting DSA problems.

Inputs can include:

``` text
topic
difficulty
exclude_ids
```

Example:

``` text
Give me a medium DP problem.
```

The tool selects an appropriate problem while avoiding previously used
problems when session information is available.

------------------------------------------------------------------------

## 5.2 Hint Tool

Responsible for progressive hints.

Example:

``` text
Give me a hint.
```

The tool resolves the current problem ID and returns:

``` text
Hint 1
Hint 2
Hint 3
```

Hints are stored alongside the problem definitions in the problem bank.

------------------------------------------------------------------------

## 5.3 RAG Tool

Responsible for concept and problem explanations.

Example:

``` text
Explain Coin Change.
```

The RAG tool retrieves relevant knowledge and sends the retrieved
context to the configured Qwen model.

------------------------------------------------------------------------

## 5.4 Code Analysis Tool

Responsible for evaluating student code.

Example:

``` text
Analyze my solution for Partition Equal Subset Sum.
```

The tool can provide feedback about correctness, complexity, bugs, edge
cases, and improvements.

------------------------------------------------------------------------

## 5.5 Memory Tool

Responsible for persistent learning state.

Example stored information:

``` text
Problem: House Robber
Topic: dynamic_programming
Difficulty: medium
Hints Used: 2
Attempts: 1
Status: in_progress
Last Action: requested_hint
```

This enables the coach to maintain continuity between interactions.

------------------------------------------------------------------------

# 6. RAG Architecture

The RAG implementation is separated into several components.

``` text
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

``` text
knowledge_base/documents/
```

## Recursive Chunker

Breaks larger documents into smaller overlapping chunks.

The current pipeline uses:

``` text
chunk_size = 500
chunk_overlap = 100
```

## Hybrid Retriever

Combines:

-   Semantic search
-   BM25 keyword search
-   Reciprocal Rank Fusion (RRF)

This gives the system both semantic and lexical retrieval capabilities.

## Context Builder

Combines the highest-ranked retrieved chunks into the context supplied
to the LLM.

## RAG Prompt

Constrains the generation process around retrieved knowledge.

## Ollama Client

Provides the local LLM interface.

The project has used Qwen 2.5 Coder models through Ollama.

------------------------------------------------------------------------

# 7. Knowledge Base

The knowledge base is stored under:

``` text
knowledge_base/
└── documents/
```

The current DP knowledge coverage includes:

1.  House Robber
2.  Climbing Stairs
3.  Coin Change
4.  Longest Increasing Subsequence
5.  Partition Equal Subset Sum
6.  0/1 Knapsack
7.  Unbounded Knapsack
8.  House Robber II
9.  Decode Ways
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

-   Problem statement
-   Core idea
-   DP state
-   Base case
-   Transition
-   Example
-   Complexity
-   Common mistakes
-   Key takeaway

------------------------------------------------------------------------

# 8. Problem Bank

Problems are maintained in:

``` text
problems/problem_bank.py
```

Each problem follows a structure similar to:

``` python
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

This creates a single source of truth for the Problem Tool and Hint
Tool.

------------------------------------------------------------------------

# 9. Memory Architecture

The Memory Tool uses PostgreSQL to maintain persistent student state.

The system tracks:

``` text
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

``` text
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

``` text
hints_used = 1
last_action = requested_hint
```

After submitting code:

``` text
attempts = 1
```

------------------------------------------------------------------------

# 10. Database

The project uses **PostgreSQL** for persistent application data.

`pgvector` can be used for vector similarity search.

The database layer supports the project's:

-   Student progress
-   Session information
-   Conversation memory
-   Vector retrieval components where configured

------------------------------------------------------------------------

# 11. API Layer

The backend is exposed through **FastAPI**.

Example server command:

``` bash
uvicorn api.main:app --reload
```

The API exposes health and chat functionality.

### Health Check

``` text
GET /health
```

### Chat

``` text
POST /chat
```

The Streamlit frontend communicates with the FastAPI backend.

------------------------------------------------------------------------

# 12. Frontend

The UI is implemented using **Streamlit**.

The frontend is responsible for:

-   Chat interface
-   Student interaction
-   Problem display
-   Hint interaction
-   Code submission
-   Coach responses

The UI communicates with the FastAPI backend instead of directly
managing agent orchestration.

------------------------------------------------------------------------

# 13. Technology Stack

## Programming Language

-   Python

## AI / LLM

-   Qwen 2.5 Coder
-   Ollama

## Agent Orchestration

-   LangGraph
-   ReAct-style planning

## RAG

-   Semantic embeddings
-   BM25
-   Hybrid retrieval
-   Reciprocal Rank Fusion (RRF)
-   Vector search / pgvector where configured

## Backend

-   FastAPI
-   Uvicorn

## Frontend

-   Streamlit

## Database

-   PostgreSQL
-   pgvector

## Embeddings

The project uses:

``` text
all-MiniLM-L6-v2
```

for semantic embeddings.

## Development Environment

-   Python virtual environment
-   Windows development environment
-   Git / GitHub

------------------------------------------------------------------------

# 14. Project Structure

A simplified project structure is:

``` text
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

> File names can vary slightly depending on the final local project
> structure.

------------------------------------------------------------------------

# 15. End-to-End Example

Consider a student starting a session.

### Step 1 --- Problem

``` text
Student:
Give me a medium DP problem.
```

Router:

``` text
PROBLEM
```

Problem Tool:

``` text
Coin Change
```

Memory:

``` text
problem_id = dp_003
status = in_progress
```

------------------------------------------------------------------------

### Step 2 --- Hint

``` text
Student:
Give me a hint.
```

Router:

``` text
HINT
```

Hint Tool:

``` text
Hint 1:
Think about solving smaller amounts before solving the target amount.
```

Memory:

``` text
hints_used = 1
```

------------------------------------------------------------------------

### Step 3 --- Explanation

``` text
Student:
Explain this problem.
```

Router:

``` text
RAG
```

RAG:

``` text
Retrieve Coin Change knowledge
        ↓
Build context
        ↓
Qwen
        ↓
Generate explanation
```

------------------------------------------------------------------------

### Step 4 --- Code Analysis

Student submits:

``` python
def coinChange(coins, amount):
    ...
```

Router:

``` text
CODE
```

Code Analysis Tool evaluates the solution and returns feedback.

------------------------------------------------------------------------

### Step 5 --- Progress

Memory records:

``` text
Problem: Coin Change
Hints Used: 1
Attempts: 1
Status: in_progress
```

This allows the next interaction to continue from the student's current
state.

------------------------------------------------------------------------

# 16. LangGraph Role

LangGraph is responsible for **workflow orchestration**, not for being
the LLM itself.

The distinction is:

``` text
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

------------------------------------------------------------------------

# 17. ReAct Orchestration

The project includes a ReAct-style planner for requests that genuinely
require multiple steps.

For a simple request:

``` text
Explain dynamic programming.
```

the workflow can be:

``` text
Router
  ↓
RAG
  ↓
Memory
  ↓
Final
```

For a multi-step request:

``` text
Analyze my code and then explain the optimal approach.
```

the workflow can become:

``` text
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

This prevents unnecessary planner calls for every simple request and is
especially useful when running local LLMs.

------------------------------------------------------------------------

# 18. Local LLM Architecture

Ollama is used to run the LLM locally.

This provides:

-   Local inference
-   No mandatory external model API
-   Full control over the model runtime
-   Ability to switch between model sizes

The project has used:

``` text
qwen2.5-coder:1.5b
qwen2.5-coder:7b
```

A smaller model can be used for latency-sensitive operations, while a
larger model can be used for heavier reasoning/code analysis depending
on available hardware.

------------------------------------------------------------------------

# 19. Setup

## Clone the repository

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd dsa-ai-coach
```

## Create virtual environment

Windows:

``` powershell
python -m venv .venv
```

Activate:

``` powershell
.venv\Scripts\activate
```

## Install dependencies

``` powershell
pip install -r requirements.txt
```

## Configure environment variables

Create:

``` text
.env
```

and configure the required PostgreSQL/database settings used by the
project.

Do not commit secrets.

------------------------------------------------------------------------

# 20. Ollama Setup

Install Ollama and pull the required model.

Example:

``` bash
ollama pull qwen2.5-coder:1.5b
```

For heavier local inference:

``` bash
ollama pull qwen2.5-coder:7b
```

Verify Ollama:

``` bash
ollama list
```

------------------------------------------------------------------------

# 21. Run the Backend

From the project root:

``` powershell
uvicorn api.main:app --reload
```

The API will normally be available at:

``` text
http://127.0.0.1:8000
```

Health check:

``` text
http://127.0.0.1:8000/health
```

------------------------------------------------------------------------

# 22. Run Streamlit

Start the frontend using:

``` powershell
streamlit run dashboard/app.py
```

The Streamlit application will provide the user-facing DSA Coach
interface.

------------------------------------------------------------------------

# 23. Testing

The project contains component-level tests for important parts of the
system.

Useful tests include:

### Code Analysis

``` powershell
python test_code_analysis.py
```

### Memory

``` powershell
python test_memory_tool.py
```

### Hint data

``` powershell
python test_hint_data.py
```

Testing should verify:

-   Tool behavior
-   Database connectivity
-   Agent routing
-   Memory updates
-   RAG retrieval
-   Code analysis
-   Hint progression
-   End-to-end agent behavior

------------------------------------------------------------------------

# 24. Example Supported Interactions

### Problem generation

``` text
Give me a medium DP problem.
```

### Different problem

``` text
Give me another DP problem.
```

### Hint

``` text
Give me a hint.
```

### More guidance

``` text
Give me another hint.
```

### Concept explanation

``` text
Explain dynamic programming.
```

### Problem explanation

``` text
Explain Coin Change.
```

### Code analysis

``` text
Analyze my solution for Partition Equal Subset Sum.
```

### Complexity

``` text
What is the time complexity of my solution?
```

### Learning progress

``` text
What problem am I currently solving?
```

------------------------------------------------------------------------

# 25. Design Principles

The project follows several design principles.

### Separation of Responsibilities

Each tool has a specific responsibility.

### Stateful Agent

Student progress is persisted instead of treating every request as
independent.

### Grounded Generation

RAG answers are based on retrieved project knowledge.

### Modular Architecture

Individual tools can be replaced or improved without rebuilding the
entire system.

### Efficient Orchestration

Simple requests avoid unnecessary ReAct iterations.

### Progressive Learning

Hints provide guidance incrementally instead of immediately exposing the
solution.

------------------------------------------------------------------------

# 26. Future Improvements

Potential future improvements include:

-   Authentication and student accounts
-   More DSA topics
-   Larger problem bank
-   More comprehensive hint datasets
-   Automated code execution and test cases
-   Unit-test generation
-   Difficulty adaptation based on student performance
-   Learning analytics dashboard
-   Topic-wise mastery scoring
-   Spaced repetition
-   Personalized problem recommendations
-   Streaming responses
-   Production database configuration
-   Docker deployment
-   Cloud deployment
-   CI/CD
-   Observability and logging
-   Rate limiting
-   Production-grade authentication

------------------------------------------------------------------------

# 27. Current Scope

The current implementation focuses on building a functional AI DSA
coaching backend with:

``` text
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

The system is intended as an educational AI assistant and is not a
replacement for formal evaluation or human instruction.

------------------------------------------------------------------------

# 28. Summary

DSA AI Coach combines traditional DSA practice with an agentic AI
architecture.

The core architecture is:

``` text
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

The result is a modular, stateful, RAG-enabled DSA coaching system
capable of guiding students from **problem selection → hints →
explanation → code analysis → progress tracking**.
