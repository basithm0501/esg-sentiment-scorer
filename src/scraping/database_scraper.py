"""
Database-integrated news scraper for ESG Sentiment Scorer
This scraper saves scraped data directly to PostgreSQL database
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Import the existing scraper
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.scraping.news_scraper import NewsScraperEngine, NewsArticle
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseIntegratedScraper:
    """News scraper that saves results to PostgreSQL database"""
    
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        
    def get_or_create_company(self, company_name: str, ticker: str = None, sector: str = None) -> str:
        """Get existing company or create new one, return company ID"""
        
        with self.engine.begin() as conn:
            # Check if company exists
            check_query = text("""
                SELECT id FROM companies 
                WHERE name ILIKE :name OR (ticker = :ticker AND ticker IS NOT NULL)
            """)
            
            result = conn.execute(check_query, {
                "name": f"%{company_name}%",
                "ticker": ticker
            }).fetchone()
            
            if result:
                return str(result[0])
            
            # Create new company
            company_id = str(uuid.uuid4())
            insert_query = text("""
                INSERT INTO companies (id, name, ticker, sector, created_at, updated_at)
                VALUES (:id, :name, :ticker, :sector, :created_at, :updated_at)
                RETURNING id
            """)
            
            result = conn.execute(insert_query, {
                "id": company_id,
                "name": company_name,
                "ticker": ticker,
                "sector": sector,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            
            logger.info(f"✅ Created company: {company_name} ({company_id})")
            return company_id
    
    def save_article_to_database(self, article: NewsArticle, company_id: str) -> str:
        """Save news article to database, return article ID"""
        
        with self.engine.begin() as conn:
            # Check if article already exists (by URL)
            check_query = text("SELECT id FROM news_articles WHERE url = :url")
            result = conn.execute(check_query, {"url": article.url}).fetchone()
            
            if result:
                logger.info(f"📰 Article already exists: {article.title[:50]}...")
                return str(result[0])
            
            # Insert new article
            article_id = str(uuid.uuid4())
            
            insert_query = text("""
                INSERT INTO news_articles (
                    id, title, content, url, source, published_date,
                    scraped_date, language, word_count, company_id, created_at
                ) VALUES (
                    :id, :title, :content, :url, :source, :published_date,
                    :scraped_date, :language, :word_count, :company_id, :created_at
                )
            """)
            
            conn.execute(insert_query, {
                "id": article_id,
                "title": article.title,
                "content": article.content,
                "url": article.url,
                "source": article.source,
                "published_date": article.published_date,
                "scraped_date": datetime.now(),
                "language": article.language,
                "word_count": len(article.content.split()) if article.content else 0,
                "company_id": company_id,
                "created_at": datetime.now()
            })
            
            logger.info(f"✅ Saved article: {article.title[:50]}...")
            return article_id
    
    def log_analysis_activity(self, company_id: str, search_query: str, 
                            articles_found: int, processing_time_ms: int, 
                            status: str = "completed", error_message: str = None):
        """Log scraping activity to analysis_logs table"""
        
        with self.engine.begin() as conn:
            log_query = text("""
                INSERT INTO analysis_logs (
                    id, company_id, search_query, articles_found, 
                    processing_time_ms, status, error_message, created_at
                ) VALUES (
                    :id, :company_id, :search_query, :articles_found,
                    :processing_time_ms, :status, :error_message, :created_at
                )
            """)
            
            conn.execute(log_query, {
                "id": str(uuid.uuid4()),
                "company_id": company_id,
                "search_query": search_query,
                "articles_found": articles_found,
                "processing_time_ms": processing_time_ms,
                "status": status,
                "error_message": error_message,
                "created_at": datetime.now()
            })
    
    async def scrape_company_news_to_database(self, company_name: str, 
                                            ticker: str = None, 
                                            sector: str = None,
                                            days_back: int = 30) -> Dict:
        """Scrape news for a company and save everything to database"""
        
        start_time = datetime.now()
        
        try:
            logger.info(f"🚀 Starting database scraping for: {company_name}")
            
            # 1. Get or create company
            company_id = self.get_or_create_company(company_name, ticker, sector)
            
            # 2. Use existing scraper to get articles
            async with NewsScraperEngine() as scraper:
                articles = await scraper.search_company_news(company_name, days_back)
            
            # 3. Save articles to database
            saved_articles = []
            for article in articles:
                try:
                    article_id = self.save_article_to_database(article, company_id)
                    saved_articles.append(article_id)
                except Exception as e:
                    logger.error(f"❌ Failed to save article {article.title[:30]}: {e}")
            
            # 4. Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 5. Log the activity
            self.log_analysis_activity(
                company_id=company_id,
                search_query=f"news:{company_name}:last_{days_back}d",
                articles_found=len(articles),
                processing_time_ms=int(processing_time),
                status="completed"
            )
            
            result = {
                "company_id": company_id,
                "company_name": company_name,
                "articles_found": len(articles),
                "articles_saved": len(saved_articles),
                "processing_time_ms": int(processing_time),
                "status": "success"
            }
            
            logger.info(f"✅ Database scraping completed for {company_name}")
            logger.info(f"📊 Results: {len(saved_articles)} articles saved in {processing_time:.0f}ms")
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log error
            if 'company_id' in locals():
                self.log_analysis_activity(
                    company_id=company_id,
                    search_query=f"news:{company_name}:last_{days_back}d",
                    articles_found=0,
                    processing_time_ms=int(processing_time),
                    status="failed",
                    error_message=str(e)
                )
            
            logger.error(f"❌ Database scraping failed for {company_name}: {e}")
            
            return {
                "company_name": company_name,
                "articles_found": 0,
                "articles_saved": 0,
                "processing_time_ms": int(processing_time),
                "status": "error",
                "error": str(e)
            }
    
    async def scrape_multiple_companies(self, companies: List[Dict]) -> List[Dict]:
        """Scrape news for multiple companies"""
        
        results = []
        
        for company_info in companies:
            company_name = company_info.get("name")
            ticker = company_info.get("ticker")
            sector = company_info.get("sector")
            
            if not company_name:
                logger.warning("⚠️ Skipping company with no name")
                continue
                
            result = await self.scrape_company_news_to_database(
                company_name=company_name,
                ticker=ticker,
                sector=sector
            )
            
            results.append(result)
            
            # Small delay between companies to be respectful
            await asyncio.sleep(1)
        
        return results

# Test companies to scrape
SAMPLE_COMPANIES = [
    {"name": "Apple Inc.", "ticker": "AAPL", "sector": "Technology"},
    {"name": "Microsoft Corporation", "ticker": "MSFT", "sector": "Technology"},
    {"name": "Tesla Inc.", "ticker": "TSLA", "sector": "Automotive"},
    {"name": "Johnson & Johnson", "ticker": "JNJ", "sector": "Healthcare"},
    {"name": "JPMorgan Chase", "ticker": "JPM", "sector": "Financial"},
]

async def main():
    """Test the database-integrated scraper"""
    
    scraper = DatabaseIntegratedScraper()
    
    print("🌍 ESG Database Scraper - Testing Mode")
    print("=" * 50)
    
    # Test single company
    print("📰 Testing single company scraping...")
    result = await scraper.scrape_company_news_to_database(
        company_name="Apple Inc.",
        ticker="AAPL", 
        sector="Technology"
    )
    
    print(f"✅ Single company result: {result}")
    print()
    
    # Test multiple companies
    print("🏢 Testing multiple companies scraping...")
    results = await scraper.scrape_multiple_companies(SAMPLE_COMPANIES[:3])  # Just first 3
    
    print("📊 Multiple companies results:")
    for result in results:
        print(f"  - {result['company_name']}: {result['articles_saved']} articles saved")
    
    print("\n🎉 Database scraping test completed!")
    print("💡 Run 'python3 view_database.py' to see the results in your database")

if __name__ == "__main__":
    asyncio.run(main())
