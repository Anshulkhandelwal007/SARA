# Project SARA - Google Workspace OAuth Setup Guide

This guide provides step-by-step instructions for setting up Google OAuth for Project SARA to access Google Sheets and Google Drive.

## Overview

Project SARA requires Google OAuth to:
- Read Google Sheets for lead import
- Create and manage Google Drive folders
- Create and manage Google Sheets spreadsheets
- Automate lead data synchronization

## Prerequisites

- Google Account (Gmail or Google Workspace)
- Google Cloud Console access
- n8n running at http://localhost:5678
- SARA Docker stack running

## Step 1: Create Google Cloud Project

### 1.1 Access Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project dropdown in the top navigation
4. Click "New Project"

### 1.2 Configure Project

**Project Name**: `SARA CRM Automation`
**Organization**: (Your organization or leave blank)
**Location**: No organization

Click "Create"

### 1.3 Select Project

1. Wait for project creation (1-2 minutes)
2. Select the newly created project from the dropdown
3. Note the Project ID (e.g., `sara-crm-automation-123456`)

## Step 2: Enable Required APIs

### 2.1 Access API Library

1. In the left sidebar, click "APIs & Services" → "Library"
2. Search for the following APIs one by one and enable them:

### Required APIs

**Google Sheets API**
- Search: "Google Sheets API"
- Click on "Google Sheets API"
- Click "Enable"

**Google Drive API**
- Search: "Google Drive API"
- Click on "Google Drive API"
- Click "Enable"

**Google Docs API** (optional, for future use)
- Search: "Google Docs API"
- Click on "Google Docs API"
- Click "Enable"

### Verification

After enabling APIs, verify they appear in:
- "APIs & Services" → "Enabled APIs & services"

## Step 3: Configure OAuth Consent Screen

### 3.1 Access OAuth Consent Screen

1. In the left sidebar, click "APIs & Services" → "OAuth consent screen"
2. Choose user type: **External** (since this is for personal use)
3. Click "Create"

### 3.2 OAuth Consent Screen Configuration

**Step 1: OAuth consent screen**

- **App name**: `SARA CRM Automation`
- **User support email**: Your email address
- **App logo**: (Optional - upload SARA logo if available)
- **Application home page**: `http://localhost:5678`
- **Authorized domains**: 
  - `localhost`
- **Developer contact information**: Your email address
- **Scopes**: Click "Add or Remove Scopes" (see Step 3.3)

Click "Save and Continue"

### 3.3 Configure Scopes

Click "Add or Remove Scopes" and search for/add the following:

**Required Scopes**:

```
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/drive.file
```

**Scope Descriptions**:

- `https://www.googleapis.com/auth/spreadsheets` - View and manage Google Sheets
- `https://www.googleapis.com/auth/drive` - View and manage Google Drive files
- `https://www.googleapis.com/auth/drive.file` - View and manage files created by this app

Click "Update" then "Save and Continue"

### 3.4 Test Users

**Step 2: Test users**

- Add your email address as a test user
- Click "Add users"
- Enter your email address
- Click "Add"
- Click "Save and Continue"

### 3.5 Summary

**Step 3: Summary**

Review the configuration and click "Back to Dashboard"

## Step 4: Create OAuth Client ID

### 4.1 Create Credentials

1. In the left sidebar, click "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"

### 4.2 Configure OAuth Client

**Application Type**: **Web application**

**Name**: `SARA n8n Integration`

**Authorized redirect URIs**:

```
http://localhost:5678/oauth2/callback
http://localhost:5678/rest/oauth2-credential/callback
```

**Authorized JavaScript origins**:

```
http://localhost:5678
```

**IMPORTANT**: Ensure your n8n instance has the following environment variables configured:
- `N8N_EDITOR_BASE_URL=http://localhost:5678`
- `WEBHOOK_URL=http://localhost:5678`

These are critical for OAuth to work correctly. Without them, n8n will generate relative redirect URIs that Google will reject.

### 4.3 Create and Save

1. Click "Create"
2. **IMPORTANT**: Copy the following values immediately:
   - **Client ID**: (e.g., `123456789-abc123def456.apps.googleusercontent.com`)
   - **Client Secret**: (e.g., `GOCSPX-abc123def456`)
3. Save these values securely (you will need them for n8n configuration)

## Step 5: Configure n8n with OAuth Credentials

### 5.1 Access n8n

1. Open n8n at http://localhost:5678
2. Log in with your n8n credentials
3. Navigate to "Credentials" (left sidebar)

### 5.2 Add Google Sheets OAuth2 Credential

1. Click "Add Credential"
2. Search for "Google Sheets"
3. Select "Google Sheets OAuth2 API"
4. Configure:

**Credential Name**: `Google Sheets`

**Client ID**: (paste from Step 4.3)

**Client Secret**: (paste from Step 4.3)

**Redirect URI**: `http://localhost:5678/oauth2/callback`

5. Click "Save"

### 5.3 Authorize OAuth

1. After saving, click "Sign in with Google"
2. Select your Google account
3. Grant permissions (you will see the scopes you configured)
4. You should be redirected back to n8n with a success message

## Step 6: Verify OAuth Configuration

### 6.1 Test Credential

1. In n8n, create a simple test workflow
2. Add a "Google Sheets" node
3. Select the "Google Sheets" credential
4. Try to list spreadsheets
5. If successful, OAuth is working correctly

### 6.2 Verify Redirect URI

The correct redirect URI for n8n is:

```
http://localhost:5678/oauth2/callback
```

**Note**: If you encounter redirect URI errors, also add:

```
http://localhost:5678/rest/oauth2-credential/callback
```

## Step 7: Google Workspace Initialization

After OAuth is configured, run the Google Workspace Initialization workflow (see `docs/google-workspace-initialization.md`).

This workflow will automatically:
- Create "SARA CRM" folder in Google Drive
- Create "Lead Master" spreadsheet
- Create required tabs
- Populate headers
- Configure permissions

## Troubleshooting

### OAuth Consent Screen Error

**Error**: "OAuth consent screen not configured"

**Solution**:
1. Complete Step 3 (OAuth consent screen configuration)
2. Wait 5-10 minutes for Google to process the configuration
3. Try again

### Redirect URI Mismatch

**Error**: "redirect_uri_mismatch"

**Solution**:
1. Verify the redirect URI in Google Cloud Console matches n8n
2. Ensure you're using http://localhost:5678 (not https)
3. Check for trailing slashes
4. Try adding both redirect URIs mentioned in Step 4.2
5. **CRITICAL**: Verify n8n environment variables:
   - `N8N_EDITOR_BASE_URL=http://localhost:5678`
   - `WEBHOOK_URL=http://localhost:5678`
6. Restart n8n after changing environment variables
7. Delete and recreate OAuth credentials if they were created with wrong configuration

### Access Blocked

**Error**: "Access blocked: Authorization request denied"

**Solution**:
1. Ensure your email is added as a test user in Step 3.4
2. Verify you're using the correct Google account
3. Clear browser cookies and try again

### Invalid Client ID

**Error**: "invalid_client"

**Solution**:
1. Verify Client ID and Client Secret are correct
2. Ensure you copied the entire values (no truncation)
3. Re-create OAuth client ID if necessary

## Security Best Practices

1. **Never commit OAuth credentials to Git**
2. **Use environment variables for production deployments**
3. **Rotate Client Secrets periodically**
4. **Monitor OAuth usage in Google Cloud Console**
5. **Revoke unused OAuth tokens**
6. **Use separate OAuth clients for development and production**

## Production Deployment

For production deployment:

1. **Use a custom domain** instead of localhost
2. **Configure proper OAuth consent screen** for production use
3. **Add your domain to authorized domains**
4. **Remove test user restrictions** after verification
5. **Enable Google Workspace marketplace integration** (if applicable)
6. **Set up OAuth consent verification** for public apps

## Next Steps

After completing OAuth setup:

1. Run Google Workspace Initialization workflow
2. Configure Lead Import workflow with the new spreadsheet
3. Test lead import from Google Sheets
4. Verify data flows correctly to PostgreSQL

## Related Documentation

- [Google Workspace Initialization Guide](google-workspace-initialization.md)
- [Deployment Guide](deployment.md)
- [Operating Guide](operating-guide.md)
