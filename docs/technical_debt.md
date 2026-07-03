# Technical Debt

**Last Updated**: 2026-07-03
**Repository**: SARA
**Commit**: ed4ed74

---

## Critical

### 1. Architecture Violation - Direct PostgreSQL Access from n8n
**Location**: `workflows/exports/lead-import-google-sheets.json`
**Impact**: Violates core architecture principle, business logic in wrong layer
**Effort**: 2 days
**Priority**: P0 - Must fix in Sprint 1

**Description**: Current Google Sheets workflow uses PostgreSQL nodes directly from n8n instead of calling backend API. This violates the architecture principle that business logic must live in the backend and n8n should only orchestrate.

**Solution**: Migrate workflow to use HTTP Request nodes calling backend API endpoints. Move validation, normalization, and upsert logic to backend service.

**Related**: Sprint1.md Deliverable 2.1

---

### 2. Business Logic in n8n Code Nodes
**Location**: `workflows/exports/lead-import-google-sheets.json` (Map Columns, Validate Lead Data, Normalize Data nodes)
**Impact**: Business logic scattered across workflow nodes, hard to test and maintain
**Effort**: 1 day
**Priority**: P0 - Must fix in Sprint 1

**Description**: Validation and normalization logic is implemented in n8n Code nodes instead of backend service. This makes the logic hard to test, version control, and reuse.

**Solution**: Move all business logic to backend service. Keep n8n for orchestration only (trigger, batch processing, error handling).

**Related**: Sprint1.md Deliverable 2.1

---

### 3. Missing Standard API Response Wrapper
**Location**: All backend endpoints
**Impact**: Inconsistent response format, doesn't match Blueprint specification
**Effort**: 1 day
**Priority**: P0 - Must fix in Sprint 1

**Description**: Backend endpoints return direct responses instead of the standard wrapper defined in Blueprint (success, data, message, errors, meta).

**Solution**: Implement response wrapper middleware or base response class. Update all endpoints to use wrapper.

**Related**: Sprint1.md Deliverable 1.1

---

### 4. Database Schema vs Blueprint Mismatch
**Location**: `database/schema-documentation.md`, `database/migrations/`
**Impact**: Schema doesn't match Blueprint entity definitions
**Effort**: 3 days
**Priority**: P0 - Must fix before Phase 2

**Description**: Blueprint defines 11 entities (Company, Contact, Lead, Opportunity, Quotation, Order, Invoice, Payment, Service Request, AMC, Interaction). Current schema has 10 tables with different structure. Missing tables for full customer lifecycle.

**Solution**: Add missing tables as placeholders. Align existing table structures with Blueprint. This is a larger effort that may span multiple sprints.

**Related**: Sprint1.md Deliverable 3.1

---

### 5. Lead Status Value Mismatch
**Location**: `database/schema-documentation.md`, `leads` table
**Impact**: Status values don't match between Blueprint and schema
**Effort**: 0.5 days
**Priority**: P0 - Must fix in Sprint 1

**Description**: Blueprint has lead status: new, contacted, qualified, converted, lost. Schema has: new, contacted, engaged, qualified, opportunity, customer, churned, lost. Values don't match.

**Solution**: Update schema to match Blueprint. Add CHECK constraint for valid values. Migration script needed.

**Related**: Sprint1.md Deliverable 3.2

---

## High

### 6. Stale Documentation - README.md
**Location**: `README.md`
**Impact**: Documentation references deprecated files and workflows
**Effort**: 0.5 days
**Priority**: P1 - Should fix in Sprint 1

**Description**: README.md references `workflows/exports/lead-import-v1.json` which no longer exists. Mentions "Lead Import v1 workflow" which is deprecated. States "n8n workflow integration with backend" as in-progress when it's not implemented.

**Solution**: Update README.md to reference correct workflow file and current state.

**Related**: Sprint1.md Deliverable 4.1

---

### 7. Missing Schema Documentation
**Location**: `database/schema-documentation.md`
**Impact**: import_tracking table not documented
**Effort**: 0.25 days
**Priority**: P1 - Should fix in Sprint 1

**Description**: import_tracking table was added in migration 002 but not documented in schema documentation.

**Solution**: Add import_tracking table documentation to schema-documentation.md.

**Related**: Sprint1.md Deliverable 3.1

---

### 8. Obsolete Workflow Documentation
**Location**: `workflows/lead-automation-workflow.md`, `workflows/lead-import-v1.md`
**Impact**: Documentation references deprecated workflows and architecture
**Effort**: 0.5 days
**Priority**: P1 - Should fix in Sprint 1

**Description**: lead-automation-workflow.md is a specification that references direct PostgreSQL access. lead-import-v1.md references archived mock workflow.

**Solution**: Update lead-automation-workflow.md to reference backend API. Update lead-import-v1.md to reference Google Sheets workflow or mark as deprecated.

**Related**: Sprint1.md Deliverable 4.4

---

### 9. Architecture.md Future Integration References
**Location**: `docs/architecture.md`
**Impact**: Documentation references integrations that don't exist yet
**Effort**: 0.25 days
**Priority**: P1 - Should fix in Sprint 1

**Description**: Architecture.md references Brevo (Sendinblue), WhatsApp, and Voice integrations that are not implemented yet. May confuse users.

**Solution**: Mark these integrations as "Future" or "Phase 4" in documentation.

**Related**: Sprint1.md Deliverable 4.3

---

### 10. ROADMAP.md Phase 1.5 Not in Blueprint
**Location**: `ROADMAP.md`, `SARA_BLUEPRINT.md`
**Impact**: Inconsistency between planning documents
**Effort**: 0.25 days
**Priority**: P1 - Should fix in Sprint 1

**Description**: ROADMAP.md includes "Phase 1.5: Real Data Integration" which is not in SARA_BLUEPRINT.md. Blueprint has phases 0-6.

**Solution**: Add Phase 1.5 to Blueprint or remove from ROADMAP to align documents.

**Related**: Sprint1.md Deliverable 4.2

---

### 11. Empty Folders
**Location**: `backups/`, `knowledge-base/`, `logs/`, `prompts/`
**Impact**: Clutter, unclear purpose
**Effort**: 0.25 days
**Priority**: P1 - Should fix in Sprint 1

**Description**: Four empty folders exist in repository with no clear purpose or documentation.

**Solution**: Delete empty folders or add README.md in each explaining purpose.

---

### 12. No Unit Tests
**Location**: `backend/tests/`
**Impact**: No automated testing, high risk of regressions
**Effort**: 2 days
**Priority**: P1 - Should add in Sprint 1

**Description**: Backend has no unit tests. High risk of introducing bugs when making changes.

**Solution**: Add unit tests for all backend services and endpoints. Target >80% coverage.

**Related**: Sprint1.md Deliverable 5.1

---

### 13. No Integration Tests
**Location**: `backend/tests/integration/`
**Impact**: No end-to-end testing, high risk of deployment failures
**Effort**: 2 days
**Priority**: P1 - Should add in Sprint 1

**Description**: No integration tests for workflow-backend integration. High risk of deployment failures.

**Solution**: Add integration tests for n8n workflow calling backend API.

**Related**: Sprint1.md Deliverable 5.2

---

## Medium

### 14. Missing API Endpoints
**Location**: `backend/routers/`
**Impact**: Blueprint defines endpoints that don't exist
**Effort**: 5 days
**Priority**: P2 - Can fix in Sprint 2

**Description**: Blueprint defines Company, Contact, Opportunity, Quotation, Order, Invoice, Service Request, AMC, Interaction endpoints. Backend only has Lead endpoints.

**Solution**: Implement missing endpoints as needed for future phases. This is a larger effort.

---

### 15. Placeholder Tables Not in Schema
**Location**: `database/schema-documentation.md`
**Impact**: Schema doesn't have tables for full customer lifecycle
**Effort**: 3 days
**Priority**: P2 - Can fix in Sprint 2

**Description**: Blueprint defines tables for opportunities, quotations, orders, invoices, payments, service_requests, amcs. These don't exist in schema.

**Solution**: Add placeholder tables with basic structure. Full implementation in future phases.

---

### 16. No Error Handling in Backend
**Location**: `backend/routers/`, `backend/services/`
**Impact**: Poor error handling, hard to debug issues
**Effort**: 1 day
**Priority**: P2 - Can fix in Sprint 2

**Description**: Backend has basic error handling but could be improved with custom exceptions, error codes, and better logging.

**Solution**: Implement custom exception classes, error codes, and structured error responses.

---

### 17. No Logging Strategy
**Location**: `backend/`
**Impact**: Hard to debug issues in production
**Effort**: 1 day
**Priority**: P2 - Can fix in Sprint 2

**Description**: Basic logging exists but no structured logging strategy. No log levels, no correlation IDs, no log aggregation.

**Solution**: Implement structured logging with correlation IDs, log levels, and log aggregation strategy.

---

### 18. No Monitoring
**Location**: All services
**Impact**: No visibility into system health and performance
**Effort**: 2 days
**Priority**: P2 - Can fix in Sprint 2

**Description**: No application monitoring, performance monitoring, or alerting. Hard to detect issues in production.

**Solution**: Add Prometheus metrics, Grafana dashboards, and alerting rules.

---

### 19. No Automated Backups
**Location**: Docker stack
**Impact**: Risk of data loss
**Effort**: 1 day
**Priority**: P2 - Can fix in Sprint 2

**Description**: No automated backup strategy. Manual pgAdmin exports only.

**Solution**: Implement automated daily PostgreSQL backups with offsite storage.

---

### 20. No CI/CD Pipeline
**Location**: Repository
**Impact**: Manual deployment process, high risk of human error
**Effort**: 2 days
**Priority**: P2 - Can fix in Sprint 2

**Description**: No automated CI/CD pipeline. Manual deployment process.

**Solution**: Set up GitHub Actions or similar for automated testing and deployment.

---

## Low

### 21. Inconsistent Naming
**Location**: Various files
**Impact**: Minor inconsistency, doesn't affect functionality
**Effort**: 0.25 days
**Priority**: P3 - Fix when convenient

**Description**: Some minor naming inconsistencies (e.g., lead_import vs import-lead).

**Solution**: Standardize naming conventions across codebase.

---

### 22. No Code Comments
**Location**: Backend code
**Impact**: Hard to understand complex logic
**Effort**: 1 day
**Priority**: P3 - Fix when convenient

**Description**: Backend code has minimal comments. Complex logic may be hard to understand.

**Solution**: Add comments to complex functions and classes.

---

### 23. No API Versioning Strategy
**Location**: Backend API
**Impact**: Hard to make breaking changes in future
**Effort**: 0.5 days
**Priority**: P3 - Fix when convenient

**Description**: API has /api/v1/ prefix but no versioning strategy for breaking changes.

**Solution**: Define API versioning strategy and document it.

---

### 24. No Rate Limiting
**Location**: Backend API
**Impact**: Risk of abuse, no protection against overload
**Effort**: 0.5 days
**Priority**: P3 - Fix when convenient

**Description**: No rate limiting on API endpoints. Risk of abuse.

**Solution**: Add rate limiting middleware.

---

### 25. No Request Validation Beyond Pydantic
**Location**: Backend API
**Impact**: Potential security vulnerabilities
**Effort**: 0.5 days
**Priority**: P3 - Fix when convenient

**Description**: Basic Pydantic validation but no additional security validation (e.g., SQL injection prevention beyond ORM).

**Solution**: Add additional security validation layers.

---

## Summary

### Critical: 5 items
- Architecture violations (3)
- API response format (1)
- Schema mismatch (1)

### High: 8 items
- Documentation issues (5)
- Testing gaps (2)
- Empty folders (1)

### Medium: 7 items
- Missing features (2)
- Infrastructure gaps (5)

### Low: 5 items
- Code quality (3)
- Security (2)

### Total Effort Estimate
- Critical: 7.5 days
- High: 5.75 days
- Medium: 15 days
- Low: 3.25 days
- **Total**: 31.5 days

### Recommended Priority
1. **Sprint 1**: Fix all Critical (7.5 days) + High documentation (2 days) = 9.5 days
2. **Sprint 2**: Fix High testing (4 days) + Medium infrastructure (5 days) = 9 days
3. **Sprint 3**: Fix Medium features (5 days) + Low (3.25 days) = 8.25 days
