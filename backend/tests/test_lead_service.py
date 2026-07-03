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
