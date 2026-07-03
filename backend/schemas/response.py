from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class StandardResponse(BaseModel, Generic[T]):
    """Standard API response wrapper for all endpoints."""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[T] = Field(None, description="Response data payload")
    message: str = Field(..., description="Human-readable message")
    errors: Optional[List[str]] = Field(None, description="List of error messages if any")
    meta: Optional[dict] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": "123"},
                "message": "Operation successful",
                "errors": None,
                "meta": {"timestamp": "2026-07-03T00:00:00Z"}
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    database: str = Field(..., description="Database connection status")
    timestamp: str = Field(..., description="Current timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "timestamp": "2026-07-03T00:00:00Z"
            }
        }


class ImportLeadRequest(BaseModel):
    """Request for importing a single lead."""
    company_name: str = Field(..., description="Company name")
    company_website: Optional[str] = Field(None, description="Company website")
    first_name: str = Field(..., description="Contact first name")
    last_name: str = Field(..., description="Contact last name")
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    mobile: Optional[str] = Field(None, description="Contact mobile")
    title: Optional[str] = Field(None, description="Contact job title")
    source: str = Field(..., description="Lead source")
    estimated_value: Optional[float] = Field(None, description="Estimated deal value")
    status: str = Field(default="new", description="Lead status")
    custom_fields: Optional[dict] = Field(None, description="Custom fields")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Acme Corp",
                "company_website": "https://acme.com",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@acme.com",
                "phone": "+1234567890",
                "mobile": "+1234567890",
                "title": "CTO",
                "source": "google_sheets",
                "estimated_value": 50000.0,
                "status": "new",
                "custom_fields": {}
            }
        }


class ImportLeadResponse(BaseModel):
    """Response for lead import."""
    lead_id: str = Field(..., description="Lead ID")
    contact_id: str = Field(..., description="Contact ID")
    company_id: str = Field(..., description="Company ID")
    is_new: bool = Field(..., description="Whether this is a new lead")

    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "123e4567-e89b-12d3-a456-426614174000",
                "contact_id": "123e4567-e89b-12d3-a456-426614174001",
                "company_id": "123e4567-e89b-12d3-a456-426614174002",
                "is_new": True
            }
        }


class BatchImportRequest(BaseModel):
    """Request for batch importing leads."""
    leads: List[ImportLeadRequest] = Field(..., description="List of leads to import")
    source: str = Field(..., description="Import source")

    class Config:
        json_schema_extra = {
            "example": {
                "leads": [
                    {
                        "company_name": "Acme Corp",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john@acme.com",
                        "source": "google_sheets"
                    }
                ],
                "source": "google_sheets"
            }
        }


class BatchImportResponse(BaseModel):
    """Response for batch import."""
    imported: int = Field(..., description="Number of leads imported")
    updated: int = Field(..., description="Number of leads updated")
    failed: int = Field(..., description="Number of leads that failed")
    errors: List[str] = Field(default_factory=list, description="Error messages")

    class Config:
        json_schema_extra = {
            "example": {
                "imported": 10,
                "updated": 5,
                "failed": 2,
                "errors": ["Invalid email for row 3", "Missing company name for row 7"]
            }
        }


class ActivityLogRequest(BaseModel):
    """Request for logging activity."""
    entity_type: str = Field(..., description="Type of entity (lead, contact, company)")
    entity_id: str = Field(..., description="ID of the entity")
    action: str = Field(..., description="Action performed")
    actor: str = Field(..., description="Who performed the action")
    details: Optional[dict] = Field(None, description="Additional details")

    class Config:
        json_schema_extra = {
            "example": {
                "entity_type": "lead",
                "entity_id": "123e4567-e89b-12d3-a456-426614174000",
                "action": "imported",
                "actor": "Google Sheets Import",
                "details": {"source": "google_sheets"}
            }
        }


class PriorityScoreResponse(BaseModel):
    """Response for lead priority score."""
    lead_id: str = Field(..., description="Lead ID")
    score: int = Field(..., description="Priority score (0-100)")
    label: str = Field(..., description="Priority label (Hot/Warm/Cold/Overdue)")
    reason: str = Field(..., description="Reason for the score")
    next_action: str = Field(..., description="Recommended next action")
    factors: dict = Field(..., description="Scoring factors breakdown")

    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "123e4567-e89b-12d3-a456-426614174000",
                "score": 85,
                "label": "Hot",
                "reason": "High value lead with overdue follow-up",
                "next_action": "Call immediately",
                "factors": {
                    "status_score": 30,
                    "recency_score": 25,
                    "value_score": 20,
                    "interaction_score": 10
                }
            }
        }


class FollowupLead(BaseModel):
    """Lead with follow-up information."""
    lead_id: str = Field(..., description="Lead ID")
    contact_name: str = Field(..., description="Contact name")
    company_name: str = Field(..., description="Company name")
    next_followup_at: str = Field(..., description="Scheduled follow-up time")
    days_overdue: int = Field(..., description="Days overdue (negative if not overdue)")
    priority_score: int = Field(..., description="Priority score")
    priority_label: str = Field(..., description="Priority label")
    last_contacted_at: Optional[str] = Field(None, description="Last contact time")
    status: str = Field(..., description="Lead status")

    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "123e4567-e89b-12d3-a456-426614174000",
                "contact_name": "John Doe",
                "company_name": "Acme Corp",
                "next_followup_at": "2026-07-01T10:00:00Z",
                "days_overdue": 2,
                "priority_score": 85,
                "priority_label": "Hot",
                "last_contacted_at": "2026-06-28T15:30:00Z",
                "status": "qualified"
            }
        }


class FollowupsDueResponse(BaseModel):
    """Response for follow-ups due."""
    total_leads: int = Field(..., description="Total number of leads")
    overdue_count: int = Field(..., description="Number of overdue leads")
    due_today_count: int = Field(..., description="Number due today")
    due_this_week_count: int = Field(..., description="Number due this week")
    leads: List[FollowupLead] = Field(..., description="List of leads sorted by urgency")

    class Config:
        json_schema_extra = {
            "example": {
                "total_leads": 15,
                "overdue_count": 5,
                "due_today_count": 3,
                "due_this_week_count": 7,
                "leads": []
            }
        }


class TimelineEvent(BaseModel):
    """Timeline event for a lead."""
    event_type: str = Field(..., description="Type of event")
    description: str = Field(..., description="Event description")
    timestamp: str = Field(..., description="Event timestamp")
    actor: Optional[str] = Field(None, description="Who performed the action")
    details: Optional[dict] = Field(None, description="Additional details")

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "interaction",
                "description": "Email sent",
                "timestamp": "2026-07-01T10:00:00Z",
                "actor": "system",
                "details": {"channel": "email"}
            }
        }


class TimelineResponse(BaseModel):
    """Response for lead timeline."""
    lead_id: str = Field(..., description="Lead ID")
    contact_name: str = Field(..., description="Contact name")
    company_name: str = Field(..., description="Company name")
    events: List[TimelineEvent] = Field(..., description="Timeline events")

    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "123e4567-e89b-12d3-a456-426614174000",
                "contact_name": "John Doe",
                "company_name": "Acme Corp",
                "events": []
            }
        }


class DashboardSummary(BaseModel):
    """Dashboard summary statistics."""
    total_leads: int = Field(..., description="Total number of leads")
    hot_leads: int = Field(..., description="Number of hot leads")
    warm_leads: int = Field(..., description="Number of warm leads")
    cold_leads: int = Field(..., description="Number of cold leads")
    overdue_leads: int = Field(..., description="Number of overdue leads")
    due_today: int = Field(..., description="Number due today")
    due_this_week: int = Field(..., description="Number due this week")
    total_value: float = Field(..., description="Total estimated value of all leads")

    class Config:
        json_schema_extra = {
            "example": {
                "total_leads": 100,
                "hot_leads": 25,
                "warm_leads": 40,
                "cold_leads": 35,
                "overdue_leads": 10,
                "due_today": 5,
                "due_this_week": 20,
                "total_value": 2500000.0
            }
        }


class RecentActivity(BaseModel):
    """Recent activity item."""
    lead_id: str = Field(..., description="Lead ID")
    contact_name: str = Field(..., description="Contact name")
    company_name: str = Field(..., description="Company name")
    activity_type: str = Field(..., description="Type of activity")
    activity_description: str = Field(..., description="Activity description")
    timestamp: str = Field(..., description="Activity timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": "123e4567-e89b-12d3-a456-426614174000",
                "contact_name": "John Doe",
                "company_name": "Acme Corp",
                "activity_type": "status_change",
                "activity_description": "Status changed to qualified",
                "timestamp": "2026-07-03T10:00:00Z"
            }
        }


class DashboardResponse(BaseModel):
    """Dashboard data response."""
    summary: DashboardSummary = Field(..., description="Summary statistics")
    recent_activities: List[RecentActivity] = Field(..., description="Recent activities")
    hot_leads: List[FollowupLead] = Field(..., description="Hot leads")
    overdue_leads: List[FollowupLead] = Field(..., description="Overdue leads")

    class Config:
        json_schema_extra = {
            "example": {
                "summary": {
                    "total_leads": 100,
                    "hot_leads": 25,
                    "warm_leads": 40,
                    "cold_leads": 35,
                    "overdue_leads": 10,
                    "due_today": 5,
                    "due_this_week": 20,
                    "total_value": 2500000.0
                },
                "recent_activities": [],
                "hot_leads": [],
                "overdue_leads": []
            }
        }
