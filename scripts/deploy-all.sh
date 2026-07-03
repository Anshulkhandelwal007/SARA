#!/bin/bash

# Project SARA - One-Command Deployment Script
# This script deploys the entire SARA stack from scratch

set -e  # Exit on error

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

# Function to check if Docker is running
check_docker() {
    print_info "Checking Docker..."
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker."
        exit 1
    fi
    
    print_success "Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    print_info "Checking Docker Compose..."
    if command_exists docker-compose; then
        print_success "Docker Compose is available (docker-compose)"
        DOCKER_COMPOSE="docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        print_success "Docker Compose is available (docker compose)"
        DOCKER_COMPOSE="docker compose"
    else
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi
}

# Function to verify Git state
verify_git_state() {
    print_info "Verifying Git state..."
    
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        print_warning "Not in a Git repository. Skipping Git verification."
        return
    fi
    
    BRANCH=$(git branch --show-current)
    print_info "Current branch: $BRANCH"
    
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "Git working directory has uncommitted changes."
        git status --short
        read -p "Continue deployment? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Deployment cancelled by user."
            exit 1
        fi
    else
        print_success "Git working directory is clean"
    fi
}

# Function to check environment file
check_env_file() {
    print_info "Checking environment file..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            print_warning ".env file not found. Copying from .env.example..."
            cp .env.example .env
            print_warning "Please edit .env file with your configuration before proceeding."
            print_warning "Press Enter to continue after editing .env file..."
            read
        else
            print_error ".env file not found and .env.example does not exist."
            print_error "Please create .env file with required environment variables."
            exit 1
        fi
    fi
    
    print_success ".env file exists"
}

# Function to start Docker services
start_docker_services() {
    print_info "Starting Docker services..."
    
    $DOCKER_COMPOSE up -d
    
    print_info "Waiting for services to be healthy..."
    sleep 10
    
    print_success "Docker services started"
}

# Function to wait for PostgreSQL
wait_for_postgres() {
    print_info "Waiting for PostgreSQL to be ready..."
    
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if docker exec sara-postgres pg_isready -U sara_user -d sara_db >/dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            return
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo -n "."
        sleep 2
    done
    
    print_error "PostgreSQL failed to start within expected time"
    exit 1
}

# Function to wait for Backend
wait_for_backend() {
    print_info "Waiting for Backend to be ready..."
    
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend is ready"
            return
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo -n "."
        sleep 2
    done
    
    print_error "Backend failed to start within expected time"
    exit 1
}

# Function to wait for n8n
wait_for_n8n() {
    print_info "Waiting for n8n to be ready..."
    
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -s http://localhost:5678/healthz >/dev/null 2>&1; then
            print_success "n8n is ready"
            return
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo -n "."
        sleep 2
    done
    
    print_error "n8n failed to start within expected time"
    exit 1
}

# Function to import n8n workflows
import_n8n_workflows() {
    print_info "Importing n8n workflows..."
    
    if [ ! -d "workflows/exports" ]; then
        print_warning "workflows/exports directory not found. Skipping workflow import."
        return
    fi
    
    WORKFLOW_COUNT=$(ls -1 workflows/exports/*.json 2>/dev/null | wc -l)
    
    if [ $WORKFLOW_COUNT -eq 0 ]; then
        print_warning "No workflow files found in workflows/exports/"
        return
    fi
    
    print_info "Found $WORKFLOW_COUNT workflow files"
    
    for WORKFLOW_FILE in workflows/exports/*.json; do
        WORKFLOW_NAME=$(basename "$WORKFLOW_FILE")
        print_info "Importing $WORKFLOW_NAME..."
        
        # Copy workflow to n8n container
        docker cp "$WORKFLOW_FILE" sara-n8n:/tmp/"$WORKFLOW_NAME"
        
        # Import workflow using n8n CLI
        docker exec sara-n8n n8n import:workflow --input=/tmp/"$WORKFLOW_NAME"
        
        print_success "Imported $WORKFLOW_NAME"
    done
    
    print_success "All workflows imported"
}

# Function to verify workflows
verify_workflows() {
    print_info "Verifying n8n workflows..."
    
    WORKFLOW_COUNT=$(docker exec sara-postgres psql -U sara_user -d sara_db -t -c "SELECT COUNT(*) FROM workflow_entity;" | tr -d ' ')
    
    print_info "Total workflows in database: $WORKFLOW_COUNT"
    
    if [ "$WORKFLOW_COUNT" -eq 0 ]; then
        print_error "No workflows found in database"
        return 1
    fi
    
    docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT id, name FROM workflow_entity;"
    
    print_success "Workflows verified"
}

# Function to restart n8n
restart_n8n() {
    print_info "Restarting n8n to reload workflows..."
    
    $DOCKER_COMPOSE restart n8n
    
    sleep 5
    
    wait_for_n8n
    
    print_success "n8n restarted successfully"
}

# Function to print deployment summary
print_summary() {
    print_info "=========================================="
    print_info "DEPLOYMENT SUMMARY"
    print_info "=========================================="
    
    print_info "Services:"
    $DOCKER_COMPOSE ps
    
    print_info ""
    print_info "Service URLs:"
    print_info "  - Backend API: http://localhost:8000"
    print_info "  - Backend Health: http://localhost:8000/health"
    print_info "  - Backend Docs: http://localhost:8000/docs"
    print_info "  - n8n: http://localhost:5678"
    print_info "  - n8n Health: http://localhost:5678/healthz"
    print_info "  - pgAdmin: http://localhost:5050"
    
    print_info ""
    print_info "Database:"
    print_info "  - PostgreSQL: localhost:5432"
    print_info "  - Database: sara_db"
    print_info "  - User: sara_user"
    
    print_info ""
    print_info "Next Steps:"
    print_info "  1. Configure Google Sheets credentials in n8n (if using Google Sheets import)"
    print_info "  2. Activate workflows in n8n UI"
    print_info "  3. Run ./scripts/verify-deployment.sh to verify deployment"
    
    print_info ""
    print_success "Deployment completed successfully!"
}

# Main deployment flow
main() {
    print_info "=========================================="
    print_info "Project SARA - Deployment Script"
    print_info "=========================================="
    print_info ""
    
    check_docker
    check_docker_compose
    verify_git_state
    check_env_file
    start_docker_services
    wait_for_postgres
    wait_for_backend
    wait_for_n8n
    import_n8n_workflows
    verify_workflows
    restart_n8n
    print_summary
}

# Run main function
main "$@"
