import pytest
from sqlalchemy.orm import Session
from services.lead_service import LeadService
from schemas.response import ImportLeadRequest, BatchImportRequest, ActivityLogRequest
from models.company import Company
from models.contact import Contact
from models.lead import Lead


class TestLeadValidation:
    """Test lead data validation."""
    
    def test_valid_lead_data(self, db_session: Session):
        """Test validation of valid lead data."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            company_website="https://acme.com",
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
            phone="+1234567890",
            mobile="+1234567890",
            title="CTO",
            source="google_sheets",
            estimated_value=50000.0,
            status="new"
        )
        
        is_valid, errors = service.validate_lead_data(lead_data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_missing_email(self, db_session: Session):
        """Test validation fails with missing email."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="John",
            last_name="Doe",
            email="",
            source="google_sheets"
        )
        
        is_valid, errors = service.validate_lead_data(lead_data)
        
        assert is_valid is False
        assert any("Email is required" in error for error in errors)
    
    def test_invalid_email_format(self, db_session: Session):
        """Test validation fails with invalid email format."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="John",
            last_name="Doe",
            email="invalid-email",
            source="google_sheets"
        )
        
        is_valid, errors = service.validate_lead_data(lead_data)
        
        assert is_valid is False
        assert any("Invalid email format" in error for error in errors)
    
    def test_missing_company_name(self, db_session: Session):
        """Test validation fails with missing company name."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="",
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
            source="google_sheets"
        )
        
        is_valid, errors = service.validate_lead_data(lead_data)
        
        assert is_valid is False
        assert any("Company name is required" in error for error in errors)
    
    def test_missing_first_name(self, db_session: Session):
        """Test validation fails with missing first name."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="",
            last_name="Doe",
            email="john@acme.com",
            source="google_sheets"
        )
        
        is_valid, errors = service.validate_lead_data(lead_data)
        
        assert is_valid is False
        assert any("First name is required" in error for error in errors)
    
    def test_missing_last_name(self, db_session: Session):
        """Test validation fails with missing last name."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="John",
            last_name="",
            email="john@acme.com",
            source="google_sheets"
        )
        
        is_valid, errors = service.validate_lead_data(lead_data)
        
        assert is_valid is False
        assert any("Last name is required" in error for error in errors)
    
    def test_missing_source(self, db_session: Session):
        """Test validation fails with missing source."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
            source=""
        )
        
        is_valid, errors = service.validate_lead_data(lead_data)
        
        assert is_valid is False
        assert any("Source is required" in error for error in errors)
    
    def test_invalid_phone_format(self, db_session: Session):
        """Test validation fails with invalid phone format."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
            phone="123",
            source="google_sheets"
        )
        
        is_valid, errors = service.validate_lead_data(lead_data)
        
        assert is_valid is False
        assert any("Invalid phone format" in error for error in errors)


class TestLeadNormalization:
    """Test lead data normalization."""
    
    def test_normalize_email(self, db_session: Session):
        """Test email normalization."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="John",
            last_name="Doe",
            email="JOHN@ACME.COM",
            source="google_sheets"
        )
        
        normalized = service.normalize_lead_data(lead_data)
        
        assert normalized.email == "john@acme.com"
    
    def test_normalize_names(self, db_session: Session):
        """Test name normalization."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="john",
            last_name="doe",
            email="john@acme.com",
            source="google_sheets"
        )
        
        normalized = service.normalize_lead_data(lead_data)
        
        assert normalized.first_name == "John"
        assert normalized.last_name == "Doe"
    
    def test_normalize_website(self, db_session: Session):
        """Test website normalization."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            company_website="acme.com",
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
            source="google_sheets"
        )
        
        normalized = service.normalize_lead_data(lead_data)
        
        assert normalized.company_website == "https://acme.com"
    
    def test_normalize_phone(self, db_session: Session):
        """Test phone normalization."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
            phone="+1 (234) 567-8900",
            source="google_sheets"
        )
        
        normalized = service.normalize_lead_data(lead_data)
        
        assert "+" in normalized.phone
        assert " " not in normalized.phone
        assert "(" not in normalized.phone
        assert ")" not in normalized.phone
    
    def test_normalize_source(self, db_session: Session):
        """Test source normalization."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
            source="GOOGLE_SHEETS"
        )
        
        normalized = service.normalize_lead_data(lead_data)
        
        assert normalized.source == "google_sheets"
    
    def test_normalize_status(self, db_session: Session):
        """Test status normalization."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Acme Corp",
            first_name="John",
            last_name="Doe",
            email="john@acme.com",
            source="google_sheets",
            status="NEW"
        )
        
        normalized = service.normalize_lead_data(lead_data)
        
        assert normalized.status == "new"


class TestLeadImport:
    """Test lead import functionality."""
    
    def test_import_new_lead(self, db_session: Session):
        """Test importing a new lead."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="New Company",
            company_website="https://newcompany.com",
            first_name="Jane",
            last_name="Smith",
            email="jane@newcompany.com",
            phone="+1234567890",
            source="google_sheets",
            estimated_value=100000.0,
            status="new"
        )
        
        result = service.import_lead_new(lead_data)
        
        assert result.lead_id is not None
        assert result.contact_id is not None
        assert result.company_id is not None
        assert result.is_new is True
        
        # Verify records exist in database
        company = db_session.query(Company).filter(Company.id == result.company_id).first()
        assert company is not None
        assert company.name == "New Company"
        
        contact = db_session.query(Contact).filter(Contact.id == result.contact_id).first()
        assert contact is not None
        assert contact.email == "jane@newcompany.com"
        
        lead = db_session.query(Lead).filter(Lead.id == result.lead_id).first()
        assert lead is not None
        assert lead.source == "google_sheets"
    
    def test_import_duplicate_lead(self, db_session: Session):
        """Test importing a duplicate lead (idempotency)."""
        service = LeadService(db_session)
        
        lead_data = ImportLeadRequest(
            company_name="Duplicate Company",
            company_website="https://duplicate.com",
            first_name="Bob",
            last_name="Johnson",
            email="bob@duplicate.com",
            phone="+1234567890",
            source="google_sheets",
            estimated_value=75000.0,
            status="new"
        )
        
        # First import
        result1 = service.import_lead_new(lead_data)
        assert result1.is_new is True
        
        # Second import (same email and source)
        result2 = service.import_lead_new(lead_data)
        assert result2.is_new is False
        assert result2.contact_id == result1.contact_id
        assert result2.company_id == result1.company_id
        
        # Verify only one lead exists
        leads = db_session.query(Lead).filter(
            Lead.contact_id == result1.contact_id,
            Lead.source == "google_sheets"
        ).all()
        assert len(leads) == 1
    
    def test_batch_import_leads(self, db_session: Session):
        """Test batch importing multiple leads."""
        service = LeadService(db_session)
        
        leads = [
            ImportLeadRequest(
                company_name="Batch Company 1",
                first_name="Alice",
                last_name="Williams",
                email="alice@batch1.com",
                source="google_sheets"
            ),
            ImportLeadRequest(
                company_name="Batch Company 2",
                first_name="Charlie",
                last_name="Brown",
                email="charlie@batch2.com",
                source="google_sheets"
            ),
            ImportLeadRequest(
                company_name="Batch Company 3",
                first_name="David",
                last_name="Miller",
                email="david@batch3.com",
                source="google_sheets"
            )
        ]
        
        result = service.batch_import_leads(leads, "google_sheets")
        
        assert result.imported == 3
        assert result.updated == 0
        assert result.failed == 0
        assert len(result.errors) == 0
    
    def test_batch_import_with_invalid_data(self, db_session: Session):
        """Test batch import with some invalid data."""
        service = LeadService(db_session)
        
        leads = [
            ImportLeadRequest(
                company_name="Valid Company",
                first_name="Eve",
                last_name="Davis",
                email="eve@valid.com",
                source="google_sheets"
            ),
            ImportLeadRequest(
                company_name="",  # Invalid
                first_name="Frank",
                last_name="Wilson",
                email="frank@invalid.com",
                source="google_sheets"
            ),
            ImportLeadRequest(
                company_name="Another Valid Company",
                first_name="Grace",
                last_name="Lee",
                email="grace@valid2.com",
                source="google_sheets"
            )
        ]
        
        result = service.batch_import_leads(leads, "google_sheets")
        
        assert result.imported == 2
        assert result.failed == 1
        assert len(result.errors) == 1


class TestActivityLogging:
    """Test activity logging."""
    
    def test_log_activity(self, db_session: Session):
        """Test logging activity."""
        service = LeadService(db_session)
        
        activity_data = ActivityLogRequest(
            entity_type="lead",
            entity_id="test-lead-id",
            action="imported",
            actor="Google Sheets Import",
            details={"source": "google_sheets"}
        )
        
        result = service.log_activity(activity_data)
        
        assert result is True


class TestResponseFormat:
    """Test API response format."""
    
    def test_standard_response_structure(self):
        """Test standard response structure."""
        from schemas.response import StandardResponse
        
        response = StandardResponse(
            success=True,
            data={"test": "data"},
            message="Test message",
            errors=None,
            meta={"timestamp": "2026-07-03T00:00:00Z"}
        )
        
        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.message == "Test message"
        assert response.errors is None
        assert response.meta == {"timestamp": "2026-07-03T00:00:00Z"}
    
    def test_health_response_structure(self):
        """Test health response structure."""
        from schemas.response import HealthResponse
        
        response = HealthResponse(
            status="healthy",
            database="connected",
            timestamp="2026-07-03T00:00:00Z"
        )
        
        assert response.status == "healthy"
        assert response.database == "connected"
        assert response.timestamp == "2026-07-03T00:00:00Z"


class TestPriorityScoring:
    """Test lead priority scoring logic."""
    
    def test_priority_score_hot_lead(self, db_session: Session):
        """Test scoring for a hot lead."""
        from services.lead_service import LeadService
        from datetime import datetime, timedelta
        
        service = LeadService(db_session)
        
        # Create a hot lead
        lead_data = ImportLeadRequest(
            company_name="Hot Company",
            first_name="John",
            last_name="Doe",
            email="john@hotcompany.com",
            source="referral",
            estimated_value=100000.0,
            status="qualified"
        )
        
        result = service.import_lead_new(lead_data)
        lead_id = result.lead_id
        
        # Update lead to make it hot
        lead = db_session.query(Lead).filter(Lead.id == lead_id).first()
        lead.last_contacted_at = datetime.utcnow() - timedelta(days=1)
        lead.next_followup_at = datetime.utcnow() - timedelta(days=1)  # Overdue
        lead.interaction_count = 5
        db_session.commit()
        
        # Calculate priority score
        priority = service.calculate_priority_score(lead_id)
        
        assert priority.score >= 70
        assert priority.label in ["Hot", "Overdue"]
        assert "overdue follow-up" in priority.reason or "high status" in priority.reason
        assert priority.next_action == "Call immediately"
    
    def test_priority_score_warm_lead(self, db_session: Session):
        """Test scoring for a warm lead."""
        from services.lead_service import LeadService
        from datetime import datetime, timedelta
        
        service = LeadService(db_session)
        
        # Create a warm lead
        lead_data = ImportLeadRequest(
            company_name="Warm Company",
            first_name="Jane",
            last_name="Smith",
            email="jane@warmcompany.com",
            source="web_form",
            estimated_value=50000.0,
            status="contacted"
        )
        
        result = service.import_lead_new(lead_data)
        lead_id = result.lead_id
        
        # Update lead to make it warm
        lead = db_session.query(Lead).filter(Lead.id == lead_id).first()
        lead.last_contacted_at = datetime.utcnow() - timedelta(days=3)
        lead.next_followup_at = datetime.utcnow() + timedelta(days=2)
        lead.interaction_count = 2
        db_session.commit()
        
        # Calculate priority score
        priority = service.calculate_priority_score(lead_id)
        
        assert 50 <= priority.score < 70
        assert priority.label == "Warm"
        assert priority.next_action == "Send email within 24 hours"
    
    def test_priority_score_cold_lead(self, db_session: Session):
        """Test scoring for a cold lead."""
        from services.lead_service import LeadService
        from datetime import datetime, timedelta
        
        service = LeadService(db_session)
        
        # Create a cold lead
        lead_data = ImportLeadRequest(
            company_name="Cold Company",
            first_name="Bob",
            last_name="Johnson",
            email="bob@coldcompany.com",
            source="api",
            estimated_value=5000.0,
            status="new"
        )
        
        result = service.import_lead_new(lead_data)
        lead_id = result.lead_id
        
        # Update lead to make it cold
        lead = db_session.query(Lead).filter(Lead.id == lead_id).first()
        lead.last_contacted_at = datetime.utcnow() - timedelta(days=30)
        lead.interaction_count = 0
        db_session.commit()
        
        # Calculate priority score
        priority = service.calculate_priority_score(lead_id)
        
        assert priority.score < 50
        assert priority.label == "Cold"
        assert priority.next_action == "Schedule follow-up for next week"
    
    def test_priority_score_factors_breakdown(self, db_session: Session):
        """Test that priority score factors are correctly calculated."""
        from services.lead_service import LeadService
        from datetime import datetime, timedelta
        
        service = LeadService(db_session)
        
        # Create a lead
        lead_data = ImportLeadRequest(
            company_name="Test Company",
            first_name="Test",
            last_name="User",
            email="test@testcompany.com",
            source="manual",
            estimated_value=75000.0,
            status="engaged"
        )
        
        result = service.import_lead_new(lead_data)
        lead_id = result.lead_id
        
        # Update lead
        lead = db_session.query(Lead).filter(Lead.id == lead_id).first()
        lead.last_contacted_at = datetime.utcnow() - timedelta(days=2)
        lead.next_followup_at = datetime.utcnow() - timedelta(days=1)
        lead.interaction_count = 3
        db_session.commit()
        
        # Calculate priority score
        priority = service.calculate_priority_score(lead_id)
        
        # Verify factors exist
        assert "status_score" in priority.factors
        assert "recency_score" in priority.factors
        assert "value_score" in priority.factors
        assert "interaction_score" in priority.factors
        assert "overdue_score" in priority.factors
        
        # Verify factor ranges
        assert 0 <= priority.factors["status_score"] <= 50
        assert 0 <= priority.factors["recency_score"] <= 25
        assert 0 <= priority.factors["value_score"] <= 20
        assert 0 <= priority.factors["interaction_score"] <= 15
        assert 0 <= priority.factors["overdue_score"] <= 10


class TestFollowupReminders:
    """Test follow-up reminder logic."""
    
    def test_followups_due_overdue_detection(self, db_session: Session):
        """Test detection of overdue follow-ups."""
        from services.lead_service import LeadService
        from datetime import datetime, timedelta
        
        service = LeadService(db_session)
        
        # Create a lead with overdue follow-up
        lead_data = ImportLeadRequest(
            company_name="Overdue Company",
            first_name="Overdue",
            last_name="User",
            email="overdue@overduecompany.com",
            source="manual",
            status="qualified"
        )
        
        result = service.import_lead_new(lead_data)
        lead_id = result.lead_id
        
        # Set follow-up to yesterday
        lead = db_session.query(Lead).filter(Lead.id == lead_id).first()
        lead.next_followup_at = datetime.utcnow() - timedelta(days=1)
        db_session.commit()
        
        # Get follow-ups due
        followups = service.get_followups_due(days_ahead=7)
        
        assert followups.total_leads >= 1
        assert followups.overdue_count >= 1
        
        # Find our lead
        our_lead = next((l for l in followups.leads if l.lead_id == lead_id), None)
        assert our_lead is not None
        assert our_lead.days_overdue == 1
    
    def test_followups_due_today(self, db_session: Session):
        """Test detection of follow-ups due today."""
        from services.lead_service import LeadService
        from datetime import datetime
        
        service = LeadService(db_session)
        
        # Create a lead with follow-up due today
        lead_data = ImportLeadRequest(
            company_name="Today Company",
            first_name="Today",
            last_name="User",
            email="today@todaycompany.com",
            source="manual",
            status="contacted"
        )
        
        result = service.import_lead_new(lead_data)
        lead_id = result.lead_id
        
        # Set follow-up to today
        lead = db_session.query(Lead).filter(Lead.id == lead_id).first()
        lead.next_followup_at = datetime.utcnow()
        db_session.commit()
        
        # Get follow-ups due
        followups = service.get_followups_due(days_ahead=7)
        
        assert followups.due_today_count >= 1
    
    def test_followups_ordering_by_urgency(self, db_session: Session):
        """Test that follow-ups are ordered by urgency (most overdue first)."""
        from services.lead_service import LeadService
        from datetime import datetime, timedelta
        
        service = LeadService(db_session)
        
        # Create multiple leads with different overdue days
        lead_ids = []
        for days_overdue in [5, 2, 1, 0, -1]:  # 5 days overdue, 2 days overdue, 1 day overdue, today, tomorrow
            lead_data = ImportLeadRequest(
                company_name=f"Company {days_overdue}",
                first_name=f"User {days_overdue}",
                last_name="Test",
                email=f"user{days_overdue}@test.com",
                source="manual",
                status="new"
            )
            
            result = service.import_lead_new(lead_data)
            lead_id = result.lead_id
            lead_ids.append(lead_id)
            
            lead = db_session.query(Lead).filter(Lead.id == lead_id).first()
            lead.next_followup_at = datetime.utcnow() - timedelta(days=days_overdue)
            db_session.commit()
        
        # Get follow-ups due
        followups = service.get_followups_due(days_ahead=7)
        
        # Verify ordering (most overdue first)
        if len(followups.leads) >= 2:
            for i in range(len(followups.leads) - 1):
                assert followups.leads[i].days_overdue >= followups.leads[i + 1].days_overdue


class TestTimeline:
    """Test lead timeline functionality."""
    
    def test_timeline_basic(self, db_session: Session):
        """Test basic timeline generation."""
        from services.lead_service import LeadService
        
        service = LeadService(db_session)
        
        # Create a lead
        lead_data = ImportLeadRequest(
            company_name="Timeline Company",
            first_name="Timeline",
            last_name="User",
            email="timeline@timelinecompany.com",
            source="manual",
            status="new"
        )
        
        result = service.import_lead_new(lead_data)
        lead_id = result.lead_id
        
        # Get timeline
        timeline = service.get_lead_timeline(lead_id)
        
        assert timeline.lead_id == lead_id
        assert timeline.contact_name == "Timeline User"
        assert timeline.company_name == "Timeline Company"
        assert len(timeline.events) > 0
        
        # Verify creation event exists
        creation_event = next((e for e in timeline.events if e.event_type == "created"), None)
        assert creation_event is not None
    
    def test_timeline_with_status_change(self, db_session: Session):
        """Test timeline with status change."""
        from services.lead_service import LeadService
        
        service = LeadService(db_session)
        
        # Create a lead
        lead_data = ImportLeadRequest(
            company_name="Status Company",
            first_name="Status",
            last_name="User",
            email="status@statuscompany.com",
            source="manual",
            status="new"
        )
        
        result = service.import_lead_new(lead_data)
        lead_id = result.lead_id
        
        # Update status
        lead = db_session.query(Lead).filter(Lead.id == lead_id).first()
        lead.status = "contacted"
        db_session.commit()
        
        # Get timeline
        timeline = service.get_lead_timeline(lead_id)
        
        # Verify status change event exists
        status_event = next((e for e in timeline.events if e.event_type == "status_change"), None)
        assert status_event is not None
        assert "contacted" in status_event.description
