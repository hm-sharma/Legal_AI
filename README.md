# ⚖️ Legal AI Document Analyzer

> **Enterprise Dual-Perspective Contract Risk Scoring & PDF Coordinate Mapping Engine**

An AI-powered legal document audit workspace that detects predatory provisions, unilateral indemnification burdens, ambiguity traps, and missing contractual protections in vector PDF contracts. Features dynamic **Party Perspective Conditioning** (Service Provider / Vendor vs. Client / Buyer), **Google Gemini LLM Reasoning**, **Sentence Transformers Semantic Embeddings**, and **Physical PDF Bounding Box Localization**.

---

## 🌟 Key Features

- 🎯 **Visual PDF Coordinate Highlight Layer**: Automatically extracts vector geometry and overlays precise bounding box highlights $[x_0, y_0, x_1, y_1]$ directly onto rendered PDF canvas pages.
- ⚖️ **Dual-Perspective Role Conditioning**: Switch your bargaining perspective (*Service Provider*, *Client / Buyer*, *Disclosing Party*, *Receiving Party*) to dynamically recalculate Contract Safety Scores (0–100) and clause impacts.
- 🧠 **Google Gemini LLM Reasoning**: Utilizes Gemini 1.5 Flash structured Pydantic outputs to evaluate custom uploaded contracts, generate strategic attorney takeaways, and draft one-click copyable redline replacements.
- 📐 **Sentence Transformers Embeddings**: Uses `all-MiniLM-L6-v2` dense vector similarity matching against the **CUAD (Contract Understanding Atticus Dataset)** taxonomy to identify legal risk categories semantically.
- ⚡ **Preset Benchmark Samples**: Instant single-click audit suite with pre-generated *Master Services Agreement (MSA)* and *Mutual Non-Disclosure Agreement (NDA)* contracts.
- 🔴 **1-Click Redline Copying**: Interactive Span Inspector drawer providing attorney risk rationales and copyable redline replacements.

---

## 📁 Repository Structure

```text
legal-doc-analyzer/
├── README.md
├── .gitignore
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   └── database.py
│       ├── models/
│       │   ├── document.py
│       │   └── analysis.py
│       ├── schemas/
│       │   └── audit.py
│       ├── services/
│       │   ├── parser/
│       │   │   ├── pdf_loader.py
│       │   │   └── coordinate_mapper.py
│       │   ├── legal_engine/
│       │   │   ├── attorney_evaluator.py
│       │   │   ├── risk_scorer.py
│       │   │   └── embeddings_matcher.py
│       │   └── storage/
│       │       └── minio_client.py
│       ├── workers/
│       │   ├── celery_app.py
│       │   └── tasks.py
│       └── api/
│           ├── deps.py
│           └── v1/
│               ├── router.py
│               └── endpoints/
│                   └── documents.py
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── postcss.config.js
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   ├── page.tsx
        │   └── document/[id]/page.tsx
        ├── components/
        │   ├── viewer/
        │   │   ├── PdfViewer.tsx
        │   │   └── HighlightLayer.tsx
        │   └── analysis/
        │       ├── AnalysisSidebar.tsx
        │       ├── ClauseCard.tsx
        │       └── SpanInspector.tsx
        ├── hooks/
        │   ├── usePdfViewer.ts
        │   └── useAuditStream.ts
        └── lib/
            ├── api.ts
            └── types.ts
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend Framework** | Next.js 14 (App Router), React 18, TypeScript |
| **Styling & Icons** | Tailwind CSS 3, Lucide React, Glassmorphism UI |
| **Backend Framework** | Python 3.11, FastAPI, Uvicorn, Pydantic V2 |
| **PDF & OCR Engine** | PyMuPDF (`fitz`), ReportLab |
| **AI & NLP** | Google Gemini 1.5 Flash API, Sentence Transformers (`all-MiniLM-L6-v2`), PyTorch |
| **Database & Task Queue** | SQLAlchemy, SQLite / PostgreSQL, Celery, Redis |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10+
- **Node.js**: 18+

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Set Google Gemini API Key
set GEMINI_API_KEY=your_gemini_api_key_here  # Windows CMD
$env:GEMINI_API_KEY="your_gemini_api_key_here" # Windows PowerShell
export GEMINI_API_KEY="your_gemini_api_key_here" # Linux/macOS

# Start FastAPI Uvicorn Server
uvicorn app.main:app --reload --port 8000
```
Backend API will be running at `http://127.0.0.1:8000`.

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Next.js Development Server
npm run dev
```
Open `http://localhost:3000` in your web browser to start auditing commercial contracts.

---

## 📊 Dataset & AI Architecture

1. **CUAD Taxonomy**: Trained on standard risk categories from the open-source **Contract Understanding Atticus Dataset (CUAD)** (e.g. *Unilateral Indemnification*, *Limitation of Liability Caps*, *Background IP Forfeiture*, *Extended 90-Day Payment Terms*).
2. **Hybrid Reasoning Fallback**:
   - If `GEMINI_API_KEY` is provided, Gemini 1.5 Flash executes deep zero-shot legal evaluation.
   - If offline, the engine falls back to `SentenceTransformers` semantic similarity matching against pre-computed CUAD risk vectors.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
