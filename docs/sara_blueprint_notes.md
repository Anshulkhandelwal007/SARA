# SARA Blueprint Notes

**Companion document to SARA_BLUEPRINT.md**

This document captures open questions, assumptions, risks, and pending decisions for the SARA project.

---

## Open Questions

### Business Domain

1. **Industry Focus**: What industries should SARA target initially? (B2B SaaS, manufacturing, services, etc.)
2. **Company Size**: What company size range is the target market? (SMB, mid-market, enterprise)
3. **Geographic Scope**: Is this for a specific region or global from day one?
4. **Pricing Model**: How will SARA be priced? (per user, per company, per feature, freemium)
5. **Sales Team Size**: How many salespeople will use the system initially?

### Customer Lifecycle

1. **Lead Sources**: Besides Google Sheets, what other lead sources should be supported? (website forms, referrals, events)
2. **Quotation Approval**: What value threshold requires manager approval for quotations?
3. **Payment Terms**: What are standard payment terms? (net 30, net 60, advance payment)
4. **Service SLAs**: What are the response and resolution SLAs for different priority levels?
5. **AMC Renewal Terms**: What are standard AMC renewal terms and pricing?

### Operating Model

1. **Follow-Up Frequency**: What is the optimal follow-up cadence for different lead scores?
2. **Qualification Criteria**: Should we use BANT or a different qualification framework?
3. **Disqualification Rules**: What are the specific rules for disqualifying leads?
4. **Escalation Triggers**: When should a lead/opportunity be escalated to management?
5. **Service Request Assignment**: How should service requests be assigned to technicians?

### Architecture

1. **AI Provider**: Which AI provider should we use? (OpenAI, Anthropic, local models)
2. **Communication Providers**: Which email/WhatsApp/voice providers should we integrate with?
3. **Scalability**: What is the expected scale? (number of users, records, transactions per day)
4. **Multi-tenancy**: Should the system support multi-tenancy from the start or add later?
5. **Data Retention**: How long should different types of data be retained?

### AI Behavior

1. **Scoring Model**: Should we use a rule-based scoring system or machine learning?
2. **AI Training Data**: Where will we get training data for the AI models?
3. **AI Confidence Threshold**: What confidence threshold should AI have before making recommendations?
4. **Human Override**: How should human overrides of AI recommendations be handled?
5. **AI Transparency**: How much detail should AI provide about its reasoning?

### Data Model

1. **Custom Fields**: How flexible should the custom fields system be? (JSON, dynamic schema)
2. **Data Migration**: How will existing data be migrated to the new system?
3. **Data Export**: What export formats should be supported? (CSV, PDF, Excel)
4. **Data Privacy**: How will we handle GDPR/CCPA compliance?
5. **Data Backup**: What is the RPO/RTO for data backups?

### API Design

1. **Authentication**: What authentication method should we use? (JWT, OAuth2, API keys)
2. **Rate Limiting**: What are the rate limits for API endpoints?
3. **API Versioning**: How will we handle API versioning? (URL versioning, header versioning)
4. **Webhooks**: Should we support webhooks for external integrations?
5. **GraphQL vs REST**: Should we consider GraphQL in addition to REST?

### Dashboard

1. **Tech Stack**: What frontend framework should we use? (React, Vue, Svelte)
2. **Real-Time Updates**: How should real-time updates be implemented? (WebSockets, polling)
3. **Mobile Support**: Should we prioritize mobile web or native mobile app?
4. **Offline Support**: Should the dashboard support offline mode?
5. **Accessibility**: What accessibility standards should we meet? (WCAG 2.1)

### Security

1. **Encryption**: What encryption standards should we use? (AES-256, TLS 1.3)
2. **2FA**: Should we require two-factor authentication?
3. **Audit Log Retention**: How long should audit logs be retained?
4. **Penetration Testing**: How often should we conduct penetration testing?
5. **Compliance**: What compliance standards must we meet? (SOC 2, ISO 27001)

---

## Assumptions

### Business Assumptions

1. **Target Market**: Small to medium businesses (10-100 employees) in B2B services
2. **Sales Process**: Standard B2B sales process with 3-6 month sales cycle
3. **Data Volume**: Initial deployment will handle <10,000 leads, <1,000 companies
4. **User Base**: Initial deployment will have <50 users
5. **Geography**: Single region deployment initially (India)

### Technical Assumptions

1. **PostgreSQL**: Will remain the primary database for the foreseeable future
2. **n8n**: Will remain the orchestration layer for automation
3. **FastAPI**: Will remain the backend framework
4. **Docker**: Will be used for all deployments
5. **Cloud Provider**: Will use AWS or GCP for production deployment

### Data Assumptions

1. **Lead Quality**: Imported data will have reasonable quality (not completely garbage)
2. **Email Validity**: Email addresses will be valid and deliverable
3. **Phone Format**: Phone numbers will be in standard formats
4. **Company Data**: Company names and websites will be accurate
5. **Data Freshness**: Data will be imported regularly (at least weekly)

### User Behavior Assumptions

1. **Adoption**: Salespeople will use the system if it saves time
2. **Training**: Users will require minimal training (intuitive UI)
3. **Mobile Usage**: Salespeople will access the system from mobile devices
4. **Data Entry**: Users will enter data accurately if the process is simple
5. **AI Trust**: Users will trust AI recommendations if they are explainable

### Integration Assumptions

1. **Google Sheets**: Will be the primary data import/export interface initially
2. **Email**: Will use standard email providers (Gmail, Outlook)
3. **WhatsApp**: Will use WhatsApp Business API
4. **Phone**: Will use VoIP providers (Twilio, Plivo)
5. **Future Integrations**: Will add more integrations based on user demand

---

## Risks

### Business Risks

1. **Market Fit**: Risk that the target market doesn't need or want this solution
2. **Competition**: Risk that established CRM players (Salesforce, HubSpot) compete aggressively
3. **Pricing Pressure**: Risk that pricing becomes commoditized
4. **Customer Churn**: Risk that customers leave after initial trial
5. **Feature Creep**: Risk of adding too many features and losing focus

### Technical Risks

1. **Scalability**: Risk that the system doesn't scale to handle growth
2. **Performance**: Risk that performance degrades with data volume
3. **Data Loss**: Risk of data loss due to bugs or infrastructure failures
4. **Security Breach**: Risk of unauthorized access to customer data
5. **Integration Failures**: Risk that third-party integrations break or change

### Data Quality Risks

1. **Garbage In**: Risk that imported data is poor quality
2. **Duplicates**: Risk that duplicate records aren't caught
3. **Data Drift**: Risk that data becomes stale over time
4. **Migration Errors**: Risk that data migration introduces errors
5. **Privacy Violations**: Risk of mishandling sensitive customer data

### AI Risks

1. **Bias**: Risk that AI models introduce bias in scoring/recommendations
2. **Accuracy**: Risk that AI recommendations are inaccurate
3. **Over-reliance**: Risk that users over-rely on AI and stop thinking
4. **Explainability**: Risk that AI decisions can't be explained
5. **Cost**: Risk that AI API costs become prohibitive

### Operational Risks

1. **Staffing**: Risk of not having enough technical staff to maintain system
2. **Support**: Risk of not providing adequate customer support
3. **Documentation**: Risk that documentation becomes outdated
4. **Testing**: Risk that testing is insufficient and bugs reach production
5. **Deployment**: Risk that deployment process is error-prone

### Timeline Risks

1. **Scope Creep**: Risk that scope expands beyond initial estimates
2. **Dependency Delays**: Risk that dependencies (third-party APIs) cause delays
3. **Technical Debt**: Risk that shortcuts create technical debt
4. **Resource Constraints**: Risk of not having enough development resources
5. **User Feedback**: Risk that user feedback requires significant rework

---

## Decisions Still Pending

### High Priority Decisions

1. **AI Provider Selection**: Need to choose between OpenAI, Anthropic, or local models
2. **Communication Providers**: Need to select email, WhatsApp, and voice providers
3. **Pricing Model**: Need to determine pricing strategy and tiers
4. **Initial Target Market**: Need to define specific industry and company size focus
5. **Go-to-Market Strategy**: Need to define how we will acquire initial customers

### Medium Priority Decisions

1. **Frontend Framework**: Need to choose React, Vue, or Svelte for dashboard
2. **Authentication Method**: Need to choose JWT, OAuth2, or API keys
3. **Multi-tenancy Strategy**: Need to decide if multi-tenancy is needed from start
4. **Data Retention Policy**: Need to define retention periods for different data types
5. **SLA Definitions**: Need to define specific SLAs for different priority levels

### Low Priority Decisions

1. **Mobile App Strategy**: Need to decide between mobile web or native app
2. **GraphQL vs REST**: Need to evaluate if GraphQL is needed
3. **Advanced Analytics**: Need to define what analytics features are needed
4. **CRM Migration Tools**: Need to decide if migration tools are needed
5. **Marketing Automation**: Need to decide if marketing features are needed

### Deferred Decisions

1. **Social Media Integration**: Defer to Phase 7+
2. **Project Management Features**: Defer to Phase 7+
3. **Inventory Management**: Defer to Phase 7+
4. **Accounting Integration**: Defer to Phase 7+
5. **Advanced AI Features**: Defer to Phase 6+

---

## Technical Debt

### Current Technical Debt

1. **Mock Data Workflow**: Archived but not fully removed from database
2. **Manual Google Sheets Setup**: Requires manual credential configuration
3. **No Automated Testing**: No automated tests for workflows or API
4. **Limited Error Handling**: Basic error handling in workflows
5. **No Monitoring**: No application monitoring or alerting

### Planned Technical Debt Reduction

1. **Automated Testing**: Add unit tests for API, integration tests for workflows
2. **Error Handling**: Improve error handling and retry logic
3. **Monitoring**: Add application monitoring (Prometheus, Grafana)
4. **Logging**: Improve logging structure and log aggregation
5. **Documentation**: Keep documentation in sync with code changes

---

## Dependencies

### External Dependencies

1. **Google Sheets API**: Requires OAuth2 credentials and API access
2. **PostgreSQL**: Requires database server and backups
3. **n8n**: Requires n8n instance and task runner
4. **FastAPI**: Requires Python runtime and dependencies
5. **Docker**: Requires Docker runtime and orchestration

### Internal Dependencies

1. **Database Schema**: All features depend on normalized schema
2. **API Endpoints**: Dashboard depends on API endpoints
3. **Workflows**: Automation depends on workflow definitions
4. **AI Models**: AI features depend on trained models
5. **Communication Layer**: Automation depends on communication integrations

### Third-Party Services

1. **Email Provider**: Gmail API, Outlook API, or SMTP server
2. **WhatsApp Provider**: WhatsApp Business API
3. **Voice Provider**: Twilio, Plivo, or similar
4. **AI Provider**: OpenAI, Anthropic, or local models
5. **Cloud Provider**: AWS, GCP, or Azure for hosting

---

## Success Metrics

### Phase 1.5 Success Metrics

- Google Sheets credentials configured
- Real data imported successfully
- No duplicates created on re-import
- Activity logging working
- Import tracking table functional

### Phase 2 Success Metrics

- Lead scoring completes in <100ms
- Scores are explainable
- Scoring rules can be modified without code
- Score history tracking works

### Phase 3 Success Metrics

- Recommendations improve follow-up rates by 20%
- Salespeople accept >70% of recommendations
- Recommendations are contextually relevant

### Phase 4 Success Metrics

- All communications logged automatically
- Templates reduce email drafting time by 50%
- Automated follow-ups increase response rates by 30%

### Phase 5 Success Metrics

- Dashboard loads in <2 seconds
- Salespeople use dashboard daily
- Dashboard improves pipeline visibility

### Phase 6 Success Metrics

- Summaries reduce reading time by 70%
- Predictions have >80% accuracy
- Natural language queries work reliably

---

## Notes

### Design Decisions Made

1. **PostgreSQL as Source of Truth**: Chosen for reliability, ACID compliance, and JSON support
2. **n8n for Orchestration**: Chosen for visual workflow building and extensibility
3. **FastAPI for Backend**: Chosen for performance, type safety, and async support
4. **Google Sheets for Import/Export**: Chosen for familiarity and ease of use
5. **Layered Architecture**: Chosen for separation of concerns and testability

### Lessons Learned

1. **n8n CLI Limitations**: n8n CLI has limitations for automated execution
2. **Credential Management**: OAuth2 credentials require manual setup
3. **Database Migrations**: Need a structured migration system
4. **Workflow Versioning**: Workflows need to be version controlled
5. **Documentation**: Documentation must be kept in sync with changes

### Future Considerations

1. **Multi-tenancy**: May need to add multi-tenancy for SaaS deployment
2. **API Rate Limiting**: May need to add rate limiting for public API
3. **Caching**: May need to add caching for performance
4. **CDN**: May need CDN for static assets
5. **Load Balancing**: May need load balancing for high availability

---

## References

### Related Documents

- **SARA_BLUEPRINT.md**: Main design document
- **ROADMAP.md**: Project roadmap and milestones
- **docs/architecture.md**: Technical architecture details
- **docs/database-schema.md**: Database schema documentation
- **workflows/google-sheets-integration.md**: Google Sheets integration guide
- **workflows/WORKFLOW_MANAGEMENT.md**: Workflow management guide

### External Resources

- **n8n Documentation**: https://docs.n8n.io
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **PostgreSQL Documentation**: https://www.postgresql.org/docs
- **Docker Documentation**: https://docs.docker.com

---

## Version History

- **v1.0** (2026-07-03): Initial notes document created
