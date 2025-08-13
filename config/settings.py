"""
Configuration settings for ESG Sentiment Scorer
"""
from pydantic_settings import BaseSettings
from typing import List, Dict
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    openai_api_key: str = ""
    mistral_api_key: str = ""
    newsapi_key: str = ""
    alpha_vantage_key: str = ""
    
    # Vector Database
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-west1-gcp-free"
    pinecone_index_name: str = "esg-sentiment-index"
    
    # Database
    database_url: str = "postgresql://username:password@localhost:5432/esg_sentiment_db"
    redis_url: str = "redis://localhost:6379"
    
    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Dashboard
    streamlit_host: str = "0.0.0.0"
    streamlit_port: int = 8501
    
    # Scraping
    max_concurrent_requests: int = 10
    scraping_delay: float = 1.0
    user_agent: str = "ESG-Sentiment-Scorer/1.0"
    
    # ESG Weights
    environmental_weight: float = 0.33
    social_weight: float = 0.33
    governance_weight: float = 0.34
    
    # Models
    default_llm_model: str = "gpt-3.5-turbo"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_token_length: int = 4096
    
    # Paths
    raw_data_path: str = "./data/raw"
    processed_data_path: str = "./data/processed"
    models_path: str = "./models"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ESGCategories:
    """ESG category definitions and keywords"""
    
    ENVIRONMENTAL = {
        "name": "Environmental",
        "keywords": [
            "climate change", "carbon emissions", "greenhouse gas",
            "renewable energy", "sustainability", "pollution",
            "waste management", "water usage", "biodiversity",
            "environmental compliance", "green technology"
        ]
    }
    
    SOCIAL = {
        "name": "Social", 
        "keywords": [
            "labor practices", "human rights", "employee satisfaction",
            "diversity", "inclusion", "community relations",
            "product safety", "customer privacy", "supply chain",
            "workplace safety", "social responsibility"
        ]
    }
    
    GOVERNANCE = {
        "name": "Governance",
        "keywords": [
            "board independence", "executive compensation", "shareholder rights",
            "anti-corruption", "transparency", "audit", "risk management",
            "corporate governance", "compliance", "ethics", "accountability"
        ]
    }
    
    @classmethod
    def get_all_categories(cls) -> Dict:
        return {
            "environmental": cls.ENVIRONMENTAL,
            "social": cls.SOCIAL,
            "governance": cls.GOVERNANCE
        }


class NewsSource:
    """News source configurations"""
    
    SOURCES = {
        "reuters": {
            "name": "Reuters",
            "url": "https://www.reuters.com",
            "selectors": {
                "article": ".StandardArticleBody_container",
                "title": ".ArticleHeader_headline",
                "content": ".StandardArticleBody_body"
            }
        },
        "bloomberg": {
            "name": "Bloomberg",
            "url": "https://www.bloomberg.com",
            "selectors": {
                "article": ".article-body",
                "title": ".lede-text-v2__hed",
                "content": ".body-content"
            }
        },
        "financial_times": {
            "name": "Financial Times",
            "url": "https://www.ft.com",
            "selectors": {
                "article": ".article-body",
                "title": ".article-title",
                "content": ".article-body__content"
            }
        }
    }


# Global settings instance
settings = Settings()
