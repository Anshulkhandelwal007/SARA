# Project SARA - Google Workspace Initialization Guide

This guide covers the automatic initialization of Google Workspace resources for Project SARA.

## Overview

The Google Workspace Initialization workflow automates the setup of required Google Drive and Google Sheets resources for SARA.

## What Gets Created

### Google Drive Structure

```
My Drive
└── SARA CRM/
    └── Lead Master (Google Sheets)
        ├── Active Leads (tab)
        ├── Archived Leads (tab)
        └── Follow-up Log (tab)
```

### Spreadsheet Structure

**Lead Master Spreadsheet**:
- **Active Leads Tab**: Contains current leads with all required columns
- **Archived Leads Tab**: Contains archived/closed leads
- **Follow-up Log Tab**: Contains follow-up activity log

### Column Headers (Active Leads)

The Active Leads tab will be populated with the following headers:

```
Company Name | Company Website | First Name | Last Name | Email | Phone | Mobile | Title | Source | Estimated Value | Last Modified | Status | Priority Score | Next Follow-up | Days Overdue
```

## Idempotent Design

The initialization workflow is designed to be idempotent - it can be run multiple times safely.

### Idempotency Features

1. **Folder Check**: Checks if "SARA CRM" folder already exists
2. **Spreadsheet Check**: Checks if "Lead Master" spreadsheet already exists
3. **Conditional Creation**: Only creates resources that don't exist
4. **Reuse Existing**: Uses existing resources if found
5. **No Duplicates**: Prevents duplicate folder/spreadsheet creation

### Workflow Logic

```
Start
  ↓
Check if SARA CRM folder exists
  ↓
If exists → Use existing folder ID
If not exists → Create folder → Use new folder ID
  ↓
Check if Lead Master spreadsheet exists in folder
  ↓
If exists → Use existing spreadsheet ID
If not exists → Create spreadsheet → Create tabs → Add headers
  ↓
Return success with resource IDs
```

## Running the Initialization

### Prerequisites

1. Complete Google OAuth setup (see [Google OAuth Setup Guide](google-oauth-setup.md))
2. n8n running at http://localhost:5678
3. Google Sheets OAuth2 credential configured in n8n

### Steps

1. **Import the Initialization Workflow**:
   ```bash
   docker cp workflows/exports/google-workspace-initialization.json sara-n8n:/tmp/
   docker exec sara-n8n n8n import:workflow --input=/tmp/google-workspace-initialization.json
   ```

2. **Open n8n UI**:
   - Navigate to http://localhost:5678
   - Find "Google Workspace Initialization" workflow

3. **Configure Credentials**:
   - Click on Google Drive node
   - Select "Google Sheets" OAuth2 credential
   - Click on Google Sheets nodes
   - Select "Google Sheets" OAuth2 credential

4. **Execute Workflow**:
   - Click "Execute Workflow"
   - Monitor execution in "Executions" tab

5. **Verify Results**:
   - Check Google Drive for "SARA CRM" folder
   - Open "Lead Master" spreadsheet
   - Verify tabs are created
   - Verify headers are populated

## Expected Output

### Successful Execution

```json
{
  "success": true,
  "message": "Google Workspace initialization completed successfully",
  "folderId": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
  "folderName": "SARA CRM",
  "spreadsheetId": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
  "spreadsheetName": "Lead Master",
  "tabs": ["Active Leads", "Archived Leads", "Follow-up Log"],
  "initialized": true
}
```

### Re-running Execution

If you run the workflow again:

```json
{
  "success": true,
  "message": "Google Workspace initialization completed successfully",
  "folderId": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
  "folderName": "SARA CRM",
  "spreadsheetId": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
  "spreadsheetName": "Lead Master",
  "tabs": ["Active Leads", "Archived Leads", "Follow-up Log"],
  "initialized": true
}
```

**Note**: The IDs will be the same (existing resources reused).

## Troubleshooting

### Folder Creation Failed

**Error**: "Failed to create folder"

**Solutions**:
1. Verify OAuth credentials are valid
2. Check Google Drive API is enabled
3. Verify you have sufficient permissions
4. Check n8n execution logs for details

### Spreadsheet Creation Failed

**Error**: "Failed to create spreadsheet"

**Solutions**:
1. Verify Google Sheets API is enabled
2. Check OAuth credentials have Sheets scope
3. Verify folder ID is valid
4. Check n8n execution logs for details

### Tab Creation Failed

**Error**: "Failed to add tab"

**Solutions**:
1. Verify spreadsheet ID is valid
2. Check OAuth credentials have Sheets scope
3. Verify spreadsheet is not read-only
4. Check n8n execution logs for details

### Headers Not Populated

**Error**: "Headers not added"

**Solutions**:
1. Verify tab exists
2. Check range is correct (A1:Z1)
3. Verify OAuth credentials have Sheets scope
4. Manually add headers if needed

## Manual Fallback

If the automated workflow fails, you can manually create the resources:

### Manual Steps

1. **Create Folder**:
   - Go to Google Drive
   - Create new folder named "SARA CRM"

2. **Create Spreadsheet**:
   - In "SARA CRM" folder, create new Google Sheet
   - Name it "Lead Master"

3. **Create Tabs**:
   - In "Lead Master", create 3 tabs:
     - "Active Leads"
     - "Archived Leads"
     - "Follow-up Log"

4. **Add Headers**:
   - In "Active Leads" tab, add headers in row 1:
     ```
     Company Name | Company Website | First Name | Last Name | Email | Phone | Mobile | Title | Source | Estimated Value | Last Modified | Status | Priority Score | Next Follow-up | Days Overdue
     ```

5. **Get IDs**:
   - Note the folder ID (from URL)
   - Note the spreadsheet ID (from URL)
   - Update Lead Import workflow with these IDs

## Next Steps

After initialization:

1. **Update Lead Import Workflow**:
   - Configure "Read Google Sheet" node with the new spreadsheet ID
   - Set the correct tab (Active Leads)
   - Test the workflow

2. **Test Lead Import**:
   - Add sample data to Active Leads tab
   - Run Lead Import workflow
   - Verify data flows to PostgreSQL

3. **Configure Daily Follow-up**:
   - Ensure Daily Follow-up Summary workflow is active
   - Verify it calls the correct backend endpoint

## Security Considerations

1. **Folder Permissions**: The folder will be created in your personal Google Drive
2. **Sharing**: Do not share the folder with unauthorized users
3. **Access Control**: Review sharing settings after initialization
4. **Backup**: Google Drive automatically backs up your data
5. **Recovery**: If deleted, re-run initialization workflow

## Production Considerations

For production deployment:

1. **Shared Drive**: Consider using a Shared Drive for team collaboration
2. **Service Account**: Use a service account for automated access
3. **Domain-Wide Delegation**: Configure domain-wide delegation for Google Workspace
4. **Audit Logging**: Enable Google Workspace audit logging
5. **Access Policies**: Implement Google Workspace access policies

## Related Documentation

- [Google OAuth Setup Guide](google-oauth-setup.md)
- [Deployment Guide](deployment.md)
- [Operating Guide](operating-guide.md)
- [Runbook](runbook.md)
