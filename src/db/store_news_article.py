"""
Store news articles in the main NewsArticle table, linking each to its company by company_id.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.db.models import get_database_session, Company, NewsArticle, get_company_by_name

def store_news_article(article_dict):
    session = get_database_session()
    # Find company by name (case-insensitive)
    company = get_company_by_name(session, article_dict["company"])
    if not company:
        print(f"Company '{article_dict['company']}' not found. Skipping article.")
        session.close()
        return
    # Check for duplicate by URL
    existing = session.query(NewsArticle).filter_by(url=article_dict["url"]).first()
    if existing:
        print(f"Article with URL {article_dict['url']} already exists. Skipping insert.")
        session.close()
        return
    news_article = NewsArticle(
        title=article_dict["title"],
        content=article_dict.get("raw_text"),
        url=article_dict["url"],
        source=article_dict["source"],
        author=None,
        published_date=None,
        scraped_date=None,
        language=article_dict["language"],
        word_count=len(article_dict.get("raw_text", "").split()),
        raw_html=None,
        summary=None,
        sentiment_score=None,
        category=None,
        tags=None,
        is_analyzed=False,
        company_id=company.id
    )
    session.add(news_article)
    session.commit()
    print(f"Inserted article for company '{company.name}' with URL {news_article.url}")
    session.close()
