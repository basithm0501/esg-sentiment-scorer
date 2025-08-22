
# Import typing before any usage
from typing import List, Dict
# Training and inference pipeline
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW

class ESGDataset(Dataset):
    def __init__(self, articles: List[Dict], tokenizer, max_length=256):
        self.articles = articles
        self.tokenizer = tokenizer
        self.max_length = max_length
    def __len__(self):
        return len(self.articles)
    def __getitem__(self, idx):
        text = self.articles[idx]["text"]
        labels = [self.articles[idx]["environment"], self.articles[idx]["social"], self.articles[idx]["governance"]]
        encoding = self.tokenizer(text, truncation=True, padding="max_length", max_length=self.max_length, return_tensors="pt")
        item = {key: val.squeeze(0) for key, val in encoding.items()}
        item["labels"] = torch.tensor(labels, dtype=torch.float)
        return item

def train_esg_classifier(articles: List[Dict], model_name="bert-base-uncased", num_labels=3, epochs=3, batch_size=8, lr=2e-5):
    """
    Fine-tunes BERT for ESG multi-label classification using weak labels.
    articles: List of dicts with 'text', 'environment', 'social', 'governance' keys.
    """
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=num_labels, problem_type="multi_label_classification")
    dataset = ESGDataset(articles, tokenizer)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    optimizer = AdamW(model.parameters(), lr=lr)
    model.train()
    for epoch in range(epochs):
        for batch in dataloader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"]
            attention_mask = batch["attention_mask"]
            labels = batch["labels"]
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch+1}/{epochs} completed.")
    return model, tokenizer

def predict_esg_scores(model, tokenizer, articles: List[Dict], max_length=256) -> List[Dict]:
    """
    Runs inference on a list of articles, returns ESG scores for each.
    Each article dict should have 'text' and 'company'.
    """
    results = []
    for article in articles:
        inputs = tokenizer(article["text"], return_tensors="pt", truncation=True, max_length=max_length)
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.sigmoid(logits).squeeze().tolist()
        result = {
            "company": article["company"],
            "environment": float(probs[0]),
            "social": float(probs[1]),
            "governance": float(probs[2]),
        }
        results.append(result)
    return results
"""
ESG Classifier using BERT and keyword matching
"""

from typing import List, Dict
import re

# ESG keyword lists (expand as needed)
ESG_KEYWORDS = {
    "environment": ["climate", "carbon", "emissions", "renewable", "sustainability", "pollution", "energy", "waste", "biodiversity"],
    "social": ["diversity", "inclusion", "labor", "community", "human rights", "safety", "health", "education", "equality"],
    "governance": ["board", "audit", "compliance", "ethics", "transparency", "shareholder", "risk", "regulation", "leadership"]
}

def weak_label_esg(text: str) -> Dict[str, int]:
    """
    Returns a dict with binary labels for ESG topics based on keyword matching.
    """
    text_lower = text.lower()
    labels = {k: 0 for k in ESG_KEYWORDS}
    for topic, keywords in ESG_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\\b{re.escape(kw)}\\b", text_lower):
                labels[topic] = 1
                break
    return labels


# BERT multi-label classifier for ESG topics
from transformers import BertTokenizer, BertForSequenceClassification
import torch

ESG_LABELS = ["environment", "social", "governance"]

class ESGClassifier:
    def __init__(self, model_name="bert-base-uncased", num_labels=3, model_path=None):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        if model_path:
            self.model = BertForSequenceClassification.from_pretrained(model_path, num_labels=num_labels, problem_type="multi_label_classification")
        else:
            self.model = BertForSequenceClassification.from_pretrained(model_name, num_labels=num_labels, problem_type="multi_label_classification")
        self.model.eval()

    def predict(self, text: str) -> Dict[str, float]:
        """
        Returns ESG scores (softmax probabilities) for the input text.
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.sigmoid(logits).squeeze().tolist()
        return {label: float(prob) for label, prob in zip(ESG_LABELS, probs)}

# Example usage:
# classifier = ESGClassifier(model_path="path_to_finetuned_model")
# scores = classifier.predict("This company is investing in renewable energy and diversity.")
# print(scores)  # {'environment': 0.87, 'social': 0.65, 'governance': 0.12}

import csv
from collections import defaultdict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def evaluate_esg_classifier(true_labels: list, pred_scores: list, threshold: float = 0.5):
    """
    Evaluates ESG classifier predictions using accuracy, precision, recall, and F1-score.
    true_labels: List of dicts with 'environment', 'social', 'governance' (0/1)
    pred_scores: List of dicts with 'environment', 'social', 'governance' (float scores)
    threshold: Score threshold to convert probabilities to binary predictions
    Returns: dict of metrics per label
    """
    y_true = {label: [] for label in ESG_LABELS}
    y_pred = {label: [] for label in ESG_LABELS}
    for t, p in zip(true_labels, pred_scores):
        for label in ESG_LABELS:
            y_true[label].append(t[label])
            y_pred[label].append(int(p[label] >= threshold))
    metrics = {}
    for label in ESG_LABELS:
        metrics[label] = {
            "accuracy": accuracy_score(y_true[label], y_pred[label]),
            "precision": precision_score(y_true[label], y_pred[label], zero_division=0),
            "recall": recall_score(y_true[label], y_pred[label], zero_division=0),
            "f1": f1_score(y_true[label], y_pred[label], zero_division=0)
        }
    return metrics

def aggregate_esg_scores(articles: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    Aggregates ESG scores per company from a list of article dicts.
    Each article dict should have: 'company', 'environment', 'social', 'governance' (scores)
    Returns: {company: {environment_score, social_score, governance_score, num_articles}}
    """
    company_scores = defaultdict(lambda: {"environment": 0.0, "social": 0.0, "governance": 0.0, "num_articles": 0})
    for article in articles:
        company = article.get("company")
        if not company:
            continue
        company_scores[company]["environment"] += article.get("environment", 0.0)
        company_scores[company]["social"] += article.get("social", 0.0)
        company_scores[company]["governance"] += article.get("governance", 0.0)
        company_scores[company]["num_articles"] += 1
    # Average scores
    for company, scores in company_scores.items():
        n = scores["num_articles"]
        if n > 0:
            scores["environment"] /= n
            scores["social"] /= n
            scores["governance"] /= n
    return company_scores

def write_esg_scores_to_csv(company_scores: Dict[str, Dict[str, float]], csv_path: str):
    """
    Writes aggregated ESG scores per company to a CSV file.
    """
    with open(csv_path, "w", newline="") as csvfile:
        fieldnames = ["company", "environment_score", "social_score", "governance_score", "num_articles"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for company, scores in company_scores.items():
            writer.writerow({
                "company": company,
                "environment_score": round(scores["environment"], 4),
                "social_score": round(scores["social"], 4),
                "governance_score": round(scores["governance"], 4),
                "num_articles": scores["num_articles"]
            })
