"""
News scraping module for ESG Sentiment Scorer
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from config.settings import settings, NewsSource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Data class for news articles"""
    title: str
    content: str
    url: str
    source: str
    published_date: Optional[datetime] = None
    language: str = "en"
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class NewsScraperEngine:
    """Main news scraping engine"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': settings.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=settings.max_concurrent_requests)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def scrape_article(self, url: str, source_config: Dict) -> Optional[NewsArticle]:
        """Scrape a single article"""
        try:
            await asyncio.sleep(settings.scraping_delay)  # Rate limiting
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract title
                title_selector = source_config.get('selectors', {}).get('title', 'h1')
                title_element = soup.select_one(title_selector)
                title = title_element.get_text(strip=True) if title_element else "Unknown Title"
                
                # Extract content
                content_selector = source_config.get('selectors', {}).get('content', 'p')
                content_elements = soup.select(content_selector)
                content = ' '.join([elem.get_text(strip=True) for elem in content_elements])
                
                # Clean content
                content = self._clean_text(content)
                
                # Extract date (basic implementation)
                published_date = self._extract_date(soup, html)
                
                # Extract keywords
                keywords = self._extract_keywords(title, content)
                
                return NewsArticle(
                    title=title,
                    content=content,
                    url=url,
                    source=source_config.get('name', 'Unknown'),
                    published_date=published_date,
                    keywords=keywords
                )
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    async def search_company_news(self, company_name: str, days_back: int = 30) -> List[NewsArticle]:
        """Search for news articles about a specific company"""
        articles = []
        
        # TODO: Implement actual news search logic
        # This would involve:
        # 1. Using news APIs (NewsAPI, Alpha Vantage, etc.)
        # 2. Searching financial news websites
        # 3. Using Google News API or similar
        
        # Placeholder implementation
        logger.info(f"Searching for news about {company_name} from last {days_back} days")
        
        # Mock articles for demonstration
        mock_articles = [
            NewsArticle(
                title=f"{company_name} announces new sustainability initiative",
                content=f"In a major development, {company_name} has launched a comprehensive sustainability program aimed at reducing carbon emissions by 50% over the next decade. The initiative includes investments in renewable energy, sustainable supply chain practices, and environmental reporting transparency.",
                url="https://example.com/news/1",
                source="Reuters",
                published_date=datetime.now() - timedelta(days=1),
                keywords=["sustainability", "carbon emissions", "renewable energy"]
            ),
            NewsArticle(
                title=f"{company_name} reports strong quarterly earnings",
                content=f"{company_name} exceeded analyst expectations in its latest quarterly report, driven by strong performance across all business segments. The company also highlighted its commitment to ESG principles and social responsibility initiatives.",
                url="https://example.com/news/2",
                source="Bloomberg",
                published_date=datetime.now() - timedelta(days=3),
                keywords=["earnings", "financial performance", "ESG"]
            )
        ]
        
        return mock_articles
    
    async def scrape_multiple_sources(self, urls: List[str]) -> List[NewsArticle]:
        """Scrape multiple URLs concurrently"""
        tasks = []
        
        for url in urls:
            # Determine source configuration based on URL
            source_config = self._get_source_config(url)
            task = self.scrape_article(url, source_config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        articles = [result for result in results 
                   if isinstance(result, NewsArticle)]
        
        return articles
    
    def _get_source_config(self, url: str) -> Dict:
        """Get source configuration based on URL"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Match domain to known sources
        for source_key, source_config in NewsSource.SOURCES.items():
            if source_key in domain or any(keyword in domain for keyword in [source_key]):
                return source_config
        
        # Default configuration
        return {
            "name": "Unknown Source",
            "selectors": {
                "title": "h1, .title, [class*='title'], [class*='headline']",
                "content": "p, .content, [class*='content'], [class*='body']"
            }
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with analysis
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', '', text)
        
        return text.strip()
    
    def _extract_date(self, soup: BeautifulSoup, html: str) -> Optional[datetime]:
        """Extract publication date from article"""
        # Try common date selectors
        date_selectors = [
            'time[datetime]',
            '.date',
            '.publish-date',
            '[class*="date"]',
            '[class*="time"]'
        ]
        
        for selector in date_selectors:
            date_element = soup.select_one(selector)
            if date_element:
                # Try to extract date
                date_text = date_element.get('datetime') or date_element.get_text(strip=True)
                if date_text:
                    try:
                        # Simple date parsing - would need more sophisticated logic
                        return datetime.now()  # Placeholder
                    except:
                        continue
        
        return None
    
    def _extract_keywords(self, title: str, content: str) -> List[str]:
        """Extract keywords from title and content"""
        # Simple keyword extraction
        # TODO: Implement more sophisticated NLP-based keyword extraction
        
        text = f"{title} {content}".lower()
        
        # ESG-related keywords
        esg_keywords = []
        for category in ['environmental', 'social', 'governance']:
            category_config = getattr(NewsSource, category.upper(), {})
            keywords = category_config.get('keywords', [])
            
            for keyword in keywords:
                if keyword.lower() in text:
                    esg_keywords.append(keyword)
        
        return list(set(esg_keywords))


class NewsAPIIntegration:
    """Integration with news APIs"""
    
    def __init__(self):
        self.newsapi_key = settings.newsapi_key
    
    async def search_news(self, query: str, days_back: int = 30) -> List[NewsArticle]:
        """Search news using NewsAPI"""
        if not self.newsapi_key:
            logger.warning("NewsAPI key not configured")
            return []
        
        # TODO: Implement actual NewsAPI integration
        # This would involve making API calls to NewsAPI.org
        
        logger.info(f"Searching NewsAPI for: {query}")
        return []
    
    async def get_financial_news(self, company_ticker: str) -> List[NewsArticle]:
        """Get financial news for a specific ticker"""
        # TODO: Implement integration with financial news APIs
        # Alpha Vantage, IEX Cloud, etc.
        
        logger.info(f"Fetching financial news for: {company_ticker}")
        return []


# Usage example and testing
async def main():
    """Example usage"""
    async with NewsScraperEngine() as scraper:
        # Search for company news
        articles = await scraper.search_company_news("Apple Inc.")
        
        print(f"Found {len(articles)} articles:")
        for article in articles:
            print(f"- {article.title}")
            print(f"  Source: {article.source}")
            print(f"  Keywords: {article.keywords}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
