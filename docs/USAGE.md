# ESG Sentiment Scorer Usage Guide

This document explains how to use the ESG Sentiment Scorer system for scraping, scoring, and visualizing ESG investment risk.

## 1. Setup

- Install dependencies:
  ```sh
  pip install -r requirements.txt
  pip install streamlit plotly
  ```
- Configure database and environment variables in `.env` if needed.

## 2. Scrape News Articles

- Run the multilingual scraper to collect articles for all companies:
  ```sh
  python src/scraping/multilingual_scraper.py
  ```
- Scraped articles are stored in the database and linked to companies.

## 3. ESG Scoring

- Run the ESG scoring script to analyze articles and compute ESG scores:
  ```sh
  python src/nlp/run_esg_scoring.py
  ```
- Results are saved to `data/processed/company_esg_scores.csv` and normalized risk scores to `company_esg_risk_scores.csv`.

## 4. ESG Investment Risk Dashboard

- Launch the Streamlit dashboard to visualize ESG risk by sector and region:
  ```sh
  streamlit run src/dashboard/esg_dashboard.py
  ```
- Use sidebar filters to select sectors and regions.
- View heatmaps and detailed risk scores for all companies.

## 5. Customization

- Add or edit news sources in `config/settings.py`.
- Update company list in `config/companies.py`.
- Adjust ESG keyword taxonomy in `config/settings.py` (class `ESGCategories`).

## 6. Advanced

- Fine-tune the BERT model for ESG sentiment classification if labeled data is available.
- Extend dashboard visualizations or export results for further analysis.

## 7. Troubleshooting

- If you see missing dependencies, run `pip install` for required packages.
- For database errors, check connection settings in `.env` and `config/settings.py`.
- For scraping issues, verify source URLs and selectors in `config/settings.py`.

## 8. Contact

For questions or support, contact the project maintainer or open an issue in the repository.
