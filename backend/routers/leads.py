from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.lead import (
    LeadImportRequest, LeadImportResponse,
    LeadScoreRequest, LeadScoreResponse,
    NextActionRequest, NextActionResponse,
    CallSummaryRequest, CallSummaryResponse,
    FollowupDecisionRequest, FollowupDecisionResponse
)
from schemas.response import (
    StandardResponse, ImportLeadRequest, ImportLeadResponse,
    BatchImportRequest, BatchImportResponse, ActivityLogRequest, HealthResponse,
    PriorityScoreResponse, FollowupsDueResponse, TimelineResponse
)
from services.lead_service import LeadService
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/import-lead", response_model=StandardResponse[ImportLeadResponse])
async def import_lead(lead_data: ImportLeadRequest, db: Session = Depends(get_db)):
    """Import a lead with validation, normalization, and upsert logic."""
    service = LeadService(db)
    try:
        result = service.import_lead_new(lead_data)
        return StandardResponse(
            success=True,
            data=result,
            message="Lead imported successfully",
            errors=None,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
    except Exception as e:
        return StandardResponse(
            success=False,
            data=None,
            message=f"Import failed: {str(e)}",
            errors=[str(e)],
            meta={"timestamp": datetime.utcnow().isoformat()}
        )


@router.post("/batch-import", response_model=StandardResponse[BatchImportResponse])
async def batch_import(request: BatchImportRequest, db: Session = Depends(get_db)):
    """Batch import multiple leads."""
    service = LeadService(db)
    try:
        result = service.batch_import_leads(request.leads, request.source)
        return StandardResponse(
            success=True,
            data=result,
            message=f"Batch import completed: {result.imported} imported, {result.updated} updated, {result.failed} failed",
            errors=result.errors if result.errors else None,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
    except Exception as e:
        return StandardResponse(
            success=False,
            data=None,
            message=f"Batch import failed: {str(e)}",
            errors=[str(e)],
            meta={"timestamp": datetime.utcnow().isoformat()}
        )


@router.post("/activity-log", response_model=StandardResponse[dict])
async def log_activity(activity_data: ActivityLogRequest, db: Session = Depends(get_db)):
    """Log activity to the database."""
    service = LeadService(db)
    try:
        result = service.log_activity(activity_data)
        return StandardResponse(
            success=True,
            data={"logged": result},
            message="Activity logged successfully",
            errors=None,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
    except Exception as e:
        return StandardResponse(
            success=False,
            data=None,
            message=f"Activity logging failed: {str(e)}",
            errors=[str(e)],
            meta={"timestamp": datetime.utcnow().isoformat()}
        )


@router.post("/score-lead", response_model=StandardResponse[LeadScoreResponse])
async def score_lead(request: LeadScoreRequest, db: Session = Depends(get_db)):
    """Score a lead based on various factors."""
    service = LeadService(db)
    try:
        result = service.score_lead(request.lead_id)
        return StandardResponse(
            success=True,
            data=result,
            message="Lead scored successfully",
            errors=None,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
    except ValueError as e:
        return StandardResponse(
            success=False,
            data=None,
            message=str(e),
            errors=[str(e)],
            meta={"timestamp": datetime.utcnow().isoformat()}
        )


@router.post("/next-action", response_model=StandardResponse[NextActionResponse])
async def get_next_action(request: NextActionRequest, db: Session = Depends(get_db)):
    """Get recommended next action for a lead."""
    service = LeadService(db)
    try:
        result = service.get_next_action(request.lead_id)
        return StandardResponse(
            success=True,
            data=result,
            message="Next action retrieved successfully",
            errors=None,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
    except ValueError as e:
        return StandardResponse(
            success=False,
            data=None,
            message=str(e),
            errors=[str(e)],
            meta={"timestamp": datetime.utcnow().isoformat()}
        )


@router.post("/summarize-call", response_model=StandardResponse[CallSummaryResponse])
async def summarize_call(request: CallSummaryRequest, db: Session = Depends(get_db)):
    """Summarize a call transcript."""
    service = LeadService(db)
    try:
        result = service.summarize_call(request.lead_id, request.call_transcript, request.call_duration_seconds)
        return StandardResponse(
            success=True,
            data=result,
            message="Call summarized successfully",
            errors=None,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
    except ValueError as e:
        return StandardResponse(
            success=False,
            data=None,
            message=str(e),
            errors=[str(e)],
            meta={"timestamp": datetime.utcnow().isoformat()}
        )


@router.post("/followup-decision", response_model=StandardResponse[FollowupDecisionResponse])
async def decide_followup(request: FollowupDecisionRequest, db: Session = Depends(get_db)):
    """Decide whether to follow up and how."""
    service = LeadService(db)
    try:
        result = service.decide_followup(request.lead_id, request.last_interaction_type, request.last_interaction_summary)
        return StandardResponse(
            success=True,
            data=result,
            message="Follow-up decision retrieved successfully",
            errors=None,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
    except ValueError as e:
        return StandardResponse(
            success=False,
            data=None,
            message=str(e),
            errors=[str(e)],
            meta={"timestamp": datetime.utcnow().isoformat()}
        )


@router.get("/priority/{lead_id}", response_model=StandardResponse[PriorityScoreResponse])
async def get_priority(lead_id: str, db: Session = Depends(get_db)):
    """Get priority score for a lead."""
    service = LeadService(db)
    try:
        result = service.calculate_priority_score(lead_id)
        return StandardResponse(
            success=True,
            data=result,
            message="Priority score calculated successfully",
            errors=None,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
    except ValueError as e:
        return StandardResponse(
            success=False,
            data=None,
            message=str(e),
            errors=[str(e)],
            meta={"timestamp": datetime.utcnow().isoformat()}
        )


@router.get("/followups-due", response_model=StandardResponse[FollowupsDueResponse])
async def get_followups_due(days_ahead: int = 7, db: Session = Depends(get_db)):
    """Get leads with due or overdue follow-ups."""
    service = LeadService(db)
    try:
        result = service.get_followups_due(days_ahead)
        return StandardResponse(
            success=True,
            data=result,
            message=f"Retrieved {result.total_leads} leads with follow-ups due",
            errors=None,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
    except Exception as e:
        return StandardResponse(
            success=False,
            data=None,
            message=f"Failed to retrieve follow-ups: {str(e)}",
            errors=[str(e)],
            meta={"timestamp": datetime.utcnow().isoformat()}
        )


@router.get("/{lead_id}/timeline", response_model=StandardResponse[TimelineResponse])
async def get_timeline(lead_id: str, db: Session = Depends(get_db)):
    """Get timeline of events for a lead."""
    service = LeadService(db)
    try:
        result = service.get_lead_timeline(lead_id)
        return StandardResponse(
            success=True,
            data=result,
            message="Timeline retrieved successfully",
            errors=None,
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
    except ValueError as e:
        return StandardResponse(
            success=False,
            data=None,
            message=str(e),
            errors=[str(e)],
            meta={"timestamp": datetime.utcnow().isoformat()}
        )
