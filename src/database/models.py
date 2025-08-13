"""
SQLAlchemy ORM models for ESG Sentiment Scorer
These models match the PostgreSQL database schema exactly
"""
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, Boolean, Numeric, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid
from datetime import datetime
from typing import List, Optional

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import settings

# Create base class for models
Base = declarative_base()

class Company(Base):
    """Company model matching the companies table"""
    __tablename__ = 'companies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    ticker = Column(String(10))
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Integer)
    country = Column(String(100), default='USA')
    website = Column(String(200))
    description = Column(Text)
    employees = Column(Integer)
    founded_year = Column(Integer)
    headquarters = Column(String(200))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    news_articles = relationship("NewsArticle", back_populates="company")
    esg_analyses = relationship("ESGSentimentAnalysis", back_populates="company")
    esg_scores = relationship("CompanyESGScore", back_populates="company")
    analysis_logs = relationship("AnalysisLog", back_populates="company")
    
    def __repr__(self):
        return f"<Company(name='{self.name}', ticker='{self.ticker}')>"


class NewsArticle(Base):
    """News article model matching the news_articles table"""
    __tablename__ = 'news_articles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    url = Column(String(1000), nullable=False, unique=True)
    source = Column(String(100))
    author = Column(String(200))
    published_date = Column(DateTime)
    scraped_date = Column(DateTime, default=func.now())
    language = Column(String(10), default='en')
    word_count = Column(Integer)
    raw_html = Column(Text)
    summary = Column(Text)
    sentiment_score = Column(Numeric(3, 2))
    category = Column(String(50))
    tags = Column(ARRAY(Text))
    is_analyzed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Foreign keys
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    
    # Relationships
    company = relationship("Company", back_populates="news_articles")
    esg_analyses = relationship("ESGSentimentAnalysis", back_populates="article")
    
    def __repr__(self):
        return f"<NewsArticle(title='{self.title[:50]}...', source='{self.source}')>"


class ESGSentimentAnalysis(Base):
    """ESG sentiment analysis results matching the esg_sentiment_analysis table"""
    __tablename__ = 'esg_sentiment_analysis'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    overall_sentiment = Column(Numeric(3, 2))  # -1.00 to 1.00
    confidence_score = Column(Numeric(3, 2))   # 0.00 to 1.00
    environmental_score = Column(Numeric(3, 2))
    social_score = Column(Numeric(3, 2))
    governance_score = Column(Numeric(3, 2))
    environmental_sentiment = Column(Numeric(3, 2))
    social_sentiment = Column(Numeric(3, 2))
    governance_sentiment = Column(Numeric(3, 2))
    key_themes = Column(ARRAY(Text))
    risk_indicators = Column(ARRAY(Text))
    model_version = Column(String(50))
    article_summary = Column(Text)
    processing_metadata = Column(JSONB)
    analyzed_at = Column(DateTime, default=func.now())
    
    # Foreign keys
    article_id = Column(UUID(as_uuid=True), ForeignKey('news_articles.id', ondelete='CASCADE'))
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    
    # Relationships
    article = relationship("NewsArticle", back_populates="esg_analyses")
    company = relationship("Company", back_populates="esg_analyses")
    
    def __repr__(self):
        return f"<ESGSentimentAnalysis(overall_sentiment={self.overall_sentiment}, confidence={self.confidence_score})>"


class ESGKeyword(Base):
    """ESG keywords for classification"""
    __tablename__ = 'esg_keywords'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keyword = Column(String(100), nullable=False)
    category = Column(String(20), nullable=False)  # 'environmental', 'social', 'governance'
    weight = Column(Numeric(3, 2), default=1.00)
    language = Column(String(10), default='en')
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<ESGKeyword(keyword='{self.keyword}', category='{self.category}')>"


class NewsSource(Base):
    """News source configuration"""
    __tablename__ = 'news_sources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    url = Column(String(200), nullable=False, unique=True)
    country = Column(String(100))
    language = Column(String(10), default='en')
    reliability_score = Column(Numeric(3, 2), default=0.80)
    update_frequency = Column(Integer, default=60)  # minutes
    selectors = Column(JSONB)  # CSS selectors for scraping
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<NewsSource(name='{self.name}', reliability={self.reliability_score})>"


class CompanyESGScore(Base):
    """Aggregated ESG scores over time"""
    __tablename__ = 'company_esg_scores'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, nullable=False)
    environmental_score = Column(Numeric(3, 2))
    social_score = Column(Numeric(3, 2))
    governance_score = Column(Numeric(3, 2))
    overall_score = Column(Numeric(3, 2))
    confidence_score = Column(Numeric(3, 2))
    articles_analyzed = Column(Integer, default=0)
    sentiment_trend = Column(Numeric(3, 2))  # Week-over-week change
    risk_level = Column(String(20))  # 'low', 'medium', 'high'
    created_at = Column(DateTime, default=func.now())
    
    # Foreign keys
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    
    # Relationships
    company = relationship("Company", back_populates="esg_scores")
    
    def __repr__(self):
        return f"<CompanyESGScore(overall_score={self.overall_score}, date={self.date})>"


class AnalysisLog(Base):
    """Analysis processing logs"""
    __tablename__ = 'analysis_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_query = Column(String(200))
    articles_found = Column(Integer, default=0)
    articles_analyzed = Column(Integer, default=0)
    processing_time_ms = Column(Integer)
    error_message = Column(Text)
    status = Column(String(20), default='pending')  # 'pending', 'completed', 'failed'
    created_at = Column(DateTime, default=func.now())
    
    # Foreign keys
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    
    # Relationships
    company = relationship("Company", back_populates="analysis_logs")
    
    def __repr__(self):
        return f"<AnalysisLog(status='{self.status}', articles_found={self.articles_found})>"


# Database connection and session management
class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.database_url
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)


# Utility functions
def get_database_session():
    """Get database session for use in other modules"""
    db_manager = DatabaseManager()
    return db_manager.get_session()

def get_company_by_ticker(session, ticker: str) -> Optional[Company]:
    """Get company by ticker symbol"""
    return session.query(Company).filter(Company.ticker == ticker).first()

def get_company_by_name(session, name: str) -> Optional[Company]:
    """Get company by name (case insensitive)"""
    return session.query(Company).filter(Company.name.ilike(f"%{name}%")).first()

def get_recent_articles(session, company_id: str, days_back: int = 30) -> List[NewsArticle]:
    """Get recent articles for a company"""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    return session.query(NewsArticle).filter(
        NewsArticle.company_id == company_id,
        NewsArticle.scraped_date >= cutoff_date
    ).order_by(NewsArticle.scraped_date.desc()).all()

def get_latest_esg_analysis(session, company_id: str) -> Optional[ESGSentimentAnalysis]:
    """Get latest ESG analysis for a company"""
    return session.query(ESGSentimentAnalysis).filter(
        ESGSentimentAnalysis.company_id == company_id
    ).order_by(ESGSentimentAnalysis.analyzed_at.desc()).first()


# Usage example
if __name__ == "__main__":
    # Test the models
    db_manager = DatabaseManager()
    
    # Create session
    session = db_manager.get_session()
    
    try:
        # Test query
        companies = session.query(Company).limit(5).all()
        print(f"Found {len(companies)} companies:")
        for company in companies:
            print(f"  - {company.name} ({company.ticker})")
        
        # Test articles
        articles = session.query(NewsArticle).limit(3).all()
        print(f"\nFound {len(articles)} articles:")
        for article in articles:
            print(f"  - {article.title[:50]}... from {article.source}")
            
    finally:
        session.close()
    
    print("✅ ORM models working correctly!")
