<p align="center">
  <h1 align="center">🏛️ PolicyPilot</h1>
  <p align="center">
    <strong>AI-Powered Intelligent System for the Maharashtra Government Department</strong>
  </p>
  <p align="center">
    Multilingual RAG-based Question Answering · Semantic Search · Document Intelligence
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React%2019-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/FAISS-4285F4?style=for-the-badge&logo=meta&logoColor=white" alt="FAISS" />
    <img src="https://img.shields.io/badge/Groq%20LLaMA%203.3-FF6600?style=for-the-badge&logo=meta&logoColor=white" alt="Groq" />
    <img src="https://img.shields.io/badge/Python%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/TailwindCSS%203-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind" />
  </p>
</p>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [SRS Traceability Matrix](#srs-traceability-matrix)
- [Dataset Sources](#dataset-sources)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**PolicyPilot** is a web-based AI assistant designed for **Maharashtra HTE Government officers** to retrieve accurate, source-grounded information from Government Resolutions (GRs), circulars, notifications, office orders, admission brochures, manuals, and FAQs.

The system uses **Retrieval-Augmented Generation (RAG)** with semantic search over FAISS vector indexes to provide:
- Grounded, citation-backed answers from authenticated government documents
- Multilingual support in **English**, **Marathi (मराठी)**, and **Hindi (हिन्दी)**
- Document summarization, comparison, and administrative decision support

### Target Users

| Role | Use Case |
|------|----------|
| **Desk Officers** | Draft and reference Government Resolutions |
| **Legal Translators** | Translate GRs between Marathi and English |
| **Administrative Reviewers** | Verify policy compliance and cross-reference documents |
| **IT / System Admins** | Deploy, configure, and maintain the platform |

---

## Key Features

### 🔍 Semantic Search & RAG
- FAISS-powered vector similarity search over document chunks
- Top-K retrieval with relevance scoring and confidence badges
- Context-aware answer generation using Groq LLaMA 3.3 70B
- Source citations with every response — no hallucinated answers

### 🌐 Multilingual AI Assistant
- Accept queries in English, Marathi, or Hindi
- Auto-detect document language (Devanagari script detection + `langdetect`)
- Switch languages mid-conversation; responses preserve official government terminology

### 📄 Document Intelligence
- Upload PDF and DOCX files with automatic text extraction (PyMuPDF / python-docx)
- AI-powered structured document summarization (executive summary, key points, action items, dates)
- Side-by-side document comparison highlighting similarities, differences, and contradictions
- Metadata extraction: department, document number, category, language, status

### 🗂️ Knowledge Repository
- Centralized repository browser for all uploaded government documents
- Direct import from **orgpedia/mahGRs** GitHub repo and Maharashtra GR portals
- Document status tracking: active, amended, superseded, draft
- Full-text preview and download capabilities

### 💬 Conversational Chat
- Multi-turn conversational AI with persistent session history
- Document-scoped Q&A — ask questions about a specific document
- Conversation history sidebar with session management
- Voice input support via Web Speech API

### 📊 Analytics Dashboard
- Query volume tracking and trend visualization
- Language distribution and confidence score analytics
- Document usage statistics

### 🔐 Authentication & Security
- Login-protected officer portal
- Session-based access control via `ProtectedRoute`
- Designed for on-premise / NIC deployment for sensitive documents

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React + Vite Frontend                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │  Upload   │ │   Chat   │ │ Summary  │ │   Compare    │   │
│  │  Page     │ │   Page   │ │   Page   │ │    Page      │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │
│       └─────────────┴───────────┴──────────────┘            │
│                         REST API (Axios)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend Engine                     │
│                                                              │
│  ┌─────────────────── Ingestion Pipeline ──────────────────┐ │
│  │  PyMuPDF Extractor → LangChain Recursive Chunker       │ │
│  │  → SentenceTransformer (all-MiniLM-L6-v2) Encoder      │ │
│  │  → FAISS IndexFlatL2 Store                              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────── RAG Orchestration ───────────────────┐ │
│  │  Query Embed → FAISS Top-K Search → Context Assembly    │ │
│  │  → Groq LLaMA 3.3 70B → Confidence + Citations         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │  SQLite DB  │  │ FAISS Index│  │ File Storage (uploads/)│ │
│  └────────────┘  └────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### RAG Pipeline Flow

1. **Ingestion** — PDF/DOCX → text extraction → recursive chunking (1000 chars, 200 overlap) → sentence embedding → FAISS indexing
2. **Retrieval** — User query → embedding → FAISS cosine similarity search → top-K chunk retrieval
3. **Generation** — Retrieved context + user question → Groq LLaMA 3.3 70B → grounded answer with citations + confidence score

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | Async REST API framework |
| **SQLAlchemy + SQLite** | Relational data & document metadata storage |
| **FAISS** (Facebook AI Similarity Search) | Dense vector similarity search |
| **SentenceTransformers** (`all-MiniLM-L6-v2`) | 384-dim text embeddings |
| **Groq API** (`llama-3.3-70b-versatile`) | LLM for answer generation, summarization, comparison |
| **PyMuPDF (fitz)** | PDF text extraction |
| **python-docx** | DOCX text extraction |
| **LangChain** | Recursive text chunking |
| **langdetect** | Automatic language detection |
| **Pydantic** | Request/response validation |

### Frontend
| Technology | Purpose |
|---|---|
| **React 19** | UI component library |
| **Vite 8** | Dev server & bundler |
| **TailwindCSS 3** | Utility-first CSS with glassmorphic design system |
| **Framer Motion** | Smooth UI animations |
| **Axios** | HTTP client for API calls |
| **React Router v7** | Client-side routing |
| **Lucide React** | Icon library |
| **React Dropzone** | Drag-and-drop file upload |
| **React Markdown** | Markdown rendering for AI responses |

---

## Project Structure

```
PolicyPilot/
├── backend/
│   ├── app/
│   │   ├── api/                        # Route handlers
│   │   │   ├── routes_upload.py        # File upload & ingestion
│   │   │   ├── routes_query.py         # Single-shot Q&A
│   │   │   ├── routes_chat.py          # Multi-turn conversational Q&A
│   │   │   ├── routes_summary.py       # Document summarization
│   │   │   ├── routes_compare.py       # Document comparison
│   │   │   ├── routes_documents.py     # Document CRUD
│   │   │   ├── routes_repository.py    # External dataset import
│   │   │   ├── routes_analytics.py     # Usage analytics
│   │   │   └── routes_health.py        # Health check
│   │   ├── services/                   # Business logic
│   │   │   ├── rag_engine.py           # Central RAG orchestrator
│   │   │   ├── vector_store.py         # FAISS index wrapper
│   │   │   ├── embedder.py             # SentenceTransformer wrapper
│   │   │   ├── pdf_extractor.py        # PDF text extraction
│   │   │   ├── docx_extractor.py       # DOCX text extraction
│   │   │   ├── chunker.py             # Text chunking
│   │   │   ├── groq_client.py          # Groq API client
│   │   │   ├── language_utils.py       # Language detection
│   │   │   ├── summarizer.py           # Summarization service
│   │   │   ├── retriever.py            # Retrieval service
│   │   │   └── related_docs.py         # Related docs finder
│   │   ├── db/                         # Database layer
│   │   │   ├── database.py             # Engine & session setup
│   │   │   ├── models.py              # SQLAlchemy ORM models
│   │   │   └── schemas.py             # Pydantic schemas
│   │   ├── core/                       # Cross-cutting concerns
│   │   │   ├── exceptions.py           # Custom exception classes
│   │   │   └── logging_config.py       # Logging setup
│   │   ├── prompts/                    # LLM prompt templates
│   │   │   ├── qa_prompt.py
│   │   │   └── summary_prompt.py
│   │   ├── config.py                   # Settings (Pydantic BaseSettings)
│   │   └── main.py                     # FastAPI app entry point
│   ├── data/                           # Runtime data (gitignored)
│   │   ├── faiss_index/                # FAISS vector index files
│   │   └── policypilot.db             # SQLite database
│   ├── uploads/                        # Uploaded documents (gitignored)
│   ├── Dockerfile                      # Container build
│   ├── .env.example                    # Environment template
│   └── .env                            # Local secrets (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── pages/                      # Route-level page components
│   │   │   ├── UploadPage.jsx          # Document upload interface
│   │   │   ├── ChatPage.jsx            # Conversational Q&A
│   │   │   ├── SummaryPage.jsx         # Document summarization
│   │   │   ├── ComparePage.jsx         # Side-by-side document comparison
│   │   │   ├── DocumentsPage.jsx       # Document library
│   │   │   ├── DocumentViewerPage.jsx  # Single document viewer
│   │   │   ├── RepositoryPage.jsx      # External dataset browser
│   │   │   ├── AnalyticsPage.jsx       # Usage analytics dashboard
│   │   │   └── LoginPage.jsx           # Officer authentication
│   │   ├── components/                 # Reusable UI components
│   │   │   ├── Navbar.jsx              # Navigation bar
│   │   │   ├── ChatBubble.jsx          # Chat message bubble
│   │   │   ├── ChatHistorySidebar.jsx  # Session history panel
│   │   │   ├── ConfidenceBadge.jsx     # Color-coded confidence indicator
│   │   │   ├── SourceCitation.jsx      # Source reference card
│   │   │   ├── LanguageSelector.jsx    # EN/MR/HI language switcher
│   │   │   ├── UploadDropzone.jsx      # Drag-and-drop upload zone
│   │   │   ├── SummaryCard.jsx         # Structured summary display
│   │   │   ├── RelatedDocsList.jsx     # Related documents panel
│   │   │   ├── VoiceInputButton.jsx    # Speech-to-text input
│   │   │   └── ProtectedRoute.jsx      # Auth guard
│   │   ├── context/                    # React Context providers
│   │   │   └── ToastContext.jsx        # Toast notification system
│   │   ├── api/                        # API client functions
│   │   ├── hooks/                      # Custom React hooks
│   │   ├── styles/                     # CSS & design tokens
│   │   ├── App.jsx                     # Root application component
│   │   └── main.jsx                    # React entry point
│   ├── index.html                      # HTML shell
│   ├── vite.config.js                  # Vite configuration
│   ├── tailwind.config.js             # Tailwind design system
│   └── package.json                    # Node dependencies
│
├── docs/
│   └── architecture.md                 # Technical architecture document
├── .gitignore
└── README.md                           # ← You are here
```

---

## Getting Started

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+ and **npm**
- **Groq API Key** — Get one free at [console.groq.com](https://console.groq.com)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/PolicyPilot.git
cd PolicyPilot
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

**`.env` configuration:**

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
DATABASE_URL=sqlite:///./data/policypilot.db
VECTOR_STORE_PATH=./data/faiss_index
```

**Start the backend server:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### 4. Docker Deployment (Optional)

```bash
cd backend
docker build -t policypilot-backend .
docker run -p 8000:8000 --env-file .env policypilot-backend
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/upload` | Upload PDF/DOCX document |
| `POST` | `/api/query` | Single-shot RAG Q&A |
| `POST` | `/api/chat/sessions` | Create new chat session |
| `POST` | `/api/chat/sessions/{id}/messages` | Send message in session |
| `GET` | `/api/chat/sessions` | List chat sessions |
| `GET` | `/api/chat/sessions/{id}` | Get session with messages |
| `POST` | `/api/summary` | Generate document summary |
| `POST` | `/api/compare` | Compare two documents |
| `GET` | `/api/documents` | List all documents |
| `GET` | `/api/documents/{id}` | Get document details |
| `GET` | `/api/analytics/stats` | Get usage analytics |
| `GET` | `/api/repository/sources` | List external data sources |
| `GET` | `/api/repository/github` | Browse GitHub mahGRs repo |
| `POST` | `/api/repository/import` | Import external document |

> **Full interactive API docs:** `http://localhost:8000/docs` (Swagger UI)

---

## SRS Traceability Matrix

Mapping of implemented features to the SRS functional requirements:

### ✅ Implemented

| SRS Ref | Requirement | Implementation |
|---------|-------------|----------------|
| §3.1 FR1 | Centralized document repository | `routes_repository.py`, `DocumentsPage.jsx` |
| §3.1 FR2 | PDF/DOCX text extraction | `pdf_extractor.py`, `docx_extractor.py` |
| §3.1 FR3 | Metadata generation | `DocumentRecord` model (title, dept, doc#, date, category, lang) |
| §3.1 FR4 | Vector embeddings & indexing | `embedder.py`, `vector_store.py` (FAISS + id_map) |
| §3.2 FR1 | Semantic similarity search | `vector_store.py` → FAISS cosine search |
| §3.2 FR2 | Relevance-ranked results | Top-K retrieval with distance scoring |
| §3.2 FR4 | Source documents with scores | `SourceCitation.jsx`, `ConfidenceBadge.jsx` |
| §3.3 FR1 | RAG-based answer generation | `rag_engine.py` → Groq LLaMA 3.3 |
| §3.3 FR2 | Answers from authenticated docs only | Context-only generation with prompt guardrails |
| §3.3 FR3 | Source citations + conflict highlighting | Prompt instructions for `⚠️ Conflicting Policy Provisions` |
| §3.3 FR4 | Concise, context-aware responses | System prompt engineering in `rag_engine.py` |
| §3.3 FR5 | Notify when info unavailable | Fallback messaging when confidence < threshold |
| §3.4 FR1 | English & Marathi queries | `language_utils.py` + prompt-based multilingual |
| §3.4 FR2 | Response in preferred language | Language instruction in RAG prompt |
| §3.4 FR5 | Language switching | `LanguageSelector.jsx` |
| §3.5 FR2 | Document summarization | `summarize_document()` in `rag_engine.py` |
| §3.5 FR3 | Document comparison | `routes_compare.py`, `ComparePage.jsx` |
| §3.7 FR1 | Secure web portal | `LoginPage.jsx`, `ProtectedRoute.jsx` |
| §3.7 FR2 | Conversational AI chat | `ChatPage.jsx`, `routes_chat.py` |
| §3.7 FR3 | Conversation history | `ChatSession` / `ChatMessage` models, `ChatHistorySidebar.jsx` |
| §3.7 FR4 | View/download documents | `DocumentViewerPage.jsx`, `DocumentsPage.jsx` |
| §3.7 FR5 | User feedback on responses | Feedback UI integration |

### 🔶 Partially Implemented

| SRS Ref | Requirement | Status |
|---------|-------------|--------|
| §3.1 FR2 | OCR for scanned documents | PDF text extraction works; OCR (Tesseract) not integrated |
| §3.2 FR3 | Keyword + semantic search | Semantic search implemented; keyword fallback not yet added |
| §3.4 FR3 | Preserve govt terminology | Handled via prompt but no curated terminology glossary |
| §3.4 FR4 | Cross-language search | LLM handles translation; embeddings are monolingual |
| §3.5 FR1 | Explain GRs in simple language | LLM can simplify; no dedicated "simplify" mode |
| §3.5 FR4 | Recommend related documents | `related_docs.py` exists as placeholder |
| §3.5 FR5 | Identify superseded/amended GRs | `status` field exists; auto-detection not implemented |

### ❌ Not Yet Implemented

| SRS Ref | Requirement | Notes |
|---------|-------------|-------|
| §3.4 FR3 | Hindi language support | Prompt supports it; UI selector needs Hindi option |
| §3.5 FR6 | Administrative procedure guidance | Requires specialized prompt templates |
| §3.5 FR7 | Source-grounded recommendations | Needs enhanced RAG pipeline |
| §4 | ≤10s response time (NFR) | Not benchmarked |
| §4 | ≥95% uptime (NFR) | Needs monitoring setup |

---

## Dataset Sources

PolicyPilot integrates with official Maharashtra Government data sources:

| Source | URL | Type |
|--------|-----|------|
| Maharashtra GR Portal | [gr.maharashtra.gov.in](https://gr.maharashtra.gov.in/1145/Government-Resolutions) | Official portal |
| DTE Maharashtra | [dte.maharashtra.gov.in](https://dte.maharashtra.gov.in/government-resolutions-orders-letters-circulars-e/) | Official portal |
| orgpedia/mahGRs | [github.com/orgpedia/mahGRs](https://github.com/orgpedia/mahGRs) | Open dataset |

Documents can be imported directly from the **Repository** page in the UI, or uploaded manually as PDF/DOCX files.

---

## Screenshots

> Upload government documents, chat with the AI assistant, compare policies, and explore analytics — all from a premium glassmorphic interface.

*Screenshots coming soon — run the app locally to explore the interface.*

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is developed for the **Maharashtra Higher & Technical Education Department** as part of an AI-powered governance initiative.

---

<p align="center">
  Built with ❤️ for Maharashtra Government Officers
</p>
