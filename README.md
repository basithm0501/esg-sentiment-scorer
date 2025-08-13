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

### 📊 Intelligent Scoring Engine
- Company ranking by ESG risk profile
- Weighted scoring across multiple ESG dimensions
- Historical trend analysis and prediction

### 📈 Investment Dashboard
- Interactive risk visualization
- Sector, region, and topic filtering
- Real-time ESG score updates
- Investment recommendation insights

## 🔧 Technology Stack

### Backend & APIs
- **Python** - Core application framework
- **FastAPI** - High-performance API development
- **BeautifulSoup/Scrapy** - Web scraping and data extraction

### AI & Machine Learning
- **HuggingFace Transformers** - Pre-trained language models
- **LangChain** - LLM application framework
- **OpenAI/Mistral APIs** - Advanced language processing

### Data Storage & Vectors
- **Pinecone/ChromaDB** - Vector database for embeddings
- **PostgreSQL** - Structured data storage
- **Redis** - Caching and session management

### Frontend & Visualization
- **Streamlit** - Interactive dashboard framework
- **Plotly** - Advanced data visualization
- **Pandas** - Data manipulation and analysis

## 📁 Project Structure

```
esg-sentiment-scorer/
├── src/
│   ├── scraping/          # News scraping modules
│   ├── nlp/              # NLP and sentiment analysis
│   ├── scoring/          # ESG scoring algorithms
│   ├── api/              # FastAPI backend
│   └── dashboard/        # Streamlit frontend
├── data/
│   ├── raw/             # Raw scraped data
│   ├── processed/       # Cleaned and processed data
│   └── vectors/         # Vector embeddings
├── models/              # Trained models and checkpoints
├── config/              # Configuration files
├── tests/               # Unit and integration tests
├── docs/                # Documentation
└── notebooks/           # Jupyter analysis notebooks
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js (for any frontend components)
- Docker (optional, for containerization)

### Installation

1. **Clone and setup environment**
```bash
cd esg-sentiment-scorer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Initialize database and vector store**
```bash
python src/setup_database.py
```

4. **Run the application**
```bash
# Start API server
uvicorn src.api.main:app --reload

# Start dashboard (in another terminal)
streamlit run src/dashboard/app.py
```

## 🔑 API Keys Required

- **OpenAI API Key** (or Mistral AI)
- **News API Keys** (NewsAPI, Alpha Vantage, etc.)
- **Pinecone API Key** (if using Pinecone for vectors)

## 📊 ESG Categories Analyzed

### Environmental (E)
- Climate change and carbon emissions
- Resource usage and waste management
- Renewable energy adoption
- Environmental compliance

### Social (S)
- Labor practices and human rights
- Community relations
- Product safety and quality
- Diversity and inclusion

### Governance (G)
- Board composition and independence
- Executive compensation
- Anti-corruption policies
- Shareholder rights

## 🎯 Target Use Cases

- **Investment Firms** - ESG risk assessment for portfolio management
- **Hedge Funds** - Alternative data for investment decisions
- **Corporate Teams** - ESG compliance monitoring
- **Researchers** - ESG trend analysis and reporting

## 📈 Roadmap

- [ ] Phase 1: Basic news scraping and sentiment analysis
- [ ] Phase 2: ESG classification and scoring engine
- [ ] Phase 3: Interactive dashboard development
- [ ] Phase 4: Multi-language support expansion
- [ ] Phase 5: Real-time alerts and notifications
- [ ] Phase 6: API monetization and enterprise features

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Investment decisions should always involve professional financial advice and thorough due diligence.
