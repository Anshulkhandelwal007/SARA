# Project SARA - Google OAuth Setup Checklist

This checklist provides a step-by-step guide to complete Google OAuth setup for Project SARA.

## Pre-Setup Checklist

- [ ] Docker Desktop is running
- [ ] SARA Docker stack is deployed (`./scripts/deploy-all.sh`)
- [ ] All services are healthy (`./scripts/verify-deployment.sh`)
- [ ] n8n is accessible at http://localhost:5678
- [ ] You have a Google Account (Gmail or Google Workspace)
- [ ] You have access to Google Cloud Console

---

## Phase 1: Google Login

### Step 1.1: Access Google Cloud Console

- [ ] Go to [Google Cloud Console](https://console.cloud.google.com/)
- [ ] Sign in with your Google account
- [ ] Verify you are signed in with the correct account

**Expected Outcome**: You are logged into Google Cloud Console

---

## Phase 2: OAuth Completed

### Step 2.1: Create Google Cloud Project

- [ ] Click on project dropdown
- [ ] Click "New Project"
- [ ] Set project name: `SARA CRM Automation`
- [ ] Select organization or leave blank
- [ ] Set location: No organization
- [ ] Click "Create"
- [ ] Wait for project creation (1-2 minutes)
- [ ] Select the newly created project from dropdown
- [ ] Note the Project ID

**Expected Outcome**: Google Cloud project "SARA CRM Automation" is created

### Step 2.2: Enable Required APIs

- [ ] Navigate to "APIs & Services" → "Library"
- [ ] Search and enable "Google Sheets API"
- [ ] Search and enable "Google Drive API"
- [ ] (Optional) Enable "Google Docs API"
- [ ] Verify all APIs appear in "Enabled APIs & services"

**Expected Outcome**: Google Sheets API and Google Drive API are enabled

### Step 2.3: Configure OAuth Consent Screen

- [ ] Navigate to "APIs & Services" → "OAuth consent screen"
- [ ] Select user type: **External**
- [ ] Click "Create"
- [ ] Configure OAuth consent screen:
  - [ ] App name: `SARA CRM Automation`
  - [ ] User support email: Your email address
  - [ ] Application home page: `http://localhost:5678`
  - [ ] Authorized domains: `localhost`
  - [ ] Developer contact information: Your email address
- [ ] Click "Add or Remove Scopes"
- [ ] Add scope: `https://www.googleapis.com/auth/spreadsheets`
- [ ] Add scope: `https://www.googleapis.com/auth/drive`
- [ ] Add scope: `https://www.googleapis.com/auth/drive.file`
- [ ] Click "Update"
- [ ] Click "Save and Continue"
- [ ] Add your email as a test user
- [ ] Click "Add users"
- [ ] Click "Save and Continue"
- [ ] Click "Back to Dashboard"

**Expected Outcome**: OAuth consent screen is configured with required scopes

### Step 2.4: Create OAuth Client ID

- [ ] Navigate to "APIs & Services" → "Credentials"
- [ ] Click "Create Credentials" → "OAuth client ID"
- [ ] Configure OAuth client:
  - [ ] Application type: **Web application**
  - [ ] Name: `SARA n8n Integration`
  - [ ] Authorized redirect URIs:
    - [ ] `http://localhost:5678/oauth2/callback`
    - [ ] `http://localhost:5678/rest/oauth2-credential/callback`
  - [ ] Authorized JavaScript origins:
    - [ ] `http://localhost:5678`
- [ ] Click "Create"
- [ ] **IMPORTANT**: Copy Client ID
- [ ] **IMPORTANT**: Copy Client Secret
- [ ] Save credentials securely

**Expected Outcome**: OAuth Client ID and Client Secret are created and saved

### Step 2.5: Configure n8n with OAuth Credentials

- [ ] Open n8n at http://localhost:5678
- [ ] Log in with n8n credentials
- [ ] Navigate to "Credentials"
- [ ] Click "Add Credential"
- [ ] Search for "Google Sheets"
- [ ] Select "Google Sheets OAuth2 API"
- [ ] Configure:
  - [ ] Credential name: `Google Sheets`
  - [ ] Client ID: (paste from Step 2.4)
  - [ ] Client Secret: (paste from Step 2.4)
  - [ ] Redirect URI: `http://localhost:5678/oauth2/callback`
- [ ] Click "Save"
- [ ] Click "Sign in with Google"
- [ ] Select your Google account
- [ ] Grant permissions
- [ ] Verify success message

**Expected Outcome**: Google Sheets OAuth2 credential is configured in n8n

### Step 2.6: Verify OAuth Configuration

- [ ] Create a simple test workflow in n8n
- [ ] Add a "Google Sheets" node
- [ ] Select "Google Sheets" credential
- [ ] Try to list spreadsheets
- [ ] Verify spreadsheet list appears
- [ ] Delete test workflow

**Expected Outcome**: OAuth is working correctly

**Phase 2 Complete**: OAuth Completed ✅

---

## Phase 3: SARA Folder Created

### Step 3.1: Import Initialization Workflow

- [ ] Import Google Workspace Initialization workflow:
  ```bash
  docker cp workflows/exports/google-workspace-initialization.json sara-n8n:/tmp/
  docker exec sara-n8n n8n import:workflow --input=/tmp/google-workspace-initialization.json
  ```
- [ ] Verify workflow appears in n8n UI

**Expected Outcome**: Google Workspace Initialization workflow is imported

### Step 3.2: Configure Initialization Workflow

- [ ] Open "Google Workspace Initialization" workflow in n8n
- [ ] Click on Google Drive node
- [ ] Select "Google Sheets" OAuth2 credential
- [ ] Click on Google Sheets nodes
- [ ] Select "Google Sheets" OAuth2 credential
- [ ] Save workflow

**Expected Outcome**: Initialization workflow is configured with credentials

### Step 3.3: Execute Initialization Workflow

- [ ] Click "Execute Workflow"
- [ ] Monitor execution in "Executions" tab
- [ ] Verify execution completes successfully
- [ ] Check execution output for folder ID and spreadsheet ID

**Expected Outcome**: Initialization workflow executes successfully

### Step 3.4: Verify Google Drive Resources

- [ ] Open Google Drive
- [ ] Verify "SARA CRM" folder exists
- [ ] Open "SARA CRM" folder
- [ ] Verify "Lead Master" spreadsheet exists
- [ ] Open "Lead Master" spreadsheet
- [ ] Verify "Active Leads" tab exists
- [ ] Verify "Archived Leads" tab exists
- [ ] Verify "Follow-up Log" tab exists
- [ ] Verify headers are populated in "Active Leads" tab

**Expected Outcome**: SARA CRM folder and Lead Master spreadsheet are created

**Phase 3 Complete**: SARA Folder Created ✅

---

## Phase 4: Lead Master Created

### Step 4.1: Verify Spreadsheet Structure

- [ ] Open "Lead Master" spreadsheet
- [ ] Verify "Active Leads" tab has headers:
  - [ ] Company Name
  - [ ] Company Website
  - [ ] First Name
  - [ ] Last Name
  - [ ] Email
  - [ ] Phone
  - [ ] Mobile
  - [ ] Title
  - [ ] Source
  - [ ] Estimated Value
  - [ ] Last Modified
  - [ ] Status
  - [ ] Priority Score
  - [ ] Next Follow-up
  - [ ] Days Overdue
- [ ] Verify "Archived Leads" tab exists (empty)
- [ ] Verify "Follow-up Log" tab exists (empty)

**Expected Outcome**: Lead Master spreadsheet has correct structure

### Step 4.2: Add Sample Data (Optional)

- [ ] Add sample lead data to "Active Leads" tab
- [ ] Fill in required fields
- [ ] Save spreadsheet

**Expected Outcome**: Sample data is added for testing

**Phase 4 Complete**: Lead Master Created ✅

---

## Phase 5: Workflow Connected

### Step 5.1: Import Updated Lead Import Workflow

- [ ] Import updated Lead Import workflow:
  ```bash
  docker cp workflows/exports/lead-import-google-sheets.json sara-n8n:/tmp/
  docker exec sara-n8n n8n import:workflow --input=/tmp/lead-import-google-sheets.json
  ```
- [ ] Verify workflow appears in n8n UI

**Expected Outcome**: Updated Lead Import workflow is imported

### Step 5.2: Configure Lead Import Workflow

- [ ] Open "Lead Import - Google Sheets (Backend API)" workflow
- [ ] Click on "Read Google Sheet" node
- [ ] Configure sheetId:
  - [ ] Click on sheetId field
  - [ ] Select "Lead Master" spreadsheet from list
  - [ ] Or paste spreadsheet ID from initialization output
- [ ] Set range: `A:Z`
- [ ] Verify "Google Sheets" credential is selected
- [ ] Save workflow

**Expected Outcome**: Lead Import workflow is configured with spreadsheet

### Step 5.3: Test Lead Import Workflow

- [ ] Click "Execute Workflow"
- [ ] Monitor execution in "Executions" tab
- [ ] Verify execution completes successfully
- [ ] Check execution output for import results
- [ ] Verify data is imported to PostgreSQL

**Expected Outcome**: Lead Import workflow executes successfully

### Step 5.4: Verify Data in PostgreSQL

- [ ] Open pgAdmin at http://localhost:5050
- [ ] Connect to sara_db database
- [ ] Query leads table:
  ```sql
  SELECT * FROM leads ORDER BY created_at DESC LIMIT 10;
  ```
- [ ] Verify imported data appears
- [ ] Verify data matches Google Sheets

**Expected Outcome**: Data is correctly imported to PostgreSQL

**Phase 5 Complete**: Workflow Connected ✅

---

## Phase 6: Ready for Production

### Step 6.1: Verify Daily Follow-up Workflow

- [ ] Open "Daily Follow-up Summary" workflow in n8n
- [ ] Verify it calls backend API endpoint
- [ ] Verify schedule is set (9 AM daily)
- [ ] Activate workflow if needed
- [ ] Test manual execution

**Expected Outcome**: Daily Follow-up workflow is ready

### Step 6.2: Final Verification

- [ ] Run deployment verification:
  ```bash
  ./scripts/verify-deployment.sh
  ```
- [ ] Verify all checks pass
- [ ] Verify all services are healthy
- [ ] Verify workflows are present
- [ ] Verify architecture compliance

**Expected Outcome**: All verification checks pass

### Step 6.3: Documentation Review

- [ ] Review [Google OAuth Setup Guide](google-oauth-setup.md)
- [ ] Review [Google Workspace Initialization Guide](google-workspace-initialization.md)
- [ ] Review [Deployment Guide](deployment.md)
- [ ] Review [Operating Guide](operating-guide.md)
- [ ] Review [Disaster Recovery Guide](disaster-recovery.md)

**Expected Outcome**: Documentation is reviewed and understood

### Step 6.4: Backup Configuration

- [ ] Backup OAuth credentials (Client ID, Client Secret)
- [ ] Backup spreadsheet ID and folder ID
- [ ] Document configuration in secure location
- [ ] Test recovery procedure

**Expected Outcome**: Configuration is backed up

**Phase 6 Complete**: Ready for Production ✅

---

## Summary Checklist

- [ ] Google Login ✅
- [ ] OAuth Completed ✅
- [ ] SARA Folder Created ✅
- [ ] Lead Master Created ✅
- [ ] Workflow Connected ✅
- [ ] Ready for Production ✅

---

## Troubleshooting Quick Reference

### OAuth Issues

- **Redirect URI mismatch**: Verify redirect URIs match n8n configuration
- **Access blocked**: Add your email as test user in OAuth consent screen
- **Invalid client**: Verify Client ID and Client Secret are correct

### Google Drive Issues

- **Folder not created**: Check OAuth credentials have Drive scope
- **Spreadsheet not created**: Check OAuth credentials have Sheets scope
- **Permissions denied**: Verify you have sufficient Google Drive permissions

### Workflow Issues

- **Credential not found**: Verify Google Sheets credential is configured
- **Spreadsheet not found**: Verify sheetId is correct
- **Data not importing**: Check backend API is running

### General Issues

- **Container not running**: Run `./scripts/deploy-all.sh`
- **Service unhealthy**: Run `./scripts/verify-deployment.sh`
- **Network issues**: Restart Docker Desktop

---

## Next Steps

After completing this checklist:

1. **Add real lead data** to Google Sheets
2. **Test lead import** with real data
3. **Configure workflow schedules** for automation
4. **Set up monitoring** for workflow executions
5. **Document any custom configurations**

---

## Support

For issues or questions:

- Review [Google OAuth Setup Guide](google-oauth-setup.md)
- Review [Google Workspace Initialization Guide](google-workspace-initialization.md)
- Check [Troubleshooting](deployment.md#troubleshooting) section
- Review [Runbook](runbook.md) for operational procedures
