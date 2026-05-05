# Backend Testing Guide

## Overview

ProcurePilot's backend includes comprehensive unit and integration tests using pytest, with mocked LLM and retrieval services for fast, deterministic testing.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and shared fixtures
├── utils.py                 # Test utilities
├── mocks/                   # Mock implementations
│   ├── groq_mock.py        # Mock Groq LLM client
│   └── retriever_mock.py   # Mock ChromaDB retriever
├── fixtures/               # Test data
│   └── data.py            # Sample data for tests
├── unit/                   # Unit tests
│   ├── test_llm_client.py
│   ├── test_procurement_service.py
│   └── test_repositories.py
└── integration/            # Integration tests
    ├── test_api_endpoints.py
    └── test_workflow.py
```

## Installation

### 1. Install Dependencies

```bash
cd apps/api
pip install -r requirements.txt
```

### 2. Verify Pytest Installation

```bash
pytest --version
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/unit/test_procurement_service.py
```

### Run Specific Test Class

```bash
pytest tests/unit/test_procurement_service.py::TestProcurementService
```

### Run Specific Test

```bash
pytest tests/unit/test_procurement_service.py::TestProcurementService::test_analyze_procurement_basic
```

### Run Tests with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run Only Unit Tests

```bash
pytest tests/unit/
```

### Run Only Integration Tests

```bash
pytest tests/integration/
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests with Logging

```bash
pytest -v --log-cli-level=INFO
```

## Test Organization

### Unit Tests

Unit tests focus on individual components:

- **test_llm_client.py** — Mock Groq client functionality
  - JSON extraction
  - Text generation
  - Call tracking
  
- **test_procurement_service.py** — Procurement service logic
  - Basic analysis
  - Database persistence
  - Validation
  
- **test_repositories.py** — Database repository operations
  - CRUD operations
  - Filtering and searching
  - Counting and aggregation

### Integration Tests

Integration tests verify end-to-end flows:

- **test_api_endpoints.py** — API endpoint functionality
  - Health checks (/health/live, /health/ready)
  - Procurement analysis (/procurement/analyze)
  - Error handling and validation
  
- **test_workflow.py** — LangGraph workflow execution
  - Complete 5-node workflow
  - State transitions
  - Error tracking

## Mocks

### MockGroqClient

Simulates Groq LLM responses without API calls:

```python
from tests.mocks.groq_mock import MockGroqClient

client = MockGroqClient()

# Extract JSON
result = await client.extract_json(
    prompt="...",
    system_prompt="You are a normalization assistant"
)

# Generate text
text = await client.generate_text(
    prompt="...",
    system_prompt="You are a summary generator"
)
```

**Features:**
- Context-aware responses based on prompt content
- Call tracking
- Reset capability

### MockRetriever

Simulates ChromaDB policy retrieval:

```python
from tests.mocks.retriever_mock import MockRetriever

retriever = MockRetriever()

# Retrieve by category
policies = await retriever.retrieve_policies(category="IT_HARDWARE")

# Retrieve by similarity
policies = await retriever.retrieve_by_similarity(query="hardware approval")
```

**Features:**
- Pre-loaded mock policies by category
- Keyword-based similarity matching
- Configurable result limits

## Fixtures

### conftest.py Fixtures

- **event_loop** — Async event loop for tests
- **test_db** — In-memory SQLite database session
- **settings** — Application settings
- **sample_request** — Sample procurement request
- **sample_analysis_response** — Sample API response

### Usage

```python
@pytest.mark.asyncio
async def test_something(test_db, sample_request):
    """Test using fixtures."""
    # test_db is an AsyncSession
    # sample_request is a dict with procurement data
    pass
```

## Test Data

Pre-defined test data in `tests/fixtures/data.py`:

- `SAMPLE_PROCUREMENT_REQUEST` — Valid request
- `SAMPLE_NORMALIZED_REQUEST` — Normalized version
- `SAMPLE_REQUIREMENTS` — Extracted requirements
- `SAMPLE_RISKS` — Risk assessments
- `SAMPLE_RECOMMENDATIONS` — Recommendations

## Environment Variables

Tests use in-memory SQLite (no env file needed):

```python
# In conftest.py
engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    ...
)
```

## Writing New Tests

### Unit Test Template

```python
import pytest
from app.some_module import SomeClass

class TestSomeClass:
    """Test SomeClass."""

    @pytest.fixture
    def instance(self):
        """Create instance."""
        return SomeClass()

    @pytest.mark.asyncio
    async def test_something(self, instance):
        """Test a specific behavior."""
        result = await instance.some_method()
        assert result is not None
```

### Integration Test Template

```python
import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

class TestSomeEndpoint:
    """Test API endpoint."""

    def test_endpoint_success(self, client):
        """Test successful response."""
        response = client.get("/api/v1/some/endpoint")
        assert response.status_code == 200
```

## Async Testing

All async tests use `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test async code."""
    result = await some_async_function()
    assert result
```

The `asyncio_mode = auto` in `pytest.ini` enables automatic event loop management.

## Coverage

Generate coverage reports:

```bash
# Terminal output
pytest --cov=app

# HTML report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## Troubleshooting

### "No module named 'app'"

Make sure you're in the `apps/api` directory and have installed dependencies:

```bash
cd apps/api
pip install -r requirements.txt
```

### "RuntimeError: no running event loop"

Tests should use `@pytest.mark.asyncio`. Ensure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio
```

### "Database is locked"

In-memory SQLite shouldn't lock, but if using file-based SQLite:

```bash
rm -f test.db
```

## CI/CD Integration

Add to GitHub Actions workflow:

```yaml
- name: Run tests
  run: |
    cd apps/api
    pip install -r requirements.txt
    pytest --cov=app --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Performance

Tests typically complete in < 5 seconds with mocked LLM and in-memory database.

## Next Steps

- Add tests for edge cases and error scenarios
- Increase coverage target (aim for > 80%)
- Add performance/load tests
- Add frontend component tests (Phase 6 continued)
