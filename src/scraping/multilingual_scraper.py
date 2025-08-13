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
    def search_and_scrape_articles(self, company: Dict, max_articles: int = 5) -> List[Dict]:
        """
        Search for articles mentioning the company and scrape their content.
        This is a simple implementation using BeautifulSoup and keyword search.
        """
        results = []
        company_name = company["name"]
        for source_key, source in self.sources.items():
            lang = source.get("language", "en")
            if lang not in self.supported_languages:
                continue
            base_url = source.get("base_url")
            if not base_url:
                continue
            try:
                resp = requests.get(base_url, timeout=10)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                # Find links containing the company name (simple keyword search)
                links = []
                for a in soup.find_all("a", href=True):
                    if company_name.lower() in a.get_text(strip=True).lower():
                        links.append(a["href"])
                # Limit to max_articles
                links = links[:max_articles]
                for link in links:
                    # Resolve relative URLs
                    if not link.startswith("http"):
                        link = base_url.rstrip("/") + "/" + link.lstrip("/")
                    article_html = self.fetch_article(link)
                    if article_html:
                        soup_article = BeautifulSoup(article_html, "html.parser")
                        title_tag = soup_article.find("title")
                        title = title_tag.get_text(strip=True) if title_tag else None
                        raw_text = self.clean_text(article_html)
                        translated_text = self.translate_text(raw_text, lang)
                        results.append({
                            "company": company_name,
                            "source": source["name"],
                            "language": lang,
                            "title": title,
                            "raw_text": raw_text,
                            "translated_text": translated_text,
                            "url": link
                        })
            except Exception as e:
                logger.error(f"Error scraping from {base_url}: {e}")
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
        # Truncate to 5000 characters for translation API
        max_len = 5000
        text = text[:max_len]
        # Map unsupported language codes to supported ones
        lang_map = {"zh": "zh-CN"}
        src_lang_mapped = lang_map.get(src_lang, src_lang)
        try:
            translated = GoogleTranslator(source=src_lang_mapped, target="en").translate(text)
            return translated
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    def scrape_company_news(self, company: Dict) -> List[Dict]:
        """Scrape news for a single company from all sources"""
        results = []
        for source_key, source in self.sources.items():
            # Example: Only process sources with supported language
            lang = source.get("language", "en")
            if lang not in self.supported_languages:
                continue
            # TODO: Implement actual scraping logic per source type (html/rss/blog)
            # For now, just mock a result
            article_url = source.get("base_url")
            html = self.fetch_article(article_url)
            if html:
                soup_article = BeautifulSoup(html, "html.parser")
                title_tag = soup_article.find("title")
                title = title_tag.get_text(strip=True) if title_tag else None
                raw_text = self.clean_text(html)
                translated_text = self.translate_text(raw_text, lang)
                results.append({
                    "company": company["name"],
                    "source": source["name"],
                    "language": lang,
                    "title": title,
                    "raw_text": raw_text,
                    "translated_text": translated_text,
                    "url": article_url
                })
        return results

# Example usage (to be replaced with actual pipeline)
if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from config.settings import NewsSource, Settings
    from config.companies import COMPANIES
    logging.basicConfig(level=logging.INFO)
    scraper = MultilingualScraper(NewsSource.SOURCES, Settings().SUPPORTED_LANGUAGES)
    from src.db.article_store import store_article
    for company in COMPANIES[:3]:
        articles = scraper.scrape_company_news(company)
        for article in articles:
            print(f"{article['company']} | {article['source']} | {article['language']}")
            print(f"Raw: {article['raw_text'][:100]}")
            print(f"Translated: {article['translated_text'][:100]}")
            print()
            store_article(article)
            print("Article stored in database.")
