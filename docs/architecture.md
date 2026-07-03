# SARA Architecture

## System Overview

SARA is a layered sales automation system with clear separation of concerns:
- **Orchestration Layer**: n8n manages workflows and external triggers
- **Business Logic Layer**: FastAPI backend handles rules, scoring, and decisions
- **Data Layer**: PostgreSQL is the single source of truth
- **Intelligence Layer**: AI services provide scoring and recommendations
- **Communication Layer**: External services deliver messages

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         External Sources                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Google Sheets│  │ Web Forms    │  │ CRM/API      │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      n8n (Orchestration)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Trigger → Validate → Call Backend API → Execute → Log  │  │
│  │  - No direct database access (Sprint 1)                  │  │
│  │  - Business logic in Backend API (Sprint 1)              │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Business Logic)                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  POST /import-lead (validation, normalization)           │  │
│  │  POST /batch-import (batch processing)                    │  │
│  │  POST /score-lead (lead scoring)                          │  │
│  │  POST /next-action (recommendations)                      │  │
│  │  POST /activity-log (logging)                              │  │
│  │  GET /health (health check)                                │  │
│  │  Standard response wrapper (Sprint 1)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   PostgreSQL    │ │   AI Services   │ │  Communication  │
│   (Data Layer)  │ │ (Intelligence)  │ │   Channels      │
│                 │ │                 │ │                 │
│ • leads         │ │ • Scoring       │ │ • Brevo (Email) │
│ • contacts      │ │ • Summarization │ │ • WhatsApp      │
│ • companies     │ │ • Recommendations│ │ • Voice Calls   │
│ • interactions  │ │                 │ │                 │
│ • followups     │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         pgAdmin UI                              │
│                    (Database Management)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Layer 1: Orchestration (n8n)

**Purpose**: Workflow automation and external integration

**Responsibilities**:
- Trigger workflows from external sources (webhooks, schedules)
- Validate incoming data format
- Call backend API for business operations
- Execute communication actions based on API responses
- Handle errors and retries
- Log workflow execution

**What it does NOT do**:
- Business logic (scoring, decisions)
- Data validation beyond format
- Direct database writes (goes through backend)
- AI processing

### Layer 2: Business Logic (FastAPI Backend)

**Purpose**: Encapsulate all business rules and decisions

**Responsibilities**:
- Lead ingestion with upsert logic
- Lead scoring based on configurable rules
- Next-action recommendations
- Follow-up decisions
- Call summarization (with AI integration)
- Data validation and normalization
- Database operations (CRUD)

**API Endpoints**:
- `GET /health` - Health check
- `POST /api/v1/leads/import-lead` - Import lead with upsert
- `POST /api/v1/leads/score-lead` - Score a lead
- `POST /api/v1/leads/next-action` - Get recommended action
- `POST /api/v1/leads/summarize-call` - Summarize call transcript
- `POST /api/v1/leads/followup-decision` - Decide on follow-up

### Layer 3: Data Persistence (PostgreSQL)

**Purpose**: Single source of truth for all data

**Responsibilities**:
- Store all lead, contact, and company data
- Track all communication history
- Maintain follow-up schedules
- Store AI-generated summaries
- Enable analytics and reporting

## Component Roles

### n8n (Workflow Orchestration)

**Purpose**: n8n is the orchestration layer, responsible for:
- Triggering workflows based on events (webhooks, schedules)
- Calling backend API for business operations
- Executing communication actions based on API responses
- Coordinating multi-channel communications
- Managing state and error handling
- Integrating with external APIs

**Key Responsibilities**:
- Lead intake from multiple sources
- Call backend API for lead import
- Call backend API for scoring and recommendations
- Execute communication via appropriate channel
- Log workflow execution
- Handle errors and retries

**Data Flow**:
1. External trigger → n8n webhook
2. n8n calls backend API to import lead
3. Backend API writes to PostgreSQL
4. n8n calls backend API for scoring
5. Backend API returns score and tier
6. n8n calls backend API for next action
7. Backend API returns recommendation
8. n8n executes communication based on recommendation
9. n8n logs workflow execution

### FastAPI Backend (Business Logic)

**Purpose**: Backend API encapsulates all business logic

**Key Responsibilities**:
- Lead ingestion with upsert logic
- Lead scoring based on configurable rules
- Next-action recommendations
- Follow-up decisions
- Call summarization (with AI integration)
- Data validation and normalization
- Database operations (CRUD)

**Data Flow**:
1. Receive API request from n8n
2. Validate and normalize data
3. Execute business logic (scoring, decisions)
4. Write to PostgreSQL
5. Return response to n8n

**API Endpoints**:
- `GET /health` - Health check with database connectivity
- `POST /api/v1/leads/import-lead` - Import lead with upsert
- `POST /api/v1/leads/score-lead` - Score a lead
- `POST /api/v1/leads/next-action` - Get recommended action
- `POST /api/v1/leads/summarize-call` - Summarize call transcript
- `POST /api/v1/leads/followup-decision` - Decide on follow-up

**Docker Integration**:
- Container name: `sara-backend`
- Port: 8000
- Depends on PostgreSQL service
- Environment variables for database connection
- Restart policy: unless-stopped

### PostgreSQL (Data Persistence)

**Purpose**: PostgreSQL serves as the single source of truth for all SARA data.

**Key Responsibilities**:
- Store lead information and status
- Track all communication history
- Maintain follow-up schedules
- Store company/organization data
- Enable analytics and reporting
- Provide data for AI model training

**Schema Overview**:
- `companies`: Organization/company information with duplicate prevention
- `contacts`: Individual people (can exist without being leads)
- `leads`: Sales opportunities linked to contacts
- `lead_interactions`: Complete audit trail of all lead touchpoints
- `email_history`: Detailed email tracking with delivery status
- `whatsapp_history`: WhatsApp message tracking
- `call_logs`: Voice call records and transcripts
- `followups`: Scheduled and completed follow-ups
- `ai_summaries`: AI-generated summaries of interactions
- `activity_log`: System-wide activity tracking

**Data Flow**:
1. Backend API writes lead data on import
2. Backend API updates lead status after scoring
3. Backend API logs each interaction
4. Backend API queries for lead history before decisions
5. Analytics queries for reporting

## Relationships

```
companies (1) ──────< (N) contacts
companies (1) ──────< (N) leads
contacts (1) ──────< (N) leads
leads (1) ──────< (N) lead_interactions
leads (1) ──────< (N) email_history
leads (1) ──────< (N) whatsapp_history
leads (1) ──────< (N) call_logs
leads (1) ──────< (N) followups
leads (1) ──────< (N) ai_summaries
lead_interactions (1) ──────< (N) email_history
lead_interactions (1) ──────< (N) whatsapp_history
lead_interactions (1) ──────< (N) call_logs
```

### pgAdmin (Database Management)

**Purpose**: pgAdmin provides a web-based interface for database administration.

**Key Responsibilities**:
- Visual database schema management
- Query execution and debugging
- Performance monitoring
- Backup and restore operations
- User and permission management

**Usage**:
- Development and debugging
- Ad-hoc data queries
- Schema modifications
- Backup verification

## Integration Points

### Google Sheets
- **Purpose**: Lead source and manual data entry
- **Integration**: n8n Google Sheets node
- **Data Flow**: Sheet changes → n8n webhook → PostgreSQL
- **Use Cases**: Manual lead entry, bulk imports, CRM sync

### Brevo (Sendinblue)
- **Purpose**: Email communication
- **Integration**: n8n HTTP node or Brevo node
- **Data Flow**: n8n decision → Brevo API → Email sent → Log to PostgreSQL
- **Use Cases**: Automated follow-up emails, newsletters

### WhatsApp Business API
- **Purpose**: Instant messaging
- **Integration**: n8n HTTP node with WhatsApp API
- **Data Flow**: n8n decision → WhatsApp API → Message sent → Log to PostgreSQL
- **Use Cases**: Quick follow-ups, appointment reminders

### AI Voice Calling
- **Purpose**: Voice communication with AI agents
- **Integration**: n8n HTTP node with voice API provider
- **Data Flow**: n8n decision → Voice API → Call placed → Transcript → Log to PostgreSQL
- **Use Cases**: Personalized outreach, qualification calls

## Data Flow Examples

### Lead Intake Flow
```
1. Lead enters system (Google Sheets/Web Form)
   ↓
2. n8n webhook triggered
   ↓
3. n8n validates data format
   ↓
4. n8n calls backend API: POST /api/v1/leads/import-lead
   ↓
5. Backend API validates, normalizes, and upserts to PostgreSQL
   ↓
6. Backend API returns lead_id, contact_id, company_id
   ↓
7. n8n calls backend API: POST /api/v1/leads/score-lead
   ↓
8. Backend API calculates score and tier
   ↓
9. Backend API updates lead in PostgreSQL
   ↓
10. Backend API returns score and tier
   ↓
11. n8n calls backend API: POST /api/v1/leads/next-action
   ↓
12. Backend API returns recommended action
   ↓
13. n8n schedules follow-up if recommended
```

### Follow-Up Execution Flow
```
1. Scheduled trigger fires in n8n
   ↓
2. n8n calls backend API: POST /api/v1/leads/next-action
   ↓
3. Backend API queries PostgreSQL for lead history
   ↓
4. Backend API applies decision logic
   ↓
5. Backend API returns recommended action and channel
   ↓
6. n8n executes communication via selected channel
   ↓
7. n8n logs interaction to PostgreSQL (via backend API)
   ↓
8. Backend API updates lead status
   ↓
9. If lead is hot, n8n sends notification to owner
```

## Security Considerations

- All credentials stored in environment variables (.env)
- n8n encryption key for sensitive data
- PostgreSQL connections within Docker network
- API keys managed via n8n credentials
- pgAdmin access protected by authentication
- No secrets committed to version control

## Scalability Considerations

### Current (Local Development)
- Single Docker Compose stack
- Shared PostgreSQL instance
- n8n with SQLite (default) or PostgreSQL

### Future (Production)
- Separate PostgreSQL instance (managed service)
- n8n clustered or cloud-hosted
- Redis for queue management
- Separate worker processes for heavy tasks
- Load balancer for n8n webhooks

## Monitoring and Observability

### Current
- Docker container logs
- n8n execution logs
- PostgreSQL query logs (if enabled)

### Future
- Application performance monitoring
- Error tracking (Sentry)
- Database performance monitoring
- Custom metrics dashboard
- Alerting for failures

## Backup Strategy

### Current
- Manual pgAdmin exports
- Docker volume snapshots

### Future
- Automated daily PostgreSQL backups
- n8n workflow exports
- Offsite backup storage
- Backup restoration testing
