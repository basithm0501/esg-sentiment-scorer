-- Complete Database Migration Script
-- Add all missing columns that your application expects

-- Add missing columns to news_articles
DO $$ 
BEGIN
    -- company column (string version of company name)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='company') THEN
        ALTER TABLE news_articles ADD COLUMN company VARCHAR(255);
    END IF;
    
    -- raw_text column (alternative to content)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='raw_text') THEN
        ALTER TABLE news_articles ADD COLUMN raw_text TEXT;
    END IF;
    
    -- translated_text column (for multilingual support)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='translated_text') THEN
        ALTER TABLE news_articles ADD COLUMN translated_text TEXT;
    END IF;
    
    -- timestamp column (alternative to scraped_date/published_date)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='timestamp') THEN
        ALTER TABLE news_articles ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
    
    -- Make sure source column exists (should already exist)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='source') THEN
        ALTER TABLE news_articles ADD COLUMN source VARCHAR(100);
    END IF;
    
    -- Make sure language column exists (should already exist)  
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='language') THEN
        ALTER TABLE news_articles ADD COLUMN language VARCHAR(10) DEFAULT 'en';
    END IF;
    
    -- Make sure url column exists (should already exist)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='news_articles' AND column_name='url') THEN
        ALTER TABLE news_articles ADD COLUMN url VARCHAR(1000) UNIQUE NOT NULL;
    END IF;
    
END $$;

-- Update existing data to populate the new columns
UPDATE news_articles 
SET company = companies.name
FROM companies 
WHERE news_articles.company_id = companies.id
AND news_articles.company IS NULL;

-- Set raw_text = content where raw_text is null
UPDATE news_articles 
SET raw_text = content 
WHERE raw_text IS NULL AND content IS NOT NULL;

-- Set timestamp = scraped_date where timestamp is null
UPDATE news_articles 
SET timestamp = scraped_date 
WHERE timestamp IS NULL AND scraped_date IS NOT NULL;

-- Create triggers to keep company column in sync
CREATE OR REPLACE FUNCTION sync_company_name()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.company_id IS NOT NULL THEN
        SELECT name INTO NEW.company 
        FROM companies 
        WHERE id = NEW.company_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if it exists and create new one
DROP TRIGGER IF EXISTS trigger_sync_company_name ON news_articles;
CREATE TRIGGER trigger_sync_company_name
    BEFORE INSERT OR UPDATE ON news_articles
    FOR EACH ROW
    EXECUTE FUNCTION sync_company_name();

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_news_articles_company ON news_articles(company);
CREATE INDEX IF NOT EXISTS idx_news_articles_timestamp ON news_articles(timestamp);
CREATE INDEX IF NOT EXISTS idx_news_articles_raw_text ON news_articles USING gin(to_tsvector('english', raw_text));

-- Create a view that maps to the expected column names
CREATE OR REPLACE VIEW v_news_articles_compat AS
SELECT 
    id,
    title,
    content,
    raw_text,
    translated_text,
    url,
    source,
    author,
    published_date,
    scraped_date,
    timestamp,
    language,
    word_count,
    company,
    company_id,
    raw_html,
    summary,
    sentiment_score,
    category,
    tags,
    is_analyzed,
    created_at
FROM news_articles;

-- Show the updated schema
\echo 'Updated news_articles schema:'
\d news_articles

-- Show sample data
\echo 'Sample data with new columns:'
SELECT title, company, source, language, url, timestamp FROM news_articles LIMIT 3;
