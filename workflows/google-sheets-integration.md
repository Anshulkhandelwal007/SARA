# Google Sheets Integration Guide

## Overview

This document describes the Google Sheets integration for SARA lead import, replacing mock data with real Google Sheets data.

## Prerequisites

### Google Sheets Setup

1. **Create a Google Sheet** with the following columns (or custom columns mapped via configuration):
   - Company Name (required)
   - Company Website (optional)
   - First Name (required)
   - Last Name (required)
   - Email (required)
   - Phone (optional)
   - Mobile (optional)
   - Title (optional)
   - Source (required - e.g., "google_sheets")
   - Estimated Value (optional)
   - Last Modified (optional - for incremental imports)
   - Status (optional - e.g., "new", "contacted", "qualified")

2. **Share the Sheet** with the service account email (if using service account) or ensure OAuth access.

### Google Cloud Console Setup

1. **Create a Google Cloud Project** (if not exists)
2. **Enable Google Sheets API**:
   - Go to Google Cloud Console
   - Select your project
   - Navigate to APIs & Services > Library
   - Search for "Google Sheets API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**:
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Web application"
   - Name: "SARA n8n Integration"
   - Authorized redirect URIs: Add your n8n instance URL (e.g., http://localhost:5678)
   - Save the Client ID and Client Secret

### n8n Credentials Setup

1. **Open n8n UI** at http://localhost:5678
2. **Navigate to Credentials** (left sidebar)
3. **Click "Add Credential"**
4. **Select "Google OAuth2 API"**
5. **Configure**:
   - Credential Name: "Google Sheets"
   - Client ID: From Google Cloud Console
   - Client Secret: From Google Cloud Console
   - Scopes: `https://www.googleapis.com/auth/spreadsheets.readonly`
6. **Save and authorize** the credential

## Column Mapping Layer

### Standard Column Mapping

The column mapping layer allows flexible schema mapping between Google Sheets and the CRM database.

**Default Mapping:**
```json
{
  "company_name": "Company Name",
  "company_website": "Company Website",
  "first_name": "First Name",
  "last_name": "Last Name",
  "email": "Email",
  "phone": "Phone",
  "mobile": "Mobile",
  "title": "Title",
  "source": "Source",
  "estimated_value": "Estimated Value",
  "last_modified": "Last Modified",
  "status": "Status"
}
```

### Custom Mapping Configuration

To use different column names, modify the mapping in the workflow's "Map Columns" node:

```javascript
// Example: Mapping different column names
const mapping = {
  company_name: "Company",           // Maps "Company" column to company_name
  company_website: "Website",         // Maps "Website" column to company_website
  first_name: "First",                // Maps "First" column to first_name
  last_name: "Last",                 // Maps "Last" column to last_name
  email: "Email Address",            // Maps "Email Address" column to email
  phone: "Work Phone",               // Maps "Work Phone" column to phone
  mobile: "Cell Phone",              // Maps "Cell Phone" column to mobile
  title: "Job Title",                // Maps "Job Title" column to title
  source: "Lead Source",             // Maps "Lead Source" column to source
  estimated_value: "Deal Size",      // Maps "Deal Size" column to estimated_value
  last_modified: "Updated At",       // Maps "Updated At" column to last_modified
  status: "Lead Status"              // Maps "Lead Status" column to status
};

// Apply mapping
const mapped = {};
for (const [key, sheetColumn] of Object.entries(mapping)) {
  mapped[key] = $json[sheetColumn];
}

return [{ json: mapped }];
```

## Incremental Import Strategy

### Timestamp-Based Filtering

The workflow supports incremental imports using the "Last Modified" column:

1. **First Import**: All rows are imported
2. **Subsequent Imports**: Only rows with `last_modified` > last import timestamp are imported

### Implementation

The workflow stores the last import timestamp in the database:

```sql
-- Create import tracking table
CREATE TABLE IF NOT EXISTS import_tracking (
  id SERIAL PRIMARY KEY,
  source VARCHAR(100) NOT NULL,
  last_import_at TIMESTAMP NOT NULL,
  imported_count INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Workflow Logic

1. **Get Last Import Time**: Query `import_tracking` for the last Google Sheets import
2. **Filter Rows**: Only read rows where `last_modified` > last import time
3. **Import Rows**: Process filtered rows through the import pipeline
4. **Update Tracking**: Store the current timestamp as the new last import time

### Alternative: Full Import with Deduplication

If timestamp tracking is not available, use full import with database-level deduplication:

1. **Read All Rows**: Read all rows from the sheet
2. **Upsert Logic**: Use PostgreSQL `ON CONFLICT` clauses to handle duplicates
3. **No Tracking**: No timestamp tracking required

## Data Validation

### Required Fields

- Company Name
- First Name
- Last Name
- Email (valid format)
- Source

### Validation Rules

```javascript
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
```

## Data Normalization

### Company Names

- Trim whitespace
- Convert to title case
- Remove common suffixes (Inc, LLC, Ltd) if desired

### Email Addresses

- Trim whitespace
- Convert to lowercase
- Validate format

### Phone Numbers

- Trim whitespace
- Format to international standard if needed
- Remove non-numeric characters for storage

## Duplicate Prevention

### Database-Level Deduplication

The PostgreSQL schema uses unique constraints and `ON CONFLICT` clauses:

```sql
-- Companies: Unique on (name, domain)
INSERT INTO companies (name, website, domain, ...)
VALUES ($1, $2, $3, ...)
ON CONFLICT (name, domain) DO UPDATE SET
  website = EXCLUDED.website,
  updated_at = CURRENT_TIMESTAMP
RETURNING id;

-- Contacts: Unique on email
INSERT INTO contacts (company_id, first_name, last_name, email, ...)
VALUES ($1, $2, $3, $4, ...)
ON CONFLICT (email) DO UPDATE SET
  company_id = EXCLUDED.company_id,
  phone = EXCLUDED.phone,
  updated_at = CURRENT_TIMESTAMP
RETURNING id;

-- Leads: Unique on (contact_id, company_id) - no duplicate leads for same contact/company
INSERT INTO leads (contact_id, company_id, source, ...)
VALUES ($1, $2, $3, ...)
ON CONFLICT (contact_id, company_id) DO UPDATE SET
  status = EXCLUDED.status,
  updated_at = CURRENT_TIMESTAMP
RETURNING id;
```

## Workflow Structure

### Nodes

1. **Trigger**: Manual or Webhook trigger
2. **Google Sheets Reader**: Read rows from Google Sheet
3. **Column Mapper**: Map sheet columns to CRM schema
4. **Process Each Lead**: Loop over each row
5. **Validate Data**: Validate required fields
6. **Normalize Data**: Normalize company names, emails, phones
7. **Upsert Company**: Insert/update company
8. **Upsert Contact**: Insert/update contact
9. **Upsert Lead**: Insert/update lead
10. **Log Activity**: Log import to activity_log table
11. **Update Tracking**: Update import tracking timestamp
12. **Generate Response**: Return import statistics

### Incremental Import Variant

Add after Google Sheets Reader:
- **Get Last Import Time**: Query import_tracking table
- **Filter Rows**: Filter by timestamp if available

## Testing

### Test 1: Initial Import

1. Add 3 rows to Google Sheet
2. Execute workflow
3. Verify 3 companies, 3 contacts, 3 leads created
4. Check activity_log for import entries

### Test 2: Incremental Import

1. Add 1 new row to Google Sheet with current timestamp
2. Execute workflow
3. Verify only 1 new lead created (total: 4)
4. Check import_tracking updated

### Test 3: Duplicate Prevention

1. Execute workflow again (same data)
2. Verify no new records created
3. Verify existing records updated if changed

### Test 4: Data Validation

1. Add a row with invalid email
2. Execute workflow
3. Verify row is rejected
4. Check error logs

## Troubleshooting

### Google Sheets API Errors

**Error**: "API key not authorized"

**Solution**: Ensure Google Sheets API is enabled in Google Cloud Console and credentials are correct.

**Error**: "Insufficient permissions"

**Solution**: Ensure the OAuth2 credentials have the correct scopes and the sheet is shared with the service account.

### Mapping Errors

**Error**: "Column not found"

**Solution**: Check column mapping configuration matches actual sheet column names (case-sensitive).

### Duplicate Records

**Error**: Duplicates created despite ON CONFLICT

**Solution**: Verify unique constraints are properly defined and the conflict target matches the actual data.

## Migration from Mock Data

1. **Deploy new Google Sheets workflow** using deployment script
2. **Test with sample data** in Google Sheets
3. **Verify all imports work correctly**
4. **Archive or delete** the mock data workflow
5. **Update documentation** to reflect new data source

## Security Considerations

- **OAuth2 Credentials**: Store securely in n8n credentials, never in code
- **Sheet Access**: Limit sheet access to necessary users
- **API Scopes**: Use read-only scopes where possible
- **Data Privacy**: Ensure sensitive data is handled according to privacy policies
