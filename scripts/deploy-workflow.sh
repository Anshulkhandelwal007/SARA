#!/bin/bash

# SARA Workflow Management Script
# Automates workflow deployment, replacement, and export
# Note: Execution still requires manual trigger via n8n UI due to API authentication limitations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORKFLOW_NAME="Lead Import v1"
WORKFLOW_FILE="$PROJECT_ROOT/workflows/exports/lead-import-v1.json"
BACKUP_DIR="$PROJECT_ROOT/workflows/backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to backup existing workflow
backup_workflow() {
    log_info "Backing up existing workflow..."
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/lead-import-v1-backup-$timestamp.json"
    
    docker exec sara-n8n n8n export:workflow --all --output=/tmp/backup.json
    docker cp sara-n8n:/tmp/backup.json "$backup_file"
    
    # Extract just the Lead Import v1 workflow if it exists
    if [ -f "$backup_file" ]; then
        log_info "Backup saved to: $backup_file"
    else
        log_warn "No existing workflow to backup"
    fi
}

# Function to delete existing workflow
delete_workflow() {
    log_info "Deleting existing workflow from n8n..."
    
    # Get workflow ID by name
    local workflow_id=$(docker exec sara-postgres psql -U sara_user -d sara_db -t -c "SELECT id FROM workflow_entity WHERE name = '$WORKFLOW_NAME';" | tr -d ' ')
    
    if [ -n "$workflow_id" ]; then
        docker exec sara-postgres psql -U sara_user -d sara_db -c "DELETE FROM workflow_entity WHERE id = '$workflow_id';"
        log_info "Deleted workflow: $workflow_id"
    else
        log_warn "No existing workflow found to delete"
    fi
}

# Function to import workflow
import_workflow() {
    log_info "Importing workflow from: $WORKFLOW_FILE"
    
    # Copy workflow to container
    docker cp "$WORKFLOW_FILE" sara-n8n:/tmp/lead-import-v1.json
    
    # Import workflow
    docker exec sara-n8n n8n import:workflow --input=/tmp/lead-import-v1.json
    
    log_info "Workflow imported successfully"
}

# Function to export workflow
export_workflow() {
    log_info "Exporting workflow..."
    
    # Get workflow ID
    local workflow_id=$(docker exec sara-postgres psql -U sara_user -d sara_db -t -c "SELECT id FROM workflow_entity WHERE name = '$WORKFLOW_NAME';" | tr -d ' ')
    
    if [ -n "$workflow_id" ]; then
        docker exec sara-n8n n8n export:workflow --id="$workflow_id" --output=/tmp/exported-workflow.json
        docker cp sara-n8n:/tmp/exported-workflow.json "$WORKFLOW_FILE"
        log_info "Workflow exported to: $WORKFLOW_FILE"
    else
        log_error "Workflow not found for export"
        exit 1
    fi
}

# Function to verify database state
verify_database() {
    log_info "Verifying database state..."
    
    local company_count=$(docker exec sara-postgres psql -U sara_user -d sara_db -t -c "SELECT COUNT(*) FROM companies;")
    local contact_count=$(docker exec sara-postgres psql -U sara_user -d sara_db -t -c "SELECT COUNT(*) FROM contacts;")
    local lead_count=$(docker exec sara-postgres psql -U sara_user -d sara_db -t -c "SELECT COUNT(*) FROM leads;")
    
    log_info "Database state:"
    log_info "  Companies: $company_count"
    log_info "  Contacts: $contact_count"
    log_info "  Leads: $lead_count"
}

# Main execution
case "${1:-deploy}" in
    backup)
        backup_workflow
        ;;
    delete)
        delete_workflow
        ;;
    import)
        import_workflow
        ;;
    export)
        export_workflow
        ;;
    deploy)
        log_info "Starting workflow deployment..."
        backup_workflow
        delete_workflow
        import_workflow
        verify_database
        log_info "Deployment complete. Please execute the workflow manually via n8n UI at http://localhost:5678"
        ;;
    redeploy)
        log_info "Starting workflow redeployment..."
        backup_workflow
        delete_workflow
        import_workflow
        export_workflow
        verify_database
        log_info "Redeployment complete. Workflow exported back to: $WORKFLOW_FILE"
        ;;
    verify)
        verify_database
        ;;
    *)
        echo "Usage: $0 {backup|delete|import|export|deploy|redeploy|verify}"
        echo ""
        echo "Commands:"
        echo "  backup    - Backup existing workflow"
        echo "  delete   - Delete existing workflow from n8n"
        echo "  import   - Import workflow from JSON file"
        echo "  export   - Export workflow to JSON file"
        echo "  deploy   - Full deployment (backup, delete, import, verify)"
        echo "  redeploy - Full redeployment with export back to file"
        echo "  verify   - Verify database state"
        exit 1
        ;;
esac
