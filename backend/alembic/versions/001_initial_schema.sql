-- brandguard/backend/alembic/versions/001_initial_schema.sql
-- Initial database schema for BrandGuard

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Companies table
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    industry VARCHAR(100),
    website VARCHAR(255),
    country VARCHAR(100),
    description TEXT,
    
    -- Reputation metrics
    reputation_score FLOAT DEFAULT 0.0,
    reputation_trend FLOAT DEFAULT 0.0,
    total_mentions INTEGER DEFAULT 0,
    positive_mentions INTEGER DEFAULT 0,
    negative_mentions INTEGER DEFAULT 0,
    neutral_mentions INTEGER DEFAULT 0,
    
    -- Risk assessment
    risk_score FLOAT DEFAULT 0.0,
    risk_factors JSON DEFAULT '[]',
    
    -- Metadata
    sources_config JSON DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_analyzed TIMESTAMP WITH TIME ZONE
);

-- Data sources table
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- news, reviews, social, financial
    url VARCHAR(500) NOT NULL,
    api_endpoint VARCHAR(500),
    credibility_score FLOAT DEFAULT 0.8,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 100,
    last_accessed TIMESTAMP WITH TIME ZONE,
    api_key_required BOOLEAN DEFAULT FALSE,
    
    -- Compliance
    terms_accepted BOOLEAN DEFAULT FALSE,
    privacy_compliant BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Articles table
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
    
    -- Article data
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    url VARCHAR(1000) NOT NULL,
    published_date TIMESTAMP WITH TIME ZONE NOT NULL,
    author VARCHAR(255),
    
    -- Analysis results
    sentiment VARCHAR(20) DEFAULT 'neutral',
    confidence_score FLOAT DEFAULT 0.0,
    keywords JSON DEFAULT '[]',
    entities JSON DEFAULT '[]',
    relevance_score FLOAT DEFAULT 0.0,
    
    -- Compliance
    is_public BOOLEAN DEFAULT TRUE,
    data_retention_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reviews table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    platform VARCHAR(100) NOT NULL,
    
    -- Review data (public only)
    reviewer_id VARCHAR(255),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(500),
    content TEXT NOT NULL,
    review_date TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Analysis
    sentiment VARCHAR(20) DEFAULT 'neutral',
    verified BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    
    -- Compliance
    platform_terms_compliant BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alerts table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_active ON companies(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_articles_company_date ON articles(company_id, published_date DESC);
CREATE INDEX idx_articles_sentiment ON articles(sentiment);
CREATE INDEX idx_reviews_company_date ON reviews(company_id, review_date DESC);
CREATE INDEX idx_alerts_company_unread ON alerts(company_id, is_read) WHERE is_read = FALSE;

-- Full text search indexes
CREATE INDEX idx_articles_content_fts ON articles USING gin(to_tsvector('english', content));
CREATE INDEX idx_articles_title_fts ON articles USING gin(to_tsvector('english', title));

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_sources_updated_at BEFORE UPDATE ON data_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();