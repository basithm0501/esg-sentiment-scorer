-- ESG Sentiment Scorer Database Schema Fixes
-- Migration script to ensure all expected columns exist

-- Add missing columns if they don't exist
-- (PostgreSQL will ignore if they already exist)

-- Fix news_articles table - ensure all expected columns exist
DO $$ 
BEGIN
    -- Add company column as an alias/view of company_id if needed
    -- (But we should use company_id instead)
    
    -- Ensure source column exists (it should already)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='source') THEN
        ALTER TABLE news_articles ADD COLUMN source VARCHAR(100);
    END IF;
    
    -- Ensure author column exists  
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='author') THEN
        ALTER TABLE news_articles ADD COLUMN author VARCHAR(200);
    END IF;
    
    -- Ensure summary column exists (for article summaries)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='summary') THEN
        ALTER TABLE news_articles ADD COLUMN summary TEXT;
    END IF;
    
    -- Ensure sentiment_score column exists (for quick access)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='sentiment_score') THEN
        ALTER TABLE news_articles ADD COLUMN sentiment_score DECIMAL(3,2);
    END IF;
    
    -- Ensure category column exists (for article classification)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='category') THEN
        ALTER TABLE news_articles ADD COLUMN category VARCHAR(50);
    END IF;
    
    -- Ensure tags column exists (for article tags)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='tags') THEN
        ALTER TABLE news_articles ADD COLUMN tags TEXT[];
    END IF;
    
    -- Ensure is_analyzed column exists (to track analysis status)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='is_analyzed') THEN
        ALTER TABLE news_articles ADD COLUMN is_analyzed BOOLEAN DEFAULT FALSE;
    END IF;
    
END $$;

-- Fix companies table - ensure all expected columns exist
DO $$ 
BEGIN
    -- Ensure website column exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='companies' AND column_name='website') THEN
        ALTER TABLE companies ADD COLUMN website VARCHAR(200);
    END IF;
    
    -- Ensure description column exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='companies' AND column_name='description') THEN
        ALTER TABLE companies ADD COLUMN description TEXT;
    END IF;
    
    -- Ensure employees count exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='companies' AND column_name='employees') THEN
        ALTER TABLE companies ADD COLUMN employees INTEGER;
    END IF;
    
    -- Ensure founded_year exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='companies' AND column_name='founded_year') THEN
        ALTER TABLE companies ADD COLUMN founded_year INTEGER;
    END IF;
    
    -- Ensure headquarters exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='companies' AND column_name='headquarters') THEN
        ALTER TABLE companies ADD COLUMN headquarters VARCHAR(200);
    END IF;
    
END $$;

-- Fix esg_sentiment_analysis table - ensure all expected columns exist
DO $$ 
BEGIN
    -- Ensure article_summary column exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='esg_sentiment_analysis' AND column_name='article_summary') THEN
        ALTER TABLE esg_sentiment_analysis ADD COLUMN article_summary TEXT;
    END IF;
    
    -- Ensure processing_metadata column exists (for storing model info, etc.)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='esg_sentiment_analysis' AND column_name='processing_metadata') THEN
        ALTER TABLE esg_sentiment_analysis ADD COLUMN processing_metadata JSONB;
    END IF;
    
END $$;

-- Create useful views for easier data access
CREATE OR REPLACE VIEW v_articles_with_companies AS
SELECT 
    na.id,
    na.title,
    na.content,
    na.url,
    na.source,
    na.author,
    na.published_date,
    na.scraped_date,
    na.language,
    na.word_count,
    na.sentiment_score,
    na.category,
    na.tags,
    na.is_analyzed,
    c.name as company_name,
    c.ticker as company_ticker,
    c.sector as company_sector,
    c.industry as company_industry,
    c.country as company_country
FROM news_articles na
LEFT JOIN companies c ON na.company_id = c.id;

-- Create view for latest ESG analysis per company
CREATE OR REPLACE VIEW v_latest_esg_analysis AS
SELECT DISTINCT ON (c.id)
    c.id as company_id,
    c.name as company_name,
    c.ticker,
    c.sector,
    esa.overall_sentiment,
    esa.confidence_score,
    esa.environmental_score,
    esa.social_score,
    esa.governance_score,
    esa.key_themes,
    esa.risk_indicators,
    esa.analyzed_at,
    COUNT(na.id) OVER (PARTITION BY c.id) as total_articles
FROM companies c
LEFT JOIN esg_sentiment_analysis esa ON c.id = esa.company_id
LEFT JOIN news_articles na ON c.id = na.company_id
ORDER BY c.id, esa.analyzed_at DESC NULLS LAST;

-- Create indexes for better performance on new columns
CREATE INDEX IF NOT EXISTS idx_news_articles_sentiment_score ON news_articles(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_news_articles_category ON news_articles(category);
CREATE INDEX IF NOT EXISTS idx_news_articles_is_analyzed ON news_articles(is_analyzed);
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);

-- Update statistics
ANALYZE;

-- Show the updated schema
\echo 'Updated schema for news_articles:'
\d news_articles

\echo 'Updated schema for companies:'  
\d companies

\echo 'Created views:'
\dv
