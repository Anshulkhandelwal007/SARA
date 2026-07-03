# Project SARA Roadmap

## Current State

**Phase 0: Foundation (Completed)**

Project SARA has a solid foundation in place:
- ✅ Docker stack running (PostgreSQL 16, n8n, pgAdmin)
- ✅ Normalized CRM database schema v2 (10 tables with proper relationships)
- ✅ Lead Import v1 workflow (idempotent, validated, documented)
- ✅ Initial documentation (README, architecture, schema docs)
- ✅ Clean repo structure with core folders

**Phase 1: Backend API Foundation (Completed)**

Backend API layer is complete and running in Docker:
- ✅ FastAPI backend skeleton with clean structure
- ✅ Database models and schemas (Pydantic)
- ✅ Core CRUD operations for leads, contacts, companies
- ✅ API endpoints for lead operations (import, score, next-action, summarize, followup)
- ✅ Integration with existing PostgreSQL database
- ✅ Backend Dockerfile created
- ✅ Backend service added to docker-compose.yml
- ✅ Backend environment variables configured
- ✅ Backend service running and verified
- ✅ Health endpoint working with PostgreSQL connectivity
- ✅ API contract documented in OpenAPI/Swagger

**Phase 1.5: Real Data Integration (In Progress)**

Replacing mock data with real Google Sheets integration:
- ✅ Google Sheets integration documentation created
- ✅ Column mapping layer for flexible schema mapping
- ✅ Incremental import strategy designed (import_tracking table)
- ✅ Google Sheets integration workflow created
- ✅ Data validation and normalization implemented
- ✅ Company upsert with duplicate prevention (ON CONFLICT)
- ✅ Contact upsert with duplicate prevention (ON CONFLICT)
- ✅ Lead upsert with duplicate prevention (ON CONFLICT)
- ✅ Activity logging implemented
- ✅ Import tracking table created in PostgreSQL
- ✅ Mock data workflow archived
- ⚠️ Google Sheets credentials setup in n8n (manual step required)
- ⚠️ Workflow testing with real Google Sheets data (pending)
- ⚠️ Incremental import testing (pending)

**What's Working:**
- PostgreSQL is the system of record with normalized tables for companies, contacts, leads, and communication history
- n8n is running and ready for workflow automation
- Backend API is running in Docker with health endpoint verified
- Google Sheets integration workflow is ready for deployment
- Column mapping layer supports flexible schema mapping
- Database-level duplicate prevention with ON CONFLICT clauses
- Import tracking table enables incremental imports
- Automated workflow deployment script
- Documentation covers architecture, workflow management, and Google Sheets integration

**What's Missing:**
- Google Sheets credentials setup in n8n (requires manual OAuth2 configuration)
- Real Google Sheets data testing
- Incremental import verification
- n8n workflows calling backend API instead of direct PostgreSQL access (future migration)
- Lead scoring engine (real implementation)
- Next-action recommendation system (real implementation)
- AI integration layer
- Communication layer (email, WhatsApp, voice)

---

## Phase 1: Backend API Foundation

**Goal:** Build a clean, modular backend API that encapsulates all business logic and provides a clear interface for n8n workflows.

**Definition of Done:**
- FastAPI backend running in Docker alongside existing services
- Health endpoint returning system status
- Lead ingestion endpoint with validation
- Lead scoring endpoint (mock for now, ready for AI)
- Next-action recommendation endpoint (mock for now)
- Call summary endpoint (mock for now)
- Follow-up decision endpoint (mock for now)
- Clean separation: n8n calls backend API, backend API talks to PostgreSQL
- API contract documented in OpenAPI/Swagger
- Unit tests for core business logic
- Environment-based configuration

**Milestones:**
1. ✅ Backend skeleton with FastAPI structure
2. ✅ Database models and schemas (Pydantic)
3. ✅ Core CRUD operations for leads, contacts, companies
4. ✅ API endpoints for lead ingestion and scoring
5. ✅ Integration with existing PostgreSQL database
6. ✅ Dockerization of backend service
7. ✅ API documentation and testing

**Prerequisites for Next Phase:**
- All endpoints return consistent JSON responses
- Error handling is standardized
- Database connection pooling is configured
- Logging is implemented
- n8n can successfully call backend endpoints

---

## Phase 2: Lead Scoring Engine

**Goal:** Implement a production-ready lead scoring system that evaluates leads based on multiple factors and assigns scores/tiers.

**Definition of Done:**
- Configurable scoring rules (company size, industry, engagement, etc.)
- Real-time score calculation on lead creation/update
- Score recalculation trigger (manual or scheduled)
- Lead tier assignment (hot/warm/cold) based on score thresholds
- Score history tracking in database
- API endpoint for manual score refresh
- Scoring rules documented and editable
- Performance: scoring completes in <100ms per lead

**Milestones:**
1. Define scoring criteria and weights
2. Implement scoring engine in backend service
3. Add score calculation to lead ingestion flow
4. Create score history table
5. Build scoring rules editor (simple UI or config file)
6. Add scheduled score recalculation job
7. Performance testing and optimization

**Prerequisites for Next Phase:**
- Scoring is accurate and consistent
- Score changes are logged
- n8n workflows can trigger score refreshes
- Scoring rules are documented

---

## Phase 3: Next-Action Recommendation

**Goal:** Build an intelligent system that recommends the best next action for each lead based on their status, history, and score.

**Definition of Done:**
- Rule-based recommendation engine (initially)
- Recommendation types: email, call, WhatsApp, wait, no-action
- Priority-based action queue
- Integration with follow-ups table
- API endpoint for getting next action
- Recommendation history tracking
- Performance: recommendation completes in <50ms

**Milestones:**
1. Define recommendation logic matrix
2. Implement recommendation engine
3. Create next-action API endpoint
4. Integrate with follow-ups scheduling
5. Build recommendation history tracking
6. Add recommendation confidence scoring
7. Test with real lead scenarios

**Prerequisites for Next Phase:**
- Recommendations are actionable and accurate
- n8n can fetch and execute recommendations
- Recommendation history is queryable
- System handles edge cases (no action needed, etc.)

---

## Phase 4: AI Integration Layer

**Goal:** Integrate AI capabilities for lead scoring, call summarization, and intelligent recommendations.

**Definition of Done:**
- AI service abstraction layer (provider-agnostic)
- Call transcript summarization
- Email thread summarization
- AI-enhanced lead scoring
- AI-powered next-action recommendations
- Cost tracking and rate limiting
- Fallback to rule-based logic when AI fails
- AI model versioning and A/B testing capability

**Milestones:**
1. Design AI service abstraction
2. Integrate with AI provider (OpenAI/Anthropic/etc.)
3. Implement call summarization
4. Implement email summarization
5. Enhance scoring with AI insights
6. Enhance recommendations with AI
7. Add cost monitoring and controls
8. Implement fallback mechanisms

**Prerequisites for Next Phase:**
- AI integration is reliable and cost-effective
- Fallback mechanisms work correctly
- AI responses are stored in ai_summaries table
- System can switch between AI providers

---

## Phase 5: Communication Layer

**Goal:** Implement actual communication channels (email, WhatsApp, voice) with proper tracking and logging.

**Definition of Done:**
- Email integration (Brevo/SendGrid) with delivery tracking
- WhatsApp Business API integration
- Voice calling integration (Twilio/Vonage)
- All communication logged to respective history tables
- Two-way sync (inbound messages update lead status)
- Template management system
- Rate limiting and compliance checks
- Failed delivery handling and retry logic

**Milestones:**
1. Email provider integration (Brevo)
2. Email template system
3. Email delivery tracking
4. WhatsApp Business API integration
5. WhatsApp message templates
6. Voice calling integration
7. Communication logging to database
8. Inbound message handling
9. Compliance and rate limiting

**Prerequisites for Next Phase:**
- All channels are functional
- Communication history is complete
- Templates are manageable
- System handles failures gracefully

---

## Phase 6: Advanced Automation

**Goal:** Build sophisticated automation workflows that leverage all previous phases.

**Definition of Done:**
- Automated lead nurturing sequences
- Smart follow-up scheduling based on engagement
- Hot lead notification system
- Automated meeting scheduling
- Lead handoff to human sales reps
- Performance dashboards and reporting
- A/B testing for messages and timing

**Milestones:**
1. Design nurturing sequence logic
2. Build sequence engine in backend
3. Create hot lead notification workflow
4. Implement meeting scheduling integration
5. Build lead handoff process
6. Create performance dashboards
7. Implement A/B testing framework

**Prerequisites for Next Phase:**
- All previous phases are stable
- Automation is measurable and optimizable
- System can scale to handle increased volume

---

## Next 3-5 Concrete Milestones

### Milestone 1: Backend API Skeleton (Current)
- Create FastAPI backend structure
- Implement health endpoint
- Implement lead ingestion endpoint
- Dockerize backend service
- Integrate with existing PostgreSQL
- **Estimated effort:** 2-3 days

### Milestone 2: Lead Scoring Rules Engine
- Define scoring criteria
- Implement scoring logic
- Add scoring to lead ingestion
- Create score history tracking
- **Estimated effort:** 3-4 days

### Milestone 3: Next-Action Recommendation System
- Define recommendation matrix
- Implement recommendation engine
- Create next-action API endpoint
- Integrate with follow-ups
- **Estimated effort:** 3-4 days

### Milestone 4: AI Service Integration
- Design AI abstraction layer
- Integrate with AI provider
- Implement call summarization
- **Estimated effort:** 4-5 days

### Milestone 5: Email Communication Integration
- Integrate Brevo API
- Build email template system
- Implement delivery tracking
- Log to email_history table
- **Estimated effort:** 3-4 days

---

## Phase Transition Criteria

Before moving from Phase N to Phase N+1:

1. **All milestones in current phase are complete**
2. **Definition of Done for current phase is met**
3. **All prerequisites for next phase are satisfied**
4. **Code is reviewed and documented**
5. **Tests pass and performance meets requirements**
6. **No critical bugs or technical debt**
7. **Stakeholder approval (if applicable)**

---

## Architecture Evolution

### Current Architecture (Phase 0)
```
Google Sheets → n8n → PostgreSQL
                ↓
              pgAdmin
```

### Target Architecture (Phase 1-2)
```
Google Sheets → n8n → Backend API → PostgreSQL
                           ↓
                         pgAdmin
```

### Final Architecture (Phase 6)
```
Google Sheets → n8n → Backend API → PostgreSQL
                     ↓              ↓
                   AI Services   Communication Providers
                     ↓              ↓
                   Email/WhatsApp/Voice
```

---

## Technical Debt Tracking

**Current Debt:**
- None identified

**Potential Debt to Monitor:**
- n8n workflow complexity as business rules grow
- Database query performance as data volume increases
- AI cost management as usage scales
- Template management complexity

---

## Risk Assessment

**High Risks:**
- AI cost overruns if not monitored
- Communication provider rate limits
- Data privacy and compliance (GDPR, etc.)

**Medium Risks:**
- n8n workflow becoming too complex
- Database performance at scale
- Integration provider reliability

**Mitigation Strategies:**
- Implement cost monitoring and alerts
- Use rate limiting and queuing
- Keep business logic in backend, not n8n
- Regular database performance reviews
- Provider diversification where possible

---

## Success Metrics

**Phase 1:**
- Backend API response time <100ms
- 99.9% uptime
- Zero data loss in lead ingestion

**Phase 2:**
- Scoring accuracy >80% (based on human validation)
- Score calculation time <100ms

**Phase 3:**
- Recommendation adoption rate >70%
- Recommended actions improve conversion by >20%

**Phase 4:**
- AI summarization accuracy >85%
- AI cost per lead <$0.50

**Phase 5:**
- Email delivery rate >95%
- WhatsApp message delivery rate >90%
- Call connection rate >70%

**Phase 6:**
- Automated follow-up response rate >60%
- Lead-to-opportunity conversion increase >30%
