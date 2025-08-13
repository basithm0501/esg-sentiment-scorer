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
    Each source has:
      - name: str
      - base_url: str
      - type: "html" | "rss" | "blog"
      - region: str
      - language: ISO 2-letter (e.g., "en", "fr")
      - list_selectors: how to extract article links from listing pages (ignored for rss)
      - article_selectors: how to extract fields from article pages (ignored for rss)
      - link_filters: optional substrings/regex to keep relevant links
      - rss_feeds: list[str], if type == "rss"
      - notes: optional
    """

    DEFAULT_ARTICLE_SELECTORS = {
        # Multiple fallbacks for robustness
        "title": [
            "h1",
            "header h1",
            "article h1",
            "[data-testid='headline']",
            "meta[property='og:title']::attr(content)"
        ],
        "content": [
            "article p",
            "article .article__content p",
            "[itemprop='articleBody'] p",
            ".story-content p",
            ".article-body p",
            ".c-article-body p",
            ".body__inner-container p",
            ".article__body p"
        ],
        "date": [
            "time[datetime]::attr(datetime)",
            "meta[property='article:published_time']::attr(content)",
            "meta[name='pubdate']::attr(content)",
            "meta[name='date']::attr(content)"
        ],
        "author": [
            "[rel='author']",
            ".byline a",
            ".byline span",
            "[itemprop='author']",
            "meta[name='author']::attr(content)"
        ]
    }

    SOURCES = {
        # ---------------------------
        # Major financial news (HTML)
        # ---------------------------
        "reuters": {
            "name": "Reuters",
            "base_url": "https://www.reuters.com",
            "type": "html",
            "region": "Global",
            "language": "en",
            "list_selectors": {
                # Use topic/market pages; adjust start URLs in your spider
                "article_link": [
                    "a[href^='/markets/']::attr(href)",
                    "a[href^='/business/']::attr(href)",
                    "a[href^='/world/']::attr(href)"
                ]
            },
            "article_selectors": {
                "title": [
                    "h1[data-testid='Heading']",
                    "h1",
                    "meta[property='og:title']::attr(content)"
                ],
                "content": [
                    "article p",
                    "div[data-testid='Body'] p",
                    ".article-body__content p"
                ],
                "date": [
                    "time[datetime]::attr(datetime)",
                    "meta[property='article:published_time']::attr(content)"
                ],
                "author": [
                    "[data-testid='Byline'] a",
                    ".byline__names a",
                    "meta[name='author']::attr(content)"
                ]
            },
            "link_filters": {
                "allow_regex": [r"^/markets/.*", r"^/business/.*", r"^/world/.*"],
                "deny_regex": [r"/pictures/", r"/graphics/", r"/video/"]
            },
            "notes": "Reuters markup shifts occasionally; keep multiple fallbacks."
        },

        "bloomberg": {
            "name": "Bloomberg",
            "base_url": "https://www.bloomberg.com",
            "type": "html",
            "region": "Global",
            "language": "en",
            "list_selectors": {
                "article_link": [
                    "a[href^='/news/articles/']::attr(href)",
                    "a[href*='/news/articles/']::attr(href)"
                ]
            },
            "article_selectors": {
                "title": [
                    "h1",
                    "meta[property='og:title']::attr(content)"
                ],
                "content": [
                    "article p",
                    "[data-component='article-body'] p",
                    ".body-content p"
                ],
                "date": [
                    "time[datetime]::attr(datetime)",
                    "meta[property='article:published_time']::attr(content)"
                ],
                "author": [
                    "a[data-component='byline-name']",
                    ".byline__authors a",
                    "meta[name='author']::attr(content)"
                ]
            },
            "link_filters": {
                "allow_regex": [r"^/news/articles/.*"],
                "deny_regex": [r"/video/", r"/live/"]
            },
            "notes": "Some stories are paywalled; handle 403s and consider RSS if available."
        },

        "financial_times": {
            "name": "Financial Times",
            "base_url": "https://www.ft.com",
            "type": "html",
            "region": "Europe",
            "language": "en",
            "list_selectors": {
                "article_link": [
                    "a[href^='/content/']::attr(href)"
                ]
            },
            "article_selectors": {
                "title": [
                    "h1",
                    "meta[property='og:title']::attr(content)"
                ],
                "content": [
                    "article p",
                    ".article__content-body p",
                    "[data-component='article-body'] p"
                ],
                "date": [
                    "time[datetime]::attr(datetime)",
                    "meta[property='article:published_time']::attr(content)"
                ],
                "author": [
                    "a[href*='/author/']",
                    ".o-typography-author a",
                    "meta[name='author']::attr(content)"
                ]
            },
            "link_filters": {
                "allow_regex": [r"^/content/.*"],
                "deny_regex": []
            },
            "notes": "Paywall likely; support graceful degradation."
        },

        # -----------
        # RSS sources
        # -----------
        "rss_marketwatch": {
            "name": "MarketWatch RSS",
            "base_url": "https://www.marketwatch.com",
            "type": "rss",
            "region": "Americas",
            "language": "en",
            "rss_feeds": [
                "https://www.marketwatch.com/feeds/topstories",
                "https://www.marketwatch.com/feeds/latestnews"
            ],
            "notes": "Use feedparser; fetch article page for full text if summary-only."
        },

        "rss_yahoo_finance": {
            "name": "Yahoo Finance RSS",
            "base_url": "https://finance.yahoo.com",
            "type": "rss",
            "region": "Americas",
            "language": "en",
            "rss_feeds": [
                "https://finance.yahoo.com/news/rssindex"
            ],
            "notes": "Some items link to partner sites; follow redirects before scraping."
        },

        # -------------------
        # Financial blogs/web
        # -------------------
        "seeking_alpha": {
            "name": "Seeking Alpha",
            "base_url": "https://seekingalpha.com",
            "type": "blog",
            "region": "Americas",
            "language": "en",
            "list_selectors": {
                "article_link": [
                    "a[href^='/news/']::attr(href)",
                    "a[href^='/market-news/']::attr(href)"
                ]
            },
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)"],
                "content": ["article p", ".sa-art article p", ".content p"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)"],
                "author": [".author-name", ".byline a", "meta[name='author']::attr(content)"]
            },
            "link_filters": {
                "allow_regex": [r"^/news/.*", r"^/market-news/.*"],
                "deny_regex": [r"/symbol/", r"/etfs/"]
            },
            "notes": "Some content behind login; scrape responsibly."
        },

        "zerohedge": {
            "name": "ZeroHedge",
            "base_url": "https://www.zerohedge.com",
            "type": "blog",
            "region": "Global",
            "language": "en",
            "list_selectors": {
                "article_link": [
                    "a[href^='/markets/']::attr(href)",
                    "a[href^='/geopolitical/']::attr(href)",
                    "a[href^='/economics/']::attr(href)"
                ]
            },
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)"],
                "content": ["article p", ".article-body p", ".field-item p"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)"],
                "author": [".author a", "meta[name='author']::attr(content)"]
            },
            "link_filters": {
                "allow_regex": [r"^/(markets|geopolitical|economics)/.*"],
                "deny_regex": [r"/video/", r"/tags/"]
            }
        },

        # -----------------------
        # Regional / non-English
        # -----------------------
        "china_daily": {
            "name": "China Daily (Business)",
            "base_url": "https://www.chinadaily.com.cn/business",
            "type": "html",
            "region": "Asia",
            "language": "zh",
            "list_selectors": {
                "article_link": [
                    "a[href*='/a/'][href$='.html']::attr(href)",
                    ".bus_list a::attr(href)",
                    "a[href^='https://www.chinadaily.com.cn/a/']::attr(href)"
                ]
            },
            "article_selectors": {
                "title": ["h1", ".main_art h1", "meta[property='og:title']::attr(content)"],
                "content": ["article p", ".main_art p", ".article-content p"],
                "date": ["time[datetime]::attr(datetime)", ".info span::text", "meta[property='article:published_time']::attr(content)"],
                "author": [".editor", ".reporter", "meta[name='author']::attr(content)"]
            },
            "link_filters": {
                "allow_regex": [r"/a/\d{8}/\d+\.htm", r"/a/\d{4}-\d{2}/\d{2}/.*\.html"],
                "deny_regex": [r"/photo/", r"/video/"]
            }
        },

        "le_figaro": {
            "name": "Le Figaro Économie",
            "base_url": "https://www.lefigaro.fr/economie/",
            "type": "html",
            "region": "Europe",
            "language": "fr",
            "list_selectors": {
                "article_link": [
                    "a[href^='https://www.lefigaro.fr/economie/']::attr(href)",
                    "a[href*='/economie/']::attr(href)"
                ]
            },
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)"],
                "content": ["article p", ".article-body p", ".fig-paragraph"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)"],
                "author": [".fig-author a", "meta[name='author']::attr(content)"]
            },
            "link_filters": {
                "allow_regex": [r"^https://www\.lefigaro\.fr/economie/.*"],
                "deny_regex": [r"/podcasts?/", r"/videos?/"]
            }
        },

        "el_pais": {
            "name": "El País Economía",
            "base_url": "https://elpais.com/economia/",
            "type": "html",
            "region": "Europe",
            "language": "es",
            "list_selectors": {
                "article_link": [
                    "a[href^='https://elpais.com/economia/']::attr(href)",
                    "a[href*='/economia/']::attr(href)"
                ]
            },
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)"],
                "content": ["article p", ".a_c p", ".article_body p"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)"],
                "author": [".a_md_a a", ".byline a", "meta[name='author']::attr(content)"]
            },
            "link_filters": {
                "allow_regex": [r"^https://elpais\.com/economia/.*"],
                "deny_regex": [r"/videos?/", r"/album/"]
            }
        },

        "arab_news": {
            "name": "Arab News — Business",
            "base_url": "https://www.arabnews.com/business",
            "type": "html",
            "region": "Middle East",
            "language": "ar",
            "list_selectors": {
                "article_link": [
                    "a[href^='/node/']::attr(href)",
                    "a[href*='/business']::attr(href)"
                ]
            },
            "article_selectors": {
                "title": ["h1", "meta[property='og:title']::attr(content)"],
                "content": ["article p", ".field--name-body p", ".content p"],
                "date": ["time[datetime]::attr(datetime)", "meta[property='article:published_time']::attr(content)"],
                "author": [".author a", "meta[name='author']::attr(content)"]
            },
            "link_filters": {
                "allow_regex": [r"^/node/\d+$"],
                "deny_regex": [r"/tags/", r"/category/"]
            }
        },
    }



# Global settings instance
settings = Settings()
