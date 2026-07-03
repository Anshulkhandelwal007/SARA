# Workflow Management Guide

## Overview

This document describes the automated workflow management system for SARA n8n workflows.

## Automated Deployment Script

The `scripts/deploy-workflow.sh` script automates workflow deployment, backup, and export operations.

### Usage

```bash
# Deploy workflow (backup, delete, import, verify)
./scripts/deploy-workflow.sh deploy

# Redeploy workflow (includes export back to file)
./scripts/deploy-workflow.sh redeploy

# Backup existing workflow
./scripts/deploy-workflow.sh backup

# Delete existing workflow
./scripts/deploy-workflow.sh delete

# Import workflow from JSON
./scripts/deploy-workflow.sh import

# Export workflow to JSON
./scripts/deploy-workflow.sh export

# Verify database state
./scripts/deploy-workflow.sh verify
```

### What the Script Does

**Deploy Command:**
1. Backs up existing workflow to `workflows/backups/`
2. Deletes existing workflow from n8n database
3. Imports new workflow from `workflows/exports/lead-import-v1.json`
4. Verifies database state

**Redeploy Command:**
1. Same as deploy
2. Exports the imported workflow back to `workflows/exports/lead-import-v1.json`
3. This ensures the exported JSON matches the running workflow

## Manual Execution Steps

Due to n8n API authentication limitations, workflow execution must be triggered manually via the UI.

### Step 1: Access n8n UI

Open http://localhost:5678 in your browser.

### Step 2: Login

- Email: `admin@n8n.local` (or as configured in `.env`)
- Password: As configured in `.env`

### Step 3: Open Workflow

1. Click on "Workflows" in the left sidebar
2. Find "Lead Import v1"
3. Click to open the workflow editor

### Step 4: Execute Workflow

1. Click the "Execute Workflow" button in the top-right
2. The workflow will process the mock data (2 leads)
3. Watch the execution progress on the canvas

### Step 5: Verify Results

After execution completes:

1. **Check execution status**: All nodes should show green (success)
2. **Check final response**: Should show `processed: 2, created: 2`
3. **Verify database**:
   ```bash
   docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT COUNT(*) FROM companies;"
   docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT COUNT(*) FROM contacts;"
   docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT COUNT(*) FROM leads;"
   ```

### Step 6: Test Idempotency

Execute the workflow a second time and verify no duplicates are created:

```bash
# Should still show 2 companies, 2 contacts, 2 leads
docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT COUNT(*) FROM companies;"
```

## PostgreSQL Credentials

The workflow uses the existing PostgreSQL credential in n8n:
- **Credential Name**: "SARA PostgreSQL"
- **Credential ID**: `sara-postgres`
- **Status**: Automatically bound to PostgreSQL nodes during import

The credential is stored in the n8n database and encrypted. No manual credential management is required.

## Workflow File Structure

```
workflows/
├── exports/
│   └── lead-import-v1.json    # Source of truth for workflow definition
├── backups/
│   └── lead-import-v1-backup-*.json  # Automatic backups before deployment
└── lead-import-v1.md          # Workflow documentation
```

## Best Practices

1. **Always use the deployment script** - Never manually import workflows
2. **Commit workflow JSON changes** - Keep the source of truth in Git
3. **Test after deployment** - Always execute the workflow after deployment
4. **Check idempotency** - Run twice to ensure no duplicates
5. **Review backups** - Check backup files before major changes

## Troubleshooting

### Workflow Import Fails

**Error**: `null value in column "id" violates not-null constraint`

**Solution**: Ensure the workflow JSON has an `id` field at the root level:
```json
{
  "name": "Lead Import v1",
  "id": "lead-import-v1",
  "nodes": [...]
}
```

### PostgreSQL Nodes Not Connected

**Error**: Workflow nodes show credential errors

**Solution**: The credential should auto-bind. If not:
1. Open the workflow in n8n UI
2. Click on each PostgreSQL node
3. Select "SARA PostgreSQL" credential
4. Save the workflow
5. Export using: `./scripts/deploy-workflow.sh export`

### Execution Fails

**Error**: Workflow execution shows errors

**Solution**:
1. Check n8n execution logs
2. Verify PostgreSQL is running: `docker-compose ps`
3. Verify database schema is initialized
4. Check PostgreSQL credentials in n8n

## Future Automation

To fully automate workflow execution, the following would be needed:

1. **n8n API Authentication**: Configure proper API credentials
2. **Webhook Triggers**: Add webhook nodes for programmatic execution
3. **Test Framework**: Implement automated testing of workflow outputs
4. **CI/CD Integration**: Add workflow deployment to CI/CD pipeline

## Migration to Backend API

When the backend API is ready, the workflow will be migrated to call the backend instead of accessing PostgreSQL directly. See `workflows/lead-import-v1.md` for the migration plan.
