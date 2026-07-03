# Project SARA - Deployment Guide

This guide covers the deployment process for Project SARA, including infrastructure setup, service configuration, and workflow management.

## Prerequisites

- Docker Desktop (Mac/Windows) or Docker Engine (Linux)
- Docker Compose
- Git
- Bash shell (for deployment scripts)
- At least 4GB RAM available for Docker
- At least 10GB disk space available

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Anshulkhandelwal007/SARA.git
cd SARA
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Deploy

```bash
./scripts/deploy-all.sh
```

### 4. Verify

```bash
./scripts/verify-deployment.sh
```

## Detailed Deployment Process

### Step 1: Environment Configuration

The `.env` file contains all required environment variables for the SARA stack:

```bash
# PostgreSQL
POSTGRES_DB=sara_db
POSTGRES_USER=sara_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432
TZ=Asia/Kolkata

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
PGADMIN_CONFIG_SERVER_MODE=False

# n8n
N8N_PORT=5678
N8N_HOST=localhost
N8N_PROTOCOL=http
N8N_ENCRYPTION_KEY=your_encryption_key_32_chars
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_n8n_password
N8N_EDITOR_BASE_URL=http://localhost:5678
WEBHOOK_URL=http://localhost:5678
N8N_TIMEZONE=Asia/Kolkata

# Backend
BACKEND_APP_NAME=SARA Backend API
BACKEND_APP_VERSION=1.0.0
BACKEND_DEBUG=false
BACKEND_PORT=8000
```

**Important Notes**:
- Change all default passwords in production
- `N8N_ENCRYPTION_KEY` must be exactly 32 characters
- Use strong passwords for PostgreSQL and pgAdmin
- **CRITICAL**: `N8N_EDITOR_BASE_URL` and `WEBHOOK_URL` must be set to `http://localhost:5678` for OAuth to work correctly

### Step 2: Docker Services

The deployment script starts the following services:

1. **PostgreSQL** - Database (port 5432)
2. **pgAdmin** - Database management UI (port 5050)
3. **n8n** - Workflow automation (port 5678)
4. **Backend** - FastAPI backend (port 8000)

### Step 3: Workflow Import

The deployment script automatically imports all workflows from `workflows/exports/`:

- `lead-import-google-sheets.json` - Google Sheets lead import
- `daily-followup-summary.json` - Daily follow-up summary

### Step 4: Service Health Checks

The deployment script waits for all services to be healthy:

- PostgreSQL: `pg_isready` check
- Backend: HTTP health endpoint
- n8n: HTTP health endpoint

## Manual Deployment

If you prefer manual deployment instead of using the script:

### Start Services

```bash
docker-compose up -d
```

### Wait for Services

```bash
# Wait for PostgreSQL
docker exec sara-postgres pg_isready -U sara_user -d sara_db

# Wait for Backend
curl http://localhost:8000/health

# Wait for n8n
curl http://localhost:5678/healthz
```

### Import Workflows

```bash
# Copy workflow to n8n container
docker cp workflows/exports/lead-import-google-sheets.json sara-n8n:/tmp/

# Import workflow
docker exec sara-n8n n8n import:workflow --input=/tmp/lead-import-google-sheets.json

# Repeat for daily-followup-summary.json
```

### Restart n8n

```bash
docker-compose restart n8n
```

## Service URLs

After deployment, access services at:

- **Backend API**: http://localhost:8000
- **Backend Health**: http://localhost:8000/health
- **Backend Docs**: http://localhost:8000/docs
- **n8n UI**: http://localhost:5678
- **n8n Health**: http://localhost:5678/healthz
- **pgAdmin**: http://localhost:5050

## Updating Workflows

To update n8n workflows:

1. Update workflow JSON in `workflows/exports/`
2. Copy to n8n container:
   ```bash
   docker cp workflows/exports/workflow-name.json sara-n8n:/tmp/
   ```
3. Import workflow:
   ```bash
   docker exec sara-n8n n8n import:workflow --input=/tmp/workflow-name.json
   ```
4. Restart n8n:
   ```bash
   docker-compose restart n8n
   ```

## Restarting Services

### Restart All Services

```bash
docker-compose restart
```

### Restart Specific Service

```bash
docker-compose restart backend
docker-compose restart n8n
docker-compose restart postgres
```

### Stop All Services

```bash
docker-compose down
```

### Stop and Remove Volumes (⚠️ Destructive)

```bash
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Check what's using the port
lsof -i :5432
lsof -i :5678
lsof -i :8000
lsof -i :5050

# Stop conflicting service or change port in .env
```

### Container Won't Start

Check container logs:

```bash
docker logs sara-backend
docker logs sara-n8n
docker logs sara-postgres
```

### Database Connection Failed

1. Verify PostgreSQL is running:
   ```bash
   docker ps | grep postgres
   ```

2. Check PostgreSQL logs:
   ```bash
   docker logs sara-postgres
   ```

3. Verify environment variables in `.env`

### n8n Workflows Not Loading

1. Verify n8n is connected to PostgreSQL
2. Check n8n logs:
   ```bash
   docker logs sara-n8n
   ```
3. Manually re-import workflows
4. Restart n8n container

### OAuth Redirect URI Issues

If Google OAuth fails with "redirect_uri_mismatch" or "invalid_request":

1. Verify n8n environment variables:
   ```bash
   docker exec sara-n8n env | grep -E "N8N_EDITOR_BASE_URL|WEBHOOK_URL"
   ```
2. Should show:
   - `N8N_EDITOR_BASE_URL=http://localhost:5678`
   - `WEBHOOK_URL=http://localhost:5678`
3. If incorrect, update `.env` file and restart n8n:
   ```bash
   docker-compose down n8n
   docker-compose up -d n8n
   ```
4. Delete and recreate OAuth credentials in n8n UI
5. See [Google OAuth Setup Guide](google-oauth-setup.md) for detailed troubleshooting

### Backend API Not Responding

1. Check backend logs:
   ```bash
   docker logs sara-backend
   ```

2. Verify database connectivity
3. Check if backend is built:
   ```bash
   docker-compose build backend
   ```

## Production Deployment

For production deployment:

1. **Security**:
   - Change all default passwords
   - Use strong encryption keys
   - Enable HTTPS/TLS
   - Configure firewall rules

2. **Performance**:
   - Allocate sufficient resources
   - Configure PostgreSQL for production
   - Enable n8n queue mode for high throughput
   - Add load balancing if needed

3. **Monitoring**:
   - Set up log aggregation
   - Configure health check monitoring
   - Set up alerts for service failures
   - Monitor resource usage

4. **Backup**:
   - Regular PostgreSQL backups
   - n8n workflow exports
   - Configuration backups
   - Disaster recovery testing

## Maintenance

### Regular Tasks

- **Daily**: Monitor service health
- **Weekly**: Review logs for errors
- **Monthly**: Update Docker images
- **Quarterly**: Review and update security patches

### Updates

Update Docker images:

```bash
docker-compose pull
docker-compose up -d
```

Update backend code:

```bash
git pull
docker-compose build backend
docker-compose up -d backend
```

## Support

For issues or questions:

1. Check this deployment guide
2. Review logs for error messages
3. Check the troubleshooting section
4. Review architecture documentation
5. Check GitHub issues
