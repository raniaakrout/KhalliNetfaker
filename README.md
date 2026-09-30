# KhalliNetfaker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)

> An intelligent AI agent for meeting transcript analysis powered by RAG pipeline, automatic summarization, and LLM-as-Judge evaluation.

## 🎯 Overview

**KhalliNetfaker** is a comprehensive meeting transcript analysis platform combining:

- **Automatic Summarization**: Hierarchical summarization pipeline with structured minutes generation
- **RAG System**: Retrieval-Augmented Generation for accurate question answering
- **Intelligent Agent**: LangGraph ReAct agent with dynamic tool selection (search + summary)
- **Automated Evaluation**: Quality metrics via DeepEval (Faithfulness, Relevancy, Precision)
- **Benchmarking**: Compare RAG configurations (LLMs, embeddings, chunking strategies)

### Key Features

✅ Drag-and-drop transcript upload (.txt/.vtt) with real-time processing  
✅ Semantic chunking (SemanticChunker with percentile 95)& token chunking   
✅ FAISS vector search with HuggingFace embeddings  
✅ LangGraph agent with persistent conversation memory  
✅ Explicit source citations in answers ([Chunk X])  
✅ DeepEval metrics (Faithfulness, Relevancy, Precision)  
✅ Configurable benchmarking system  
✅ JWT authentication with PostgreSQL

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 16)                         │
│        Chat UI  |  Upload Modal  |  Benchmark Modal             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│      Auth API  |  Chat API  |  Evaluation  |  Benchmark         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              PIPELINES                                           │
│  Summarization (Token→Hierarchical)  |  RAG (Index→Retrieve) │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE                                   │
│    PostgreSQL  |  FAISS Vector Store  |  File System            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ with pnpm
- PostgreSQL
- OpenRouter API Key

### Installation

```bash
# Clone repository
git clone https://github.com/raniaakrout/KhalliNetfaker.git
cd KhalliNetfaker

# Backend setup
cd meeting_rag
python -m venv .venv
.venv\Scripts\activate  # Windows | source .venv/bin/activate (Linux/Mac)
pip install -e .

# Database setup
createdb meeting_minutes_db
alembic upgrade head

# Frontend setup
cd ../transcript-upload-pipeline
pnpm install
```

### Environment Variables

**Backend (`meeting_rag/.env`):**

```env
OPENROUTER_API_KEY=sk-or-v1-xxx


EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
JUDGE_MODEL=openai/gpt-oss-120b

DB_HOST=localhost
DB_PORT=Port num
DB_NAME=meeting_minutes_db
DB_USER=user_name
DB_PASSWORD=your_password

JWT_SECRET_KEY=your-secret-key
```

**Frontend (`transcript-upload-pipeline/.env.local`):**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Run Application

```bash
# Backend (terminal 1)
cd meeting_rag
uvicorn src.api.main:app --reload --port 8000

# Frontend (terminal 2)
cd transcript-upload-pipeline
pnpm dev
```

- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

---

## 📖 Usage

### 1. Upload Transcript
Drag-and-drop a `.txt` or `.vtt` file. The system will:
- Compute hash for deduplication
- Create semantic & token chunks
- Build FAISS vector store
- Generate hierarchical summary

### 2. Ask Questions
Type natural language questions:
- "What was the Q3 revenue?" → `search_meeting` tool
- "Summarize the meeting" → `get_meeting_summary` tool
- "And what about action items?" → Uses conversation history

Answers include explicit citations: `[Chunk 3]`

### 3. Evaluate
Click **🔍 Evaluate RAG** to run LLM-as-Judge metrics:
- **Faithfulness**: Claims supported by chunks?
- **Answer Relevancy**: On-topic response?


### 4. Benchmark
Configure and compare multiple RAG setups:
- Select LLM models, embeddings, chunking strategies
- Run automated tests
- View results ranked by `score_global`

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - REST API framework
- **LangGraph** - Agent orchestration with ReAct
- **LangChain** - LLM chains and tools
- **FAISS** - Vector similarity search
- **DeepEval** - LLM-as-Judge evaluation
- **PostgreSQL** - Database + conversation memory
- **SQLAlchemy** - ORM

### Frontend
- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Zustand** - State management
- **Tailwind CSS + shadcn/ui** - Styling
- **Axios** - API client

### Infrastructure
- **OpenRouter** - Multi-LLM provider (GPT-4, Claude, Gemma, Llama)
- **HuggingFace** - Embeddings models

---

## 📂 Project Structure

```
KhalliNetfaker/
├── meeting_rag/                    # Backend (Python)
│   ├── src/
│   │   ├── api/                    # FastAPI routes
│   │   ├── rag/                    # RAG pipeline (indexer, retriever, chunker)
│   │   ├── evaluation/             # DeepEval metrics
│   │   ├── benchmark/              # Benchmarking system
│   │   ├── database/               # PostgreSQL layer
│   │   ├── agent.py                # LangGraph agent
│   │   ├── tools.py                # Agent tools
│   │   └── summarizer.py           # Hierarchical summarization
│   ├── data/                       # Uploads & chunks
│   ├── vectorstore/                # FAISS indices
│   └── pyproject.toml              # Dependencies
│
├── transcript-upload-pipeline/     # Frontend (Next.js)
│   ├── app/                        # Pages (chat, auth)
│   ├── components/                 # React components
│   ├── lib/                        # API client, store, utils
│   └── package.json                # Dependencies
│
├── ARCHITECTURE.md                 # Architecture docs
├── BENCHMARKING_PLAN.md            # Benchmarking strategy
├── documentation.md                # Complete technical docs
├── README.md                       # This file
├── LICENSE                         # MIT License
└── .gitignore                      # Git ignore rules
```

---

## 🔍 Evaluation Metrics

| Metric | Description | Score Range |
|--------|-------------|-------------|
| **Faithfulness** | Claims supported by retrieved chunks | 0.0 - 1.0 |
| **Answer Relevancy** | Answer stays on topic | 0.0 - 1.0 |
| **Contextual Precision** | Relevant chunks ranked first | 0.0 - 1.0 |
| **Contextual Recall** | Context covers ground truth | 0.0 - 1.0 |
| **Contextual Relevancy** | Chunks relevant to question | 0.0 - 1.0 |

**Scoring**: ≥0.7 (High) | 0.4-0.7 (Moderate) | <0.4 (Low)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with **LangChain**, **LangGraph**, **DeepEval**, **OpenRouter**, **FAISS**, **Next.js**, and **PostgreSQL**.

---

## 📧 Contact

**Author**: Rania Akrout  
**GitHub**: [@raniaakrout](https://github.com/raniaakrout)

---

**Status**: Internship prototype 
