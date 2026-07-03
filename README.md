# Project SARA

**S**ales **A**utomation & **R**esponse **A**gent

An AI-powered sales follow-up system with a clean, modular architecture separating orchestration, business logic, and data persistence.

## Architecture Principles

SARA follows a strict separation of concerns to ensure maintainability and scalability:

- **PostgreSQL** = System of record (single source of truth)
- **n8n** = Workflow orchestration layer (automation glue)
- **Backend API** = Business logic layer (rules, scoring, decisions)
- **AI Services** = Intelligence layer (scoring, summarization, recommendations)
- **Communication Layer** = Delivery channels (email, WhatsApp, voice)

**Why this separation?**
- Business logic lives in code (backend), not in workflow nodes
- n8n orchestrates, it doesn't decide
- PostgreSQL remains the authoritative data source
- AI can be swapped without changing workflows
- Each layer can be tested and scaled independently

## What is SARA?

SARA is an intelligent sales automation system that:
- Captures leads from multiple sources (Google Sheets, web forms, etc.)
- Scores leads based on custom criteria
- Determines optimal follow-up timing and channel
- Executes follow-ups via email, WhatsApp, or AI voice calls
- Notifies you when hot leads need immediate attention
- Tracks all interactions in a centralized database

## Current Stack

- **PostgreSQL 16**: System of record for leads, contacts, companies, and interaction history
- **n8n**: Workflow orchestration engine for automation
- **FastAPI Backend**: Business logic layer for lead operations, scoring, and recommendations
- **pgAdmin**: Database management interface
- **Docker Compose**: Container orchestration for local development

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Git (for version control)

### Initial Setup

1. Clone or navigate to the SARA directory:
   ```bash
   cd /path/to/SARA
   ```

2. Copy the environment example:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your secure credentials:
   - Change all passwords to strong, unique values
   - Update the n8n encryption key (generate with: `openssl rand -base64 32`)
   - Set your preferred timezone

4. Start the containers:
   ```bash
   docker-compose up -d
   ```

### Accessing Services

- **n8n**: http://localhost:5678
  - Username: `admin` (or as set in `.env`)
  - Password: As set in `.env`

- **pgAdmin**: http://localhost:5050
  - Email: As set in `.env`
  - Password: As set in `.env`
  - Server name: `sara-postgres`
  - Host: `postgres`
  - Port: `5432`
  - Database: `sara_db`
  - Username: `sara_user`
  - Password: As set in `.env`

- **Backend API**: http://localhost:8000
  - Health check: http://localhost:8000/health
  - API docs: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

### Stopping the Stack

```bash
docker-compose down
```

### Resetting the Stack

To stop and remove all containers, networks, and volumes (⚠️ **deletes all data**):
```bash
docker-compose down -v
```

## Project Structure

```
SARA/
├── backend/              # FastAPI backend service (business logic)
│   ├── core/            # Configuration and database setup
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response models
│   ├── services/        # Business logic services
│   ├── routers/         # API route handlers
│   ├── tests/           # Unit tests
│   ├── requirements.txt  # Python dependencies
│   └── README.md        # Backend documentation
├── backups/              # Database backups
├── database/             # SQL schemas and migrations
│   ├── init/            # Initialization scripts
│   └── schema-documentation.md  # Database reference
├── docs/                 # Project documentation
│   └── architecture.md  # System design documentation
├── knowledge-base/       # AI training data and context
├── prompts/              # AI prompt templates
├── workflows/            # n8n workflow exports and specs
│   ├── exports/         # Workflow JSON exports
│   ├── lead-import-v1.md  # Lead Import workflow docs
│   └── lead-automation-workflow.md  # Automation workflow specs
├── scripts/              # Utility scripts
├── logs/                 # Application logs
├── ROADMAP.md            # Product roadmap and phases
├── .env                  # Environment variables (not committed)
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── docker-compose.yml    # Docker orchestration
└── README.md            # This file
```

## Next Phases

See [ROADMAP.md](ROADMAP.md) for detailed phases, milestones, and success metrics.

### Current Phase: Backend API Foundation
- ✅ Docker stack setup
- ✅ Database schema v2 (normalized CRM foundation)
- ✅ Lead Import v1 workflow
- ✅ Backend API skeleton with FastAPI
- ✅ API endpoints for lead operations
- ✅ Backend Docker integration
- ✅ Backend service running in Docker
- 🔄 n8n workflow integration with backend

### Upcoming Phases
- Phase 2: Lead Scoring Engine
- Phase 3: Next-Action Recommendation
- Phase 4: AI Integration Layer
- Phase 5: Communication Layer
- Phase 6: Advanced Automation

## Development Workflow

1. Business logic changes: Modify backend services and schemas
2. Workflow changes: Update n8n workflows to call backend API
3. Export workflows to `workflows/exports/` directory
4. Document workflow logic in `workflows/*.md`
5. Document any database changes in `database/`
6. Update prompts in `prompts/` as needed
7. Test thoroughly before committing

**Key Principle:** Keep business rules in the backend, not in n8n nodes.

## Importing Workflows

To import the Lead Import v1 workflow:
1. Open n8n at http://localhost:5678
2. Click "Import from File" or drag-and-drop
3. Select `workflows/exports/lead-import-v1.json`
4. Configure PostgreSQL credentials in n8n
5. Test with manual trigger

## Troubleshooting

### Port Conflicts
If port 5678 is in use, edit `.env` and change `N8N_PORT` to an available port.

### Database Connection Issues
Check that PostgreSQL is healthy:
```bash
docker-compose ps
```

### Reset n8n Data
To clear n8n workflows and credentials:
```bash
docker-compose down -v n8n_data
docker-compose up -d
```

## Security Notes

- Never commit `.env` to version control
- Use strong, unique passwords for production
- Rotate encryption keys periodically
- Keep dependencies updated
- Review n8n workflow permissions

## License

Internal project - All rights reserved

## Support

For issues or questions, refer to `docs/architecture.md` or contact the development team.
