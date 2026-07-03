from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    website: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    revenue_range: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[int] = None
    notes: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContactBase(BaseModel):
    company_id: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    mobile: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    linkedin_url: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeadBase(BaseModel):
    contact_id: str
    company_id: Optional[str] = None
    source: str = Field(..., pattern="^(google_sheets|web_form|api|referral|manual)$")
    status: Optional[str] = Field(default="new", pattern="^(new|contacted|engaged|qualified|opportunity|customer|churned|lost)$")
    score: Optional[int] = Field(default=0, ge=0, le=100)
    tier: Optional[str] = Field(None, pattern="^(hot|warm|cold)$")
    assigned_to: Optional[str] = None
    estimated_value: Optional[Decimal] = None
    probability: Optional[int] = Field(default=0, ge=0, le=100)
    expected_close_date: Optional[date] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LeadCreate(LeadBase):
    pass


class LeadResponse(LeadBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_contacted_at: Optional[datetime] = None
    next_followup_at: Optional[datetime] = None
    interaction_count: int = 0
    notified_hot: bool = False
    notified_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LeadImportRequest(BaseModel):
    company_name: str = Field(..., min_length=1)
    company_website: Optional[str] = None
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr
    phone: Optional[str] = None
    mobile: Optional[str] = None
    title: Optional[str] = None
    source: str = Field(..., pattern="^(google_sheets|web_form|api|referral|manual)$")
    estimated_value: Optional[Decimal] = None


class LeadImportResponse(BaseModel):
    success: bool
    lead_id: Optional[str] = None
    contact_id: Optional[str] = None
    company_id: Optional[str] = None
    message: str
    is_new: bool


class LeadScoreRequest(BaseModel):
    lead_id: str


class LeadScoreResponse(BaseModel):
    lead_id: str
    score: int
    tier: str
    factors: Dict[str, Any]
    previous_score: Optional[int] = None


class NextActionRequest(BaseModel):
    lead_id: str


class NextActionResponse(BaseModel):
    lead_id: str
    recommended_action: str
    channel: str
    priority: str
    reason: str
    confidence: float
    suggested_template: Optional[str] = None


class CallSummaryRequest(BaseModel):
    lead_id: str
    call_transcript: str
    call_duration_seconds: int


class CallSummaryResponse(BaseModel):
    lead_id: str
    summary: str
    key_points: list[str]
    sentiment: str
    next_steps: list[str]


class FollowupDecisionRequest(BaseModel):
    lead_id: str
    last_interaction_type: str
    last_interaction_summary: str


class FollowupDecisionResponse(BaseModel):
    lead_id: str
    should_followup: bool
    channel: str
    timing: str
    reason: str
