# ProcurePilot Backend README

## Quick Start

### 1. Install Dependencies

```bash
cd apps/api
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

**Required configuration:**
- `PROCUREPILOT_GROQ_API_KEY`: Get from https://console.groq.com/

### 3. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/api/v1/health/live`

### 4. Run Tests

```bash
pytest tests/ -v
```

## Project Structure

- `app/core/` — Application configuration, logging, middleware, exceptions
- `app/api/v1/` — API routes and schemas
- `app/services/` — Business logic layer (coming in Phase 3)
- `app/agents/` — LangGraph workflow orchestration (coming in Phase 3)
- `app/retrieval/` — ChromaDB integration (coming in Phase 4)
- `app/db/` — Database models and repositories (coming in Phase 4)
- `tests/` — Unit, integration, and mocking tests

## API Endpoints (Phase 2)

### Health & Readiness
- `GET /api/v1/health/live` — Liveness probe
- `GET /api/v1/health/ready` — Readiness probe  
- `GET /api/v1/health` — Health status

## Coming in Phase 3
- `/api/v1/procurement/analyze` — Main workflow endpoint

## Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `PROCUREPILOT_ENVIRONMENT` — development, staging, or production
- `PROCUREPILOT_GROQ_API_KEY` — Groq API key (required)
- `PROCUREPILOT_DATABASE_URL` — Database connection string
- `PROCUREPILOT_CORS_ORIGINS` — Allowed frontend origins

## Docker

### Build

```bash
docker build -t procurepilot-api:latest .
```

### Run

```bash
docker run -p 8000:8000 \
  -e PROCUREPILOT_GROQ_API_KEY=your_key \
  -e PROCUREPILOT_DATABASE_URL=sqlite:///./procurepilot.db \
  procurepilot-api:latest
```

### Hugging Face Spaces

See `DEPLOYMENT.md` for deployment instructions.

## Development

### Code Formatting

```bash
black app/
isort app/
```

### Type Checking

```bash
mypy app/
```

### Linting

```bash
flake8 app/
```

## Troubleshooting

### ImportError: No module named 'app'

Make sure you're running commands from the `apps/api/` directory.

### Groq API Key Error

1. Visit https://console.groq.com/
2. Sign up and generate an API key
3. Add it to `.env`: `PROCUREPILOT_GROQ_API_KEY=xxx`
4. Restart the server

### Database Connection Error

If using PostgreSQL, ensure the database is running and the URL is correct in `.env`.

For SQLite (default), ensure write permissions in the app directory.

## Next Steps

- Phase 3: Services, LangGraph agents, LLM integration
- Phase 4: Database models, repositories, ingestion service
- Phase 5: Frontend (Next.js)
- Phase 6: Integration and testing
