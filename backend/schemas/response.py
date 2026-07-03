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
