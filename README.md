---
title: ProcurePilot
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---
# ProcurePilot

**An AI-Powered Procurement Copilot for Intelligent Request Analysis and Recommendations**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14%2B-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)](https://fastapi.tiangolo.com/)
[![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)](README.md)

---

## Overview

**ProcurePilot** is a production-grade AI procurement copilot that transforms natural language procurement requests into structured, actionable analysis and recommendations. It combines modern LLM capabilities (via Groq's llama-3.1-8b-instant model) with enterprise policy retrieval, risk evaluation, and intelligent recommendation generation.

### The Problem It Solves

Procurement teams spend significant time manually analyzing requests, cross-referencing policies, identifying risks, and crafting recommendations. This process is repetitive, error-prone, and slow. **ProcurePilot automates this workflow**, allowing procurement professionals to:

- ✅ Submit requests in natural language (no forms required)
- ✅ Automatically extract structured requirements
- ✅ Retrieve relevant policies in seconds
- ✅ Identify compliance risks and violations
- ✅ Get prioritized, actionable recommendations
- ✅ Track all analyses for audit and compliance

### Why It Matters

In enterprise procurement, policy compliance, risk management, and decision velocity are critical. ProcurePilot delivers:

- **Speed**: Analysis in seconds, not hours
- **Consistency**: AI-driven evaluation removes human bias
- **Compliance**: Every decision backed by policy context
- **Indian Procurement Ready**: Built-in support for GFR guidelines, GSTIN, PAN, and MSME/Udyam verification
- **Auditability**: Complete analysis trail for every request
- **Scalability**: Process unlimited requests without additional staff

---

## Key Features

🎯 **Natural Language Processing**
- Submit procurement requests in conversational language
- Automatically normalize and structure messy input

📋 **Requirement Extraction**
- Extract structured requirements from unstructured requests
- Identify technical specs, business constraints, and priorities

📚 **Policy Context Retrieval**
- Automatically retrieve relevant policies from ChromaDB
- Semantic search for policy relevance (not just keyword matching)
- Show supporting policy context for every recommendation

⚠️ **Risk Assessment**
- Identify policy violations and compliance risks
- Categorize risks by severity (Critical, High, Medium, Low)
- Suggest mitigation strategies

💡 **Smart Recommendations**
- Generate prioritized recommendations (P1, P2, P3)
- Include owner assignment and timeline estimates
- Backed by policy context and risk analysis

🎯 **Confidence Scoring**
- AI confidence score for each analysis (0-100%)
- Intelligent confidence calculation based on:
  - Request clarity and completeness
  - Policy context retrieved
  - Risk assessment findings
  - Supporting evidence quality
- Never returns 0% — always explainable

📊 **Request History & Audit Trail**
- View all submitted procurement requests
- Track request status (Submitted, Analyzed)
- Access historical analyses with full context
- Complete audit trail for compliance

🏢 **Vendor Onboarding & Compliance (Indian Context)**
- Dynamic Vendor Registry handling legal entities
- Automated GSTIN & PAN format validation and cross-checking
- MSME/Udyam classification and verification
- Visual compliance badges and approval routing rules

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer (Next.js)                 │
│  Dashboard │ Request Submission │ History │ Analysis View   │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              API Orchestration Layer (FastAPI)              │
│  POST /api/v1/procurement/analyze                           │
│  GET  /api/v1/procurement/requests                          │
│  GET  /api/v1/procurement/requests/{id}                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│         Data Processing Layer (LangGraph Workflow)          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │   Normalize  │ │   Extract    │ │  Evaluate    │        │
│  │   Request   │ │ Requirements │ │    Risk      │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│  ┌──────────────┐ ┌──────────────┐                         │
│  │   Retrieve   │ │   Generate   │                         │
│  │   Policies   │ │ Recommendations                         │
│  └──────────────┘ └──────────────┘                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│       Embeddings & Retrieval Layer (ChromaDB + Groq)        │
│  Vector Database │ Semantic Search │ LLM Calls              │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│            Database Layer (SQLite / PostgreSQL)             │
│  Procurement Requests │ Recommendation Logs │ Audit Trail   │
└─────────────────────────────────────────────────────────────┘
```

### Layered Architecture (7 Layers)

| Layer | Purpose | Technology |
|-------|---------|-----------|
| **Interface** | User interaction & visualization | Next.js, TypeScript, Tailwind CSS |
| **API Orchestration** | Request routing & endpoint management | FastAPI, Pydantic |
| **Data Processing** | Workflow orchestration & LLM chaining | LangGraph, LangChain |
| **Embeddings & Retrieval** | Vector search & semantic matching | ChromaDB, Groq API |
| **Database** | Persistent storage | SQLite (dev), PostgreSQL (prod) |
| **External Services** | Third-party integrations | Groq LLM, ChromaDB |
| **Testing & Observability** | Quality & monitoring | Logging, Tracing, Unit tests |

### How It Works

```
1. User submits procurement request (natural language)
                    ↓
2. NORMALIZE NODE: Parse & structure the request
   - Extract title, description, category, budget, urgency
   - Validate input
                    ↓
3. EXTRACT REQUIREMENTS NODE: Break down into structured requirements
   - Identify 3-7 key requirements
   - Assign priority (MUST_HAVE, SHOULD_HAVE, NICE_TO_HAVE)
                    ↓
4. RETRIEVE POLICIES NODE: Find relevant policy documents
   - Semantic search in ChromaDB
   - Rank by relevance score
   - Return top 3-5 most relevant policies
                    ↓
5. EVALUATE RISK NODE: Assess compliance & risks
   - Check requirement alignment with policies
   - Identify violations or gaps
   - Categorize risks (Critical → Low)
                    ↓
6. GENERATE RECOMMENDATIONS NODE: Create action plan
   - LLM generates prioritized recommendations
   - Calculates confidence score (based on analysis quality)
   - Produces executive summary
                    ↓
7. Response returned with:
   - Summary
   - Normalized request
   - Extracted requirements
   - Policy context
   - Risk flags
   - Recommendations
   - Confidence score (with explanation)
   - Metadata (processing time, request ID, trace ID)
                    ↓
8. Analysis stored in database for audit trail & history
```

---

## Tech Stack

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios with interceptors
- **State Management**: React Hooks (useEffect, useState)
- **Hosting**: Vercel (recommended)

### Backend
- **Framework**: FastAPI 0.100+
- **Language**: Python 3.9+
- **Async Runtime**: AsyncIO
- **ORM**: SQLAlchemy (async)
- **Validation**: Pydantic v2
- **Hosting**: Hugging Face Spaces (or any Python host)

### AI & LLM
- **LLM Provider**: Groq (ultra-fast inference)
- **Model**: llama-3.1-8b-instant
- **Orchestration**: LangGraph + LangChain
- **Vector DB**: ChromaDB (in-memory or persistent)

### Database
- **Development**: SQLite
- **Production**: PostgreSQL
- **ORM**: SQLAlchemy with async support

### DevOps & Deployment
- **Frontend Hosting**: Vercel
- **Backend Hosting**: Hugging Face Spaces (free tier available)
- **Container**: Docker support available
- **Environment**: .env-based configuration

---

## Folder Structure

```
ProcurePilot/
├── apps/
│   ├── api/                          # FastAPI backend
│   │   ├── app/
│   │   │   ├── agents/               # LangGraph workflow nodes
│   │   │   │   ├── nodes/
│   │   │   │   │   ├── normalize.py
│   │   │   │   │   ├── extract.py
│   │   │   │   │   ├── retrieve.py
│   │   │   │   │   ├── evaluate.py
│   │   │   │   │   └── recommend.py
│   │   │   │   ├── prompts/          # LLM prompt templates
│   │   │   │   ├── confidence.py     # Confidence calculation
│   │   │   │   ├── state.py          # Workflow state definition
│   │   │   │   └── workflow.py       # Main orchestration
│   │   │   ├── api/
│   │   │   │   └── v1/
│   │   │   │       ├── routes/       # API endpoints
│   │   │   │       └── schemas/      # Pydantic models
│   │   │   ├── core/
│   │   │   │   ├── config.py         # Settings & environment
│   │   │   │   ├── logging.py        # Logging setup
│   │   │   │   └── exceptions.py     # Custom exceptions
│   │   │   ├── db/
│   │   │   │   ├── models.py         # SQLAlchemy models
│   │   │   │   ├── repositories/     # Data access layer
│   │   │   │   └── session.py        # DB session management
│   │   │   ├── llm/
│   │   │   │   └── groq_client.py    # Groq API wrapper
│   │   │   └── main.py               # FastAPI app entry
│   │   ├── tests/                    # Unit & integration tests
│   │   ├── requirements.txt          # Python dependencies
│   │   ├── .env.example              # Environment template
│   │   └── Dockerfile                # Container config
│   │
│   └── web/                          # Next.js frontend
│       ├── app/
│       │   ├── dashboard/            # Main analysis page
│       │   ├── requests/             # Request history
│       │   │   └── [id]/             # Request detail page
│       │   ├── layout.tsx            # Root layout
│       │   └── page.tsx              # Home page
│       ├── components/
│       │   ├── procurement-request-form.tsx
│       │   ├── recommendation-panel.tsx
│       │   ├── request-history.tsx
│       │   ├── policy-snippets.tsx
│       │   ├── risk-flags.tsx
│       │   └── recommendation-items.tsx
│       ├── services/
│       │   └── api.ts                # API client
│       ├── types/
│       │   └── procurement.ts        # TypeScript interfaces
│       ├── lib/
│       │   └── utils.ts              # Utility functions
│       ├── styles/
│       │   └── globals.css           # Global styles
│       ├── .env.local.example        # Environment template
│       └── package.json
│
├── docs/
│   ├── images/                       # Screenshots & diagrams
│   ├── architecture.md               # Detailed architecture docs
│   ├── api-reference.md              # API documentation
│   └── deployment.md                 # Deployment guides
│
├── docker-compose.yml                # Local dev containers
├── .gitignore
├── README.md                         # This file
└── CONTRIBUTING.md                   # Contribution guidelines
```

---

## Screenshots

### 1. Home & Dashboard
![Dashboard](docs/images/dashboard.png)
*Main procurement analysis dashboard where users submit requests*

### 2. Request Submission Form
![Request Form](docs/images/request-form.png)
*Natural language procurement request form*

### 3. Analysis Results
![Analysis Results](docs/images/analysis-results.png)
*AI-generated analysis with confidence score, requirements, policies, and recommendations*

### 4. Request History
![Request History](docs/images/request-history.png)
*Historical view of all submitted procurement requests with status tracking*

### 5. Request Detail View
![Request Detail](docs/images/request-detail.png)
*Detailed analysis page with full context and embedded recommendations*

---

## Getting Started

### Prerequisites

- **Backend**: Python 3.9+, pip
- **Frontend**: Node.js 18+, npm or yarn
- **Optional**: Docker & Docker Compose for containerized development

### Backend Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/procurepilot.git
cd procurepilot/apps/api
```

#### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```bash
PROCUREPILOT_GROQ_API_KEY=gsk_your_api_key_here
PROCUREPILOT_GROQ_MODEL=llama-3.1-8b-instant
PROCUREPILOT_DATABASE_URL=sqlite:///./procurepilot.db
PROCUREPILOT_CHROMA_DB_PATH=./chroma_db
```

#### 5. Initialize the Database
```bash
python -c "from app.db.models import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"
```

#### 6. Load Sample Policies (Optional)
```bash
python scripts/load_policies.py
```

#### 7. Run the Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`  
API Docs: `http://localhost:8000/docs`

---

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd ../web
```

#### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

#### 3. Configure Environment Variables
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

#### 4. Run the Frontend Development Server
```bash
npm run dev
# or
yarn dev
```

Frontend will be available at: `http://localhost:3000`

---

## Running Locally

### Option 1: Separate Terminals

**Terminal 1 - Backend:**
```bash
cd apps/api
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd apps/web
npm run dev
```

Then visit `http://localhost:3000` in your browser.

### Option 2: Docker Compose

```bash
docker-compose up -d
```

This will start:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## Environment Variables

### Backend (.env)

```bash
# Application
PROCUREPILOT_APP_NAME=ProcurePilot
PROCUREPILOT_DEBUG=true
PROCUREPILOT_ENVIRONMENT=development
PROCUREPILOT_API_V1_PREFIX=/api/v1

# Server
PROCUREPILOT_HOST=0.0.0.0
PROCUREPILOT_PORT=8000

# Logging
PROCUREPILOT_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# CORS
PROCUREPILOT_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
PROCUREPILOT_CORS_CREDENTIALS=true
PROCUREPILOT_CORS_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
PROCUREPILOT_CORS_HEADERS=["*"]

# Database
PROCUREPILOT_DATABASE_URL=sqlite:///./procurepilot.db
# For PostgreSQL: postgresql://user:password@localhost:5432/procurepilot

# Groq LLM
PROCUREPILOT_GROQ_API_KEY=gsk_your_api_key_here
PROCUREPILOT_GROQ_MODEL=llama-3.1-8b-instant

# ChromaDB
PROCUREPILOT_CHROMA_DB_PATH=./chroma_db
PROCUREPILOT_CHROMA_COLLECTION_NAME=procurement_policies

# Feature Flags
PROCUREPILOT_ENABLE_AUTH=false
PROCUREPILOT_ENABLE_AUDIT_LOG=true
PROCUREPILOT_ENABLE_POLICY_RETRIEVAL=true
PROCUREPILOT_ENABLE_REQUEST_TRACING=true
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=ProcurePilot
NEXT_PUBLIC_DEBUG=true
```

---

## API Reference

### Submit a Procurement Request

**Endpoint**: `POST /api/v1/procurement/analyze`

**Request Body**:
```json
{
  "title": "Server purchase for data center upgrade",
  "description": "We need to purchase 10 high-performance servers with redundant power supplies, 48+ cores per server, support for VMware 8.0+. Budget is $500,000 USD. This is urgent - we need deployment within 2 weeks.",
  "category": "IT_HARDWARE",
  "budget": 500000,
  "urgency": "CRITICAL",
  "department": "Infrastructure",
  "preferred_supplier": "Dell"
}
```

**Response** (200 OK):
```json
{
  "request_id": "req-a1b2c3d4",
  "trace_id": "trace-xyz789",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "summary": "Server procurement request approved with conditions. Recommend obtaining supplier approval and reviewing VMware licensing requirements before proceeding.",
  "confidence_score": 0.82,
  "confidence_label": "HIGH",
  "confidence_reason": "Complete information provided, 3 policies retrieved, 5 requirements extracted",
  "recommendation_items": [
    {
      "id": "rec-1",
      "action": "Get supplier approval",
      "description": "Submit Dell for vendor approval through procurement team",
      "priority": "P1",
      "owner": "Procurement Manager",
      "timeline": "1 week"
    }
  ],
  "processing_time_ms": 3245.5
}
```

### Get Submitted Requests

**Endpoint**: `GET /api/v1/procurement/requests?skip=0&limit=50`

Returns list of submitted requests with status.

### Get Request Detail

**Endpoint**: `GET /api/v1/procurement/requests/{id}`

Returns full analysis with all details.

---

## Example Workflow

### Scenario: Enterprise IT Purchase

A procurement manager submits:

```
Title: "Need new laptops for engineering team expansion"

Description: "We're expanding our engineering team by 50 people over the next 
quarter. We need to procure 50 new laptops suitable for software development 
with strong performance specs. Budget is $80,000 total (~$1,600 per unit). 
We prefer Dell XPS or similar high-end models. This is moderately urgent - 
we need them delivered within 4-6 weeks."

Category: IT_HARDWARE
Budget: $80,000
Urgency: HIGH
Department: Engineering
Preferred Supplier: Dell
```

**System Output**:
- ✅ **Confidence**: 78% (HIGH) — Complete information, clear requirements
- ✅ **Summary**: "Recommended for approval pending security baseline verification"
- ✅ **3 Policies**: Full text with relevance scores
- ✅ **2 Risk Flags**: Highlighted with mitigation steps
- ✅ **3 Recommendations**: Prioritized action items

---

## Production-Grade Design

### Modularity
- Service-oriented architecture
- Repository pattern for data access
- Dependency injection throughout
- Independent, testable nodes

### Observability
- Structured logging with request tracking
- Correlation IDs for distributed tracing
- Detailed processing metrics
- Confidence explanations for transparency

### Extensibility
- Pluggable LLM providers
- Swappable vector databases
- Replaceable database backends
- Easy to add new workflow nodes

---

## Deployment

### Frontend Deployment (Vercel)
```bash
git push origin main
# Vercel auto-deploys
# Set env var: NEXT_PUBLIC_API_BASE_URL=https://your-backend.com
```

### Backend Deployment (Hugging Face Spaces or Docker)
1. Create a Space or container registry
2. Set environment variables (GROQ_API_KEY, DATABASE_URL)
3. Deploy via git push or docker push

---

## Testing

### Backend Tests
```bash
cd apps/api
pytest tests/ -v
```

### Frontend Tests
```bash
cd apps/web
npm test
```

---

## Future Roadmap

### Phase 2 (Completed)
- [x] Request History / Submitted Requests Views
- [x] Indian Procurement Readiness (GSTIN, PAN, MSME, GFR 2017)
- [x] Vendor Onboarding & Management Module
- [x] Dynamic Approval Matrix Engine

### Phase 3 (Completed)
- [x] Production-grade API validation and schema consistency
- [x] Advanced Confidence Scoring logic (penalizing missing vendors)
- [x] Security Hardening (Auth & Telemetry middleware placeholders)
- [x] Testing suite for Service, API, and Core logic
- [x] Portfolio-ready documentation and developer experience improvements

### Phase 4 (Future)
- [ ] Integration with procurement systems (SAP, Coupa, Ariba)
- [ ] Approval workflow automation
- [ ] Supplier performance tracking
- [ ] Cost optimization recommendations

### Phase 4 (Q4 2024+)
- [ ] Fine-tuned models for specific industries
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Real-time collaboration features

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with tests
4. **Commit** with clear messages
5. **Push** to the branch
6. **Open** a Pull Request

**Code Style**:
- Python: PEP 8, Black formatter
- TypeScript: ESLint + Prettier
- Commit messages: Conventional Commits

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author & Support

**ProcurePilot** is developed and maintained by [Your Name/Organization].

### Questions or Issues?

- 📧 **Email**: [hariktm05@gmail.com]

---

## Acknowledgments

- **Groq** for ultra-fast LLM inference
- **LangChain & LangGraph** for workflow orchestration
- **ChromaDB** for vector search capabilities
- **FastAPI & Next.js** communities for excellent frameworks

---

**Made with ❤️ for procurement professionals and AI enthusiasts**

⭐ If you find this project helpful, please consider giving it a star on GitHub!
