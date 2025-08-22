# 🌍 AI-Powered ESG Sentiment Scorer for Investment

> **Tagline**: A system that scrapes global news, rates companies by ESG (Environmental, Social, Governance) factors using NLP + LLMs, and visualizes ESG investment risks.

## 🔥 Why This Project Stands Out

- **Targets the ESG investment trend** - Hot topic in investment firms and hedge funds
- **Massive multilingual scraping** - Global news coverage with transformer models
- **Proprietary-grade tool** - Looks like internal hedge fund technology
- **Real-world impact** - Addresses actual market needs for ESG risk assessment

## 💡 Key Features

### 🌐 Multi-Language News Scraping & Analysis
- Scrape and summarize financial news in 5+ languages using LLMs (Mistral/GPT-4)
- Real-time news processing and content extraction
- Source diversity across global financial publications

### 🤖 Advanced NLP & Sentiment Analysis
- Sentiment and stance classification for ESG categories
- Environmental, Social, and Governance factor detection
- Context-aware analysis using transformer models


### 📊 Intelligent Scoring & Risk Engine
- Company ranking by ESG risk profile
- Weighted scoring across multiple ESG dimensions
- ESG scores normalized to 0–100 risk scale for investors
- CSV output for scores and risk metrics
- Historical trend analysis and prediction

### 📈 Investment Dashboard & Visualization
- Streamlit dashboard for ESG risk heatmaps by sector & region
- Interactive filtering by sector and region
- Real-time ESG score and risk updates
- Investment recommendation insights

### 📈 Investment Dashboard
- Interactive risk visualization
- Sector, region, and topic filtering
- Real-time ESG score updates
- Investment recommendation insights

## 🔧 Technology Stack

### Core Stack
- **Python** - Main language for all modules
- **BeautifulSoup** - Web scraping and HTML parsing
- **Requests** - HTTP requests for scraping
- **SQLAlchemy** - Database ORM for PostgreSQL
- **PostgreSQL** - Relational database for articles and companies
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical operations
- **Matplotlib/Seaborn/Plotly** - Data visualization
- **Streamlit** - Interactive dashboard
- **HuggingFace Transformers** - BERT-based ESG sentiment classification

## 📁 Project Structure

```
esg-sentiment-scorer/
├── src/
│   ├── scraping/          # News scraping modules
│   │   ├── news_scraper.py
│   │   └── multilingual_scraper.py
│   ├── nlp/               # NLP and sentiment analysis
│   │   └── sentiment_analyzer.py
│   ├── scoring/           # ESG scoring algorithms
│   ├── api/               # (Optional) API backend
│   │   └── main.py
│   ├── dashboard/         # Streamlit dashboard
│   │   └── esg_dashboard.py
│   └── __init__.py
├── data/
│   ├── raw/               # Raw scraped data
│   ├── processed/         # Cleaned and processed data
│   │   ├── company_esg_scores.csv
│   │   └── company_esg_risk_scores.csv
│   └── vectors/           # Vector embeddings
├── models/                # Trained models and checkpoints
├── config/
│   ├── settings.py        # Configuration and sources
│   └── companies.py       # Company list
├── tests/                 # Unit and integration tests [TODO]
├── docs/                  # Documentation
│   └── USAGE.md
├── notebooks/
│   └── esg_analysis_demo.ipynb
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── README.md
├── requirements.txt
└── LICENSE
```


## 🚀 Getting Started & Usage

See `docs/USAGE.md` for all setup, usage, and troubleshooting instructions.

## 📈 Roadmap & Next Steps

- [x] Multilingual news scraping with fuzzy/keyword matching
- [x] ESG scoring pipeline with BERT classifier
- [x] Normalized ESG risk scores (0–100 scale)
- [x] Streamlit dashboard for ESG risk heatmaps by sector & region
- [x] Usage guide in `docs/USAGE.md`
- [x] CSV output for scores and risk metrics
- [x] Improved error handling, translation, and logging

### Next Steps
- Add more ESG/business news sources and data
- Implement unit and integration tests
- Automate data updates and dashboard refresh

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Investment decisions should always involve professional financial advice and thorough due diligence.
