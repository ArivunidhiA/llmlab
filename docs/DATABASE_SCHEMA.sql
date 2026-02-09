-- LLMLab Database Schema (PostgreSQL)
-- Use with Supabase PostgreSQL

-- ============================================================================
-- USERS TABLE
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key ON users(api_key);

-- ============================================================================
-- PROJECTS TABLE
-- ============================================================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_user_id ON projects(user_id);

-- ============================================================================
-- COST EVENTS TABLE
-- ============================================================================

CREATE TABLE cost_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    model VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    tokens_input INT DEFAULT 0,
    tokens_output INT DEFAULT 0,
    cost_usd DECIMAL(10, 6) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Critical indexes for fast queries
CREATE INDEX idx_cost_events_user_id ON cost_events(user_id);
CREATE INDEX idx_cost_events_timestamp ON cost_events(timestamp);
CREATE INDEX idx_cost_events_user_timestamp ON cost_events(user_id, timestamp DESC);
CREATE INDEX idx_cost_events_user_model ON cost_events(user_id, model);
CREATE INDEX idx_cost_events_user_provider ON cost_events(user_id, provider);

-- ============================================================================
-- BUDGETS TABLE
-- ============================================================================

CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    amount_usd DECIMAL(10, 2) NOT NULL,
    period VARCHAR(20) DEFAULT 'monthly',
    start_date DATE NOT NULL,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_budgets_user_id ON budgets(user_id);

-- ============================================================================
-- RECOMMENDATIONS TABLE (Cached)
-- ============================================================================

CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    current_model VARCHAR(100),
    suggested_model VARCHAR(100),
    savings_usd DECIMAL(10, 2),
    savings_percent DECIMAL(5, 2),
    confidence DECIMAL(3, 2),
    effort VARCHAR(20),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_expires_at ON recommendations(expires_at);

-- ============================================================================
-- SAMPLE DATA (for testing/demo)
-- ============================================================================

-- Sample user (password: 'demo123' hashed with bcrypt)
INSERT INTO users (email, api_key, password_hash, is_active)
VALUES (
    'demo@llmlab.dev',
    'llmlab_sk_demo_' || encode(random()::text::bytea, 'hex'),
    '$2b$12$Yd.kzCxqU8gFDT9b8V0WyO1tGRCfgXJb3cHpXLkY6VF1fqON1nOJm',
    true
);

-- Sample project
INSERT INTO projects (user_id, name, description)
SELECT id, 'Demo Project', 'Example project for testing'
FROM users WHERE email = 'demo@llmlab.dev';

-- Sample cost events (last 30 days)
INSERT INTO cost_events (user_id, model, provider, tokens_input, tokens_output, cost_usd, timestamp)
SELECT 
    u.id,
    models.model,
    models.provider,
    (RANDOM() * 1000)::INT,
    (RANDOM() * 500)::INT,
    models.cost,
    CURRENT_TIMESTAMP - (RANDOM() * 30)::INT * INTERVAL '1 day'
FROM users u, (
    VALUES
        ('gpt-4', 'openai', 0.05),
        ('gpt-3.5-turbo', 'openai', 0.005),
        ('claude-3-opus', 'anthropic', 0.03),
        ('claude-3-sonnet', 'anthropic', 0.003),
        ('gemini-pro', 'google', 0.0005)
) AS models(model, provider, cost)
WHERE u.email = 'demo@llmlab.dev'
LIMIT 50;

-- Sample budget
INSERT INTO budgets (user_id, amount_usd, period, start_date)
SELECT id, 1000.00, 'monthly', CURRENT_DATE
FROM users WHERE email = 'demo@llmlab.dev';

-- ============================================================================
-- VIEWS (for analytics)
-- ============================================================================

-- Total spend by user
CREATE VIEW user_total_spend AS
SELECT 
    user_id,
    SUM(cost_usd) as total_usd,
    COUNT(*) as call_count,
    AVG(cost_usd) as avg_cost_usd,
    MAX(timestamp) as last_call
FROM cost_events
GROUP BY user_id;

-- Spend by model
CREATE VIEW user_spend_by_model AS
SELECT 
    user_id,
    model,
    provider,
    SUM(cost_usd) as total_usd,
    COUNT(*) as call_count,
    AVG(cost_usd) as avg_cost_usd
FROM cost_events
GROUP BY user_id, model, provider;

-- Daily spend
CREATE VIEW user_daily_spend AS
SELECT 
    user_id,
    DATE(timestamp) as date,
    SUM(cost_usd) as daily_spend_usd,
    COUNT(*) as call_count
FROM cost_events
GROUP BY user_id, DATE(timestamp)
ORDER BY user_id, date DESC;

-- Budget status
CREATE VIEW budget_status AS
SELECT 
    b.id,
    b.user_id,
    b.amount_usd,
    COALESCE(SUM(ce.cost_usd), 0) as spent_usd,
    b.amount_usd - COALESCE(SUM(ce.cost_usd), 0) as remaining_usd,
    ROUND(100.0 * COALESCE(SUM(ce.cost_usd), 0) / b.amount_usd, 2) as percentage_used
FROM budgets b
LEFT JOIN cost_events ce ON ce.user_id = b.user_id 
    AND DATE(ce.timestamp) >= b.start_date
    AND (b.end_date IS NULL OR DATE(ce.timestamp) <= b.end_date)
GROUP BY b.id, b.user_id, b.amount_usd;

-- ============================================================================
-- SECURITY NOTES
-- ============================================================================
/*
1. API Keys should be encrypted using a key management service in production
2. Password hashes should use bcrypt with salt rounds >= 12
3. All queries should use parameterized statements (prevent SQL injection)
4. Row-level security (RLS) should be enabled on sensitive tables
5. Audit logging should be enabled for cost_events table
6. Regular backups should be configured in Supabase
*/

-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================
/*
To run this migration:

1. Connect to Supabase:
   psql postgresql://[user]:[password]@[project].supabase.co:5432/postgres

2. Create extension for UUID:
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

3. Run this file:
   psql < DATABASE_SCHEMA.sql

4. Verify tables were created:
   \dt

5. Test sample queries:
   SELECT * FROM users;
   SELECT * FROM cost_events LIMIT 10;
   SELECT * FROM user_total_spend;
*/

-- ============================================================================
-- PERFORMANCE TIPS
-- ============================================================================
/*
1. Add partitioning for cost_events by user_id for large tables
2. Use CLUSTER for frequently-accessed indexes
3. Regularly run ANALYZE to update table statistics
4. Create materialized views for expensive analytics queries
5. Use connection pooling (Supabase provides this)
*/
