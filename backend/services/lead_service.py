from sqlalchemy.orm import Session
from models.company import Company
from models.contact import Contact
from models.lead import Lead
from schemas.lead import LeadImportRequest, LeadImportResponse, LeadScoreResponse, NextActionResponse, CallSummaryResponse, FollowupDecisionResponse
from schemas.response import ImportLeadRequest, ImportLeadResponse, BatchImportResponse, ActivityLogRequest
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import re


class LeadService:
    def __init__(self, db: Session):
        self.db = db
    
    def validate_lead_data(self, lead_data: ImportLeadRequest) -> tuple[bool, List[str]]:
        """Validate lead data and return (is_valid, errors)."""
        errors = []
        
        # Validate email
        if not lead_data.email:
            errors.append("Email is required")
        elif not self._is_valid_email(lead_data.email):
            errors.append(f"Invalid email format: {lead_data.email}")
        
        # Validate company name
        if not lead_data.company_name or not lead_data.company_name.strip():
            errors.append("Company name is required")
        
        # Validate names
        if not lead_data.first_name or not lead_data.first_name.strip():
            errors.append("First name is required")
        if not lead_data.last_name or not lead_data.last_name.strip():
            errors.append("Last name is required")
        
        # Validate source
        if not lead_data.source or not lead_data.source.strip():
            errors.append("Source is required")
        
        # Validate phone format if provided
        if lead_data.phone and not self._is_valid_phone(lead_data.phone):
            errors.append(f"Invalid phone format: {lead_data.phone}")
        
        if lead_data.mobile and not self._is_valid_phone(lead_data.mobile):
            errors.append(f"Invalid mobile format: {lead_data.mobile}")
        
        return len(errors) == 0, errors
    
    def normalize_lead_data(self, lead_data: ImportLeadRequest) -> ImportLeadRequest:
        """Normalize lead data fields."""
        # Normalize email
        if lead_data.email:
            lead_data.email = lead_data.email.lower().strip()
        
        # Normalize names
        if lead_data.first_name:
            lead_data.first_name = lead_data.first_name.strip().title()
        if lead_data.last_name:
            lead_data.last_name = lead_data.last_name.strip().title()
        
        # Normalize company name
        if lead_data.company_name:
            lead_data.company_name = lead_data.company_name.strip()
        
        # Normalize website
        if lead_data.company_website:
            lead_data.company_website = lead_data.company_website.strip()
            if not lead_data.company_website.startswith(('http://', 'https://')):
                lead_data.company_website = 'https://' + lead_data.company_website
        
        # Normalize phone numbers
        if lead_data.phone:
            lead_data.phone = self._normalize_phone(lead_data.phone)
        if lead_data.mobile:
            lead_data.mobile = self._normalize_phone(lead_data.mobile)
        
        # Normalize source
        if lead_data.source:
            lead_data.source = lead_data.source.strip().lower()
        
        # Normalize status
        if lead_data.status:
            lead_data.status = lead_data.status.strip().lower()
        
        return lead_data
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone format (basic check)."""
        # Remove all non-numeric characters
        cleaned = re.sub(r'[^\d+]', '', phone)
        # Should have at least 10 digits
        return len(cleaned) >= 10
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number."""
        # Remove all non-numeric characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        return cleaned
    
    def import_lead_new(self, lead_data: ImportLeadRequest) -> ImportLeadResponse:
        """Import a lead with validation, normalization, and upsert logic."""
        try:
            # Validate data
            is_valid, errors = self.validate_lead_data(lead_data)
            if not is_valid:
                return ImportLeadResponse(
                    lead_id=None,
                    contact_id=None,
                    company_id=None,
                    is_new=False
                )
            
            # Normalize data
            lead_data = self.normalize_lead_data(lead_data)
            
            # Extract domain from website
            domain = None
            if lead_data.company_website:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(lead_data.company_website)
                    domain = parsed.netloc
                except:
                    pass
            
            # Upsert company
            company = self.db.query(Company).filter(
                Company.name == lead_data.company_name,
                Company.domain == domain
            ).first()
            
            if company:
                company_id = company.id
                is_new_company = False
            else:
                company = Company(
                    id=str(uuid.uuid4()),
                    name=lead_data.company_name,
                    website=lead_data.company_website,
                    domain=domain
                )
                self.db.add(company)
                self.db.commit()
                self.db.refresh(company)
                company_id = company.id
                is_new_company = True
            
            # Upsert contact
            contact = self.db.query(Contact).filter(
                Contact.email == lead_data.email
            ).first()
            
            if contact:
                contact_id = contact.id
                # Update contact if needed
                contact.company_id = company_id
                contact.phone = lead_data.phone
                contact.mobile = lead_data.mobile
                contact.title = lead_data.title
                self.db.commit()
                is_new_contact = False
            else:
                contact = Contact(
                    id=str(uuid.uuid4()),
                    company_id=company_id,
                    first_name=lead_data.first_name,
                    last_name=lead_data.last_name,
                    email=lead_data.email,
                    phone=lead_data.phone,
                    mobile=lead_data.mobile,
                    title=lead_data.title
                )
                self.db.add(contact)
                self.db.commit()
                self.db.refresh(contact)
                contact_id = contact.id
                is_new_contact = True
            
            # Check if lead exists
            lead = self.db.query(Lead).filter(
                Lead.contact_id == contact_id,
                Lead.source == lead_data.source
            ).first()
            
            if lead:
                lead_id = lead.id
                is_new_lead = False
            else:
                lead = Lead(
                    id=str(uuid.uuid4()),
                    contact_id=contact_id,
                    company_id=company_id,
                    source=lead_data.source,
                    status=lead_data.status or "new",
                    score=0,
                    estimated_value=lead_data.estimated_value
                )
                self.db.add(lead)
                self.db.commit()
                self.db.refresh(lead)
                lead_id = lead.id
                is_new_lead = True
            
            return ImportLeadResponse(
                lead_id=lead_id,
                contact_id=contact_id,
                company_id=company_id,
                is_new=is_new_lead
            )
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def batch_import_leads(self, leads: List[ImportLeadRequest], source: str) -> BatchImportResponse:
        """Batch import multiple leads."""
        imported = 0
        updated = 0
        failed = 0
        errors = []
        
        for i, lead_data in enumerate(leads):
            try:
                # Set source if not provided
                if not lead_data.source:
                    lead_data.source = source
                
                result = self.import_lead_new(lead_data)
                
                if result.is_new:
                    imported += 1
                else:
                    updated += 1
                    
            except Exception as e:
                failed += 1
                errors.append(f"Row {i+1}: {str(e)}")
        
        return BatchImportResponse(
            imported=imported,
            updated=updated,
            failed=failed,
            errors=errors
        )
    
    def log_activity(self, activity_data: ActivityLogRequest) -> bool:
        """Log activity to the database."""
        try:
            # For now, we'll just return True
            # In the future, this would write to an activity_log table
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def import_lead(self, lead_data: LeadImportRequest) -> LeadImportResponse:
        """Import a lead with company and contact upsert logic."""
        try:
            # Extract domain from website
            domain = None
            if lead_data.company_website:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(lead_data.company_website)
                    domain = parsed.netloc
                except:
                    pass
            
            # Upsert company
            company = self.db.query(Company).filter(
                Company.name == lead_data.company_name,
                Company.domain == domain
            ).first()
            
            if company:
                company_id = company.id
                is_new_company = False
            else:
                company = Company(
                    id=str(uuid.uuid4()),
                    name=lead_data.company_name,
                    website=lead_data.company_website,
                    domain=domain
                )
                self.db.add(company)
                self.db.commit()
                self.db.refresh(company)
                company_id = company.id
                is_new_company = True
            
            # Upsert contact
            contact = self.db.query(Contact).filter(
                Contact.email == lead_data.email
            ).first()
            
            if contact:
                contact_id = contact.id
                # Update contact if needed
                contact.company_id = company_id
                contact.phone = lead_data.phone
                contact.mobile = lead_data.mobile
                contact.title = lead_data.title
                self.db.commit()
                is_new_contact = False
            else:
                contact = Contact(
                    id=str(uuid.uuid4()),
                    company_id=company_id,
                    first_name=lead_data.first_name,
                    last_name=lead_data.last_name,
                    email=lead_data.email,
                    phone=lead_data.phone,
                    mobile=lead_data.mobile,
                    title=lead_data.title
                )
                self.db.add(contact)
                self.db.commit()
                self.db.refresh(contact)
                contact_id = contact.id
                is_new_contact = True
            
            # Check if lead exists
            lead = self.db.query(Lead).filter(
                Lead.contact_id == contact_id,
                Lead.source == lead_data.source
            ).first()
            
            if lead:
                lead_id = lead.id
                is_new_lead = False
                message = "Lead already exists, updated contact details"
            else:
                lead = Lead(
                    id=str(uuid.uuid4()),
                    contact_id=contact_id,
                    company_id=company_id,
                    source=lead_data.source,
                    status="new",
                    score=0,
                    estimated_value=lead_data.estimated_value
                )
                self.db.add(lead)
                self.db.commit()
                self.db.refresh(lead)
                lead_id = lead.id
                is_new_lead = True
                message = "Lead imported successfully"
            
            return LeadImportResponse(
                success=True,
                lead_id=lead_id,
                contact_id=contact_id,
                company_id=company_id,
                message=message,
                is_new=is_new_lead
            )
            
        except Exception as e:
            self.db.rollback()
            return LeadImportResponse(
                success=False,
                lead_id=None,
                contact_id=None,
                company_id=None,
                message=f"Import failed: {str(e)}",
                is_new=False
            )
    
    def score_lead(self, lead_id: str) -> LeadScoreResponse:
        """Score a lead based on various factors (mock implementation)."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise ValueError("Lead not found")
        
        # Mock scoring logic - will be replaced with real scoring engine
        factors = {
            "company_size": 20,
            "industry_fit": 15,
            "engagement_level": 10,
            "estimated_value": 25,
            "source_quality": 10
        }
        
        score = sum(factors.values())
        previous_score = lead.score
        
        # Determine tier
        if score >= 70:
            tier = "hot"
        elif score >= 40:
            tier = "warm"
        else:
            tier = "cold"
        
        # Update lead
        lead.score = score
        lead.tier = tier
        self.db.commit()
        
        return LeadScoreResponse(
            lead_id=lead_id,
            score=score,
            tier=tier,
            factors=factors,
            previous_score=previous_score
        )
    
    def get_next_action(self, lead_id: str) -> NextActionResponse:
        """Get recommended next action for a lead (mock implementation)."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise ValueError("Lead not found")
        
        # Mock recommendation logic - will be replaced with real engine
        if lead.tier == "hot":
            return NextActionResponse(
                lead_id=lead_id,
                recommended_action="call",
                channel="voice_call",
                priority="high",
                reason="Hot lead with high score",
                confidence=0.85,
                suggested_template="hot_lead_intro"
            )
        elif lead.tier == "warm":
            return NextActionResponse(
                lead_id=lead_id,
                recommended_action="email",
                channel="email",
                priority="normal",
                reason="Warm lead, nurture with email",
                confidence=0.70,
                suggested_template="warm_lead_nurture"
            )
        else:
            return NextActionResponse(
                lead_id=lead_id,
                recommended_action="wait",
                channel="none",
                priority="low",
                reason="Cold lead, wait for engagement",
                confidence=0.60,
                suggested_template=None
            )
    
    def summarize_call(self, lead_id: str, transcript: str, duration: int) -> CallSummaryResponse:
        """Summarize a call transcript (mock implementation)."""
        # Mock summarization - will be replaced with AI
        return CallSummaryResponse(
            lead_id=lead_id,
            summary="Lead expressed interest in product features and pricing. Follow-up meeting scheduled for next week.",
            key_points=[
                "Interested in enterprise features",
                "Budget approved for Q1",
                "Decision maker involved",
                "Competitor comparison ongoing"
            ],
            sentiment="positive",
            next_steps=[
                "Send pricing proposal",
                "Schedule demo with technical team",
                "Provide case studies"
            ]
        )
    
    def decide_followup(self, lead_id: str, last_interaction_type: str, summary: str) -> FollowupDecisionResponse:
        """Decide whether to follow up and how (mock implementation)."""
        # Mock decision logic - will be replaced with AI
        return FollowupDecisionResponse(
            lead_id=lead_id,
            should_followup=True,
            channel="email",
            timing="2_days",
            reason="Positive engagement detected, follow up recommended"
        )
