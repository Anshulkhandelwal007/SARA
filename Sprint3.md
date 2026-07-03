# Sprint 3 - Lead Intelligence + Follow-up Operations

## Overview

Sprint 3 transforms SARA from a lead import system into an operational sales intelligence system by adding lead prioritization, follow-up management, and dashboard capabilities.

## Objectives

1. **Lead Prioritization**: Implement explainable scoring logic to classify leads as Hot/Warm/Cold/Overdue
2. **Follow-up Engine**: Build endpoints for tracking due follow-ups and generating summaries
3. **Dashboard Data**: Create endpoints to power an operations dashboard
4. **n8n Orchestration**: Create workflows that fetch prioritized leads and generate summaries
5. **Documentation**: Update all documentation to reflect new capabilities
6. **Tests**: Add comprehensive tests for new functionality

## Deliverables

### 1. Lead Prioritization Engine

**Backend Implementation** (`backend/services/lead_service.py`):
- `calculate_priority_score(lead_id)` - Calculate priority score (0-100)
- Scoring factors:
  - Status score (30 points): Based on lead status (new, contacted, engaged, qualified, opportunity, customer)
  - Recency score (25 points): Based on days since last contact
  - Value score (20 points): Based on estimated deal value
  - Interaction score (15 points): Based on interaction count
  - Overdue score (10 points): Based on days overdue for follow-up
- Priority labels: Hot (70+), Warm (50-69), Cold (30-49), Overdue (override)
- Next action recommendations based on priority

**API Endpoint** (`backend/routers/leads.py`):
- `GET /api/v1/leads/priority/{lead_id}` - Get priority score for a specific lead

**Response Schema** (`backend/schemas/response.py`):
```python
class PriorityScoreResponse:
    lead_id: str
    score: int  # 0-100
    label: str  # Hot/Warm/Cold/Overdue
    reason: str
    next_action: str
    factors: dict  # Breakdown of scoring factors
```

### 2. Follow-up Engine

**Backend Implementation** (`backend/services/lead_service.py`):
- `get_followups_due(days_ahead)` - Get leads with due/overdue follow-ups
- `get_lead_timeline(lead_id)` - Get timeline of events for a lead

**API Endpoints** (`backend/routers/leads.py`):
- `GET /api/v1/leads/followups-due?days_ahead=7` - Get leads with follow-ups due
- `GET /api/v1/leads/{lead_id}/timeline` - Get lead timeline

**Response Schemas** (`backend/schemas/response.py`):
```python
class FollowupLead:
    lead_id: str
    contact_name: str
    company_name: str
    next_followup_at: str
    days_overdue: int
    priority_score: int
    priority_label: str
    last_contacted_at: str
    status: str

class FollowupsDueResponse:
    total_leads: int
    overdue_count: int
    due_today_count: int
    due_this_week_count: int
    leads: List[FollowupLead]

class TimelineEvent:
    event_type: str
    description: str
    timestamp: str
    actor: str
    details: dict

class TimelineResponse:
    lead_id: str
    contact_name: str
    company_name: str
    events: List[TimelineEvent]
```

### 3. Dashboard Data Endpoints

**Backend Implementation** (`backend/services/lead_service.py`):
- `get_dashboard_summary()` - Get summary statistics
- `get_recent_activities(limit)` - Get recent activities
- `get_hot_leads(limit)` - Get hot leads sorted by priority
- `get_overdue_leads(limit)` - Get overdue leads sorted by days overdue
- `get_dashboard_data()` - Get complete dashboard data

**API Endpoint** (`backend/routers/leads.py`):
- `GET /api/v1/leads/dashboard/summary` - Get complete dashboard data

**Response Schema** (`backend/schemas/response.py`):
```python
class DashboardSummary:
    total_leads: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    overdue_leads: int
    due_today: int
    due_this_week: int
    total_value: float

class RecentActivity:
    lead_id: str
    contact_name: str
    company_name: str
    activity_type: str
    activity_description: str
    timestamp: str

class DashboardResponse:
    summary: DashboardSummary
    recent_activities: List[RecentActivity]
    hot_leads: List[FollowupLead]
    overdue_leads: List[FollowupLead]
```

### 4. n8n Workflows

**New Workflows** (`workflows/exports/`):

1. **Dashboard Data Fetch** (`dashboard-data-fetch.json`):
   - Fetches dashboard data from backend API
   - Processes response
   - Returns summary, recent activities, hot leads, overdue leads

2. **Daily Call List** (`daily-call-list.json`):
   - Fetches follow-ups due from backend API
   - Sorts by priority score and days overdue
   - Generates readable call list summary
   - Manual trigger for on-demand call list generation

**Updated Workflow**:

1. **Daily Follow-up Summary** (`daily-followup-summary.json`):
   - Already exists from Sprint 2
   - Calls `/api/v1/leads/followups-due` endpoint
   - Generates daily summary at 9 AM
   - Saves summary to file
   - No business logic in n8n (orchestration only)

### 5. Architecture

**Lead Intelligence Flow**:
```
Google Sheets → n8n (Orchestration) → FastAPI Backend (Business Logic) → PostgreSQL
                                                    ↓
                                            Lead Prioritization Engine
                                                    ↓
                                            Follow-up Engine
                                                    ↓
                                            Dashboard Data
```

**Business Logic Location**:
- ✅ All scoring logic in FastAPI backend (`LeadService.calculate_priority_score`)
- ✅ All follow-up logic in FastAPI backend (`LeadService.get_followups_due`)
- ✅ All dashboard logic in FastAPI backend (`LeadService.get_dashboard_data`)
- ✅ n8n only orchestrates API calls and formats output
- ✅ No business logic in n8n workflows

### 6. API Endpoints Summary

**Sprint 3 New Endpoints**:
- `GET /api/v1/leads/priority/{lead_id}` - Get priority score
- `GET /api/v1/leads/followups-due` - Get follow-ups due
- `GET /api/v1/leads/{lead_id}/timeline` - Get lead timeline
- `GET /api/v1/leads/dashboard/summary` - Get dashboard data

**Sprint 2 Existing Endpoints**:
- `POST /api/v1/leads/import-lead` - Import single lead
- `POST /api/v1/leads/batch-import` - Batch import leads
- `POST /api/v1/leads/activity-log` - Log activity

### 7. Testing

**Test Coverage** (`backend/tests/test_lead_service.py`):
- Lead priority scoring tests (already implemented in Sprint 2)
- Follow-up detection tests (already implemented in Sprint 2)
- Lead ordering tests (already implemented in Sprint 2)
- Timeline generation tests (already implemented in Sprint 2)
- Dashboard summary tests (new)
- Hot leads retrieval tests (new)
- Overdue leads retrieval tests (new)
- Dashboard data endpoint tests (new)

### 8. Documentation Updates

**Files Updated**:
- `Sprint3.md` - This file
- `ROADMAP.md` - Sprint 3 status
- `SARA_BLUEPRINT.md` - Lead intelligence features
- `docs/architecture.md` - New endpoints
- `README.md` - New capabilities

## Sprint 2.5 Status

**Completed**:
- ✅ Google OAuth credential configured in n8n
- ✅ Google Workspace initialization workflow created
- ✅ SARA CRM Drive folder structure defined
- ✅ Lead Master spreadsheet structure defined
- ✅ Active Leads/Archived Leads/Follow-up Log tabs defined
- ✅ Lead Import workflow updated with column mapping
- ✅ Daily Follow-up workflow created and working

**Manual Steps Required**:
- User must run Google Workspace Initialization workflow in n8n
- User must configure Lead Import workflow with actual spreadsheet ID
- User must add sample data to Google Sheets
- User must test end-to-end import

## Success Criteria

- ✅ Lead prioritization logic implemented in backend
- ✅ Follow-up engine implemented in backend
- ✅ Dashboard data endpoints implemented in backend
- ✅ n8n workflows created for orchestration
- ✅ No business logic in n8n
- ✅ All business logic in FastAPI backend
- ✅ Documentation updated
- ⏳ Tests added (in progress)
- ⏳ Repository committed and pushed (pending)

## Next Steps

1. Complete test coverage for new endpoints
2. Commit and push all changes to develop branch
3. User completes manual Google Workspace setup
4. User tests end-to-end lead import
5. User activates n8n workflows for production use

## Risks

- **Low Risk**: Backend changes are additive, no breaking changes
- **Low Risk**: n8n workflows are new, don't affect existing functionality
- **Medium Risk**: Dashboard queries may need optimization for large datasets
- **Mitigation**: Add database indexes if performance issues arise

## Dependencies

- Sprint 2 lead prioritization implementation (completed)
- Sprint 2 follow-up reminder implementation (completed)
- Google OAuth configuration (completed)
- PostgreSQL database (operational)
- n8n instance (operational)
