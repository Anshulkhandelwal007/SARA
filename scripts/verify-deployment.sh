#!/bin/bash

# Project SARA - Deployment Verification Script
# This script verifies that all components are running correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker
check_docker() {
    print_info "Checking Docker..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed"
        return 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running"
        return 1
    fi
    
    print_success "Docker is running"
    return 0
}

# Function to check Docker Compose
check_docker_compose() {
    print_info "Checking Docker Compose..."
    
    if command_exists docker-compose; then
        DOCKER_COMPOSE="docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    else
        print_error "Docker Compose is not installed"
        return 1
    fi
    
    print_success "Docker Compose is available"
    return 0
}

# Function to check Docker containers
check_containers() {
    print_info "Checking Docker containers..."
    
    CONTAINERS=("sara-postgres" "sara-backend" "sara-n8n" "sara-pgadmin")
    ALL_RUNNING=true
    
    for CONTAINER in "${CONTAINERS[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
            print_success "Container $CONTAINER is running"
        else
            print_error "Container $CONTAINER is not running"
            ALL_RUNNING=false
        fi
    done
    
    if [ "$ALL_RUNNING" = true ]; then
        print_success "All containers are running"
        return 0
    else
        print_error "Some containers are not running"
        return 1
    fi
}

# Function to check Backend health
check_backend_health() {
    print_info "Checking Backend health..."
    
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    
    if [ $? -eq 0 ]; then
        if echo "$HEALTH_RESPONSE" | grep -q '"success":true'; then
            print_success "Backend is healthy"
            print_info "Response: $HEALTH_RESPONSE"
            return 0
        else
            print_error "Backend health check failed"
            print_info "Response: $HEALTH_RESPONSE"
            return 1
        fi
    else
        print_error "Backend is not responding"
        return 1
    fi
}

# Function to check PostgreSQL connectivity
check_postgres_connectivity() {
    print_info "Checking PostgreSQL connectivity..."
    
    if docker exec sara-postgres pg_isready -U sara_user -d sara_db >/dev/null 2>&1; then
        print_success "PostgreSQL is ready and accepting connections"
        return 0
    else
        print_error "PostgreSQL is not ready"
        return 1
    fi
}

# Function to check n8n health
check_n8n_health() {
    print_info "Checking n8n health..."
    
    HEALTH_RESPONSE=$(curl -s http://localhost:5678/healthz)
    
    if [ $? -eq 0 ]; then
        if echo "$HEALTH_RESPONSE" | grep -q '"status":"ok"'; then
            print_success "n8n is healthy"
            print_info "Response: $HEALTH_RESPONSE"
            return 0
        else
            print_error "n8n health check failed"
            print_info "Response: $HEALTH_RESPONSE"
            return 1
        fi
    else
        print_error "n8n is not responding"
        return 1
    fi
}

# Function to check workflow count
check_workflow_count() {
    print_info "Checking workflow count..."
    
    WORKFLOW_COUNT=$(docker exec sara-postgres psql -U sara_user -d sara_db -t -c "SELECT COUNT(*) FROM workflow_entity;" | tr -d ' ')
    
    print_info "Total workflows in database: $WORKFLOW_COUNT"
    
    if [ "$WORKFLOW_COUNT" -ge 2 ]; then
        print_success "Expected number of workflows found (>= 2)"
        return 0
    else
        print_warning "Unexpected workflow count (expected >= 2, found $WORKFLOW_COUNT)"
        return 1
    fi
}

# Function to check workflow names
check_workflow_names() {
    print_info "Checking workflow names..."
    
    WORKFLOWS=$(docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT id, name FROM workflow_entity;")
    
    print_info "Current workflows:"
    echo "$WORKFLOWS"
    
    EXPECTED_WORKFLOWS=(
        "lead-import-google-sheets-backend"
        "daily-followup-summary"
    )
    
    ALL_FOUND=true
    for WORKFLOW_ID in "${EXPECTED_WORKFLOWS[@]}"; do
        if echo "$WORKFLOWS" | grep -q "$WORKFLOW_ID"; then
            print_success "Workflow $WORKFLOW_ID found"
        else
            print_error "Workflow $WORKFLOW_ID not found"
            ALL_FOUND=false
        fi
    done
    
    if [ "$ALL_FOUND" = true ]; then
        print_success "All expected workflows found"
        return 0
    else
        print_error "Some expected workflows are missing"
        return 1
    fi
}

# Function to check for obsolete workflows
check_obsolete_workflows() {
    print_info "Checking for obsolete workflows..."
    
    OBSOLETE_PATTERNS=("v1" "mock" "deprecated")
    HAS_OBSOLETE=false
    
    for PATTERN in "${OBSOLETE_PATTERNS[@]}"; do
        COUNT=$(docker exec sara-postgres psql -U sara_user -d sara_db -t -c "SELECT COUNT(*) FROM workflow_entity WHERE name ILIKE '%$PATTERN%';" | tr -d ' ')
        if [ "$COUNT" -gt 0 ]; then
            print_error "Found workflow with pattern: $PATTERN"
            HAS_OBSOLETE=true
        fi
    done
    
    if [ "$HAS_OBSOLETE" = true ]; then
        print_error "Obsolete workflows found"
        return 1
    else
        print_success "No obsolete workflows found"
        return 0
    fi
}

# Function to check architecture compliance
check_architecture_compliance() {
    print_info "Checking architecture compliance..."
    
    # Check Lead Import workflow nodes
    LEAD_IMPORT_NODES=$(docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT nodes FROM workflow_entity WHERE id = 'lead-import-google-sheets-backend';")
    
    if echo "$LEAD_IMPORT_NODES" | grep -q "googleSheets"; then
        print_success "Lead Import uses Google Sheets"
    else
        print_error "Lead Import does not use Google Sheets"
        return 1
    fi
    
    if echo "$LEAD_IMPORT_NODES" | grep -q "httpRequest"; then
        print_success "Lead Import uses HTTP Request"
    else
        print_error "Lead Import does not use HTTP Request"
        return 1
    fi
    
    if echo "$LEAD_IMPORT_NODES" | grep -q "sara-backend:8000"; then
        print_success "Lead Import calls Backend API"
    else
        print_error "Lead Import does not call Backend API"
        return 1
    fi
    
    if echo "$LEAD_IMPORT_NODES" | grep -iq "postgres"; then
        print_error "Lead Import contains PostgreSQL nodes (violation)"
        return 1
    else
        print_success "Lead Import does not contain PostgreSQL nodes"
    fi
    
    print_success "Architecture compliance verified"
    return 0
}

# Function to check repository sync
check_repository_sync() {
    print_info "Checking repository synchronization..."
    
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        print_warning "Not in a Git repository. Skipping repository sync check."
        return 0
    fi
    
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "Git working directory has uncommitted changes"
        git status --short
        return 1
    else
        print_success "Git working directory is clean"
        return 0
    fi
}

# Function to print verification summary
print_summary() {
    print_info "=========================================="
    print_info "VERIFICATION SUMMARY"
    print_info "=========================================="
    
    TOTAL_CHECKS=0
    PASSED_CHECKS=0
    FAILED_CHECKS=0
    WARNING_CHECKS=0
    
    # Count checks
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_docker >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_docker_compose >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_containers >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_backend_health >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_postgres_connectivity >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_n8n_health >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_workflow_count >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_workflow_names >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_obsolete_workflows >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_architecture_compliance >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    REPO_SYNC_RESULT=$(check_repository_sync)
    if [ $? -eq 0 ]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        WARNING_CHECKS=$((WARNING_CHECKS + 1))
    fi
    
    print_info "Total Checks: $TOTAL_CHECKS"
    print_success "Passed: $PASSED_CHECKS"
    print_error "Failed: $FAILED_CHECKS"
    print_warning "Warnings: $WARNING_CHECKS"
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        print_success "All critical checks passed!"
        return 0
    else
        print_error "Some checks failed. Please review the output above."
        return 1
    fi
}

# Main verification flow
main() {
    print_info "=========================================="
    print_info "Project SARA - Deployment Verification"
    print_info "=========================================="
    print_info ""
    
    check_docker
    check_docker_compose
    check_containers
    check_backend_health
    check_postgres_connectivity
    check_n8n_health
    check_workflow_count
    check_workflow_names
    check_obsolete_workflows
    check_architecture_compliance
    check_repository_sync
    
    print_info ""
    print_summary
}

# Run main function
main "$@"
