# Project SARA - Disaster Recovery Guide

This guide covers disaster recovery procedures for Project SARA, including recovery from various failure scenarios.

## Backup Strategy

### What to Backup

1. **PostgreSQL Database**
   - All CRM data (companies, contacts, leads, interactions)
   - n8n workflow definitions
   - n8n execution history
   - Credentials (encrypted)

2. **Configuration Files**
   - `.env` file (environment variables)
   - `docker-compose.yml`
   - Workflow JSON files

3. **Repository**
   - Git repository (source code, documentation)

### Automated Backups

#### PostgreSQL Backup

```bash
# Create backup
docker exec sara-postgres pg_dump -U sara_user sara_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Docker Volume Backup

```bash
# Backup PostgreSQL volume
docker run --rm -v sara_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_volume_backup_$(date +%Y%m%d).tar.gz /data

# Backup n8n volume
docker run --rm -v sara_n8n_data:/data -v $(pwd):/backup alpine tar czf /backup/n8n_volume_backup_$(date +%Y%m%d).tar.gz /data
```

### Manual Backup Procedure

1. **Stop all services**:
   ```bash
   docker-compose down
   ```

2. **Backup volumes**:
   ```bash
   docker run --rm -v sara_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_$(date +%Y%m%d).tar.gz /data
   docker run --rm -v sara_n8n_data:/data -v $(pwd):/backup alpine tar czf /backup/n8n_$(date +%Y%m%d).tar.gz /data
   ```

3. **Backup configuration**:
   ```bash
   cp .env .env.backup
   cp docker-compose.yml docker-compose.yml.backup
   ```

4. **Restart services**:
   ```bash
   docker-compose up -d
   ```

## Recovery Scenarios

### Scenario 1: Mac Restart / System Reboot

**Symptoms**: Docker containers not running after system restart

**Recovery Steps**:

1. **Start Docker Desktop**:
   - Open Docker Desktop application
   - Wait for Docker to start
   - Verify Docker is running: `docker ps`

2. **Start SARA services**:
   ```bash
   cd /Users/anshulkhandelwal/SARA
   docker-compose up -d
   ```

3. **Verify services**:
   ```bash
   ./scripts/verify-deployment.sh
   ```

4. **If workflows are missing**:
   ```bash
   # Re-import workflows
   ./scripts/deploy-all.sh
   ```

**Prevention**:
- Configure Docker Desktop to start on login
- Use `restart: unless-stopped` in docker-compose.yml (already configured)

### Scenario 2: Docker Volumes Disappear

**Symptoms**: Data loss, empty database, missing workflows

**Recovery Steps**:

1. **Stop services**:
   ```bash
   docker-compose down
   ```

2. **Restore PostgreSQL volume**:
   ```bash
   docker run --rm -v sara_postgres_data:/data -v $(pwd):/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/postgres_YYYYMMDD.tar.gz -C /"
   ```

3. **Restore n8n volume**:
   ```bash
   docker run --rm -v sara_n8n_data:/data -v $(pwd):/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/n8n_YYYYMMDD.tar.gz -C /"
   ```

4. **Start services**:
   ```bash
   docker-compose up -d
   ```

5. **Verify recovery**:
   ```bash
   ./scripts/verify-deployment.sh
   ```

**Prevention**:
- Regular automated backups
- Monitor disk space
- Use volume snapshots if using Docker Desktop

### Scenario 3: n8n Loses Workflows

**Symptoms**: n8n UI shows no workflows or incorrect workflows

**Recovery Steps**:

1. **Check database**:
   ```bash
   docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT id, name FROM workflow_entity;"
   ```

2. **If workflows are missing from database**:
   ```bash
   # Re-import from repository
   for workflow in workflows/exports/*.json; do
       docker cp "$workflow" sara-n8n:/tmp/
       docker exec sara-n8n n8n import:workflow --input=/tmp/$(basename "$workflow")
   done
   ```

3. **Restart n8n**:
   ```bash
   docker-compose restart n8n
   ```

4. **Verify in UI**:
   - Open http://localhost:5678
   - Check workflows list

**Prevention**:
- Keep workflow JSON files in repository
- Regular database backups
- Verify workflow count after changes

### Scenario 4: Database Corruption

**Symptoms**: PostgreSQL errors, data inconsistencies, connection failures

**Recovery Steps**:

1. **Stop services**:
   ```bash
   docker-compose down
   ```

2. **Backup corrupted data**:
   ```bash
   docker run --rm -v sara_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_corrupted_$(date +%Y%m%d).tar.gz /data
   ```

3. **Restore from backup**:
   ```bash
   docker run --rm -v sara_postgres_data:/data -v $(pwd):/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/postgres_YYYYMMDD.tar.gz -C /"
   ```

4. **Start services**:
   ```bash
   docker-compose up -d
   ```

5. **Verify data integrity**:
   ```bash
   docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT COUNT(*) FROM leads;"
   docker exec sara-postgres psql -U sara_user -d sara_db -c "SELECT COUNT(*) FROM companies;"
   ```

**Prevention**:
- Regular database backups
- Monitor disk space
- Use PostgreSQL WAL archiving for production

### Scenario 5: Git Clone on New Machine

**Symptoms**: Fresh machine, need to set up SARA from scratch

**Recovery Steps**:

1. **Clone repository**:
   ```bash
   git clone https://github.com/Anshulkhandelwal007/SARA.git
   cd SARA
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Deploy**:
   ```bash
   ./scripts/deploy-all.sh
   ```

4. **Restore data** (if backup available):
   ```bash
   # Stop services
   docker-compose down
   
   # Restore volumes
   docker run --rm -v sara_postgres_data:/data -v $(path_to_backup):/backup alpine tar xzf /backup/postgres_YYYYMMDD.tar.gz -C /
   docker run --rm -v sara_n8n_data:/data -v $(path_to_backup):/backup alpine tar xzf /backup/n8n_YYYYMMDD.tar.gz -C /
   
   # Start services
   docker-compose up -d
   ```

5. **Verify**:
   ```bash
   ./scripts/verify-deployment.sh
   ```

**Prevention**:
- Keep backups in cloud storage
- Document environment configuration
- Use version control for configuration

### Scenario 6: Container Image Corruption

**Symptoms**: Container won't start, image errors

**Recovery Steps**:

1. **Remove corrupted containers**:
   ```bash
   docker-compose down
   ```

2. **Remove corrupted images**:
   ```bash
   docker rmi sara-backend
   docker rmi n8nio/n8n:latest
   docker rmi postgres:16-alpine
   docker rmi dpage/pgadmin4:latest
   ```

3. **Rebuild backend**:
   ```bash
   docker-compose build backend
   ```

4. **Pull fresh images**:
   ```bash
   docker-compose pull
   ```

5. **Start services**:
   ```bash
   docker-compose up -d
   ```

**Prevention**:
- Regular image updates
- Use specific image tags in production
- Monitor image health

### Scenario 7: Network Issues

**Symptoms**: Services can't communicate, connection refused

**Recovery Steps**:

1. **Check Docker network**:
   ```bash
   docker network ls
   docker network inspect sara_network
   ```

2. **Recreate network**:
   ```bash
   docker-compose down
   docker network rm sara_network
   docker-compose up -d
   ```

3. **Verify connectivity**:
   ```bash
   docker exec sara-backend ping sara-postgres
   docker exec sara-n8n ping sara-backend
   ```

**Prevention**:
- Use Docker networks (already configured)
- Monitor network connectivity
- Check firewall settings

## Emergency Procedures

### Complete System Failure

If the entire system fails:

1. **Assess the situation**:
   - Identify what's broken
   - Determine data loss extent
   - Check backup availability

2. **Priority recovery order**:
   1. PostgreSQL data (most critical)
   2. n8n workflows
   3. Configuration files
   4. Docker volumes

3. **Recovery steps**:
   - Restore from most recent backup
   - Verify data integrity
   - Start services
   - Run verification script

### Partial Failure

If only some components fail:

1. **Identify failed component**
2. **Check logs for errors**
3. **Attempt restart**
4. **If restart fails, restore from backup**
5. **Verify component is working**

## Testing Recovery Procedures

Regularly test recovery procedures:

1. **Monthly**: Test backup restoration
2. **Quarterly**: Full disaster recovery drill
3. **After major changes**: Test new backup/restore procedures

### Test Procedure

1. **Create test backup**:
   ```bash
   ./scripts/backup-all.sh
   ```

2. **Simulate failure**:
   ```bash
   docker-compose down
   docker volume rm sara_postgres_data sara_n8n_data
   ```

3. **Restore from backup**:
   ```bash
   ./scripts/restore-all.sh backup_YYYYMMDD
   ```

4. **Verify**:
   ```bash
   ./scripts/verify-deployment.sh
   ```

## Monitoring and Alerts

Set up monitoring for:

- Disk space usage
- Container health
- Database connectivity
- Service response times
- Error rates

Alert thresholds:

- Disk space > 80%: Warning
- Disk space > 90%: Critical
- Container down > 5 minutes: Critical
- Database connection failed: Critical

## Contact Information

For critical issues:

- **Primary**: [Your contact]
- **Secondary**: [Backup contact]
- **Emergency**: [Emergency contact]

## Documentation Updates

Keep this document updated:

- After any recovery procedure
- When adding new services
- When changing backup strategy
- After testing recovery procedures

## Related Documentation

- [Deployment Guide](deployment.md)
- [Operating Guide](operating-guide.md)
- [Runbook](runbook.md)
- [Architecture Documentation](architecture.md)
