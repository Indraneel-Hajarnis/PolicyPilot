# PolicyPilot 🛡️✈️

**PolicyPilot** is an enterprise-grade, full-stack Retrieval-Augmented Generation (RAG) platform specifically engineered for policy, compliance, and legal document intelligence.

Powered by **FastAPI**, **FAISS**, **SentenceTransformers**, **Groq LLMs**, and a modern **React + Vite + Tailwind CSS** frontend.

---

## 🌟 Key Features

- 📑 **PDF Ingestion & Text Extraction**: High-fidelity page-by-page extraction via `PyMuPDF` with OCR fallback detection and language recognition.
- 🧩 **Semantic Text Chunking**: Recursive character splitting with page-number metadata preservation for exact source attribution.
- ⚡ **FAISS Vector Search**: High-performance cosine similarity vector store (`IndexFlatIP` on L2-normalized embeddings) with instant indexing and persistent storage.
- 🤖 **Groq LLM Q&A Engine**: Ultra-fast retrieval-grounded Q&A with strict confidence scoring (0.0 - 1.0) and page-level source citations.
- 📋 **Structured Executive Summaries**: Auto-generated briefs detailing key points, section breakdowns, deadlines, and actionable compliance steps.
- 🌐 **Multilingual Support**: Language detection via `langdetect` with LLM-powered real-time translation into 9+ target languages.
- 💎 **Modern Glassmorphic UI**: Sleek dark-mode aesthetic with custom design tokens, smooth animations, interactive dropzone, and responsive layout.

---

## 🏗️ Project Architecture

```
PolicyPilot/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint
│   │   ├── config.py                   # Pydantic environment configuration
│   │   ├── db/                         # SQLAlchemy models, schemas, database setup
│   │   ├── api/                        # FastAPI route handlers (upload, query, summary, docs, health)
│   │   ├── services/                   # RAG pipeline services (extractor, chunker, embedder, FAISS, Groq)
│   │   └── prompts/                    # System & QA prompt templates
│   ├── data/                           # Uploaded PDFs & FAISS vector index
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── api/client.js               # Axios client instance
│   │   ├── components/                 # Navbar, ChatBubble, SourceCitation, ConfidenceBadge, etc.
│   │   ├── context/AppContext.jsx      # Global React state provider
│   │   ├── hooks/useChat.js            # Custom Q&A chat hook
│   │   ├── pages/                      # Upload, Chat, Summary, Documents, DocumentViewer
│   │   └── styles/index.css            # Tailwind & glassmorphism design system
│   ├── package.json
│   └── vite.config.js
│
├── docs/architecture.md
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Environment Setup

Copy `.env.example` in the `backend/` directory to `.env` and insert your **Groq API Key**:

```bash
cd backend
cp .env.example .env
```
Edit `.env`:
```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

---

### 2. Backend Setup & Run

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs`

---

### 3. Frontend Setup & Run

Open a new terminal tab and navigate into the `frontend` folder:

```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📊 Verification & Health Check

You can verify the backend status at any time:
```bash
curl http://localhost:8000/api/health
```
Expected output:
```json
{
  "status": "healthy",
  "document_count": 0,
  "faiss_index_size": 0,
  "embedding_model": "all-MiniLM-L6-v2",
  "llm_model": "llama-3.3-70b-versatile"
}
```
