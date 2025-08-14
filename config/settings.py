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
    esg_db_password: str = "esg_password"
    
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

    # Supported languages for news and analysis
    SUPPORTED_LANGUAGES: List[str] = [
        "en",   # English
        "fr",   # French
        "es",   # Spanish
        "ar",   # Arabic
        "zh"    # Chinese
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ESGCategories:
    """ESG category definitions and keywords"""
    
    # ESG Scoring Criteria & Taxonomy
    # Each pillar contains sub-factors with associated keywords for sentiment tagging
    ENVIRONMENTAL = {
        "name": "Environmental",
        "sub_factors": {
            "carbon_emissions": ["carbon emissions", "carbon footprint", "CO2", "greenhouse gas", "emissions reduction"],
            "renewable_energy": ["renewable energy", "solar", "wind", "hydro", "clean energy", "green technology"],
            "pollution": ["pollution", "air quality", "water pollution", "soil contamination", "waste", "toxic"],
            "waste_management": ["waste management", "recycling", "circular economy", "landfill", "waste reduction"],
            "water_usage": ["water usage", "water conservation", "water efficiency", "drought", "water scarcity"],
            "biodiversity": ["biodiversity", "ecosystem", "habitat", "species protection", "deforestation"],
            "compliance": ["environmental compliance", "regulation", "ESG reporting", "environmental law"],
        }
    }
    
    SOCIAL = {
        "name": "Social",
        "sub_factors": {
            "labor_practices": ["labor practices", "fair wages", "working conditions", "collective bargaining", "child labor"],
            "human_rights": ["human rights", "forced labor", "discrimination", "freedom of association", "civil rights"],
            "diversity_inclusion": ["diversity", "inclusion", "gender equality", "minority representation", "equal opportunity"],
            "community_relations": ["community relations", "philanthropy", "volunteering", "local impact", "stakeholder engagement"],
            "product_safety": ["product safety", "quality control", "recall", "customer safety"],
            "data_privacy": ["customer privacy", "data privacy", "GDPR", "data breach", "privacy policy"],
            "supply_chain": ["supply chain", "supplier standards", "responsible sourcing", "traceability"],
            "workplace_safety": ["workplace safety", "occupational health", "injury", "safety training"],
            "social_responsibility": ["social responsibility", "social impact", "community investment"],
        }
    }
    
    GOVERNANCE = {
        "name": "Governance",
        "sub_factors": {
            "board_independence": ["board independence", "board diversity", "board structure", "independent directors"],
            "executive_compensation": ["executive compensation", "CEO pay", "pay ratio", "bonus", "incentive"],
            "shareholder_rights": ["shareholder rights", "proxy", "voting", "shareholder engagement"],
            "anti_corruption": ["anti-corruption", "bribery", "fraud", "whistleblower", "ethics"],
            "transparency": ["transparency", "disclosure", "reporting", "audit", "accountability"],
            "risk_management": ["risk management", "internal controls", "compliance", "regulatory risk"],
            "corporate_governance": ["corporate governance", "governance framework", "governance policy"],
        }
    }
    
    @classmethod
    def get_all_categories(cls) -> Dict:
        return {
            "environmental": cls.ENVIRONMENTAL,
            "social": cls.SOCIAL,
            "governance": cls.GOVERNANCE
        }

    @classmethod
    def get_all_keywords(cls) -> Dict[str, List[str]]:
        """Return a flat mapping of all sub-factor keywords for each pillar"""
        result = {}
        for pillar in [cls.ENVIRONMENTAL, cls.SOCIAL, cls.GOVERNANCE]:
            for sub, keywords in pillar["sub_factors"].items():
                result[sub] = keywords
        return result

# --- ESG Scoring Weights & Calculation ---
# Pillar weights (can be customized in Settings):
#   Environmental: settings.environmental_weight
#   Social: settings.social_weight
#   Governance: settings.governance_weight
#
# Sub-factor weights: currently equal within each pillar, can be customized
#
# Scoring logic:
#   - Tag text with ESG sub-factor keywords
#   - Aggregate sentiment scores for each sub-factor
#   - Calculate weighted average for each pillar
#   - Final ESG score = weighted sum of pillar scores
    
    @classmethod
    def get_all_categories(cls) -> Dict:
        return {
            "environmental": cls.ENVIRONMENTAL,
            "social": cls.SOCIAL,
            "governance": cls.GOVERNANCE
        }


class NewsSource:
    """
    News source configurations (schema-consistent).
    """
    SOURCES = {
        # French sources

        # Spanish sources
        "expansion": {
            "name": "Expansión",
            "base_url": "https://e00-expansion.uecdn.es/rss/portada.xml",
            "type": "rss",
            "region": "Europe",
            "language": "es",
            "rss_feeds": ["https://e00-expansion.uecdn.es/rss/portada.xml"],
            "notes": "Spanish business news, RSS."
        },
        # Arabic sources
        "skynews_arabia_economy": {
            "name": "Sky News Arabia Economy",
            "base_url": "https://www.skynewsarabia.com/rss/business",
            "type": "rss",
            "region": "Middle East",
            "language": "ar",
            "rss_feeds": ["https://www.skynewsarabia.com/rss/business"],
            "notes": "Arabic business news, RSS."
        },
        "asharq_business": {
            "name": "Asharq Business",
            "base_url": "https://www.asharqbusiness.com/",
            "type": "html",
            "region": "Middle East",
            "language": "ar",
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)", "meta[name='title']::attr(content)"],
                "content": ["article p", ".article-content p", ".main-content p"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)", "meta[name='date']::attr(content)"],
                "author": [".author a", "meta[name='author']::attr(content)"]
            },
            "notes": "Arabic finance news, HTML."
        },
        # Chinese sources
        "ce_daily": {
            "name": "经济日报 (Economic Daily)",
            "base_url": "http://www.ce.cn/",
            "type": "html",
            "region": "Asia",
            "language": "zh",
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)", "meta[name='title']::attr(content)"],
                "content": ["article p", ".article-content p", ".main-content p"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)", "meta[name='date']::attr(content)"],
                "author": [".author a", "meta[name='author']::attr(content)"]
            },
            "notes": "Chinese economy news, HTML."
        },
        "sina_finance": {
            "name": "新浪财经 (Sina Finance)",
            "base_url": "https://finance.sina.com.cn/",
            "type": "html",
            "region": "Asia",
            "language": "zh",
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)", "meta[name='title']::attr(content)"],
                "content": ["article p", ".article-content p", ".main-content p"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)", "meta[name='date']::attr(content)"],
                "author": [".author a", "meta[name='author']::attr(content)"]
            },
            "notes": "Chinese markets news, HTML."
        },
        # English sources
        "investing_com_esg": {
            "name": "Investing.com ESG News",
            "base_url": "https://www.investing.com/rss/news_25.rss",
            "type": "rss",
            "region": "Global",
            "language": "en",
            "rss_feeds": ["https://www.investing.com/rss/news_25.rss"],
            "notes": "ESG and finance news, open RSS."
        },
        "motley_fool_investing": {
            "name": "The Motley Fool Investing News",
            "base_url": "https://www.fool.com/investing-news/",
            "type": "html",
            "region": "Global",
            "language": "en",
            "list_selectors": {"article_link": ["a[href*='/investing-news/']::attr(href)"]},
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)"],
                "content": ["article p", ".article-content p"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)"],
                "author": [".author a", "meta[name='author']::attr(content)"]
            },
            "notes": "Easy HTML, no hard blocking."
        },
        "benzinga_news": {
            "name": "Benzinga News",
            "base_url": "https://www.benzinga.com/news",
            "type": "html",
            "region": "Global",
            "language": "en",
            "list_selectors": {"article_link": ["a[href*='/news/']::attr(href)"]},
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)"],
                "content": ["article p", ".article-content p"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)"],
                "author": [".author a", "meta[name='author']::attr(content)"]
            },
            "notes": "Finance focus, high volume."
        },
        "prnewswire_esg": {
            "name": "PR Newswire ESG",
            "base_url": "https://www.prnewswire.com/rss/",
            "type": "rss",
            "region": "Global",
            "language": "en",
            "rss_feeds": ["https://www.prnewswire.com/rss/"],
            "notes": "ESG press releases, open RSS."
        },
        "esg_today": {
            "name": "ESG Today",
            "base_url": "https://www.esgtoday.com",
            "type": "html",
            "region": "Global",
            "language": "en",
            "list_selectors": {"article_link": ["a[href*='/news/']::attr(href)"]},
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)"],
                "content": ["article p", ".post-content p"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)"],
                "author": [".author a", "meta[name='author']::attr(content)"]
            },
            "notes": "ESG-specific industry news."
        }
    }

# Global settings instance
settings = Settings()
