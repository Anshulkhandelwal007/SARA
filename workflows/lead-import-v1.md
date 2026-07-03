# Lead Import v1 Workflow

## Overview

The Lead Import v1 workflow handles the ingestion of lead data from external sources (currently mock input, future Google Sheets integration), validates and normalizes the data, and upserts records into the PostgreSQL database in an idempotent manner.

## Architecture Alignment

**Current State (Phase 0):**
- Workflow directly accesses PostgreSQL for upsert operations
- Business logic (validation, normalization, upsert) lives in n8n nodes
- Suitable for initial development and testing

**Target State (Phase 1+):**
- n8n calls backend API for all business operations
- Backend API handles validation, normalization, and upsert logic
- n8n orchestrates and executes based on API responses
- PostgreSQL is accessed only by backend API

**Migration Path:**
When the backend API is Docker-integrated and n8n can reach it:
1. Replace PostgreSQL nodes with HTTP Request nodes calling backend API
2. Replace validation/normalization function nodes with backend API calls
3. Keep n8n for orchestration (trigger, batch processing, error handling)
4. Backend API becomes the single source of business logic

**Integration Steps for Lead Import v1:**

1. **Replace Company Upsert Node:**
   - Current: PostgreSQL node with INSERT ... ON CONFLICT
   - New: HTTP Request node to `POST http://backend:8000/api/v1/leads/import-lead`
   - The backend API handles company, contact, and lead upsert in one call

2. **Simplify Workflow:**
   - Remove: Company upsert PostgreSQL node
   - Remove: Contact upsert PostgreSQL node
   - Remove: Lead creation PostgreSQL node
   - Remove: Validation function node (backend handles this)
   - Remove: Normalization function node (backend handles this)
   - Keep: Trigger node
   - Keep: Batch processing node
   - Add: HTTP Request node to backend API
   - Keep: Response generation node

3. **Example HTTP Request Node Configuration:**
   ```
   Method: POST
   URL: http://backend:8000/api/v1/leads/import-lead
   Body:
   {
     "company_name": "{{ $json.company_name }}",
     "company_website": "{{ $json.company_website }}",
     "first_name": "{{ $json.first_name }}",
     "last_name": "{{ $json.last_name }}",
     "email": "{{ $json.email }}",
     "phone": "{{ $json.phone }}",
     "mobile": "{{ $json.mobile }}",
     "title": "{{ $json.title }}",
     "source": "{{ $json.source }}",
     "estimated_value": {{ $json.estimated_value }}
   }
   ```

4. **Benefits of Migration:**
   - Business logic centralized in backend
   - Easier to test and maintain
   - Consistent validation across all sources
   - Backend can be called from multiple systems
   - AI integration happens in backend

**Why This Separation:**
- Business rules live in code (backend), not workflow nodes
- Easier to test and maintain business logic
- Backend can be called from multiple sources (not just n8n)
- AI integration happens in backend, not in n8n
- Clear separation of concerns

## n8n Version Compatibility Fix (July 2026)

**Issue:**
The original workflow was incompatible with current n8n version due to incorrect node connections for the `splitInBatches` node (typeVersion 3). The Loop Branch was connected correctly, but the Done Branch was missing, causing the workflow to not execute properly.

**Fix Applied:**
1. **Process Each Lead node connections:**
   - Loop Branch (index 0): Connected to Validate Lead Data (unchanged)
   - Done Branch (index 1): Connected to Collect Results (added)

2. **Loop continuation:**
   - Log Import node now connects back to Process Each Lead to continue the loop

**Workflow Flow:**
```
Start Import → Generate Mock Data → Process Each Lead
                                          ↓
                              ┌───────────┴───────────┐
                              ↓                       ↓
                        Loop Branch              Done Branch
                              ↓                       ↓
                    Validate Lead Data        Collect Results
                              ↓                       ↓
                        Is Valid?               Generate Response
                              ↓ (if valid)
                        Normalize Data
                              ↓
                        Upsert Company
                              ↓
                        Upsert Contact
                              ↓
                        Create Lead
                              ↓
                        Log Import
                              ↓
                    (back to Process Each Lead)
```

**Testing Instructions:**
1. Import the corrected workflow from `workflows/exports/lead-import-v1.json`
2. Open the workflow in n8n
3. Execute the workflow manually
4. Verify that both mock leads are processed
5. Check PostgreSQL for created records
6. Verify the response shows correct statistics

## Workflow Stages

### 1. Trigger (Webhook or Manual)

**Purpose**: Entry point for the workflow

**Implementation**: 
- Current: Manual trigger with mock data
- Future: Webhook trigger for Google Sheets integration

**Input Schema**:
```json
{
  "leads": [
    {
      "company_name": "string (required)",
      "company_website": "string (optional)",
      "first_name": "string (required)",
      "last_name": "string (required)",
      "email": "string (required, email format)",
      "phone": "string (optional)",
      "mobile": "string (optional)",
      "title": "string (optional)",
      "source": "string (required)",
      "estimated_value": "number (optional)"
    }
  ]
}
```

---

### 2. Data Validation

**Purpose**: Validate required fields and data formats

**Rules**:
- `company_name`: Required, non-empty
- `first_name`: Required, non-empty
- `last_name`: Required, non-empty
- `email`: Required, valid email format
- `mobile` or `phone`: At least one required

**Error Handling**:
- Skip invalid records
- Log validation errors to activity_log
- Continue processing valid records

---

### 3. Data Normalization

**Purpose**: Clean and standardize data formats

**Transformations**:
- Trim whitespace from all string fields
- Convert email to lowercase
- Extract domain from company website
- Format phone numbers to E.164 standard
- Capitalize first letter of names
- Set default values for missing optional fields

---

### 4. Company Lookup/Upsert

**Purpose**: Ensure company exists in database, create if needed

**Logic**:
1. Check if company exists by name and domain
2. If exists: retrieve company_id
3. If not exists: insert new company and retrieve new company_id
4. Log activity to activity_log

**PostgreSQL Query**:
```sql
-- Check if company exists
SELECT id FROM companies 
WHERE name = $1 AND (domain = $2 OR domain IS NULL)
LIMIT 1;

-- If not exists, insert
INSERT INTO companies (name, website, domain, industry, size, location, country)
VALUES ($1, $2, $3, $4, $5, $6, $7)
ON CONFLICT (name, domain) DO UPDATE SET
  website = EXCLUDED.website,
  updated_at = CURRENT_TIMESTAMP
RETURNING id;
```

---

### 5. Contact Lookup/Upsert

**Purpose**: Ensure contact exists in database, create if needed

**Logic**:
1. Check if contact exists by email
2. If exists: update contact details, retrieve contact_id
3. If not exists: insert new contact and retrieve new contact_id
4. Log activity to activity_log

**PostgreSQL Query**:
```sql
-- Check if contact exists
SELECT id FROM contacts 
WHERE email = $1
LIMIT 1;

-- If not exists, insert
INSERT INTO contacts (company_id, first_name, last_name, email, phone, mobile, title, department)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
ON CONFLICT (email) DO UPDATE SET
  company_id = EXCLUDED.company_id,
  phone = EXCLUDED.phone,
  mobile = EXCLUDED.mobile,
  title = EXCLUDED.title,
  updated_at = CURRENT_TIMESTAMP
RETURNING id;
```

---

### 6. Lead Creation

**Purpose**: Create lead record linked to contact

**Logic**:
1. Check if lead already exists for this contact and source
2. If exists: update lead details (idempotent)
3. If not exists: insert new lead
4. Log activity to activity_log

**PostgreSQL Query**:
```sql
-- Check if lead exists
SELECT id FROM leads 
WHERE contact_id = $1 AND source = $2
LIMIT 1;

-- If not exists, insert
INSERT INTO leads (contact_id, company_id, source, status, score, estimated_value, custom_fields)
VALUES ($1, $2, $3, 'new', 0, $4, $5)
RETURNING id;
```

---

### 7. Import Logging

**Purpose**: Track import statistics and results

**Log to activity_log**:
```sql
INSERT INTO activity_log (entity_type, entity_id, action, actor, details)
VALUES ('lead', $1, 'imported', 'Lead Import v1', $2);
```

**Details JSON**:
```json
{
  "source": "google_sheets",
  "company_name": "Acme Corp",
  "contact_email": "john@example.com",
  "import_timestamp": "2026-07-02T23:00:00Z",
  "is_new": true
}
```

---

### 8. Response

**Purpose**: Return import results to caller

**Response Schema**:
```json
{
  "success": true,
  "processed": 10,
  "created": 7,
  "updated": 3,
  "failed": 0,
  "errors": [],
  "leads": [
    {
      "lead_id": "uuid",
      "contact_id": "uuid",
      "company_id": "uuid",
      "email": "john@example.com",
      "status": "new"
    }
  ]
}
```

---

## n8n Node Configuration

### Node 1: Manual Trigger (or Webhook)
- **Type**: Manual Trigger / Webhook
- **Name**: Start Import
- **Configuration**: 
  - Method: POST (if webhook)
  - Authentication: None (or API key later)

### Node 2: Function - Mock Data
- **Type**: Function
- **Name**: Generate Mock Data
- **Code**:
```javascript
// Mock data for testing - replace with Google Sheets node later
return [
  {
    json: {
      leads: [
        {
          company_name: "Tech Startup Inc",
          company_website: "https://techstartup.com",
          first_name: "Alice",
          last_name: "Chen",
          email: "alice.chen@techstartup.com",
          mobile: "+1-555-0201",
          title: "VP of Engineering",
          source: "google_sheets",
          estimated_value: 50000
        },
        {
          company_name: "Global Solutions",
          company_website: "https://globalsolutions.io",
          first_name: "Marcus",
          last_name: "Johnson",
          email: "marcus.johnson@globalsolutions.io",
          phone: "+1-555-0202",
          title: "CTO",
          source: "google_sheets",
          estimated_value: 75000
        }
      ]
    }
  }
];
```

### Node 3: Split In Batches
- **Type**: Split In Batches
- **Name**: Process Each Lead
- **Batch Size**: 1
- **Options**: Reset = false

### Node 4: Function - Validate Data
- **Type**: Function
- **Name**: Validate Lead Data
- **Code**:
```javascript
const lead = $input.item.json;

const errors = [];

if (!lead.company_name || lead.company_name.trim() === '') {
  errors.push('company_name is required');
}
if (!lead.first_name || lead.first_name.trim() === '') {
  errors.push('first_name is required');
}
if (!lead.last_name || lead.last_name.trim() === '') {
  errors.push('last_name is required');
}
if (!lead.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email)) {
  errors.push('valid email is required');
}
if (!lead.phone && !lead.mobile) {
  errors.push('at least one of phone or mobile is required');
}

if (errors.length > 0) {
  return [{
    json: {
      valid: false,
      errors: errors,
      lead: lead
    }
  }];
}

return [{
  json: {
    valid: true,
    lead: lead
  }
}];
```

### Node 5: IF - Check Valid
- **Type**: IF
- **Name**: Is Valid?
- **Condition**: valid == true

### Node 6: Function - Normalize Data
- **Type**: Function
- **Name**: Normalize Data
- **Code**:
```javascript
const lead = $input.item.json.lead;

// Normalize data
const normalized = {
  company_name: lead.company_name.trim(),
  company_website: lead.company_website ? lead.company_website.trim() : null,
  first_name: lead.first_name.trim().charAt(0).toUpperCase() + lead.first_name.trim().slice(1).toLowerCase(),
  last_name: lead.last_name.trim().charAt(0).toUpperCase() + lead.last_name.trim().slice(1).toLowerCase(),
  email: lead.email.trim().toLowerCase(),
  phone: lead.phone ? lead.phone.trim() : null,
  mobile: lead.mobile ? lead.mobile.trim() : null,
  title: lead.title ? lead.title.trim() : null,
  source: lead.source,
  estimated_value: lead.estimated_value || 0
};

// Extract domain from website
if (normalized.company_website) {
  try {
    const url = new URL(normalized.company_website);
    normalized.domain = url.hostname;
  } catch (e) {
    normalized.domain = null;
  }
} else {
  normalized.domain = null;
}

return [{
  json: normalized
}];
```

### Node 7: PostgreSQL - Upsert Company
- **Type**: PostgreSQL
- **Name**: Upsert Company
- **Operation**: Execute Query
- **Query**:
```sql
INSERT INTO companies (name, website, domain, industry, size, location, country)
VALUES ($1, $2, $3, $4, $5, $6, $7)
ON CONFLICT (name, domain) DO UPDATE SET
  website = EXCLUDED.website,
  updated_at = CURRENT_TIMESTAMP
RETURNING id;
```
- **Parameters**: 
  - $1: company_name
  - $2: company_website
  - $3: domain
  - $4: null (industry)
  - $5: null (size)
  - $6: null (location)
  - $7: null (country)

### Node 8: PostgreSQL - Upsert Contact
- **Type**: PostgreSQL
- **Name**: Upsert Contact
- **Operation**: Execute Query
- **Query**:
```sql
INSERT INTO contacts (company_id, first_name, last_name, email, phone, mobile, title, department)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
ON CONFLICT (email) DO UPDATE SET
  company_id = EXCLUDED.company_id,
  phone = EXCLUDED.phone,
  mobile = EXCLUDED.mobile,
  title = EXCLUDED.title,
  updated_at = CURRENT_TIMESTAMP
RETURNING id;
```
- **Parameters**:
  - $1: company_id (from previous node)
  - $2: first_name
  - $3: last_name
  - $4: email
  - $5: phone
  - $6: mobile
  - $7: title
  - $8: null (department)

### Node 9: PostgreSQL - Create Lead
- **Type**: PostgreSQL
- **Name**: Create Lead
- **Operation**: Execute Query
- **Query**:
```sql
INSERT INTO leads (contact_id, company_id, source, status, score, estimated_value, custom_fields)
VALUES ($1, $2, $3, 'new', 0, $4, $5)
ON CONFLICT DO NOTHING
RETURNING id;
```
- **Parameters**:
  - $1: contact_id (from previous node)
  - $2: company_id (from company node)
  - $3: source
  - $4: estimated_value
  - $5: null (custom_fields)

### Node 10: PostgreSQL - Log Activity
- **Type**: PostgreSQL
- **Name**: Log Import
- **Operation**: Execute Query
- **Query**:
```sql
INSERT INTO activity_log (entity_type, entity_id, action, actor, details)
VALUES ('lead', $1, 'imported', 'Lead Import v1', $2);
```
- **Parameters**:
  - $1: lead_id (from previous node)
  - $2: JSON object with import details

### Node 11: Merge - Collect Results
- **Type**: Merge
- **Name**: Collect Results
- **Mode**: Combine
- **Combine By**: Append

### Node 12: Function - Generate Response
- **Type**: Function
- **Name**: Generate Response
- **Code**:
```javascript
const items = $input.all();
const processed = items.length;
const created = items.filter(i => i.json.lead_id).length;
const failed = items.filter(i => i.json.error).length;

return [{
  json: {
    success: true,
    processed: processed,
    created: created,
    updated: 0,
    failed: failed,
    leads: items.map(i => ({
      lead_id: i.json.lead_id || null,
      contact_id: i.json.contact_id || null,
      company_id: i.json.company_id || null,
      email: i.json.email || null,
      status: i.json.lead_id ? 'new' : 'error'
    }))
  }
}];
```

---

## PostgreSQL Connection Settings

Configure PostgreSQL node credentials:
- **Host**: `postgres`
- **Port**: `5432`
- **Database**: `sara_db`
- **User**: `sara_user`
- **Password**: From `.env` file (use n8n credentials)

---

## Error Handling

1. **Validation Errors**: Skip invalid records, log to activity_log
2. **Database Errors**: Retry up to 3 times with exponential backoff
3. **Duplicate Errors**: Handled by ON CONFLICT clauses (idempotent)
4. **Network Errors**: Log and continue with next record

---

## Idempotency

The workflow is idempotent due to:
- ON CONFLICT clauses in all INSERT statements
- Unique constraints on email (contacts) and name+domain (companies)
- Lead creation checks for existing leads by contact_id and source

Running the same import multiple times will:
- Update existing company/contact details
- Not create duplicate leads
- Log each import activity

---

## Future Google Sheets Integration

To replace the mock data node with Google Sheets:

1. **Remove**: Function - Generate Mock Data node
2. **Add**: Google Sheets node
   - Operation: Read
   - Sheet ID: Configure
   - Range: Configure
3. **Map**: Google Sheets columns to workflow schema
4. **Trigger**: Change to Webhook or Schedule trigger

---

## Testing Checklist

- [ ] Mock data generates correctly
- [ ] Validation catches invalid records
- [ ] Normalization formats data correctly
- [ ] Company upsert works (new and existing)
- [ ] Contact upsert works (new and existing)
- [ ] Lead creation works
- [ ] Activity logging works
- [ ] Response includes correct statistics
- [ ] Workflow is idempotent (run twice, no duplicates)
- [ ] Error handling catches and logs failures

---

## Performance Considerations

- Batch size: Process 1 lead at a time for better error isolation
- Connection pooling: Use n8n's built-in PostgreSQL connection pooling
- Indexes: Ensure all foreign key columns are indexed
- Transactions: Consider wrapping related operations in a transaction

---

## Security Notes

- Never hardcode credentials in workflow
- Use n8n credentials for PostgreSQL connection
- Sanitize all user inputs before database operations
- Log all import activities for audit trail
