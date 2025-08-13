-- ESG Sentiment Scorer Database Schema
-- Initialize database tables for storing scraped news and ESG analysis

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(10),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    country VARCHAR(100) DEFAULT 'USA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for companies
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);

-- News articles table
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    url VARCHAR(1000) UNIQUE NOT NULL,
    source VARCHAR(100),
    author VARCHAR(200),
    published_date TIMESTAMP,
    scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    language VARCHAR(10) DEFAULT 'en',
    word_count INTEGER,
    company_id UUID REFERENCES companies(id),
    raw_html TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for news_articles
CREATE INDEX IF NOT EXISTS idx_news_articles_published_date ON news_articles(published_date);
CREATE INDEX IF NOT EXISTS idx_news_articles_source ON news_articles(source);
CREATE INDEX IF NOT EXISTS idx_news_articles_company_id ON news_articles(company_id);
CREATE INDEX IF NOT EXISTS idx_news_articles_language ON news_articles(language);

-- ESG sentiment analysis results
CREATE TABLE IF NOT EXISTS esg_sentiment_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID REFERENCES news_articles(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id),
    overall_sentiment DECIMAL(3,2), -- -1.00 to 1.00
    confidence_score DECIMAL(3,2),  -- 0.00 to 1.00
    environmental_score DECIMAL(3,2),
    social_score DECIMAL(3,2),
    governance_score DECIMAL(3,2),
    environmental_sentiment DECIMAL(3,2),
    social_sentiment DECIMAL(3,2),
    governance_sentiment DECIMAL(3,2),
    key_themes TEXT[], -- Array of themes
    risk_indicators TEXT[], -- Array of risk indicators
    model_version VARCHAR(50),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for esg_sentiment_analysis
CREATE INDEX IF NOT EXISTS idx_esg_sentiment_article_id ON esg_sentiment_analysis(article_id);
CREATE INDEX IF NOT EXISTS idx_esg_sentiment_company_id ON esg_sentiment_analysis(company_id);
CREATE INDEX IF NOT EXISTS idx_esg_sentiment_analyzed_at ON esg_sentiment_analysis(analyzed_at);
CREATE INDEX IF NOT EXISTS idx_esg_sentiment_overall_sentiment ON esg_sentiment_analysis(overall_sentiment);

-- ESG keywords and classifications
CREATE TABLE IF NOT EXISTS esg_keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword VARCHAR(100) NOT NULL,
    category VARCHAR(20) NOT NULL, -- 'environmental', 'social', 'governance'
    weight DECIMAL(3,2) DEFAULT 1.00,
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(keyword, category, language)
);

-- Create indexes for esg_keywords
CREATE INDEX IF NOT EXISTS idx_esg_keywords_category ON esg_keywords(category);
CREATE INDEX IF NOT EXISTS idx_esg_keywords_language ON esg_keywords(language);

-- News sources configuration
CREATE TABLE IF NOT EXISTS news_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    url VARCHAR(200) NOT NULL,
    country VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en',
    reliability_score DECIMAL(3,2) DEFAULT 0.80,
    update_frequency INTEGER DEFAULT 60, -- minutes
    selectors JSONB, -- CSS selectors for scraping
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(url)
);

-- Create indexes for news_sources
CREATE INDEX IF NOT EXISTS idx_news_sources_country ON news_sources(country);
CREATE INDEX IF NOT EXISTS idx_news_sources_language ON news_sources(language);
CREATE INDEX IF NOT EXISTS idx_news_sources_is_active ON news_sources(is_active);

-- Company ESG scores aggregated over time
CREATE TABLE IF NOT EXISTS company_esg_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id),
    date DATE NOT NULL,
    environmental_score DECIMAL(3,2),
    social_score DECIMAL(3,2),
    governance_score DECIMAL(3,2),
    overall_score DECIMAL(3,2),
    confidence_score DECIMAL(3,2),
    articles_analyzed INTEGER DEFAULT 0,
    sentiment_trend DECIMAL(3,2), -- Week-over-week change
    risk_level VARCHAR(20), -- 'low', 'medium', 'high'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, date)
);

-- Create indexes for company_esg_scores
CREATE INDEX IF NOT EXISTS idx_company_esg_scores_company_id ON company_esg_scores(company_id);
CREATE INDEX IF NOT EXISTS idx_company_esg_scores_date ON company_esg_scores(date);
CREATE INDEX IF NOT EXISTS idx_company_esg_scores_overall_score ON company_esg_scores(overall_score);

-- Search and analysis logs
CREATE TABLE IF NOT EXISTS analysis_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id),
    search_query VARCHAR(200),
    articles_found INTEGER DEFAULT 0,
    articles_analyzed INTEGER DEFAULT 0,
    processing_time_ms INTEGER,
    error_message TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for analysis_logs
CREATE INDEX IF NOT EXISTS idx_analysis_logs_company_id ON analysis_logs(company_id);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_status ON analysis_logs(status);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_created_at ON analysis_logs(created_at);

-- Insert some default ESG keywords
INSERT INTO esg_keywords (keyword, category, weight, language) VALUES
-- Environmental keywords
('climate change', 'environmental', 1.0, 'en'),
('carbon emissions', 'environmental', 1.0, 'en'),
('renewable energy', 'environmental', 0.9, 'en'),
('sustainability', 'environmental', 0.8, 'en'),
('pollution', 'environmental', 0.9, 'en'),
('greenhouse gas', 'environmental', 1.0, 'en'),
('waste management', 'environmental', 0.7, 'en'),
('biodiversity', 'environmental', 0.8, 'en'),
('water usage', 'environmental', 0.7, 'en'),
('environmental compliance', 'environmental', 0.9, 'en'),

-- Social keywords
('human rights', 'social', 1.0, 'en'),
('labor practices', 'social', 0.9, 'en'),
('diversity', 'social', 0.8, 'en'),
('inclusion', 'social', 0.8, 'en'),
('employee satisfaction', 'social', 0.7, 'en'),
('workplace safety', 'social', 0.9, 'en'),
('community relations', 'social', 0.7, 'en'),
('product safety', 'social', 0.8, 'en'),
('customer privacy', 'social', 0.8, 'en'),
('social responsibility', 'social', 0.8, 'en'),

-- Governance keywords
('board independence', 'governance', 0.9, 'en'),
('executive compensation', 'governance', 0.8, 'en'),
('shareholder rights', 'governance', 0.8, 'en'),
('transparency', 'governance', 0.9, 'en'),
('anti-corruption', 'governance', 1.0, 'en'),
('audit', 'governance', 0.7, 'en'),
('risk management', 'governance', 0.8, 'en'),
('corporate governance', 'governance', 0.9, 'en'),
('compliance', 'governance', 0.8, 'en'),
('ethics', 'governance', 0.8, 'en')
ON CONFLICT (keyword, category, language) DO NOTHING;

-- Insert some major news sources
INSERT INTO news_sources (name, url, country, language, reliability_score, selectors) VALUES
('Reuters', 'https://www.reuters.com', 'USA', 'en', 0.95, '{"title": ".ArticleHeader_headline", "content": ".StandardArticleBody_body"}'),
('Bloomberg', 'https://www.bloomberg.com', 'USA', 'en', 0.90, '{"title": ".lede-text-v2__hed", "content": ".body-content"}'),
('Financial Times', 'https://www.ft.com', 'UK', 'en', 0.92, '{"title": ".article-title", "content": ".article-body__content"}'),
('Wall Street Journal', 'https://www.wsj.com', 'USA', 'en', 0.90, '{"title": ".headline", "content": ".article-content"}'),
('BBC Business', 'https://www.bbc.com/business', 'UK', 'en', 0.85, '{"title": ".story-body__h1", "content": ".story-body__inner"}')
ON CONFLICT (url) DO NOTHING;
