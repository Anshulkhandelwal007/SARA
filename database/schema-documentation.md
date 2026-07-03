# Database Schema Documentation v2

## Overview

SARA uses PostgreSQL 16 as its primary database. The schema is designed to support lead management, communication tracking, and automation workflows with a normalized CRM foundation.

## Tables

### companies

Stores organization/company information with duplicate prevention.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Company name |
| website | VARCHAR(255) | Company website URL |
| domain | VARCHAR(255) | Extracted domain for matching |
| industry | VARCHAR(100) | Industry sector |
| size | VARCHAR(50) | Company size (small, medium, large, enterprise) |
| revenue_range | VARCHAR(50) | Revenue range bracket |
| location | VARCHAR(255) | Geographic location |
| country | VARCHAR(100) | Country |
| employee_count | INTEGER | Number of employees |
| notes | TEXT | Additional notes |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

**Constraints**: UNIQUE (name, domain)

**Indexes**: name, domain, industry

---

### contacts

Individual people (can exist without being leads).

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | Foreign key to companies |
| first_name | VARCHAR(100) | First name |
| last_name | VARCHAR(100) | Last name |
| email | VARCHAR(255) | Email address (unique) |
| phone | VARCHAR(50) | Phone number |
| mobile | VARCHAR(50) | Mobile number |
| title | VARCHAR(100) | Job title |
| department | VARCHAR(100) | Department |
| linkedin_url | TEXT | LinkedIn profile URL |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

**Constraints**: UNIQUE (email)

**Indexes**: email, company_id, phone, mobile

---

### leads

Sales opportunities linked to contacts.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| contact_id | UUID | Foreign key to contacts (required) |
| company_id | UUID | Foreign key to companies |
| source | VARCHAR(50) | Lead source (google_sheets, web_form, api, referral, manual) |
| status | VARCHAR(50) | Lead status (new, contacted, engaged, qualified, opportunity, customer, churned, lost) |
| score | INTEGER | Lead score (0-100) |
| tier | VARCHAR(20) | Lead tier (hot, warm, cold) |
| assigned_to | VARCHAR(100) | Assigned salesperson |
| estimated_value | DECIMAL(15,2) | Estimated deal value |
| probability | INTEGER | Win probability (0-100) |
| expected_close_date | DATE | Expected close date |
| custom_fields | JSONB | Flexible custom data |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |
| last_contacted_at | TIMESTAMP | Last communication time |
| next_followup_at | TIMESTAMP | Scheduled follow-up time |
| interaction_count | INTEGER | Total interactions |
| notified_hot | BOOLEAN | Whether hot lead notification sent |
| notified_at | TIMESTAMP | When notification was sent |

**Indexes**: contact_id, company_id, status, score, tier, source, next_followup_at, created_at, assigned_to

**Status Flow**: new → contacted → engaged → qualified → opportunity → customer → churned/lost

---

### lead_interactions

Complete audit trail of all lead touchpoints.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | Foreign key to leads |
| interaction_type | VARCHAR(50) | Type (email, whatsapp, call, meeting, note, sms) |
| channel | VARCHAR(50) | Channel used |
| direction | VARCHAR(20) | Direction (inbound, outbound) |
| status | VARCHAR(50) | Status (sent, delivered, read, failed, scheduled) |
| subject | VARCHAR(255) | Subject line |
| content | TEXT | Interaction content |
| metadata | JSONB | Additional data |
| created_at | TIMESTAMP | Record creation time |

**Indexes**: lead_id, interaction_type, created_at

---

### email_history

Detailed email tracking with delivery status.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | Foreign key to leads |
| interaction_id | UUID | Foreign key to lead_interactions |
| from_email | VARCHAR(255) | Sender email |
| to_email | VARCHAR(255) | Recipient email |
| cc_email | TEXT | CC recipients |
| bcc_email | TEXT | BCC recipients |
| subject | VARCHAR(500) | Email subject |
| body | TEXT | Plain text body |
| html_body | TEXT | HTML body |
| message_id | VARCHAR(255) | Email message ID |
| thread_id | VARCHAR(255) | Email thread ID |
| provider | VARCHAR(50) | Email provider (brevo, sendgrid, gmail) |
| external_id | VARCHAR(255) | Provider's message ID |
| status | VARCHAR(50) | Status (sent, delivered, opened, clicked, bounced, failed) |
| opened_at | TIMESTAMP | When email was opened |
| clicked_at | TIMESTAMP | When link was clicked |
| bounced_at | TIMESTAMP | When email bounced |
| bounce_reason | TEXT | Bounce reason |
| created_at | TIMESTAMP | Record creation time |

**Indexes**: lead_id, external_id, created_at

---

### whatsapp_history

WhatsApp message tracking.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | Foreign key to leads |
| interaction_id | UUID | Foreign key to lead_interactions |
| from_number | VARCHAR(50) | Sender number |
| to_number | VARCHAR(50) | Recipient number |
| message_type | VARCHAR(50) | Type (text, image, document, audio, video) |
| content | TEXT | Message content |
| media_url | TEXT | Media URL |
| message_id | VARCHAR(255) | WhatsApp message ID |
| status | VARCHAR(50) | Status (sent, delivered, read, failed) |
| delivered_at | TIMESTAMP | When delivered |
| read_at | TIMESTAMP | When read |
| created_at | TIMESTAMP | Record creation time |

**Indexes**: lead_id, message_id, created_at

---

### call_logs

Voice call records and transcripts.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | Foreign key to leads |
| interaction_id | UUID | Foreign key to lead_interactions |
| call_provider | VARCHAR(50) | Call provider (twilio, vonage) |
| call_id | VARCHAR(255) | Provider's call ID |
| direction | VARCHAR(20) | Direction (inbound, outbound) |
| status | VARCHAR(50) | Status (completed, failed, busy, no_answer, cancelled) |
| duration_seconds | INTEGER | Call duration |
| recording_url | TEXT | Recording URL |
| transcript | TEXT | Call transcript |
| sentiment | VARCHAR(20) | Sentiment (positive, neutral, negative) |
| summary | TEXT | AI-generated summary |
| metadata | JSONB | Additional data |
| created_at | TIMESTAMP | Record creation time |

**Indexes**: lead_id, call_id, created_at

---

### followups

Scheduled and completed follow-ups.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | Foreign key to leads |
| channel | VARCHAR(50) | Channel (email, whatsapp, voice_call, sms) |
| status | VARCHAR(50) | Status (scheduled, sent, failed, cancelled, completed) |
| priority | VARCHAR(20) | Priority (low, normal, high, urgent) |
| scheduled_at | TIMESTAMP | When scheduled |
| sent_at | TIMESTAMP | When sent |
| completed_at | TIMESTAMP | When completed |
| message_content | TEXT | Message content |
| template_id | VARCHAR(100) | Template used |
| metadata | JSONB | Additional data |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

**Indexes**: lead_id, scheduled_at, status, priority

---

### ai_summaries

AI-generated summaries of interactions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | Foreign key to leads |
| interaction_id | UUID | Foreign key to lead_interactions |
| summary_type | VARCHAR(50) | Type (call_summary, email_thread, lead_overview, next_steps) |
| summary_text | TEXT | Summary content |
| key_points | JSONB | Key points extracted |
| sentiment | VARCHAR(20) | Overall sentiment |
| confidence_score | DECIMAL(3,2) | AI confidence score |
| model_used | VARCHAR(100) | AI model used |
| metadata | JSONB | Additional data |
| created_at | TIMESTAMP | Record creation time |

**Indexes**: lead_id, summary_type, created_at

---

### activity_log

System-wide activity tracking.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| entity_type | VARCHAR(50) | Entity type (lead, contact, company, workflow) |
| entity_id | UUID | Entity ID |
| action | VARCHAR(50) | Action (created, updated, deleted, imported, exported) |
| actor | VARCHAR(100) | Actor (user or system) |
| details | JSONB | Action details |
| created_at | TIMESTAMP | Record creation time |

**Indexes**: entity_type, entity_id, created_at

---

## Relationships

```
companies (1) ──────< (N) contacts
companies (1) ──────< (N) leads
contacts (1) ──────< (N) leads
leads (1) ──────< (N) lead_interactions
leads (1) ──────< (N) email_history
leads (1) ──────< (N) whatsapp_history
leads (1) ──────< (N) call_logs
leads (1) ──────< (N) followups
leads (1) ──────< (N) ai_summaries
lead_interactions (1) ──────< (N) email_history
lead_interactions (1) ──────< (N) whatsapp_history
lead_interactions (1) ──────< (N) call_logs
```

## Triggers

### update_updated_at_column

Automatically updates the `updated_at` timestamp on row modification for:
- companies
- contacts
- leads
- followups

## Sample Data

The schema includes sample data for testing:
- 3 companies (Acme Corporation, Globex Inc, Soylent Corp)
- 3 contacts linked to companies
- 3 leads linked to contacts

## Common Queries

### Get all leads with contact and company info
```sql
SELECT 
  l.id as lead_id,
  l.status,
  l.score,
  c.first_name,
  c.last_name,
  c.email,
  c.phone,
  co.name as company_name,
  co.website as company_website
FROM leads l
JOIN contacts c ON l.contact_id = c.id
LEFT JOIN companies co ON l.company_id = co.id
ORDER BY l.created_at DESC;
```

### Get hot leads needing follow-up
```sql
SELECT 
  l.*, 
  c.first_name, 
  c.last_name, 
  c.email, 
  co.name as company_name
FROM leads l
JOIN contacts c ON l.contact_id = c.id
LEFT JOIN companies co ON l.company_id = co.id
WHERE l.tier = 'hot'
  AND (l.next_followup_at IS NULL OR l.next_followup_at <= CURRENT_TIMESTAMP)
ORDER BY l.score DESC;
```

### Get lead interaction history
```sql
SELECT 
  li.*,
  CASE 
    WHEN li.interaction_type = 'email' THEN (SELECT subject FROM email_history WHERE interaction_id = li.id LIMIT 1)
    WHEN li.interaction_type = 'call' THEN (SELECT status FROM call_logs WHERE interaction_id = li.id LIMIT 1)
    ELSE NULL
  END as detail
FROM lead_interactions li
WHERE li.lead_id = 'lead-uuid-here'
ORDER BY li.created_at DESC;
```

### Get upcoming follow-ups
```sql
SELECT 
  f.*, 
  l.first_name, 
  l.last_name, 
  l.email,
  co.name as company_name
FROM followups f
JOIN leads l ON f.lead_id = l.id
JOIN contacts c ON l.contact_id = c.id
LEFT JOIN companies co ON l.company_id = co.id
WHERE f.status = 'scheduled'
  AND f.scheduled_at > CURRENT_TIMESTAMP
ORDER BY f.scheduled_at ASC;
```

### Check for duplicate companies
```sql
SELECT name, domain, COUNT(*) as count
FROM companies
GROUP BY name, domain
HAVING COUNT(*) > 1;
```

### Check for duplicate contacts
```sql
SELECT email, COUNT(*) as count
FROM contacts
GROUP BY email
HAVING COUNT(*) > 1;
```

## Migration Strategy

When modifying the schema:
1. Create a new migration file in `database/init/` with a higher number (e.g., `02-add-field.sql`)
2. Use `IF NOT EXISTS` and `IF EXISTS` for safe migrations
3. Test migrations on a copy of production data
4. Document breaking changes in this file
5. Always include rollback instructions

## Backup Strategy

- Manual backups via pgAdmin
- Automated backups can be added using `scripts/backup.sh`
- Store backups in `backups/` directory
- Keep at least 7 days of backups
- Test restore procedures regularly
