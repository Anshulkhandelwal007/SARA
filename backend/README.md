# SARA Backend API

FastAPI backend service for Project SARA. This is the business logic layer that n8n workflows call for lead operations, scoring, and recommendations.

## Purpose

- Encapsulate all business logic away from n8n workflows
- Provide a clean API contract for lead operations
- Serve as the foundation for AI integration
- Maintain PostgreSQL as the system of record

## Architecture

```
n8n (Orchestration) → Backend API (Business Logic) → PostgreSQL (Data)
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Run locally:
```bash
python main.py
```

4. Run with Docker (add to docker-compose.yml):
```yaml
backend:
  build: ./backend
  ports:
    - "8000:8000"
  environment:
    - DATABASE_HOST=postgres
    - DATABASE_PORT=5432
    - DATABASE_NAME=sara_db
    - DATABASE_USER=sara_user
    - DATABASE_PASSWORD=${POSTGRES_PASSWORD}
  depends_on:
    - postgres
```

## API Endpoints

### Health
- `GET /health` - Health check

### Leads
- `POST /api/v1/leads/import-lead` - Import a lead with upsert logic
- `POST /api/v1/leads/score-lead` - Score a lead
- `POST /api/v1/leads/next-action` - Get recommended next action
- `POST /api/v1/leads/summarize-call` - Summarize a call transcript
- `POST /api/v1/leads/followup-decision` - Decide on follow-up

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

The backend is structured as:
- `main.py` - Application entry point
- `core/` - Configuration and database setup
- `models/` - SQLAlchemy ORM models
- `schemas/` - Pydantic request/response models
- `services/` - Business logic
- `routers/` - API route handlers
- `tests/` - Unit tests

## Current Status

- ✅ Skeleton structure created
- ✅ Health endpoint
- ✅ Lead import endpoint with upsert logic
- ✅ Mock scoring endpoint
- ✅ Mock next-action endpoint
- ✅ Mock call summary endpoint
- ✅ Mock followup decision endpoint
- 🔄 Real scoring logic (Phase 2)
- 🔄 Real recommendation engine (Phase 3)
- 🔄 AI integration (Phase 4)
