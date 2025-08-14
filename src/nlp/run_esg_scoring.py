"""
Script to fetch articles from PostgreSQL and run ESG classification
"""

# Ensure src is in PYTHONPATH
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.db.article_store import Article, SessionLocal
from src.nlp.esg_classifier import ESGClassifier, weak_label_esg, aggregate_esg_scores, write_esg_scores_to_csv

# Step 1: Fetch articles from DB

def fetch_articles():
    session = SessionLocal()
    articles = session.query(Article).all()
    session.close()
    return articles

# Step 2: Prepare data for classifier

def prepare_article_data(articles):
    data = []
    for a in articles:
        text = a.translated_text if a.translated_text else a.raw_text
        if not text:
            continue
        # Use weak labels for training, or dummy for inference
        weak_labels = weak_label_esg(text)
        data.append({
            "company": a.company,
            "text": text,
            "environment": weak_labels["environment"],
            "social": weak_labels["social"],
            "governance": weak_labels["governance"]
        })
    return data

# Step 3: Run inference (replace with training if needed)

def run_esg_inference():
    articles = fetch_articles()
    data = prepare_article_data(articles)
    classifier = ESGClassifier(model_name="bert-base-uncased")  # Replace with finetuned model path if available
    results = []
    for item in data:
        scores = classifier.predict(item["text"])
        results.append({
            "company": item["company"],
            "environment": scores["environment"],
            "social": scores["social"],
            "governance": scores["governance"]
        })
    company_scores = aggregate_esg_scores(results)
    write_esg_scores_to_csv(company_scores, "data/processed/company_esg_scores.csv")
    print("ESG scores written to CSV.")

if __name__ == "__main__":
    run_esg_inference()
