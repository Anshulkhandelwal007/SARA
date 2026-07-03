# Repository Audit Report

**Date**: 2026-07-03
**Commit**: ed4ed74 - Add SARA Blueprint and archive legacy workflow

---

## PART 1 — Repository Audit

### Duplicated Files
- **Status**: ✅ No duplicated files found

### Obsolete Workflows
- **Status**: ⚠️ Issues Found
  - `workflows/lead-automation-workflow.md` - Specification document references direct PostgreSQL access instead of backend API calls (violates architecture)
  - `workflows/lead-import-v1.md` - References archived mock workflow, needs update to reference Google Sheets workflow

### Stale Documentation
- **Status**: ⚠️ Issues Found
  - `README.md` line 178: References `workflows/exports/lead-import-v1.json` which no longer exists (archived)
  - `README.md` line 147: Mentions "Lead Import v1 workflow" which is deprecated
  - `README.md` line 152: States "n8n workflow integration with backend" as in-progress, but workflows still use direct PostgreSQL access
  - `docs/architecture.md` lines 251-267: References Brevo (Sendinblue), WhatsApp, and Voice integrations that are not implemented yet
  - `database/schema-documentation.md`: Missing `import_tracking` table documentation (added in migration 002)

### Inconsistent Naming
- **Status**: ✅ No significant naming inconsistencies found

### Dead Code
- **Status**: ✅ No dead code found

### Unused Folders
- **Status**: ⚠️ Issues Found
  - `backups/` - Empty folder
  - `knowledge-base/` - Empty folder
  - `logs/` - Empty folder
  - `prompts/` - Empty folder

### Configuration Problems
- **Status**: ✅ No configuration problems found

### Docker Inconsistencies
- **Status**: ✅ No Docker inconsistencies found

### API Inconsistencies
- **Status**: ✅ No API inconsistencies found

### Database Inconsistencies
- **Status**: ⚠️ Issues Found
  - `import_tracking` table exists in database but not documented in `database/schema-documentation.md`
  - Migration 002 added table but schema documentation not updated

### Roadmap Inconsistencies
- **Status**: ⚠️ Issues Found
  - `ROADMAP.md` includes "Phase 1.5: Real Data Integration" which is not in `SARA_BLUEPRINT.md`
  - Blueprint has phases 0-6, ROADMAP has phases 0-6 plus 1.5

---

## PART 2 — Blueprint Validation Checklist

### SARA_BLUEPRINT.md vs ROADMAP.md

**Phase Alignment:**
- ✅ Phase 0 (Foundation): Aligned
- ✅ Phase 1 (Backend API Foundation): Aligned
- ⚠️ Phase 1.5 (Real Data Integration): Exists in ROADMAP but not in BLUEPRINT
- ⚠️ Phase 2 (Lead Scoring): ROADMAP mentions "mock for now", Blueprint doesn't specify mock vs real
- ✅ Phase 3-6: Aligned

**Timeline Estimates:**
- ⚠️ Blueprint provides timeline estimates (23-33 weeks total), ROADMAP does not

**Success Criteria:**
- ⚠️ Blueprint has detailed success criteria for each phase, ROADMAP has less detail

### SARA_BLUEPRINT.md vs README.md

**Architecture Description:**
- ✅ Both describe layered architecture (PostgreSQL → n8n → Backend → AI → Communication)
- ⚠️ README shows n8n before Backend in architecture diagram, Blueprint shows Backend before n8n
- ⚠️ README line 152: "n8n workflow integration with backend" is in-progress, but Blueprint shows Phase 1 complete

**Current State:**
- ⚠️ README says "Lead Import v1 workflow" is working, but this is deprecated
- ⚠️ README doesn't mention Google Sheets integration workflow
- ⚠️ README doesn't mention import_tracking table

**Project Structure:**
- ⚠️ README lists `workflows/exports/lead-import-v1.json` which no longer exists
- ⚠️ README doesn't list `SARA_BLUEPRINT.md` in project structure
- ⚠️ README doesn't list `docs/sara_blueprint_notes.md`

### SARA_BLUEPRINT.md vs docs/architecture.md

**Layer Responsibilities:**
- ✅ Both define clear separation of concerns
- ⚠️ Architecture.md shows n8n calling backend API, but current workflows use direct PostgreSQL access
- ⚠️ Architecture.md mentions Brevo, WhatsApp, Voice integrations that don't exist yet

**API Endpoints:**
- ✅ Blueprint and Architecture.md list similar endpoints
- ⚠️ Blueprint has more comprehensive endpoint list (companies, contacts, opportunities, etc.) not implemented yet

**Data Flow:**
- ✅ Both describe similar data flow patterns
- ⚠️ Architecture.md shows n8n → Backend → PostgreSQL flow, but current implementation is n8n → PostgreSQL

### SARA_BLUEPRINT.md vs Database Schema

**Table Coverage:**
- ⚠️ Blueprint defines 11 entities (Company, Contact, Lead, Opportunity, Quotation, Order, Invoice, Payment, Service Request, AMC, Interaction)
- ⚠️ Current schema has 10 tables (companies, contacts, leads, lead_interactions, email_history, whatsapp_history, call_logs, followups, ai_summaries, activity_log)
- ⚠️ Missing tables: opportunities, quotations, orders, invoices, payments, service_requests, amcs
- ⚠️ Extra tables: email_history, whatsapp_history, call_logs, followups, ai_summaries (not in Blueprint)

**Schema Alignment:**
- ⚠️ Blueprint has `leads.status` with states: new, contacted, qualified, converted, lost
- ⚠️ Schema has `leads.status` with states: new, contacted, engaged, qualified, opportunity, customer, churned, lost
- ⚠️ Status values don't match between Blueprint and schema

**Relationships:**
- ✅ Blueprint and schema both have companies → contacts → leads relationships
- ⚠️ Blueprint has leads → opportunities → quotations → orders → invoices → payments flow
- ⚠️ Current schema doesn't have these tables

### SARA_BLUEPRINT.md vs Backend API

**Implemented Endpoints:**
- ✅ Backend has `/api/v1/leads/import-lead` (Blueprint: POST /api/v1/leads)
- ✅ Backend has `/api/v1/leads/score-lead` (Blueprint: POST /api/v1/leads/{id}/score)
- ⚠️ Backend has `/api/v1/leads/next-action` (Blueprint: POST /api/v1/leads/{id}/next-action)
- ✅ Backend has `/api/v1/leads/summarize-call` (Blueprint: POST /api/v1/interactions/{id}/summarize)
- ✅ Backend has `/api/v1/leads/followup-decision` (Blueprint: not explicitly listed)

**Missing Endpoints:**
- ⚠️ Blueprint defines Company, Contact, Opportunity, Quotation, Order, Invoice, Service Request, AMC, Interaction endpoints
- ⚠️ Backend only has Lead endpoints

**Response Format:**
- ⚠️ Blueprint defines standard response wrapper with success, data, message, errors, meta
- ⚠️ Backend endpoints return direct responses without wrapper

### SARA_BLUEPRINT.md vs n8n Workflows

**Current Workflow:**
- ⚠️ `workflows/exports/lead-import-google-sheets.json` uses direct PostgreSQL access
- ⚠️ Blueprint states: "Business logic must live inside backend. n8n should orchestrate only."
- ⚠️ Current workflow violates architecture principle

**Workflow Documentation:**
- ⚠️ `workflows/lead-automation-workflow.md` is a specification, not an actual workflow
- ⚠️ Specification references direct PostgreSQL access instead of backend API

---

## PART 3 — Architecture Validation

### Architecture Rule: PostgreSQL → FastAPI Backend → n8n → Communication

**Current Implementation:**
- ✅ PostgreSQL is source of truth
- ✅ FastAPI Backend exists and is running
- ✅ n8n exists and is running
- ⚠️ Communication layer not implemented yet

**Data Flow Violations:**
- ❌ **CRITICAL**: Current Google Sheets workflow accesses PostgreSQL directly from n8n
- ❌ **CRITICAL**: Business logic (validation, normalization, upsert) is in n8n nodes, not backend
- ❌ **CRITICAL**: n8n workflow does not call backend API for lead import

**Architecture Compliance Score: 3/10**

**Violations:**
1. Google Sheets workflow uses PostgreSQL node instead of backend API
2. Validation logic in n8n Code node instead of backend
3. Normalization logic in n8n Code node instead of backend
4. Upsert logic in n8n PostgreSQL node instead of backend
5. Activity logging in n8n PostgreSQL node instead of backend

---

## PART 4 — Sprint 1 Planning

**Status**: Sprint1.md will be created separately

---

## PART 5 — Technical Debt

**Status**: docs/technical_debt.md will be created separately

---

## PART 6 — Final Report

**Status**: Final report will be generated after completing all parts

---

## Summary of Critical Issues

### Must Fix Before Sprint 1
1. **Architecture Violation**: Migrate Google Sheets workflow to use backend API instead of direct PostgreSQL access
2. **Documentation Update**: Update README.md to reference correct workflow file
3. **Schema Documentation**: Add import_tracking table to schema documentation
4. **Blueprint Alignment**: Add Phase 1.5 to SARA_BLUEPRINT.md or remove from ROADMAP.md

### Should Fix Before Sprint 1
1. **Remove Empty Folders**: Delete or document purpose of empty folders
2. **Update lead-automation-workflow.md**: Update to reference backend API instead of direct PostgreSQL
3. **Update lead-import-v1.md**: Update to reference Google Sheets workflow
4. **Standardize Response Format**: Implement Blueprint response wrapper in backend

### Can Fix During Sprint 1
1. **Missing Database Tables**: Add opportunities, quotations, orders, invoices, payments, service_requests, amcs tables
2. **Status Value Alignment**: Align lead status values between Blueprint and schema
3. **API Response Wrapper**: Implement standard response format
4. **Missing API Endpoints**: Implement Company, Contact, and other entity endpoints

### Technical Debt Summary
- **Critical**: 5 issues (architecture violations)
- **High**: 4 issues (documentation gaps)
- **Medium**: 4 issues (missing features)
- **Low**: 2 issues (cosmetic)
