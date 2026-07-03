# Lead Automation Workflow Specification

## Overview

This workflow automates the complete lead lifecycle from intake to follow-up execution and notification.

## Workflow Stages

### 1. Lead Intake

**Trigger**: Webhook or scheduled polling

**Process**:
1. Receive lead data from source (Google Sheets, web form, API)
2. Validate required fields (name, email, phone, company)
3. Normalize data format
4. Check for duplicates in PostgreSQL
5. If duplicate exists, update existing record
6. If new, create new lead record in PostgreSQL
7. Trigger lead scoring workflow

**Input Schema**:
```json
{
  "name": "string (required)",
  "email": "string (required, email format)",
  "phone": "string (required)",
  "company": "string (required)",
  "title": "string (optional)",
  "source": "string (required)",
  "custom_fields": "object (optional)"
}
```

**Output**: Lead ID in PostgreSQL

---

### 2. Lead Scoring

**Trigger**: After lead intake

**Process**:
1. Retrieve lead data from PostgreSQL
2. Apply scoring rules:
   - Company size (employees, revenue)
   - Job title seniority
   - Industry fit
   - Engagement level
   - Source quality
3. Use AI model for context-aware scoring (optional enhancement)
4. Calculate total score (0-100)
5. Determine lead tier:
   - Hot: 80-100
   - Warm: 50-79
   - Cold: 0-49
6. Update lead record with score and tier
7. Trigger follow-up decision workflow

**Scoring Criteria**:
- Company size: +20 (large), +10 (medium), +5 (small)
- Job title: +20 (C-level), +15 (VP/Director), +10 (Manager), +5 (Individual contributor)
- Industry: +15 (high-fit), +10 (medium-fit), +5 (low-fit)
- Source: +10 (inbound), +5 (referral), +0 (outbound)
- Engagement: +10 (high), +5 (medium), +0 (low)

---

### 3. Follow-Up Decision

**Trigger**: After lead scoring

**Process**:
1. Retrieve lead score and tier
2. Check lead status (new, contacted, follow-up scheduled)
3. Check recent interaction history
4. Determine appropriate action:
   - **Hot leads**: Immediate notification + priority follow-up
   - **Warm leads**: Schedule follow-up within 24-48 hours
   - **Cold leads**: Schedule follow-up within 5-7 days
5. Select optimal channel:
   - **Email**: Default for initial outreach
   - **WhatsApp**: For quick responses or warm leads
   - **Voice call**: For hot leads or high-value prospects
6. Schedule follow-up action
7. Trigger execution workflow

**Decision Logic**:
```
IF tier == "hot" AND no_contact_in_24h:
    action = "immediate_notification"
    channel = "voice_call"
ELSE IF tier == "warm" AND no_contact_in_48h:
    action = "scheduled_followup"
    channel = "email"
ELSE IF tier == "cold" AND no_contact_in_7d:
    action = "scheduled_followup"
    channel = "email"
ELSE:
    action = "no_action"
```

---

### 4. Follow-Up Execution

**Trigger**: Scheduled or immediate

**Process**:
1. Retrieve lead data and follow-up details
2. Generate personalized message using AI (optional)
3. Execute communication via selected channel:
   - **Email**: Send via Brevo API
   - **WhatsApp**: Send via WhatsApp Business API
   - **Voice call**: Initiate via voice AI provider
4. Log interaction to PostgreSQL
5. Update lead status
6. Schedule next follow-up if needed
7. Trigger notification if lead responds

**Email Template**:
```
Subject: Following up on {company_name}

Hi {name},

I noticed you're {title} at {company_name}. I'd love to learn more about your {pain_point} challenges and see if we can help.

Are you available for a quick call this week?

Best regards,
{your_name}
```

---

### 5. Status Update

**Trigger**: After each interaction

**Process**:
1. Update lead status in PostgreSQL:
   - new → contacted
   - contacted → engaged
   - engaged → qualified
   - qualified → opportunity
   - opportunity → customer
   - customer → churned
2. Update last_contacted timestamp
3. Update interaction count
4. Calculate engagement score
5. Update next_followup_date

**Status Transitions**:
- new → contacted: First successful communication
- contacted → engaged: Lead responds positively
- engaged → qualified: Lead meets qualification criteria
- qualified → opportunity: Demo or proposal requested
- opportunity → customer: Deal closed
- customer → churned: Customer leaves

---

### 6. Hot Lead Notification

**Trigger**: Lead score ≥ 80 OR positive engagement

**Process**:
1. Check if lead is already notified
2. If not, send notification via:
   - Email to sales team
   - Slack/Teams message
   - SMS for urgent leads
3. Include lead details and recommended action
4. Mark lead as notified in PostgreSQL
5. Schedule follow-up reminder for sales team

**Notification Template**:
```
🔥 HOT LEAD ALERT

Name: {name}
Company: {company_name}
Title: {title}
Score: {score}/100
Source: {source}

Recommended Action: {action}

View in CRM: {crm_link}
```

---

## n8n Implementation Notes

### Nodes Required

**Lead Intake**:
- Webhook node (trigger)
- Set node (data normalization)
- PostgreSQL node (check duplicates)
- IF node (new vs update)
- PostgreSQL node (insert/update)

**Lead Scoring**:
- PostgreSQL node (retrieve lead)
- Function node (scoring logic)
- PostgreSQL node (update score)

**Follow-Up Decision**:
- PostgreSQL node (retrieve lead + history)
- Function node (decision logic)
- Wait node (for scheduled follow-ups)

**Follow-Up Execution**:
- PostgreSQL node (retrieve details)
- HTTP Request node (Brevo/WhatsApp/Voice API)
- PostgreSQL node (log interaction)

**Status Update**:
- PostgreSQL node (update status)
- Function node (calculate engagement)

**Hot Lead Notification**:
- PostgreSQL node (check notification status)
- IF node (already notified?)
- HTTP Request node (email/Slack/SMS)
- PostgreSQL node (mark notified)

### PostgreSQL Connection

Use the following n8n PostgreSQL credentials:
- Host: `postgres`
- Port: `5432`
- Database: `sara_db`
- User: `sara_user`
- Password: From `.env` file

### Error Handling

- Add error nodes for each critical step
- Log errors to PostgreSQL error table
- Retry failed operations with exponential backoff
- Send alerts for critical failures

---

## Testing Checklist

- [ ] Lead intake creates new record in PostgreSQL
- [ ] Duplicate detection works correctly
- [ ] Lead scoring produces valid scores (0-100)
- [ ] Follow-up decision logic executes correctly
- [ ] Email sends successfully via Brevo
- [ ] WhatsApp message sends successfully
- [ ] Voice call initiates successfully
- [ ] Status updates persist to PostgreSQL
- [ ] Hot lead notifications trigger correctly
- [ ] Error handling catches and logs failures

---

## Next Steps

1. Implement lead intake workflow in n8n
2. Create PostgreSQL tables (see database/schema.sql)
3. Configure Brevo API credentials
4. Set up WhatsApp Business API
5. Integrate voice AI provider
6. Test end-to-end flow
7. Add monitoring and alerting
