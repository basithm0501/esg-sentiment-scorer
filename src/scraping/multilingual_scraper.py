"""
Multilingual News Scraper for ESG Sentiment Scorer
- Scrapes news headlines and articles for target companies
- Cleans and normalizes text
- Translates non-English articles to English
- Stores raw and translated data
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import logging

# Optional: Use googletrans or deep-translator for translation
try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

logger = logging.getLogger(__name__)

class MultilingualScraper:
    def search_and_scrape_articles(self, company: Dict, max_articles: int = 25, days_back: int = 180) -> List[Dict]:
        """
        Search for articles mentioning the company and scrape their content.
        Implements partial and fuzzy matching for company names.
        """
        import difflib
        results = []
        company_name = company["name"]
        # Use first word and last word for partial matching
        partial_names = set()
        words = company_name.split()
        if len(words) > 1:
            partial_names.add(words[0])
            partial_names.add(words[-1])
        partial_names.add(company_name)
        # Add ticker if available
        if "ticker" in company:
            partial_names.add(company["ticker"])
        logger.info(f"\n==== Scraping for company: {company_name} ====")
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days_back)
        for source_key, source in self.sources.items():
            lang = source.get("language", "en")
            logger.info(f"Source: {source.get('name', source_key)} | Language: {lang}")
            if lang not in self.supported_languages:
                logger.info(f"Skipping unsupported language: {lang}")
                continue
            base_url = source.get("base_url")
            if not base_url:
                logger.info("No base_url for source, skipping.")
                continue
            try:
                resp = requests.get(base_url, timeout=10)
                if resp.status_code != 200:
                    logger.info(f"Failed to fetch {base_url} (status {resp.status_code})")
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                links = []
                for a in soup.find_all("a", href=True):
                    text = a.get_text(strip=True).lower()
                    # Partial match
                    if any(pn.lower() in text for pn in partial_names):
                        links.append(a["href"])
                        continue
                    # Fuzzy match
                    match = difflib.get_close_matches(company_name.lower(), [text], n=1, cutoff=0.65)
                    if match:
                        links.append(a["href"])
                logger.info(f"Found {len(links)} links for company '{company_name}' in source '{source.get('name', source_key)}'")
                links = links[:max_articles]
                for link in links:
                    if not link.startswith("http"):
                        link = base_url.rstrip("/") + "/" + link.lstrip("/")
                    logger.info(f"Scraping article link: {link}")
                    article_html = self.fetch_article(link)
                    if article_html:
                        soup_article = BeautifulSoup(article_html, "html.parser")
                        title_tag = soup_article.find("title")
                        title = title_tag.get_text(strip=True) if title_tag else None
                        # Try to extract publication date from meta tags
                        pub_date = None
                        meta_date = soup_article.find("meta", attrs={"property": "article:published_time"})
                        if meta_date and meta_date.get("content"):
                            try:
                                pub_date = datetime.fromisoformat(meta_date["content"].replace("Z", ""))
                            except Exception:
                                pub_date = None
                        # Fallback: look for time tag
                        if not pub_date:
                            time_tag = soup_article.find("time")
                            if time_tag and time_tag.get("datetime"):
                                try:
                                    pub_date = datetime.fromisoformat(time_tag["datetime"].replace("Z", ""))
                                except Exception:
                                    pub_date = None
                        # If no date found, include article; if date found, filter by cutoff
                        if pub_date and pub_date < cutoff_date:
                            logger.info(f"Skipping article older than {days_back} days: {title}")
                            continue
                        raw_text = self.clean_text(article_html)
                        translated_text = self.translate_text(raw_text, lang)
                        logger.info(f"Scraped article: {title}")
                        results.append({
                            "company": company_name,
                            "source": source["name"],
                            "language": lang,
                            "title": title,
                            "raw_text": raw_text,
                            "translated_text": translated_text,
                            "url": link,
                            "published_date": pub_date.isoformat() if pub_date else None
                        })
            except Exception as e:
                logger.error(f"Error scraping from {base_url}: {e}")
        logger.info(f"Total articles scraped for {company_name}: {len(results)}\n")
        return results
    def __init__(self, sources: Dict, supported_languages: List[str]):
        self.sources = sources
        self.supported_languages = supported_languages

    def fetch_article(self, url: str) -> Optional[str]:
        """Fetch raw HTML from a URL"""
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
        return None

    def clean_text(self, html: str) -> str:
        """Remove HTML tags, scripts, ads, and normalize whitespace"""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "aside", "footer", "nav"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return text

    def translate_text(self, text: str, src_lang: str) -> str:
        """Translate text to English if not already English"""
        if src_lang == "en" or not GoogleTranslator:
            return text
        # Always truncate to 5000 characters for translation API
        MAX_TRANSLATE_CHARS = 5000
        if len(text) > MAX_TRANSLATE_CHARS:
            text = text[:MAX_TRANSLATE_CHARS]
        # Map unsupported language codes to supported ones
        lang_map = {"zh": "zh-CN"}
        src_lang_mapped = lang_map.get(src_lang, src_lang)
        try:
            translated = GoogleTranslator(source=src_lang_mapped, target="en").translate(text)
            return translated
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    def scrape_company_news(self, company: Dict, max_articles: int = 5, days_back: int = 180) -> List[Dict]:
        """Scrape news for a single company using keyword search on each source, filtering by date."""
        return self.search_and_scrape_articles(company, max_articles=max_articles, days_back=days_back)

# Example usage (to be replaced with actual pipeline)
if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from config.settings import NewsSource, Settings
    from config.companies import COMPANIES
    logging.basicConfig(level=logging.INFO)
    # Use all configured sources and supported languages
    print("Active sources for scraping:")
    for src in NewsSource.SOURCES.values():
        print(f"- {src['name']} ({src['type']}) : {src['base_url']} | Language: {src.get('language')}")
    scraper = MultilingualScraper(NewsSource.SOURCES, Settings().SUPPORTED_LANGUAGES)
    from src.db.store_news_article import store_news_article
    for company in COMPANIES:
        articles = scraper.scrape_company_news(company, days_back=180)
        for article in articles:
            print(f"{article['company']} | {article['source']} | {article['language']}")
            print(f"Raw: {article['raw_text'][:100]}")
            print(f"Translated: {article['translated_text'][:100]}")
            print()
            store_news_article(article)
            print("Article stored in NewsArticle table.")
