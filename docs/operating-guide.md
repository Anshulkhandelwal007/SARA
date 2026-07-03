# Project SARA - Operating Guide

This guide covers day-to-day operations, monitoring, and maintenance of Project SARA.

## Daily Operations

### Morning Checklist

1. **Check Service Health**:
   ```bash
   ./scripts/verify-deployment.sh
   ```

2. **Review Logs**:
   ```bash
   docker logs sara-backend --tail 50
   docker logs sara-n8n --tail 50
   docker logs sara-postgres --tail 50
   ```

3. **Check n8n Workflows**:
   - Open http://localhost:5678
   - Verify workflows are active
   - Check for failed executions

4. **Review Backend API**:
   - Open http://localhost:8000/docs
   - Check API endpoints
   - Test critical endpoints

### Monitoring Dashboard

Key metrics to monitor:

- **Service Health**: All containers running
- **Database Connectivity**: PostgreSQL accepting connections
- **API Response Time**: Backend responding within acceptable time
- **Workflow Executions**: n8n workflows executing successfully
- **Disk Space**: Docker volumes not exceeding 80% capacity
- **Memory Usage**: Containers not exceeding allocated memory

## Service Management

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend
docker-compose up -d n8n
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop specific service
docker-compose stop backend
docker-compose stop n8n
```

### Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart n8n
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs n8n
docker-compose logs postgres

# View logs with tail
docker logs sara-backend --tail 100 -f
```

## n8n Workflow Management

### Activating Workflows

1. Open n8n UI: http://localhost:5678
2. Navigate to "Workflows"
3. Click on workflow
4. Click "Active" toggle
5. Save workflow

### Deactivating Workflows

1. Open n8n UI: http://localhost:5678
2. Navigate to "Workflows"
3. Click on workflow
4. Click "Active" toggle to deactivate
5. Save workflow

### Executing Workflows Manually

1. Open n8n UI: http://localhost:5678
2. Navigate to "Workflows"
3. Click on workflow
4. Click "Execute Workflow"
5. Monitor execution in "Executions" tab

### Viewing Workflow Executions

1. Open n8n UI: http://localhost:5678
2. Navigate to "Executions"
3. View execution history
4. Click on execution to see details

### Debugging Workflows

1. Open n8n UI: http://localhost:5678
2. Click on workflow
3. Click "Execute Workflow"
4. Check execution results
5. Review node outputs
6. Check logs for errors

## Database Operations

### Connecting to PostgreSQL

```bash
# Using psql
docker exec -it sara-postgres psql -U sara_user -d sara_db

# Using pgAdmin
# Open http://localhost:5050
# Login with credentials from .env
```

### Common Database Queries

```sql
-- Check lead count
SELECT COUNT(*) FROM leads;

-- Check company count
SELECT COUNT(*) FROM companies;

-- Check workflow count
SELECT COUNT(*) FROM workflow_entity;

-- View recent leads
SELECT * FROM leads ORDER BY created_at DESC LIMIT 10;

-- Check for overdue follow-ups
SELECT * FROM leads WHERE next_followup_at < NOW();
```

### Database Maintenance

```bash
# Vacuum database
docker exec sara-postgres psql -U sara_user -d sara_db -c "VACUUM ANALYZE;"

# Reindex database
docker exec sara-postgres psql -U sara_user -d sara_db -c "REINDEX DATABASE sara_db;"

# Check database size
docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT pg_size_pretty(pg_database_size('sara_db'));"
```

## Backend API Operations

### Testing API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get leads
curl http://localhost:8000/api/v1/leads

# Get follow-ups due
curl http://localhost:8000/api/v1/leads/followups-due

# Get lead priority
curl http://localhost:8000/api/v1/leads/priority/{lead_id}
```

### Viewing API Documentation

Open http://localhost:8000/docs in your browser to view interactive API documentation.

### Backend Logs

```bash
# View recent logs
docker logs sara-backend --tail 100

# Follow logs in real-time
docker logs sara-backend -f

# View logs with timestamps
docker logs sara-backend --timestamps
```

## Troubleshooting Common Issues

### Service Not Starting

**Symptoms**: Container won't start, keeps restarting

**Steps**:
1. Check logs: `docker logs <container-name>`
2. Check resource usage: `docker stats`
3. Check port conflicts: `lsof -i :<port>`
4. Restart Docker Desktop
5. Rebuild container: `docker-compose build <service>`

### Database Connection Failed

**Symptoms**: Backend can't connect to PostgreSQL

**Steps**:
1. Check PostgreSQL is running: `docker ps | grep postgres`
2. Check PostgreSQL logs: `docker logs sara-postgres`
3. Verify environment variables in `.env`
4. Test connection: `docker exec sara-backend ping sara-postgres`

### n8n Workflows Not Executing

**Symptoms**: Scheduled workflows not running

**Steps**:
1. Check workflow is active in n8n UI
2. Check n8n logs: `docker logs sara-n8n`
3. Verify schedule configuration
4. Manually execute workflow to test
5. Check n8n timezone settings

### High Memory Usage

**Symptoms**: Containers using excessive memory

**Steps**:
1. Check memory usage: `docker stats`
2. Restart heavy containers
3. Check for memory leaks in logs
4. Adjust container memory limits in docker-compose.yml
5. Restart Docker Desktop

### Disk Space Issues

**Symptoms**: Disk full, containers failing

**Steps**:
1. Check disk usage: `df -h`
2. Check Docker disk usage: `docker system df`
3. Clean up unused containers: `docker container prune`
4. Clean up unused images: `docker image prune`
5. Clean up unused volumes: `docker volume prune`
6. Clean up everything: `docker system prune -a`

## Performance Optimization

### Database Optimization

```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM leads WHERE status = 'new';

-- Create indexes if needed
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_next_followup ON leads(next_followup_at);
```

### Container Resource Limits

Add to docker-compose.yml if needed:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### n8n Performance

For high-throughput scenarios, enable n8n queue mode:

```yaml
services:
  n8n:
    environment:
      - EXECUTIONS_MODE=queue
      - QUEUE_BULL_REDIS_HOST=redis
      - QUEUE_BULL_REDIS_PORT=6379
```

## Security Operations

### Regular Security Tasks

1. **Update passwords**:
   - Change PostgreSQL password
   - Change n8n admin password
   - Change pgAdmin password

2. **Update Docker images**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

3. **Review access logs**:
   ```bash
   docker logs sara-n8n | grep -i error
   docker logs sara-backend | grep -i error
   ```

4. **Check for vulnerabilities**:
   ```bash
   docker scan sara-backend
   docker scan n8nio/n8n:latest
   ```

### Access Control

1. **Restrict network access**:
   - Use firewall rules
   - Configure Docker network isolation
   - Use VPN for remote access

2. **Enable authentication**:
   - n8n basic auth (enabled by default)
   - pgAdmin authentication
   - Consider API authentication for backend

## Backup Operations

### Daily Backup

```bash
# Automated backup script
./scripts/backup-all.sh
```

### Manual Backup

```bash
# Database backup
docker exec sara-postgres pg_dump -U sara_user sara_db > backup.sql

# Volume backup
docker run --rm -v sara_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres.tar.gz /data
```

### Backup Verification

```bash
# Test backup restoration
docker exec -i sara-postgres psql -U sara_user -d sara_db < backup.sql
```

## Update Operations

### Updating Backend Code

```bash
# Pull latest changes
git pull origin develop

# Rebuild backend
docker-compose build backend

# Restart backend
docker-compose up -d backend

# Verify
./scripts/verify-deployment.sh
```

### Updating Workflows

```bash
# Update workflow JSON in repository
git pull

# Import updated workflows
for workflow in workflows/exports/*.json; do
    docker cp "$workflow" sara-n8n:/tmp/
    docker exec sara-n8n n8n import:workflow --input=/tmp/$(basename "$workflow")
done

# Restart n8n
docker-compose restart n8n
```

### Updating Docker Images

```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d

# Verify
./scripts/verify-deployment.sh
```

## Monitoring and Alerts

### Setting Up Monitoring

1. **Container monitoring**:
   - Use Docker stats
   - Consider Prometheus + Grafana
   - Monitor resource usage

2. **Application monitoring**:
   - Backend health checks
   - API response times
   - Error rates

3. **Database monitoring**:
   - Connection pool usage
   - Query performance
   - Disk space

### Alert Thresholds

- **Critical**: Service down > 5 minutes
- **Warning**: Disk space > 80%
- **Critical**: Disk space > 90%
- **Warning**: Memory usage > 80%
- **Critical**: Memory usage > 90%
- **Warning**: CPU usage > 80% for > 10 minutes

## Incident Response

### Incident Classification

- **P1 - Critical**: System down, data loss, security breach
- **P2 - High**: Major functionality broken, performance degradation
- **P3 - Medium**: Minor functionality broken, non-critical issues
- **P4 - Low**: Cosmetic issues, documentation updates

### Incident Response Process

1. **Identify**: Detect and classify incident
2. **Contain**: Minimize impact
3. **Resolve**: Fix the issue
4. **Verify**: Confirm fix works
5. **Document**: Record lessons learned

### Escalation Matrix

- **P1**: Immediate escalation to all stakeholders
- **P2**: Escalate within 1 hour
- **P3**: Escalate within 4 hours
- **P4**: Handle during normal operations

## Documentation Maintenance

Keep this guide updated:

- After any operational changes
- When adding new services
- After incident resolution
- Quarterly review

## Related Documentation

- [Deployment Guide](deployment.md)
- [Disaster Recovery](disaster-recovery.md)
- [Runbook](runbook.md)
- [Architecture Documentation](architecture.md)
