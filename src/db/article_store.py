"""
PostgreSQL storage for scraped articles using SQLAlchemy ORM
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from config.settings import Settings
# Use password from Settings
settings = Settings()
db_user = "esg_user"
db_host = "localhost"
db_port = "5432"
db_name = "esg_sentiment_db"
db_password = settings.esg_db_password
DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Article(Base):
    __tablename__ = "news_articles"
    id = Column(String(36), primary_key=True, index=True)  # UUID as string for compatibility
    company_id = Column(String(36), index=True)  # Foreign key to companies.id
    source = Column(String(128), index=True)
    language = Column(String(8), index=True)
    title = Column(Text, nullable=False)
    content = Column(Text)
    url = Column(String(512))

# Create table if not exists
Base.metadata.create_all(bind=engine)

def store_article(article_dict):
    """Insert a single article dict into the database"""
    session = SessionLocal()
    # Check if article with this URL already exists
    existing = session.query(Article).filter_by(url=article_dict["url"]).first()
    if existing:
        session.close()
        print(f"Article with URL {article_dict['url']} already exists. Skipping insert.")
        return
    article = Article(
        company=article_dict["company"],
        source=article_dict["source"],
        language=article_dict["language"],
        title=article_dict["title"],
        raw_text=article_dict["raw_text"],
        translated_text=article_dict["translated_text"],
        url=article_dict["url"]
    )
    session.add(article)
    session.commit()
    session.close()

# Example usage:
if __name__ == "__main__":
    # Example article
    sample = {
        "company": "Apple Inc.",
        "source": "Reuters",
        "language": "en",
        "raw_text": "Apple launches new product...",
        "translated_text": "Apple launches new product...",
        "url": "https://www.reuters.com/article/apple-news"
    }
    store_article(sample)
    print("Sample article stored.")
