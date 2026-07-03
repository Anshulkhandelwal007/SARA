# SARA Blueprint

**Design Source of Truth for Project SARA / SARA OS**

---

## 1. Vision

### What SARA Is

SARA (Sales Automation and Relationship Assistant) is an AI-powered CRM and sales automation system designed for small to medium businesses. It combines traditional CRM functionality with AI-driven intelligence to help sales teams work smarter, not harder.

### The Business Problem

Small businesses struggle with:
- **Lead leakage**: Leads fall through cracks due to manual follow-up failures
- **Data fragmentation**: Customer data scattered across spreadsheets, emails, and notes
- **Inconsistent processes**: No standardized sales workflow or qualification criteria
- **Lost opportunities**: Poor tracking of quotations, callbacks, and follow-ups
- **Service gaps**: After-sales support is reactive rather than proactive
- **Manual overhead**: Salespeople spend more time on admin than selling

### Why SARA Exists

SARA exists to:
1. **Centralize customer data** in a single source of truth
2. **Automate repetitive tasks** like follow-ups, quotations, and reminders
3. **Provide AI intelligence** for lead scoring, next actions, and interaction summaries
4. **Standardize sales processes** with clear workflows and state transitions
5. **Enable proactive service** through automated AMC tracking and service requests
6. **Reduce manual overhead** so salespeople can focus on selling

---

## 2. Business Domain

### Core Entities

#### Company
The organization being sold to. Represents a business entity that may have multiple contacts and opportunities.

**Key Attributes:**
- Name (required)
- Website (optional)
- Domain (extracted from website)
- Industry (optional)
- Size (optional: small, medium, large)
- Location (optional)
- Country (optional)

**Relationships:**
- Has many Contacts
- Has many Opportunities
- Has many Orders
- Has many AMCs

#### Contact
An individual person at a company. Represents a decision-maker or influencer.

**Key Attributes:**
- First Name (required)
- Last Name (required)
- Email (required, unique)
- Phone (optional)
- Mobile (optional)
- Title (optional)
- Department (optional)

**Relationships:**
- Belongs to one Company
- Has many Leads
- Has many Interactions

#### Lead
A potential sales opportunity. The initial entry point for a prospect.

**Key Attributes:**
- Source (required: google_sheets, manual, referral, website, etc.)
- Status (required: new, contacted, qualified, converted, lost)
- Score (0-100, calculated by AI)
- Estimated Value (optional)
- Custom Fields (flexible JSON for additional data)

**Relationships:**
- Belongs to one Contact
- Belongs to one Company
- Has many Interactions
- Converts to Opportunity

#### Opportunity
A qualified lead with a defined sales cycle. Represents a potential deal.

**Key Attributes:**
- Stage (required: prospecting, qualification, proposal, negotiation, closed-won, closed-lost)
- Probability (0-100%)
- Value (required)
- Expected Close Date (optional)
- Actual Close Date (optional)

**Relationships:**
- Derived from Lead
- Belongs to one Company
- Has many Quotations
- Has one Order (when closed)

#### Quotation
A formal price quote sent to a customer.

**Key Attributes:**
- Quote Number (required, auto-generated)
- Valid Until (required)
- Total Value (required)
- Status (required: draft, sent, accepted, rejected, expired)
- Terms (optional)

**Relationships:**
- Belongs to one Opportunity
- Has many Line Items
- Leads to Order

#### Order
A confirmed purchase from a customer.

**Key Attributes:**
- Order Number (required, auto-generated)
- Order Date (required)
- Total Value (required)
- Status (required: pending, confirmed, shipped, delivered, cancelled)
- Payment Terms (optional)

**Relationships:**
- Derived from Quotation
- Belongs to one Company
- Has one Invoice
- Has many Service Requests

#### Invoice
A bill sent to a customer for an order.

**Key Attributes:**
- Invoice Number (required, auto-generated)
- Invoice Date (required)
- Due Date (required)
- Total Amount (required)
- Status (required: draft, sent, paid, overdue, cancelled)

**Relationships:**
- Belongs to one Order
- Has many Payments

#### Payment
Money received from a customer for an invoice.

**Key Attributes:**
- Payment Date (required)
- Amount (required)
- Method (required: bank_transfer, check, card, cash, upi, etc.)
- Reference (optional)
- Status (required: pending, completed, failed)

**Relationships:**
- Belongs to one Invoice

#### Service Request
A customer support or maintenance request after sale.

**Key Attributes:**
- Request Number (required, auto-generated)
- Type (required: installation, maintenance, repair, upgrade, training)
- Priority (required: low, medium, high, urgent)
- Status (required: open, in-progress, resolved, closed)
- Description (required)

**Relationships:**
- Belongs to one Order
- Belongs to one Company
- Has many Interactions

#### AMC (Annual Maintenance Contract)
A recurring service agreement with a customer.

**Key Attributes:**
- Contract Number (required, auto-generated)
- Start Date (required)
- End Date (required)
- Value (required)
- Status (required: active, expired, cancelled)
- Renewal Date (optional)

**Relationships:**
- Belongs to one Company
- Has many Service Requests

#### Interaction History
Any communication or touchpoint with a customer.

**Key Attributes:**
- Type (required: email, phone, whatsapp, meeting, note)
- Direction (required: inbound, outbound)
- Subject (optional)
- Content (required)
- Date/Time (required)

**Relationships:**
- Belongs to one Contact
- Belongs to one Lead/Opportunity/Service Request
- Has AI Summary (optional)

---

## 3. Customer Lifecycle

### Lifecycle Flow

```
Lead → Contact → Opportunity → Quotation → Order → Invoice → Payment → Service → AMC
```

### State Transitions

#### Lead States
- **new** → Initial state, no contact made yet
- **contacted** → First outreach attempted/completed
- **qualified** → Meets qualification criteria, ready for opportunity
- **converted** → Successfully converted to opportunity
- **lost** → Not interested or went with competitor

**Transitions:**
- new → contacted (when first interaction logged)
- contacted → qualified (when qualification criteria met)
- qualified → converted (when opportunity created)
- any state → lost (when prospect declines)

#### Opportunity States
- **prospecting** → Initial opportunity stage
- **qualification** → Validating budget, authority, need, timeline
- **proposal** → Quotation sent, awaiting response
- **negotiation** → Discussing terms and conditions
- **closed-won** → Order confirmed
- **closed-lost** → Deal lost

**Transitions:**
- prospecting → qualification (when qualification complete)
- qualification → proposal (when quotation sent)
- proposal → negotiation (when counter-offer received)
- negotiation → closed-won (when order confirmed)
- negotiation → closed-lost (when deal rejected)
- any stage → closed-lost (at any point)

#### Quotation States
- **draft** → Quote being prepared
- **sent** → Quote sent to customer
- **accepted** → Customer accepted quote
- **rejected** → Customer rejected quote
- **expired** → Quote past valid until date

**Transitions:**
- draft → sent (when email sent)
- sent → accepted (when customer confirms)
- sent → rejected (when customer declines)
- sent → expired (when date passes)

#### Order States
- **pending** → Order received but not confirmed
- **confirmed** → Order confirmed and processing
- **shipped** → Goods/services dispatched
- **delivered** → Goods/services delivered to customer
- **cancelled** → Order cancelled

**Transitions:**
- pending → confirmed (when payment/confirmation received)
- confirmed → shipped (when dispatch initiated)
- shipped → delivered (when delivery confirmed)
- any state → cancelled (if customer cancels)

#### Invoice States
- **draft** → Invoice being prepared
- **sent** → Invoice sent to customer
- **paid** → Payment received
- **overdue** → Past due date, not paid
- **cancelled** → Invoice cancelled

**Transitions:**
- draft → sent (when email sent)
- sent → paid (when payment recorded)
- sent → overdue (when due date passes)
- any state → cancelled (if order cancelled)

#### Service Request States
- **open** → Request created
- **in-progress** → Work in progress
- **resolved** → Issue resolved
- **closed** → Request closed

**Transitions:**
- open → in-progress (when work started)
- in-progress → resolved (when issue fixed)
- resolved → closed (when customer confirms)

#### AMC States
- **active** → Contract currently active
- **expired** → Contract period ended
- **cancelled** → Contract cancelled early

**Transitions:**
- active → expired (when end date passes)
- active → cancelled (if customer cancels)
- expired → active (if renewed)

---

## 4. Operating Model

### Sales Follow-Up Process

#### Automated Follow-Up Rules
1. **New Lead**: Auto-assign to salesperson, send welcome email within 24h
2. **No Response**: Follow-up after 3 days, then 7 days, then 14 days
3. **Interested**: Schedule call/demo within 48h
4. **Quotation Sent**: Follow-up after 2 days, then 5 days
5. **Negotiation**: Daily check-ins until closed
6. **Closed Won**: Onboarding email within 24h
7. **Closed Lost**: Reason capture, 30-day re-engagement check

#### Follow-Up Channels
- **Email**: Primary for quotations, proposals, formal communication
- **Phone**: For urgent follow-ups, negotiations, relationship building
- **WhatsApp**: For quick updates, confirmations, informal communication
- **In-Person**: For demos, site visits, relationship meetings

### Lead Qualification

#### BANT Framework
- **Budget**: Does the prospect have budget?
- **Authority**: Is the contact a decision-maker?
- **Need**: Do they have a clear pain point we can solve?
- **Timeline**: When are they looking to implement?

#### Qualification Scoring
- **High Priority**: Budget confirmed, decision-maker, urgent need, <3 months
- **Medium Priority**: Budget likely, influencer, clear need, 3-6 months
- **Low Priority**: Budget unclear, not decision-maker, exploratory, >6 months

#### Disqualification Criteria
- Budget too small/large for our offering
- No decision-maker access
- No clear need or timeline
- Competitor already selected
- Geographic or industry mismatch

### Quotation and Callback Process

#### Quotation Generation
1. **Requirement Gathering**: Capture customer needs and specifications
2. **Pricing Calculation**: Apply pricing rules, discounts, taxes
3. **Quote Creation**: Generate formal quotation document
4. **Review**: Manager approval for high-value quotes
5. **Delivery**: Send quote via email with tracking
6. **Follow-Up**: Schedule callback 2 days after sending

#### Callback Management
- **Scheduled Callbacks**: Calendar integration, reminders
- **Missed Callbacks**: Auto-reschedule, notification to manager
- **Callback Outcomes**: Log result (interested, not interested, callback later)
- **Escalation**: Manager intervention if no response after 3 attempts

### After-Sales Service

#### Service Request Handling
1. **Request Creation**: Customer submits via email, phone, or portal
2. **Triage**: Assign priority based on type and urgency
3. **Assignment**: Auto-assign to available technician
4. **SLA Tracking**: Monitor response and resolution times
5. **Resolution**: Fix issue, document solution
6. **Closure**: Customer confirmation, satisfaction survey

#### AMC Management
- **Renewal Reminders**: 30 days, 15 days, 7 days before expiry
- **Service Schedule**: Preventive maintenance calendar
- **Performance Tracking**: SLA compliance, uptime metrics
- **Renewal Process**: Quote generation, negotiation, renewal

---

## 5. Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
│  (Future: Web Dashboard, Mobile App, Email, WhatsApp)      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Orchestration Layer                        │
│                    (n8n Workflows)                           │
│  - Data import/export                                        │
│  - Process automation                                         │
│  - Communication orchestration                               │
│  - Scheduled tasks                                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic Layer                        │
│                   (FastAPI Backend)                          │
│  - API endpoints                                             │
│  - Business rules                                            │
│  - Data validation                                           │
│  - Authentication/Authorization                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    AI Layer (Future)                         │
│  - Lead scoring                                              │
│  - Next action recommendations                               │
│  - Interaction summarization                                 │
│  - Pattern detection                                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Communication Layer (Future)                     │
│  - Email integration                                         │
│  - WhatsApp integration                                      │
│  - Voice/Phone integration                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Data Layer (Source of Truth)                 │
│                   (PostgreSQL)                                │
│  - Normalized schema                                         │
│  - Audit logging                                             │
│  - Source tracking                                           │
│  - Idempotency constraints                                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### PostgreSQL (Source of Truth)
- Stores all customer, sales, and service data
- Enforces data integrity through constraints
- Provides audit trail through logging
- Supports complex queries and reporting

#### n8n (Orchestration Layer)
- Automates data import from Google Sheets
- Orchestrates communication workflows (email, WhatsApp)
- Schedules follow-ups and reminders
- Manages process flows between systems
- **Calls Backend API for all business operations** (Sprint 1)
- **No direct database access** (Sprint 1)

#### FastAPI Backend (Business Logic Layer)
- Exposes REST API for all operations
- Implements business rules and validation
- Handles authentication and authorization
- Provides consistent data access layer
- **Lead import with validation and normalization** (Sprint 1)
- **Batch import endpoint** (Sprint 1)
- **Activity logging endpoint** (Sprint 1)
- **Standard API response wrapper** (Sprint 1)
- **Lead priority scoring engine** (Sprint 2)
- **Follow-up reminder system** (Sprint 2)
- **Lead timeline endpoint** (Sprint 2)
- **Daily follow-up summary API** (Sprint 2)

#### Google Sheets (Import/Export Interface Only)
- Used for bulk data import (leads, contacts)
- Used for data export (reports, backups)
- Not a primary data store
- Temporary interface for manual operations

#### AI Layer (Future)
- Analyzes interaction patterns
- Scores leads based on multiple factors
- Suggests next actions for salespeople
- Summarizes long interaction histories

#### Communication Layer (Future)
- Sends automated emails
- Manages WhatsApp conversations
- Handles voice calls and recordings
- Tracks all communication in interaction history

---

## 6. AI Behavior

### What AI Should Remember

#### Context Memory
- **Customer History**: Past purchases, service requests, complaints
- **Interaction Patterns**: Preferred communication channels, response times
- **Relationship Depth**: How long we've known them, key contacts
- **Preferences**: Product interests, budget ranges, decision factors

#### Conversation Memory
- **Recent Interactions**: Last 5-10 interactions with context
- **Open Issues**: Unresolved problems or pending requests
- **Commitments Made**: Promises, deadlines, follow-ups owed
- **Decision Factors**: What mattered in past decisions

### What AI Should Not Do

#### Prohibited Actions
- **Never make promises** on behalf of the company
- **Never disclose sensitive information** (pricing, margins, internal data)
- **Never bypass human approval** for high-value decisions
- **Never modify customer data** without explicit instruction
- **Never send unsolicited communications** without opt-in

#### Guardrails
- **Human-in-the-loop**: All AI suggestions require human confirmation
- **Transparency**: AI must explain its reasoning when asked
- **Fallback**: AI must escalate to humans when uncertain
- **Audit**: All AI actions must be logged and reviewable

### Lead Scoring

#### Scoring Factors
1. **Company Fit** (0-25 points)
   - Industry match (0-10)
   - Company size (0-10)
   - Geographic presence (0-5)

2. **Engagement Level** (0-25 points)
   - Response speed (0-10)
   - Interaction frequency (0-10)
   - Content quality (0-5)

3. **Budget Readiness** (0-25 points)
   - Budget confirmed (0-15)
   - Timeline urgency (0-10)

4. **Relationship Strength** (0-25 points)
   - Existing customer (0-10)
   - Referral source (0-10)
   - Decision-maker access (0-5)

#### Score Interpretation
- **80-100**: Hot - Immediate attention, high probability
- **60-79**: Warm - Active engagement, good probability
- **40-59**: Lukewarm - Some interest, needs nurturing
- **20-39**: Cold - Low interest, long timeline
- **0-19**: Unqualified - Disqualify or archive

### Next Action Recommendations

#### Recommendation Logic
1. **Analyze current state** (lead stage, last interaction, score)
2. **Identify gaps** (missing information, stalled process)
3. **Propose action** (call, email, meeting, quote)
4. **Prioritize** based on score and urgency
5. **Provide context** (why this action, what to discuss)

#### Action Types
- **Call**: For high-priority leads, negotiations, relationship building
- **Email**: For quotations, follow-ups, documentation
- **Meeting**: For demos, site visits, complex discussions
- **Research**: For background information, competitive analysis
- **Wait**: If customer needs time, schedule follow-up

### Interaction Summarization

#### Summary Goals
- **Condense**: Long conversations into key points
- **Extract**: Decisions, commitments, action items
- **Context**: Provide background for next interaction
- **Tone**: Capture sentiment and relationship dynamics

#### Summary Structure
1. **Purpose**: Why the interaction happened
2. **Key Points**: Main topics discussed
3. **Decisions Made**: Agreements, confirmations
4. **Action Items**: Who needs to do what by when
5. **Next Steps**: Planned follow-up activities
6. **Sentiment**: Positive, neutral, negative

---

## 7. Data Model Principles

### Normalization

#### Third Normal Form (3NF)
- **First Normal Form**: No repeating groups, atomic values
- **Second Normal Form**: No partial dependencies
- **Third Normal Form**: No transitive dependencies

#### Example
- **Bad**: Store company name on every contact record
- **Good**: Contacts reference companies via foreign key
- **Benefit**: Update company name once, affects all contacts

### Deduplication

#### Unique Constraints
- **Companies**: Unique on (name, domain)
- **Contacts**: Unique on email
- **Leads**: Unique on (contact_id, company_id)
- **Opportunities**: Unique on (contact_id, company_id, stage)

#### Merge Strategy
- **When duplicates found**: Merge records, preserve most recent data
- **Conflict resolution**: Manual review for complex cases
- **Audit trail**: Keep record of merge operations

### Audit Logging

#### What to Log
- **CRUD operations**: Create, Read, Update, Delete on all entities
- **State changes**: All status transitions
- **AI actions**: Scoring, recommendations, summaries
- **User actions**: Manual overrides, approvals

#### Log Structure
- **Timestamp**: When the action occurred
- **Actor**: Who performed the action (user or system)
- **Entity Type**: What was affected
- **Entity ID**: Which record was affected
- **Action**: What was done
- **Changes**: Before/after values for updates
- **Reason**: Why the action was taken (if applicable)

### Source Tracking

#### Source Attribution
- **Import Source**: Where data came from (google_sheets, manual, api)
- **Last Modified**: When data was last changed
- **Modified By**: Who last changed the data
- **Confidence Score**: How confident we are in the data quality

#### Data Lineage
- **Original Source**: Ultimate source of truth
- **Transformation History**: What processing was applied
- **Validation Status**: Whether data passed validation
- **Quality Metrics**: Completeness, accuracy scores

### Idempotency

#### Upsert Pattern
- **Insert if not exists**: Create new record
- **Update if exists**: Modify existing record
- **No duplicates**: Same input produces same output

#### Implementation
- **PostgreSQL**: Use `ON CONFLICT` clauses
- **API**: Design endpoints to be idempotent
- **Workflows**: Handle re-runs gracefully

---

## 8. API Design

### Core Endpoints

#### Company Endpoints
```
POST   /api/v1/companies           - Create company
GET    /api/v1/companies           - List companies
GET    /api/v1/companies/{id}      - Get company details
PUT    /api/v1/companies/{id}      - Update company
DELETE /api/v1/companies/{id}      - Delete company
GET    /api/v1/companies/{id}/contacts - Get company contacts
GET    /api/v1/companies/{id}/opportunities - Get company opportunities
```

#### Contact Endpoints
```
POST   /api/v1/contacts            - Create contact
GET    /api/v1/contacts            - List contacts
GET    /api/v1/contacts/{id}       - Get contact details
PUT    /api/v1/contacts/{id}       - Update contact
DELETE /api/v1/contacts/{id}       - Delete contact
GET    /api/v1/contacts/{id}/interactions - Get contact interactions
```

#### Lead Endpoints
```
POST   /api/v1/leads               - Create lead (or import)
GET    /api/v1/leads               - List leads
GET    /api/v1/leads/{id}          - Get lead details
PUT    /api/v1/leads/{id}          - Update lead
DELETE /api/v1/leads/{id}          - Delete lead
POST   /api/v1/leads/{id}/convert  - Convert lead to opportunity
POST   /api/v1/leads/{id}/score    - Trigger lead scoring
GET    /api/v1/leads/{id}/next-action - Get AI-recommended next action
```

#### Opportunity Endpoints
```
POST   /api/v1/opportunities       - Create opportunity
GET    /api/v1/opportunities       - List opportunities
GET    /api/v1/opportunities/{id}  - Get opportunity details
PUT    /api/v1/opportunities/{id}  - Update opportunity
DELETE /api/v1/opportunities/{id}  - Delete opportunity
POST   /api/v1/opportunities/{id}/quote - Generate quotation
```

#### Quotation Endpoints
```
POST   /api/v1/quotations          - Create quotation
GET    /api/v1/quotations          - List quotations
GET    /api/v1/quotations/{id}     - Get quotation details
PUT    /api/v1/quotations/{id}     - Update quotation
DELETE /api/v1/quotations/{id}     - Delete quotation
POST   /api/v1/quotations/{id}/send - Send quotation to customer
POST   /api/v1/quotations/{id}/convert - Convert to order
```

#### Order Endpoints
```
POST   /api/v1/orders              - Create order
GET    /api/v1/orders              - List orders
GET    /api/v1/orders/{id}         - Get order details
PUT    /api/v1/orders/{id}         - Update order
DELETE /api/v1/orders/{id}         - Delete order
POST   /api/v1/orders/{id}/invoice - Generate invoice
```

#### Invoice Endpoints
```
POST   /api/v1/invoices            - Create invoice
GET    /api/v1/invoices            - List invoices
GET    /api/v1/invoices/{id}       - Get invoice details
PUT    /api/v1/invoices/{id}       - Update invoice
DELETE /api/v1/invoices/{id}       - Delete invoice
POST   /api/v1/invoices/{id}/payment - Record payment
```

#### Service Request Endpoints
```
POST   /api/v1/service-requests    - Create service request
GET    /api/v1/service-requests    - List service requests
GET    /api/v1/service-requests/{id} - Get service request details
PUT    /api/v1/service-requests/{id} - Update service request
DELETE /api/v1/service-requests/{id} - Delete service request
POST   /api/v1/service-requests/{id}/resolve - Mark as resolved
```

#### AMC Endpoints
```
POST   /api/v1/amcs                - Create AMC
GET    /api/v1/amcs                - List AMCs
GET    /api/v1/amcs/{id}           - Get AMC details
PUT    /api/v1/amcs/{id}           - Update AMC
DELETE /api/v1/amcs/{id}           - Delete AMC
POST   /api/v1/amcs/{id}/renew     - Renew AMC
```

#### Interaction Endpoints
```
POST   /api/v1/interactions        - Log interaction
GET    /api/v1/interactions        - List interactions
GET    /api/v1/interactions/{id}   - Get interaction details
POST   /api/v1/interactions/{id}/summarize - Generate AI summary
```

### Request/Response Contract Philosophy

#### Request Principles
- **Validation**: Validate all input before processing
- **Type Safety**: Use strong typing (Pydantic schemas)
- **Required Fields**: Clearly mark required vs optional
- **Default Values**: Provide sensible defaults for optional fields
- **Error Messages**: Return clear, actionable error messages

#### Response Principles
- **Consistent Format**: Use standard response wrapper
- **HTTP Status Codes**: Use appropriate status codes (200, 201, 400, 404, 500)
- **Pagination**: Use limit/offset for list endpoints
- **Filtering**: Support common filters (status, date range, etc.)
- **Sorting**: Support sort parameters (field, direction)

#### Standard Response Format
```json
{
  "success": true,
  "data": { /* actual response data */ },
  "message": "Operation completed successfully",
  "errors": null,
  "meta": {
    "timestamp": "2026-07-03T00:00:00Z",
    "request_id": "uuid"
  }
}
```

#### Error Response Format
```json
{
  "success": false,
  "data": null,
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ],
  "meta": {
    "timestamp": "2026-07-03T00:00:00Z",
    "request_id": "uuid"
  }
}
```

---

## 9. Dashboard Concept

### Sales Dashboard Views

#### Daily View (What a Salesperson Needs Daily)
- **Today's Tasks**: Follow-ups, callbacks, meetings
- **Hot Leads**: High-score leads needing attention
- **Pending Quotations**: Quotes sent awaiting response
- **New Leads**: Leads added in last 24 hours
- **Activity Summary**: Calls made, emails sent, meetings held

#### Pipeline View
- **Funnel Chart**: Leads → Opportunities → Quotations → Orders
- **Stage Breakdown**: Number and value per stage
- **Conversion Rates**: Stage-to-stage conversion percentages
- **Average Deal Size**: Average value per stage
- **Sales Velocity**: Time to close by stage

#### Performance View
- **Target vs Actual**: Monthly/quarterly targets vs achievement
- **Top Performers**: Leaderboard by revenue closed
- **Activity Metrics**: Calls, emails, meetings per salesperson
- **Conversion Metrics**: Lead-to-opportunity, opportunity-to-close rates
- **Trend Analysis**: Performance over time

#### Customer View
- **Customer List**: All companies with key metrics
- **Customer Health**: Satisfaction scores, engagement levels
- **AMC Status**: Active, expiring, renewal opportunities
- **Service Requests**: Open, in-progress, resolved counts
- **Interaction History**: Recent communication timeline

#### Alert View
- **Overdue Follow-ups**: Missed callbacks, delayed responses
- **Expiring AMCs**: Contracts due for renewal
- **High-Priority Service Requests**: Urgent customer issues
- **Stalled Deals**: Opportunities not progressing
- **Payment Overdue**: Invoices past due date

### Key Metrics

#### Lead Metrics
- **Lead Volume**: Number of new leads per period
- **Lead Quality**: Average lead score
- **Response Time**: Average time to first contact
- **Conversion Rate**: Lead to opportunity percentage

#### Opportunity Metrics
- **Pipeline Value**: Total value of open opportunities
- **Win Rate**: Percentage of opportunities closed won
- **Sales Cycle**: Average time from lead to close
- **Deal Size**: Average value of closed deals

#### Activity Metrics
- **Call Volume**: Number of calls made per period
- **Email Volume**: Number of emails sent per period
- **Meeting Volume**: Number of meetings held per period
- **Follow-up Rate**: Percentage of leads followed up within SLA

#### Customer Metrics
- **Customer Satisfaction**: Average satisfaction score
- **Retention Rate**: Percentage of customers retained
- **AMC Renewal Rate**: Percentage of AMCs renewed
- **Service Response Time**: Average time to resolve service requests

### Dashboard Features

#### Customization
- **Personal Views**: Each user can customize their dashboard
- **Saved Filters**: Save common filter combinations
- **Widget Layout**: Drag-and-drop widget arrangement
- **Theme Selection**: Light/dark mode options

#### Interactivity
- **Drill-Down**: Click to view detailed data
- **Date Range Picker**: Select custom time periods
- **Export**: Export data to CSV/PDF
- **Share**: Share dashboard views with team

#### Real-Time Updates
- **Live Data**: Dashboard updates in real-time
- **Notifications**: In-app notifications for important events
- **Alerts**: Proactive alerts for overdue items
- **Mobile Access**: Responsive design for mobile devices

---

## 10. Security and Deployment Principles

### Secrets Handling

#### Environment Variables
- **Never commit secrets** to Git
- **Use .env files** for local development
- **Use .env.example** as template
- **Use secret managers** for production (AWS Secrets Manager, HashiCorp Vault)

#### Secret Categories
- **Database Credentials**: PostgreSQL username, password
- **API Keys**: Google Sheets OAuth2, email service keys
- **Encryption Keys**: Data encryption at rest
- **Service Credentials**: Third-party service authentication

#### Best Practices
- **Rotate secrets** regularly
- **Use different secrets** for different environments
- **Audit secret access** logs
- **Revoke compromised secrets** immediately

### Local Development vs Production

#### Local Development
- **Use Docker Compose** for local stack
- **Mock external services** where possible
- **Use local PostgreSQL** instance
- **Enable debug logging**
- **Use test data** (not production data)

#### Production
- **Use managed services** where possible (RDS, ECS)
- **Enable SSL/TLS** for all communications
- **Use production-grade secrets** management
- **Enable monitoring and alerting**
- **Use production data** with proper backups

#### Staging
- **Mirror production** configuration
- **Use production-like data** (anonymized)
- **Test all changes** in staging first
- **Load test** before production deployment

### Versioning and Backups

#### Database Versioning
- **Use migration files** for schema changes
- **Version migrations** sequentially (001, 002, 003...)
- **Never modify** existing migrations
- **Rollback support** for each migration

#### Application Versioning
- **Semantic versioning** (MAJOR.MINOR.PATCH)
- **Tag releases** in Git
- **Maintain changelog** for each release
- **Support backward compatibility** where possible

#### Backup Strategy
- **Daily backups** of PostgreSQL database
- **Weekly full backups** with daily incrementals
- **Off-site storage** for disaster recovery
- **Restore testing** regular verification
- **Retention policy** keep backups for 90 days

#### Workflow Versioning
- **Version control** all workflow JSON files
- **Document changes** in commit messages
- **Test workflows** after changes
- **Rollback capability** for failed deployments

---

## 11. Roadmap

### Phase 0: Foundation (Completed)
**Status**: ✅ Done

**Deliverables**:
- ✅ Docker stack (PostgreSQL, n8n, pgAdmin)
- ✅ Normalized CRM database schema
- ✅ Lead Import v1 workflow (mock data)
- ✅ Initial documentation
- ✅ Clean repo structure

### Phase 1: Backend API Foundation (Completed)
**Status**: ✅ Done

**Deliverables**:
- ✅ FastAPI backend with clean structure
- ✅ Database models and Pydantic schemas
- ✅ Core CRUD operations
- ✅ API endpoints for lead operations
- ✅ Backend Docker integration
- ✅ Health endpoint with PostgreSQL connectivity
- ✅ API contract documentation

### Phase 1.5: Real Data Integration (In Progress)
**Status**: ⚠️ Manual Setup Required

**Deliverables**:
- ✅ Google Sheets integration workflow
- ✅ Column mapping layer
- ✅ Data validation and normalization
- ✅ Duplicate prevention (ON CONFLICT)
- ✅ Import tracking table
- ✅ Activity logging
- ✅ Mock data workflow archived
- ⚠️ Google Sheets credentials setup (manual)
- ⚠️ Real data testing (pending)

### Phase 2: Lead Scoring Engine
**Status**: 🚧 Not Started

**Deliverables**:
- Configurable scoring rules
- Real-time score calculation
- Lead tier assignment (hot/warm/cold)
- Score history tracking
- API endpoint for score refresh
- Scoring rules documentation

**Success Criteria**:
- Scoring completes in <100ms per lead
- Scores are explainable and transparent
- Rules can be modified without code changes

### Phase 3: Next-Action Recommendations
**Status**: 🚧 Not Started

**Deliverables**:
- AI-powered next action suggestions
- Action prioritization based on score and urgency
- Context-aware recommendations
- Action outcome tracking
- Recommendation quality metrics

**Success Criteria**:
- Recommendations improve follow-up rates by 20%
- Salespeople accept >70% of recommendations
- Recommendations are contextually relevant

### Phase 4: Communication Layer
**Status**: 🚧 Not Started

**Deliverables**:
- Email integration (send/receive)
- WhatsApp integration (send/receive)
- Voice/phone integration
- Interaction logging
- Communication templates
- Automated follow-up sequences

**Success Criteria**:
- All communications logged automatically
- Templates reduce email drafting time by 50%
- Automated follow-ups increase response rates by 30%

### Phase 5: Sales Dashboard
**Status**: 🚧 Not Started

**Deliverables**:
- Web-based dashboard UI
- Daily view for salespeople
- Pipeline view for managers
- Performance metrics and charts
- Customizable widgets
- Real-time updates
- Mobile-responsive design

**Success Criteria**:
- Dashboard loads sales data in <2 seconds
- Salespeople use dashboard daily
- Dashboard improves visibility into pipeline

### Phase 6: AI Integration
**Status**: 🚧 Not Started

**Deliverables**:
- AI-powered interaction summarization
- Pattern detection in sales data
- Predictive analytics (churn risk, upsell opportunities)
- Natural language query interface
- AI-assisted data entry

**Success Criteria**:
- Summaries reduce reading time by 70%
- Predictions have >80% accuracy
- Natural language queries work reliably

### What Should Not Be Built Yet

#### Not in Scope (Future Phases)
- **Mobile App**: Phase 7+
- **Advanced Analytics**: Phase 7+
- **Multi-tenancy**: Phase 7+
- **Advanced AI**: Phase 6+
- **CRM Migration Tools**: Phase 7+
- **Advanced Reporting**: Phase 7+

#### Explicitly Out of Scope
- **Social Media Integration**: Not a priority
- **Marketing Automation**: Focus on sales, not marketing
- **Project Management**: Focus on CRM, not PM
- **Inventory Management**: Focus on sales, not operations
- **Accounting Integration**: Focus on CRM, not finance

### Dependencies

#### Phase 2 Depends On
- Phase 1.5 completion (real data flowing)

#### Phase 3 Depends On
- Phase 2 completion (scoring data available)

#### Phase 4 Depends On
- Phase 1 completion (API endpoints available)
- Phase 2 completion (scoring for prioritization)

#### Phase 5 Depends On
- Phase 1 completion (API endpoints available)
- Phase 2 completion (scoring data)
- Phase 4 completion (interaction data)

#### Phase 6 Depends On
- Phase 2 completion (scoring foundation)
- Phase 4 completion (interaction data)
- Phase 5 completion (user feedback)

### Timeline Estimates

- **Phase 1.5**: 1 week (manual setup)
- **Phase 2**: 2-3 weeks
- **Phase 3**: 2-3 weeks
- **Phase 4**: 4-6 weeks
- **Phase 5**: 6-8 weeks
- **Phase 6**: 8-12 weeks

**Total Estimated Time**: 23-33 weeks (6-8 months)

---

## Appendix

### Terminology

- **CRM**: Customer Relationship Management
- **AMC**: Annual Maintenance Contract
- **SLA**: Service Level Agreement
- **BANT**: Budget, Authority, Need, Timeline (qualification framework)
- **SARA**: Sales Automation and Relationship Assistant

### References

- **Database Schema**: `docs/database-schema.md`
- **Architecture**: `docs/architecture.md`
- **Workflow Management**: `workflows/WORKFLOW_MANAGEMENT.md`
- **Google Sheets Integration**: `workflows/google-sheets-integration.md`

### Version History

- **v1.0** (2026-07-03): Initial blueprint creation
