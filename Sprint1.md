# Sprint 1: Architecture Compliance and Google Sheets Integration

**Sprint Duration**: 2 weeks
**Start Date**: 2026-07-03
**End Date**: 2026-07-17

---

## Objectives

### Primary Objective
Achieve full architecture compliance by migrating the Google Sheets workflow to use the backend API instead of direct PostgreSQL access, establishing the correct data flow: PostgreSQL → FastAPI Backend → n8n → Communication.

### Secondary Objectives
1. Complete Google Sheets integration with real data testing
2. Update all documentation to reflect current state
3. Resolve critical technical debt items
4. Establish foundation for Phase 2 (Lead Scoring Engine)

---

## Deliverables

### 1. Backend API Enhancement

#### 1.1 Lead Import Endpoint Enhancement
**File**: `backend/routers/leads.py`, `backend/services/lead_service.py`

**Changes**:
- Add support for batch lead import (multiple leads in single request)
- Add column mapping configuration parameter
- Add incremental import support (last_modified timestamp filtering)
- Implement standard response wrapper (success, data, message, errors, meta)

**API Contract**:
```python
POST /api/v1/leads/import-batch
Request:
{
  "leads": [
    {
      "company_name": "string",
      "company_website": "string",
      "first_name": "string",
      "last_name": "string",
      "email": "string",
      "phone": "string",
      "mobile": "string",
      "title": "string",
      "source": "string",
      "estimated_value": "number",
      "last_modified": "ISO8601 timestamp",
      "status": "string"
    }
  ],
  "column_mapping": {
    "company_name": "Company Name",
    "company_website": "Company Website",
    ...
  },
  "import_options": {
    "incremental": true,
    "since": "ISO8601 timestamp"
  }
}

Response:
{
  "success": true,
  "data": {
    "imported": 10,
    "updated": 5,
    "failed": 2,
    "errors": [...]
  },
  "message": "Batch import completed",
  "errors": null,
  "meta": {
    "timestamp": "2026-07-03T00:00:00Z",
    "request_id": "uuid"
  }
}
```

#### 1.2 Import Tracking Endpoint
**File**: `backend/routers/leads.py`

**New Endpoint**:
```python
GET /api/v1/leads/import-tracking
Response:
{
  "success": true,
  "data": {
    "source": "google_sheets",
    "last_import_at": "2026-07-03T00:00:00Z",
    "imported_count": 10,
    "updated_count": 5,
    "failed_count": 2
  }
}

POST /api/v1/leads/import-tracking
Request:
{
  "source": "google_sheets",
  "last_import_at": "2026-07-03T00:00:00Z",
  "imported_count": 10,
  "updated_count": 5,
  "failed_count": 2
}
```

#### 1.3 Activity Logging Endpoint
**File**: `backend/routers/leads.py`

**New Endpoint**:
```python
POST /api/v1/leads/log-activity
Request:
{
  "entity_type": "lead",
  "entity_id": "uuid",
  "action": "imported",
  "actor": "Google Sheets Import",
  "details": {}
}
```

### 2. Google Sheets Workflow Migration

#### 2.1 Migrate to Backend API
**File**: `workflows/exports/lead-import-google-sheets.json`

**Changes**:
- Replace PostgreSQL nodes with HTTP Request nodes calling backend API
- Remove validation logic from n8n (move to backend)
- Remove normalization logic from n8n (move to backend)
- Remove upsert logic from n8n (move to backend)
- Keep n8n for orchestration only (trigger, batch processing, error handling)

**New Workflow Structure**:
1. Manual Trigger
2. Read Google Sheet
3. Map Columns
4. HTTP Request: POST /api/v1/leads/import-batch
5. HTTP Request: POST /api/v1/leads/import-tracking
6. Generate Response

#### 2.2 Add Incremental Import Support
**File**: `workflows/exports/lead-import-google-sheets.json`

**Changes**:
- Add node to GET /api/v1/leads/import-tracking
- Use last_import_at to filter Google Sheet rows
- Pass filtered rows to import-batch endpoint

### 3. Database Changes

#### 3.1 Schema Documentation Update
**File**: `database/schema-documentation.md`

**Changes**:
- Add `import_tracking` table documentation
- Update `leads` table status values to match Blueprint
- Add missing tables (opportunities, quotations, orders, invoices, payments, service_requests, amcs) as placeholders

#### 3.2 Migration for Status Alignment
**File**: `database/migrations/003_align_lead_status.sql`

**Changes**:
```sql
-- Update lead status values to match Blueprint
ALTER TABLE leads 
ALTER COLUMN status TYPE VARCHAR(50);
UPDATE leads SET status = 'converted' WHERE status = 'opportunity';
UPDATE leads SET status = 'converted' WHERE status = 'customer';
UPDATE leads SET status = 'lost' WHERE status = 'churned';
-- Add CHECK constraint for valid status values
ALTER TABLE leads 
ADD CONSTRAINT valid_status 
CHECK (status IN ('new', 'contacted', 'qualified', 'converted', 'lost'));
```

### 4. Documentation Updates

#### 4.1 README.md Updates
**File**: `README.md`

**Changes**:
- Update line 178: Reference `workflows/exports/lead-import-google-sheets.json`
- Update line 147: Reference Google Sheets workflow instead of Lead Import v1
- Update line 152: Mark "n8n workflow integration with backend" as completed
- Add SARA_BLUEPRINT.md to project structure
- Add docs/sara_blueprint_notes.md to project structure

#### 4.2 ROADMAP.md Updates
**File**: `ROADMAP.md`

**Changes**:
- Add Phase 1.5 to align with Blueprint or remove
- Update Phase 1.5 status to "Completed" after Sprint 1
- Update "What's Working" section

#### 4.3 Architecture.md Updates
**File**: `docs/architecture.md`

**Changes**:
- Update data flow examples to reflect backend API usage
- Remove or mark as future: Brevo, WhatsApp, Voice integration references

#### 4.4 Workflow Documentation Updates
**File**: `workflows/lead-automation-workflow.md`

**Changes**:
- Update specification to reference backend API instead of direct PostgreSQL
- Update workflow stages to reflect new architecture

#### 4.5 Schema Documentation Updates
**File**: `database/schema-documentation.md`

**Changes**:
- Add import_tracking table
- Update leads status values
- Document placeholder tables for future phases

### 5. Testing

#### 5.1 Unit Tests
**File**: `backend/tests/`

**New Tests**:
- `test_lead_import_batch.py`: Test batch import endpoint
- `test_import_tracking.py`: Test import tracking endpoint
- `test_activity_logging.py`: Test activity logging endpoint
- `test_column_mapping.py`: Test column mapping logic
- `test_incremental_import.py`: Test incremental import logic

#### 5.2 Integration Tests
**File**: `backend/tests/integration/`

**New Tests**:
- `test_workflow_integration.py`: Test n8n workflow calling backend API
- `test_google_sheets_integration.py`: Test end-to-end Google Sheets import

#### 5.3 Manual Testing
**Test Plan**:
1. Set up Google Sheets with test data
2. Configure Google Sheets credentials in n8n
3. Execute workflow manually
4. Verify records created in PostgreSQL
5. Execute workflow again (test idempotency)
6. Add new row with timestamp
7. Execute workflow (test incremental import)
8. Verify only new row imported
9. Check import_tracking table updated

---

## API Endpoints

### New Endpoints
- `POST /api/v1/leads/import-batch` - Batch import leads with mapping
- `GET /api/v1/leads/import-tracking` - Get last import tracking info
- `POST /api/v1/leads/import-tracking` - Update import tracking info
- `POST /api/v1/leads/log-activity` - Log activity

### Modified Endpoints
- `POST /api/v1/leads/import-lead` - Add column mapping support
- All endpoints - Add standard response wrapper

---

## Database Changes

### New Tables
None (import_tracking already exists)

### Modified Tables
- `leads` - Update status values and add CHECK constraint

### New Migrations
- `003_align_lead_status.sql` - Align lead status with Blueprint

---

## Workflow Changes

### Modified Workflows
- `workflows/exports/lead-import-google-sheets.json` - Migrate to backend API

### New Workflows
None

---

## Testing Plan

### Unit Tests
- **Coverage**: >80% for new backend code
- **Framework**: pytest
- **Execution**: Run on every commit

### Integration Tests
- **Coverage**: End-to-end workflow testing
- **Framework**: pytest + testcontainers
- **Execution**: Run before deployment

### Manual Testing
- **Scope**: Google Sheets integration, incremental import
- **Frequency**: Before sprint completion
- **Criteria**: All acceptance criteria met

---

## Acceptance Criteria

### Must Have (P0)
- [ ] Google Sheets workflow uses backend API instead of direct PostgreSQL access
- [ ] All business logic (validation, normalization, upsert) moved to backend
- [ ] n8n workflow only orchestrates (no business logic)
- [ ] Batch import endpoint working with column mapping
- [ ] Import tracking endpoint working
- [ ] Activity logging endpoint working
- [ ] Standard response wrapper implemented on all endpoints
- [ ] Unit tests with >80% coverage
- [ ] Integration tests passing
- [ ] Manual testing with real Google Sheets data successful
- [ ] Incremental import working correctly
- [ ] No duplicates created on re-import
- [ ] Documentation updated (README, ROADMAP, Architecture, Schema)

### Should Have (P1)
- [ ] Lead status values aligned with Blueprint
- [ ] Empty folders removed or documented
- [ ] Obsolete workflow documentation updated
- [ ] Error handling improved in backend
- [ ] Logging improved in backend

### Could Have (P2)
- [ ] Placeholder tables added to schema documentation
- [ ] Performance testing completed
- [ ] Load testing completed

---

## Risks

### Technical Risks
1. **Backend API Performance**: Batch import may be slow with large datasets
   - **Mitigation**: Implement pagination, add performance monitoring
2. **n8n HTTP Node Limitations**: May have issues with complex requests
   - **Mitigation**: Test thoroughly, have fallback to direct PostgreSQL if needed
3. **Google Sheets API Rate Limits**: May hit rate limits with large sheets
   - **Mitigation**: Implement pagination, add rate limit handling

### Operational Risks
1. **Data Loss During Migration**: Risk of data loss when migrating workflows
   - **Mitigation**: Backup database before migration, test in staging first
2. **Credential Configuration**: Google Sheets credentials may be difficult to configure
   - **Mitigation**: Provide detailed documentation, test with test account first
3. **Testing Time**: Manual testing may take longer than expected
   - **Mitigation**: Start manual testing early, have test data ready

### Schedule Risks
1. **Scope Creep**: May discover additional issues during audit
   - **Mitigation**: Stick to P0 items only, defer P1/P2 to future sprints
2. **Dependencies**: May depend on external services (Google Sheets API)
   - **Mitigation**: Have fallback plans, test early

---

## Definition of Done

Sprint 1 is complete when:
1. All P0 acceptance criteria are met
2. All P1 acceptance criteria are met
3. Unit tests passing with >80% coverage
4. Integration tests passing
5. Manual testing successful with real Google Sheets data
6. Documentation updated and reviewed
7. Code reviewed and merged
8. Deployed to development environment
9. Architecture compliance score >8/10

---

## Success Metrics

- **Architecture Compliance**: Score >8/10 (currently 3/10)
- **Test Coverage**: >80%
- **Documentation Completeness**: 100%
- **Manual Testing Pass Rate**: 100%
- **Performance**: Batch import <5 seconds for 100 leads

---

## Notes

- This sprint focuses on architecture compliance, not new features
- No new database tables will be added (except status alignment)
- No new communication integrations will be added
- Focus on establishing correct data flow for future phases
- All changes should be backward compatible where possible
