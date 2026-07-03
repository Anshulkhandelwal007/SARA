-- SARA Database Schema v2
-- PostgreSQL 16
-- Production-ready CRM foundation with normalized tables

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Companies table
-- Stores organization/company information with duplicate prevention
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    domain VARCHAR(255), -- Extracted from website for matching
    industry VARCHAR(100),
    size VARCHAR(50), -- small, medium, large, enterprise
    revenue_range VARCHAR(50),
    location VARCHAR(255),
    country VARCHAR(100),
    employee_count INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT companies_name_domain_unique UNIQUE (name, domain)
);

-- Contacts table
-- Individual people (can exist without being leads)
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    mobile VARCHAR(50),
    title VARCHAR(100),
    department VARCHAR(100),
    linkedin_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT contacts_email_unique UNIQUE (email)
);

-- Leads table
-- Sales opportunities linked to contacts
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    source VARCHAR(50) NOT NULL, -- google_sheets, web_form, api, referral, manual
    status VARCHAR(50) DEFAULT 'new', -- new, contacted, engaged, qualified, opportunity, customer, churned, lost
    score INTEGER DEFAULT 0 CHECK (score >= 0 AND score <= 100),
    tier VARCHAR(20), -- hot, warm, cold
    assigned_to VARCHAR(100),
    estimated_value DECIMAL(15,2),
    probability INTEGER DEFAULT 0 CHECK (probability >= 0 AND probability <= 100),
    expected_close_date DATE,
    custom_fields JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_contacted_at TIMESTAMP WITH TIME ZONE,
    next_followup_at TIMESTAMP WITH TIME ZONE,
    interaction_count INTEGER DEFAULT 0,
    notified_hot BOOLEAN DEFAULT FALSE,
    notified_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- COMMUNICATION HISTORY TABLES
-- ============================================================================

-- Lead interactions table
-- Complete audit trail of all lead touchpoints
CREATE TABLE IF NOT EXISTS lead_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL, -- email, whatsapp, call, meeting, note, sms
    channel VARCHAR(50),
    direction VARCHAR(20), -- inbound, outbound
    status VARCHAR(50), -- sent, delivered, read, failed, scheduled
    subject VARCHAR(255),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Email history table
-- Detailed email tracking
CREATE TABLE IF NOT EXISTS email_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    interaction_id UUID REFERENCES lead_interactions(id) ON DELETE SET NULL,
    from_email VARCHAR(255) NOT NULL,
    to_email VARCHAR(255) NOT NULL,
    cc_email TEXT,
    bcc_email TEXT,
    subject VARCHAR(500) NOT NULL,
    body TEXT,
    html_body TEXT,
    message_id VARCHAR(255),
    thread_id VARCHAR(255),
    provider VARCHAR(50), -- brevo, sendgrid, gmail, etc.
    external_id VARCHAR(255), -- Provider's message ID
    status VARCHAR(50), -- sent, delivered, opened, clicked, bounced, failed
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    bounced_at TIMESTAMP WITH TIME ZONE,
    bounce_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- WhatsApp history table
-- WhatsApp message tracking
CREATE TABLE IF NOT EXISTS whatsapp_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    interaction_id UUID REFERENCES lead_interactions(id) ON DELETE SET NULL,
    from_number VARCHAR(50) NOT NULL,
    to_number VARCHAR(50) NOT NULL,
    message_type VARCHAR(50), -- text, image, document, audio, video
    content TEXT,
    media_url TEXT,
    message_id VARCHAR(255),
    status VARCHAR(50), -- sent, delivered, read, failed
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Call logs table
-- Voice call records and transcripts
CREATE TABLE IF NOT EXISTS call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    interaction_id UUID REFERENCES lead_interactions(id) ON DELETE SET NULL,
    call_provider VARCHAR(50), -- twilio, vonage, etc.
    call_id VARCHAR(255),
    direction VARCHAR(20), -- inbound, outbound
    status VARCHAR(50), -- completed, failed, busy, no_answer, cancelled
    duration_seconds INTEGER,
    recording_url TEXT,
    transcript TEXT,
    sentiment VARCHAR(20), -- positive, neutral, negative
    summary TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- FOLLOW-UP MANAGEMENT
-- ============================================================================

-- Follow-ups table
-- Scheduled and completed follow-ups
CREATE TABLE IF NOT EXISTS followups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL, -- email, whatsapp, voice_call, sms
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, sent, failed, cancelled, completed
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    message_content TEXT,
    template_id VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AI AND ANALYTICS
-- ============================================================================

-- AI summaries table
-- AI-generated summaries of interactions
CREATE TABLE IF NOT EXISTS ai_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    interaction_id UUID REFERENCES lead_interactions(id) ON DELETE SET NULL,
    summary_type VARCHAR(50), -- call_summary, email_thread, lead_overview, next_steps
    summary_text TEXT NOT NULL,
    key_points JSONB,
    sentiment VARCHAR(20),
    confidence_score DECIMAL(3,2),
    model_used VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Activity log table
-- System-wide activity tracking
CREATE TABLE IF NOT EXISTS activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL, -- lead, contact, company, workflow
    entity_id UUID,
    action VARCHAR(50) NOT NULL, -- created, updated, deleted, imported, exported
    actor VARCHAR(100), -- user or system
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Companies indexes
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(domain);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);

-- Contacts indexes
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_company_id ON contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_mobile ON contacts(mobile);

-- Leads indexes
CREATE INDEX IF NOT EXISTS idx_leads_contact_id ON leads(contact_id);
CREATE INDEX IF NOT EXISTS idx_leads_company_id ON leads(company_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score);
CREATE INDEX IF NOT EXISTS idx_leads_tier ON leads(tier);
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_leads_next_followup ON leads(next_followup_at);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_leads_assigned_to ON leads(assigned_to);

-- Lead interactions indexes
CREATE INDEX IF NOT EXISTS idx_lead_interactions_lead_id ON lead_interactions(lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_interactions_type ON lead_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_lead_interactions_created_at ON lead_interactions(created_at);

-- Email history indexes
CREATE INDEX IF NOT EXISTS idx_email_history_lead_id ON email_history(lead_id);
CREATE INDEX IF NOT EXISTS idx_email_history_external_id ON email_history(external_id);
CREATE INDEX IF NOT EXISTS idx_email_history_created_at ON email_history(created_at);

-- WhatsApp history indexes
CREATE INDEX IF NOT EXISTS idx_whatsapp_history_lead_id ON whatsapp_history(lead_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_history_message_id ON whatsapp_history(message_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_history_created_at ON whatsapp_history(created_at);

-- Call logs indexes
CREATE INDEX IF NOT EXISTS idx_call_logs_lead_id ON call_logs(lead_id);
CREATE INDEX IF NOT EXISTS idx_call_logs_call_id ON call_logs(call_id);
CREATE INDEX IF NOT EXISTS idx_call_logs_created_at ON call_logs(created_at);

-- Follow-ups indexes
CREATE INDEX IF NOT EXISTS idx_followups_lead_id ON followups(lead_id);
CREATE INDEX IF NOT EXISTS idx_followups_scheduled_at ON followups(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_followups_status ON followups(status);
CREATE INDEX IF NOT EXISTS idx_followups_priority ON followups(priority);

-- AI summaries indexes
CREATE INDEX IF NOT EXISTS idx_ai_summaries_lead_id ON ai_summaries(lead_id);
CREATE INDEX IF NOT EXISTS idx_ai_summaries_type ON ai_summaries(summary_type);
CREATE INDEX IF NOT EXISTS idx_ai_summaries_created_at ON ai_summaries(created_at);

-- Activity log indexes
CREATE INDEX IF NOT EXISTS idx_activity_log_entity ON activity_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_followups_updated_at BEFORE UPDATE ON followups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert sample companies
INSERT INTO companies (name, website, domain, industry, size, location, country) VALUES
('Acme Corporation', 'https://acme.com', 'acme.com', 'Technology', 'medium', 'San Francisco, CA', 'USA'),
('Globex Inc', 'https://globex.com', 'globex.com', 'Finance', 'large', 'New York, NY', 'USA'),
('Soylent Corp', 'https://soylent.com', 'soylent.com', 'Food & Beverage', 'small', 'Los Angeles, CA', 'USA')
ON CONFLICT (name, domain) DO NOTHING;

-- Insert sample contacts
INSERT INTO contacts (company_id, first_name, last_name, email, phone, title) VALUES
((SELECT id FROM companies WHERE domain = 'acme.com' LIMIT 1), 'John', 'Doe', 'john.doe@acme.com', '+1-555-0101', 'CTO'),
((SELECT id FROM companies WHERE domain = 'globex.com' LIMIT 1), 'Jane', 'Smith', 'jane.smith@globex.com', '+1-555-0102', 'VP of Sales'),
((SELECT id FROM companies WHERE domain = 'soylent.com' LIMIT 1), 'Bob', 'Johnson', 'bob.johnson@soylent.com', '+1-555-0103', 'Manager')
ON CONFLICT (email) DO NOTHING;

-- Insert sample leads
INSERT INTO leads (contact_id, company_id, source, status, score) VALUES
((SELECT id FROM contacts WHERE email = 'john.doe@acme.com' LIMIT 1), 
 (SELECT id FROM companies WHERE domain = 'acme.com' LIMIT 1), 'web_form', 'new', 75),
((SELECT id FROM contacts WHERE email = 'jane.smith@globex.com' LIMIT 1), 
 (SELECT id FROM companies WHERE domain = 'globex.com' LIMIT 1), 'google_sheets', 'contacted', 85),
((SELECT id FROM contacts WHERE email = 'bob.johnson@soylent.com' LIMIT 1), 
 (SELECT id FROM companies WHERE domain = 'soylent.com' LIMIT 1), 'referral', 'new', 45);
