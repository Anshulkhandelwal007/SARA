from sqlalchemy.orm import Session
from models.company import Company
from models.contact import Contact
from models.lead import Lead
from schemas.lead import LeadImportRequest, LeadImportResponse, LeadScoreResponse, NextActionResponse, CallSummaryResponse, FollowupDecisionResponse
from schemas.response import ImportLeadRequest, ImportLeadResponse, BatchImportResponse, ActivityLogRequest, PriorityScoreResponse, FollowupLead, FollowupsDueResponse, TimelineEvent, TimelineResponse, DashboardSummary, RecentActivity, DashboardResponse
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
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
            reason="Lead showed positive engagement",
            suggested_message="Following up on our previous conversation..."
        )
    
    def calculate_priority_score(self, lead_id: str) -> PriorityScoreResponse:
        """Calculate priority score for a lead based on multiple factors."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")
        
        # Get contact and company info
        contact = self.db.query(Contact).filter(Contact.id == lead.contact_id).first()
        company = self.db.query(Company).filter(Company.id == lead.company_id).first() if lead.company_id else None
        
        # Scoring factors (simple, explainable logic)
        factors = {
            "status_score": 0,
            "recency_score": 0,
            "value_score": 0,
            "interaction_score": 0,
            "overdue_score": 0
        }
        
        # Status score (30 points max)
        status_weights = {
            "new": 10,
            "contacted": 20,
            "engaged": 30,
            "qualified": 35,
            "opportunity": 40,
            "customer": 50,
            "lost": 0,
            "churned": 0
        }
        factors["status_score"] = status_weights.get(lead.status, 10)
        
        # Recency score (25 points max) - based on last contact
        if lead.last_contacted_at:
            days_since_contact = (datetime.utcnow() - lead.last_contacted_at).days
            if days_since_contact <= 1:
                factors["recency_score"] = 25
            elif days_since_contact <= 3:
                factors["recency_score"] = 20
            elif days_since_contact <= 7:
                factors["recency_score"] = 15
            elif days_since_contact <= 14:
                factors["recency_score"] = 10
            else:
                factors["recency_score"] = 5
        else:
            factors["recency_score"] = 5
        
        # Value score (20 points max) - based on estimated value
        if lead.estimated_value:
            value = float(lead.estimated_value)
            if value >= 100000:
                factors["value_score"] = 20
            elif value >= 50000:
                factors["value_score"] = 15
            elif value >= 25000:
                factors["value_score"] = 10
            elif value >= 10000:
                factors["value_score"] = 5
            else:
                factors["value_score"] = 2
        else:
            factors["value_score"] = 0
        
        # Interaction score (15 points max) - based on interaction count
        if lead.interaction_count:
            if lead.interaction_count >= 5:
                factors["interaction_score"] = 15
            elif lead.interaction_count >= 3:
                factors["interaction_score"] = 10
            elif lead.interaction_count >= 1:
                factors["interaction_score"] = 5
            else:
                factors["interaction_score"] = 0
        else:
            factors["interaction_score"] = 0
        
        # Overdue score (10 points max) - based on follow-up due date
        if lead.next_followup_at:
            days_overdue = (datetime.utcnow() - lead.next_followup_at).days
            if days_overdue > 0:
                factors["overdue_score"] = min(10, days_overdue * 2)  # 2 points per day overdue, max 10
            else:
                factors["overdue_score"] = 0
        else:
            factors["overdue_score"] = 0
        
        # Calculate total score
        total_score = sum(factors.values())
        
        # Determine label
        if total_score >= 70:
            label = "Hot"
        elif total_score >= 50:
            label = "Warm"
        elif total_score >= 30:
            label = "Cold"
        else:
            label = "Cold"
        
        # Override label if overdue
        if lead.next_followup_at and (datetime.utcnow() - lead.next_followup_at).days > 0:
            label = "Overdue"
        
        # Generate reason
        reasons = []
        if factors["status_score"] >= 30:
            reasons.append("high status")
        if factors["recency_score"] >= 20:
            reasons.append("recent contact")
        if factors["value_score"] >= 15:
            reasons.append("high value")
        if factors["interaction_score"] >= 10:
            reasons.append("engaged")
        if factors["overdue_score"] > 0:
            reasons.append("overdue follow-up")
        
        reason = ", ".join(reasons) if reasons else "standard priority"
        
        # Recommend next action
        if label == "Hot" or label == "Overdue":
            next_action = "Call immediately"
        elif label == "Warm":
            next_action = "Send email within 24 hours"
        else:
            next_action = "Schedule follow-up for next week"
        
        return PriorityScoreResponse(
            lead_id=lead_id,
            score=min(100, total_score),
            label=label,
            reason=reason,
            next_action=next_action,
            factors=factors
        )
    
    def get_followups_due(self, days_ahead: int = 7) -> FollowupsDueResponse:
        """Get leads with due or overdue follow-ups, sorted by urgency."""
        now = datetime.utcnow()
        end_date = now + timedelta(days=days_ahead)
        
        # Query leads with follow-ups due
        leads = self.db.query(Lead).filter(
            Lead.next_followup_at.isnot(None),
            Lead.next_followup_at <= end_date
        ).order_by(Lead.next_followup_at.asc()).all()
        
        followup_leads = []
        overdue_count = 0
        due_today_count = 0
        due_this_week_count = 0
        
        for lead in leads:
            # Get contact and company info
            contact = self.db.query(Contact).filter(Contact.id == lead.contact_id).first()
            company = self.db.query(Company).filter(Company.id == lead.company_id).first() if lead.company_id else None
            
            # Calculate days overdue
            days_overdue = (now - lead.next_followup_at).days
            
            # Calculate priority score
            priority_response = self.calculate_priority_score(lead.id)
            
            # Count categories
            if days_overdue > 0:
                overdue_count += 1
            if days_overdue == 0:
                due_today_count += 1
            if days_overdue >= -7:
                due_this_week_count += 1
            
            followup_lead = FollowupLead(
                lead_id=lead.id,
                contact_name=f"{contact.first_name} {contact.last_name}" if contact else "Unknown",
                company_name=company.name if company else "Unknown",
                next_followup_at=lead.next_followup_at.isoformat() if lead.next_followup_at else None,
                days_overdue=days_overdue,
                priority_score=priority_response.score,
                priority_label=priority_response.label,
                last_contacted_at=lead.last_contacted_at.isoformat() if lead.last_contacted_at else None,
                status=lead.status
            )
            followup_leads.append(followup_lead)
        
        return FollowupsDueResponse(
            total_leads=len(followup_leads),
            overdue_count=overdue_count,
            due_today_count=due_today_count,
            due_this_week_count=due_this_week_count,
            leads=followup_leads
        )
    
    def get_lead_timeline(self, lead_id: str) -> TimelineResponse:
        """Get timeline of events for a lead."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")
        
        # Get contact and company info
        contact = self.db.query(Contact).filter(Contact.id == lead.contact_id).first()
        company = self.db.query(Company).filter(Company.id == lead.company_id).first() if lead.company_id else None
        
        events = []
        
        # Lead creation event
        events.append(TimelineEvent(
            event_type="created",
            description="Lead created",
            timestamp=lead.created_at.isoformat() if lead.created_at else None,
            actor="system",
            details={"source": lead.source}
        ))
        
        # Last contact event
        if lead.last_contacted_at:
            events.append(TimelineEvent(
                event_type="contact",
                description="Last contact made",
                timestamp=lead.last_contacted_at.isoformat(),
                actor="system",
                details={"interaction_count": lead.interaction_count}
            ))
        
        # Next follow-up event
        if lead.next_followup_at:
            events.append(TimelineEvent(
                event_type="scheduled",
                description="Follow-up scheduled",
                timestamp=lead.next_followup_at.isoformat(),
                actor="system",
                details={"status": lead.status}
            ))
        
        # Status change event (if status is not new)
        if lead.status != "new":
            events.append(TimelineEvent(
                event_type="status_change",
                description=f"Status changed to {lead.status}",
                timestamp=lead.updated_at.isoformat() if lead.updated_at else None,
                actor="system",
                details={"status": lead.status}
            ))
        
        # Sort events by timestamp
        events.sort(key=lambda x: x.timestamp if x.timestamp else "")
        
        return TimelineResponse(
            lead_id=lead_id,
            contact_name=f"{contact.first_name} {contact.last_name}" if contact else "Unknown",
            company_name=company.name if company else "Unknown",
            events=events
        )
    
    def get_dashboard_summary(self) -> DashboardSummary:
        """Get dashboard summary statistics."""
        now = datetime.utcnow()
        
        # Total leads
        total_leads = self.db.query(Lead).count()
        
        # Count by priority label (using scoring logic)
        all_leads = self.db.query(Lead).all()
        hot_count = 0
        warm_count = 0
        cold_count = 0
        overdue_count = 0
        due_today_count = 0
        due_this_week_count = 0
        total_value = 0.0
        
        for lead in all_leads:
            # Calculate priority
            priority = self.calculate_priority_score(lead.id)
            
            if priority.label == "Hot":
                hot_count += 1
            elif priority.label == "Warm":
                warm_count += 1
            elif priority.label == "Cold":
                cold_count += 1
            elif priority.label == "Overdue":
                overdue_count += 1
            
            # Count due today
            if lead.next_followup_at:
                days_diff = (lead.next_followup_at.date() - now.date()).days
                if days_diff == 0:
                    due_today_count += 1
                if 0 <= days_diff <= 7:
                    due_this_week_count += 1
            
            # Sum estimated value
            if lead.estimated_value:
                total_value += float(lead.estimated_value)
        
        return DashboardSummary(
            total_leads=total_leads,
            hot_leads=hot_count,
            warm_leads=warm_count,
            cold_leads=cold_count,
            overdue_leads=overdue_count,
            due_today=due_today_count,
            due_this_week=due_this_week_count,
            total_value=total_value
        )
    
    def get_recent_activities(self, limit: int = 10) -> List[RecentActivity]:
        """Get recent activities across all leads."""
        # For now, return activities based on lead creation and updates
        # In a full implementation, this would query an activity_log table
        leads = self.db.query(Lead).order_by(Lead.updated_at.desc()).limit(limit).all()
        
        activities = []
        for lead in leads:
            contact = self.db.query(Contact).filter(Contact.id == lead.contact_id).first()
            company = self.db.query(Company).filter(Company.id == lead.company_id).first() if lead.company_id else None
            
            activity = RecentActivity(
                lead_id=lead.id,
                contact_name=f"{contact.first_name} {contact.last_name}" if contact else "Unknown",
                company_name=company.name if company else "Unknown",
                activity_type="status_update",
                activity_description=f"Lead status: {lead.status}",
                timestamp=lead.updated_at.isoformat() if lead.updated_at else None
            )
            activities.append(activity)
        
        return activities
    
    def get_hot_leads(self, limit: int = 10) -> List[FollowupLead]:
        """Get hot leads sorted by priority."""
        all_leads = self.db.query(Lead).all()
        
        hot_leads_data = []
        for lead in all_leads:
            priority = self.calculate_priority_score(lead.id)
            if priority.label == "Hot":
                contact = self.db.query(Contact).filter(Contact.id == lead.contact_id).first()
                company = self.db.query(Company).filter(Company.id == lead.company_id).first() if lead.company_id else None
                
                days_overdue = 0
                if lead.next_followup_at:
                    days_overdue = (datetime.utcnow() - lead.next_followup_at).days
                
                hot_lead = FollowupLead(
                    lead_id=lead.id,
                    contact_name=f"{contact.first_name} {contact.last_name}" if contact else "Unknown",
                    company_name=company.name if company else "Unknown",
                    next_followup_at=lead.next_followup_at.isoformat() if lead.next_followup_at else None,
                    days_overdue=days_overdue,
                    priority_score=priority.score,
                    priority_label=priority.label,
                    last_contacted_at=lead.last_contacted_at.isoformat() if lead.last_contacted_at else None,
                    status=lead.status
                )
                hot_leads_data.append(hot_lead)
        
        # Sort by priority score descending
        hot_leads_data.sort(key=lambda x: x.priority_score, reverse=True)
        
        return hot_leads_data[:limit]
    
    def get_overdue_leads(self, limit: int = 10) -> List[FollowupLead]:
        """Get overdue leads sorted by days overdue."""
        now = datetime.utcnow()
        
        leads = self.db.query(Lead).filter(
            Lead.next_followup_at.isnot(None),
            Lead.next_followup_at < now
        ).order_by(Lead.next_followup_at.asc()).all()
        
        overdue_leads_data = []
        for lead in leads:
            contact = self.db.query(Contact).filter(Contact.id == lead.contact_id).first()
            company = self.db.query(Company).filter(Company.id == lead.company_id).first() if lead.company_id else None
            
            days_overdue = (now - lead.next_followup_at).days
            priority = self.calculate_priority_score(lead.id)
            
            overdue_lead = FollowupLead(
                lead_id=lead.id,
                contact_name=f"{contact.first_name} {contact.last_name}" if contact else "Unknown",
                company_name=company.name if company else "Unknown",
                next_followup_at=lead.next_followup_at.isoformat() if lead.next_followup_at else None,
                days_overdue=days_overdue,
                priority_score=priority.score,
                priority_label=priority.label,
                last_contacted_at=lead.last_contacted_at.isoformat() if lead.last_contacted_at else None,
                status=lead.status
            )
            overdue_leads_data.append(overdue_lead)
        
        # Sort by days overdue descending
        overdue_leads_data.sort(key=lambda x: x.days_overdue, reverse=True)
        
        return overdue_leads_data[:limit]
    
    def get_dashboard_data(self) -> DashboardResponse:
        """Get complete dashboard data."""
        summary = self.get_dashboard_summary()
        recent_activities = self.get_recent_activities(limit=10)
        hot_leads = self.get_hot_leads(limit=10)
        overdue_leads = self.get_overdue_leads(limit=10)
        
        return DashboardResponse(
            summary=summary,
            recent_activities=recent_activities,
            hot_leads=hot_leads,
            overdue_leads=overdue_leads
        )
