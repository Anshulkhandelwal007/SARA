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
from services.lead_service import LeadService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/import-lead", response_model=LeadImportResponse)
async def import_lead(lead_data: LeadImportRequest, db: Session = Depends(get_db)):
    """Import a lead with company and contact upsert logic."""
    service = LeadService(db)
    result = service.import_lead(lead_data)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result


@router.post("/score-lead", response_model=LeadScoreResponse)
async def score_lead(request: LeadScoreRequest, db: Session = Depends(get_db)):
    """Score a lead based on various factors."""
    service = LeadService(db)
    try:
        return service.score_lead(request.lead_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/next-action", response_model=NextActionResponse)
async def get_next_action(request: NextActionRequest, db: Session = Depends(get_db)):
    """Get recommended next action for a lead."""
    service = LeadService(db)
    try:
        return service.get_next_action(request.lead_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/summarize-call", response_model=CallSummaryResponse)
async def summarize_call(request: CallSummaryRequest, db: Session = Depends(get_db)):
    """Summarize a call transcript."""
    service = LeadService(db)
    try:
        return service.summarize_call(request.lead_id, request.call_transcript, request.call_duration_seconds)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/followup-decision", response_model=FollowupDecisionResponse)
async def decide_followup(request: FollowupDecisionRequest, db: Session = Depends(get_db)):
    """Decide whether to follow up and how."""
    service = LeadService(db)
    try:
        return service.decide_followup(request.lead_id, request.last_interaction_type, request.last_interaction_summary)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
