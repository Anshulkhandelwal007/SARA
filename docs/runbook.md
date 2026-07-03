# Project SARA - Runbook

This runbook provides step-by-step procedures for common operational tasks and incident response.

## Table of Contents

- [Initial Deployment](#initial-deployment)
- [Daily Operations](#daily-operations)
- [Service Management](#service-management)
- [Workflow Management](#workflow-management)
- [Database Operations](#database-operations)
- [Incident Response](#incident-response)
- [Troubleshooting](#troubleshooting)

## Initial Deployment

### First-Time Setup

**Objective**: Deploy SARA stack on a new machine

**Prerequisites**:
- Docker Desktop installed
- Git installed
- 4GB RAM available
- 10GB disk space available

**Steps**:

1. Clone repository:
   ```bash
   git clone https://github.com/Anshulkhandelwal007/SARA.git
   cd SARA
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Deploy stack:
   ```bash
   ./scripts/deploy-all.sh
   ```

4. Verify deployment:
   ```bash
   ./scripts/verify-deployment.sh
   ```

5. Configure n8n:
   - Open http://localhost:5678
   - Configure Google Sheets credentials (if needed)
   - Activate workflows

**Expected Outcome**:
- All Docker containers running
- Backend API accessible at http://localhost:8000
- n8n UI accessible at http://localhost:5678
- pgAdmin accessible at http://localhost:5050
- 2 workflows imported in n8n

**Rollback**: If deployment fails:
   ```bash
   docker-compose down
   # Check logs: docker-compose logs
   # Fix issue in .env or docker-compose.yml
   ./scripts/deploy-all.sh
   ```

## Daily Operations

### Morning Health Check

**Objective**: Verify all services are healthy

**Steps**:

1. Run verification script:
   ```bash
   ./scripts/verify-deployment.sh
   ```

2. Check logs for errors:
   ```bash
   docker logs sara-backend --tail 50
   docker logs sara-n8n --tail 50
   ```

3. Check n8n workflow executions:
   - Open http://localhost:5678
   - Navigate to "Executions"
   - Review recent executions for errors

**Expected Outcome**:
- All checks pass
- No error messages in logs
- Workflows executing successfully

**If Issues Found**:
- See [Troubleshooting](#troubleshooting) section

### Backup Verification

**Objective**: Ensure backups are running correctly

**Steps**:

1. Check last backup date:
   ```bash
   ls -lh backups/
   ```

2. Verify backup integrity:
   ```bash
   # Test restore on test database
   docker exec -i sara-postgres psql -U sara_user -d sara_db_test < backup_latest.sql
   ```

**Expected Outcome**:
- Recent backup exists (within 24 hours)
- Backup can be restored successfully

## Service Management

### Restart All Services

**Objective**: Restart all SARA services

**When to Use**: After configuration changes, updates, or if services are unresponsive

**Steps**:

1. Restart services:
   ```bash
   docker-compose restart
   ```

2. Wait for services to start:
   ```bash
   sleep 30
   ```

3. Verify services:
   ```bash
   ./scripts/verify-deployment.sh
   ```

**Expected Outcome**:
- All services restart successfully
- All verification checks pass

### Restart Specific Service

**Objective**: Restart a single service without affecting others

**When to Use**: When only one service needs restart

**Steps**:

```bash
# Restart backend
docker-compose restart backend

# Restart n8n
docker-compose restart n8n

# Restart PostgreSQL
docker-compose restart postgres
```

**Expected Outcome**:
- Specified service restarts
- Other services unaffected
- System remains functional

### Rebuild Backend

**Objective**: Rebuild backend container with latest code

**When to Use**: After code changes, dependency updates

**Steps**:

1. Pull latest code:
   ```bash
   git pull origin develop
   ```

2. Rebuild backend:
   ```bash
   docker-compose build backend
   ```

3. Restart backend:
   ```bash
   docker-compose up -d backend
   ```

4. Verify:
   ```bash
   curl http://localhost:8000/health
   ```

**Expected Outcome**:
- Backend rebuilt with latest code
- Backend responding to health checks

## Workflow Management

### Import New Workflow

**Objective**: Add a new workflow to n8n

**When to Use**: When creating new automation

**Steps**:

1. Create workflow JSON in `workflows/exports/`
2. Copy to n8n container:
   ```bash
   docker cp workflows/exports/new-workflow.json sara-n8n:/tmp/
   ```
3. Import workflow:
   ```bash
   docker exec sara-n8n n8n import:workflow --input=/tmp/new-workflow.json
   ```
4. Restart n8n:
   ```bash
   docker-compose restart n8n
   ```
5. Verify in UI:
   - Open http://localhost:5678
   - Check workflow list

**Expected Outcome**:
- Workflow imported successfully
- Workflow visible in n8n UI

### Update Existing Workflow

**Objective**: Update an existing workflow

**When to Use**: When modifying workflow logic

**Steps**:

1. Update workflow JSON in `workflows/exports/`
2. Delete old workflow from database:
   ```bash
   docker exec sara-postgres psql -U sara_user -d sara_db -c "DELETE FROM workflow_entity WHERE id = 'workflow-id';"
   ```
3. Import updated workflow:
   ```bash
   docker cp workflows/exports/workflow.json sara-n8n:/tmp/
   docker exec sara-n8n n8n import:workflow --input=/tmp/workflow.json
   ```
4. Restart n8n:
   ```bash
   docker-compose restart n8n
   ```

**Expected Outcome**:
- Workflow updated with new logic
- Old version removed

### Activate Workflow

**Objective**: Enable a workflow for execution

**When to Use**: When workflow is ready for production

**Steps**:

1. Open n8n UI: http://localhost:5678
2. Navigate to "Workflows"
3. Click on workflow
4. Toggle "Active" to ON
5. Click "Save"

**Expected Outcome**:
- Workflow is active
- Scheduled workflows execute on schedule
- Manual workflows can be executed

## Database Operations

### Database Backup

**Objective**: Create a backup of the database

**When to Use**: Before major changes, regularly

**Steps**:

```bash
# Create backup
docker exec sara-postgres pg_dump -U sara_user sara_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backup_$(date +%Y%m%d_%H%M%S).sql
```

**Expected Outcome**:
- Backup file created
- Backup file compressed

### Database Restore

**Objective**: Restore database from backup

**When to Use**: After data loss, corruption

**Steps**:

1. Stop services:
   ```bash
   docker-compose down
   ```

2. Restore database:
   ```bash
   gunzip backup_YYYYMMDD_HHMMSS.sql.gz
   docker exec -i sara-postgres psql -U sara_user -d sara_db < backup_YYYYMMDD_HHMMSS.sql
   ```

3. Start services:
   ```bash
   docker-compose up -d
   ```

4. Verify:
   ```bash
   docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT COUNT(*) FROM leads;"
   ```

**Expected Outcome**:
- Database restored from backup
- Data integrity verified

### Database Maintenance

**Objective**: Optimize database performance

**When to Use**: Monthly, or when performance degrades

**Steps**:

```bash
# Vacuum database
docker exec sara-postgres psql -U sara_user -d sara_db -c "VACUUM ANALYZE;"

# Reindex database
docker exec sara-postgres psql -U sara_user -d sara_db -c "REINDEX DATABASE sara_db;"
```

**Expected Outcome**:
- Database optimized
- Performance improved

## Incident Response

### Service Down - Backend

**Severity**: P1 - Critical

**Symptoms**: Backend API not responding, health check failing

**Steps**:

1. Verify backend status:
   ```bash
   docker ps | grep sara-backend
   ```

2. Check backend logs:
   ```bash
   docker logs sara-backend --tail 100
   ```

3. If container not running:
   ```bash
   docker-compose up -d backend
   ```

4. If container failing:
   ```bash
   docker-compose restart backend
   ```

5. If still failing:
   ```bash
   docker-compose logs backend
   # Analyze logs for errors
   docker-compose build backend
   docker-compose up -d backend
   ```

6. Verify:
   ```bash
   curl http://localhost:8000/health
   ```

**Expected Outcome**: Backend restored and responding

**Escalation**: If unresolved after 15 minutes, escalate to P1

### Service Down - n8n

**Severity**: P1 - Critical

**Symptoms**: n8n UI not accessible, workflows not executing

**Steps**:

1. Verify n8n status:
   ```bash
   docker ps | grep sara-n8n
   ```

2. Check n8n logs:
   ```bash
   docker logs sara-n8n --tail 100
   ```

3. If container not running:
   ```bash
   docker-compose up -d n8n
   ```

4. If container failing:
   ```bash
   docker-compose restart n8n
   ```

5. Verify:
   ```bash
   curl http://localhost:5678/healthz
   ```

6. If workflows missing:
   ```bash
   # Re-import workflows
   ./scripts/deploy-all.sh
   ```

**Expected Outcome**: n8n restored, workflows present

**Escalation**: If unresolved after 15 minutes, escalate to P1

### Database Connection Failed

**Severity**: P1 - Critical

**Symptoms**: Services can't connect to PostgreSQL

**Steps**:

1. Verify PostgreSQL status:
   ```bash
   docker ps | grep sara-postgres
   ```

2. Check PostgreSQL logs:
   ```bash
   docker logs sara-postgres --tail 100
   ```

3. Test connectivity:
   ```bash
   docker exec sara-postgres pg_isready -U sara_user -d sara_db
   ```

4. If PostgreSQL not running:
   ```bash
   docker-compose up -d postgres
   ```

5. If PostgreSQL failing:
   ```bash
   docker-compose restart postgres
   ```

6. Verify backend can connect:
   ```bash
   docker exec sara-backend ping sara-postgres
   ```

**Expected Outcome**: PostgreSQL restored, services connected

**Escalation**: If unresolved after 15 minutes, escalate to P1

### Disk Space Full

**Severity**: P2 - High

**Symptoms**: Docker errors, containers failing to start

**Steps**:

1. Check disk usage:
   ```bash
   df -h
   ```

2. Check Docker disk usage:
   ```bash
   docker system df
   ```

3. Clean up unused containers:
   ```bash
   docker container prune
   ```

4. Clean up unused images:
   ```bash
   docker image prune
   ```

5. Clean up unused volumes:
   ```bash
   docker volume prune
   ```

6. If still full:
   ```bash
   # Identify large volumes
   docker system df -v
   # Remove specific volumes if safe
   ```

**Expected Outcome**: Disk space freed, services running

**Escalation**: If unresolved after 30 minutes, escalate to P2

### Workflow Execution Failed

**Severity**: P2 - High

**Symptoms**: n8n workflow failing to execute

**Steps**:

1. Check n8n executions:
   - Open http://localhost:5678
   - Navigate to "Executions"
   - Find failed execution
   - Review error details

2. Check workflow configuration:
   - Verify nodes are correctly configured
   - Check credentials
   - Verify API endpoints

3. Test workflow manually:
   - Click "Execute Workflow"
   - Monitor execution

4. Check backend API:
   ```bash
   curl http://localhost:8000/api/v1/leads/followups-due
   ```

5. If backend issue:
   - See [Service Down - Backend](#service-down---backend)

**Expected Outcome**: Workflow executing successfully

**Escalation**: If unresolved after 1 hour, escalate to P2

## Troubleshooting

### Container Won't Start

**Symptoms**: Container exits immediately or keeps restarting

**Diagnosis**:

```bash
# Check container status
docker ps -a

# Check container logs
docker logs <container-name>

# Check resource usage
docker stats
```

**Solutions**:

1. If port conflict:
   ```bash
   lsof -i :<port>
   # Stop conflicting service or change port in .env
   ```

2. If resource issue:
   ```bash
   # Check available memory
   # Increase Docker memory allocation
   ```

3. If configuration error:
   ```bash
   # Check .env file
   # Check docker-compose.yml
   # Fix configuration
   docker-compose up -d <service>
   ```

### Slow Performance

**Symptoms**: Services responding slowly, high latency

**Diagnosis**:

```bash
# Check resource usage
docker stats

# Check database performance
docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT * FROM pg_stat_activity;"
```

**Solutions**:

1. If high CPU:
   ```bash
   # Check which process is using CPU
   # Optimize queries
   # Add indexes
   ```

2. If high memory:
   ```bash
   # Check memory usage
   # Restart heavy containers
   # Increase memory limits
   ```

3. If database slow:
   ```bash
   # Run VACUUM ANALYZE
   # Check slow queries
   # Add indexes
   ```

### Network Issues

**Symptoms**: Services can't communicate, connection refused

**Diagnosis**:

```bash
# Check Docker network
docker network ls
docker network inspect sara_network

# Test connectivity
docker exec sara-backend ping sara-postgres
docker exec sara-n8n ping sara-backend
```

**Solutions**:

1. If network issue:
   ```bash
   docker-compose down
   docker network rm sara_network
   docker-compose up -d
   ```

2. If firewall issue:
   ```bash
   # Check firewall rules
   # Allow Docker network traffic
   ```

### Data Inconsistency

**Symptoms**: Data not matching expectations, missing records

**Diagnosis**:

```bash
# Check database
docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT COUNT(*) FROM leads;"
docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT COUNT(*) FROM companies;"
```

**Solutions**:

1. If data missing:
   ```bash
   # Restore from backup
   # See Database Restore section
   ```

2. If data corrupted:
   ```bash
   # Restore from backup
   # Investigate cause
   ```

## Escalation Procedures

### When to Escalate

- P1 incidents unresolved after 15 minutes
- P2 incidents unresolved after 1 hour
- P3 incidents unresolved after 4 hours
- Any security incident
- Data loss incident

### Escalation Contacts

- **Primary**: [Primary Contact]
- **Secondary**: [Secondary Contact]
- **Emergency**: [Emergency Contact]

### Escalation Steps

1. Document current state
2. Attempt resolution for allocated time
3. If unresolved, escalate to next level
4. Provide context and attempted solutions
5. Monitor until resolved

## Post-Incident Review

After any incident:

1. Document incident timeline
2. Identify root cause
3. Document resolution steps
4. Update runbook if needed
5. Implement preventive measures
6. Share lessons learned

## Related Documentation

- [Deployment Guide](deployment.md)
- [Operating Guide](operating-guide.md)
- [Disaster Recovery](disaster-recovery.md)
- [Architecture Documentation](architecture.md)
