"""
ESG Sentiment Analysis module using transformers and custom models
"""
import asyncio
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
import openai
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from config.settings import settings, ESGCategories

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Data class for sentiment analysis results"""
    overall_sentiment: float  # -1 to 1
    confidence: float         # 0 to 1
    esg_scores: Dict[str, float]  # ESG category scores
    key_themes: List[str]
    risk_indicators: List[str]
    language: str = "en"


@dataclass
class ESGClassification:
    """Data class for ESG classification results"""
    environmental: float
    social: float
    governance: float
    relevance_score: float
    key_topics: List[str]


class ESGSentimentAnalyzer:
    """Main ESG sentiment analysis engine"""
    
    def __init__(self):
        self.sentiment_model = None
        self.esg_classifier = None
        self.embedding_model = None
        self.llm_chain = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all ML models and components"""
        try:
            # Sentiment analysis model
            logger.info("Loading sentiment analysis model...")
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # ESG classification model (using general classifier for now)
            logger.info("Loading ESG classification model...")
            self.esg_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            
            # Embedding model for semantic analysis
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            
            # LLM chain for advanced analysis
            if settings.openai_api_key:
                logger.info("Initializing LLM chain...")
                openai.api_key = settings.openai_api_key
                
                llm = OpenAI(
                    model_name=settings.default_llm_model,
                    temperature=0.1,
                    max_tokens=1000
                )
                
                prompt_template = PromptTemplate(
                    input_variables=["text", "company"],
                    template="""
                    Analyze the following text about {company} for ESG (Environmental, Social, Governance) sentiment:
                    
                    Text: {text}
                    
                    Please provide:
                    1. Overall ESG sentiment score (-1 to 1)
                    2. Environmental impact score (0 to 1)
                    3. Social impact score (0 to 1) 
                    4. Governance impact score (0 to 1)
                    5. Key ESG themes identified
                    6. Risk indicators or concerns
                    
                    Format your response as JSON.
                    """
                )
                
                self.llm_chain = LLMChain(llm=llm, prompt=prompt_template)
            
            logger.info("All models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            # Fall back to basic models or mock implementations
            self._initialize_fallback_models()
    
    def _initialize_fallback_models(self):
        """Initialize fallback models if main models fail"""
        logger.info("Initializing fallback models...")
        
        # Use basic sentiment analysis
        try:
            self.sentiment_model = pipeline("sentiment-analysis")
        except:
            logger.warning("Could not load sentiment model")
            self.sentiment_model = None
    
    async def analyze_text(self, text: str, company_name: str = "") -> SentimentResult:
        """Analyze text for ESG sentiment"""
        try:
            # Basic sentiment analysis
            sentiment_score, confidence = await self._analyze_sentiment(text)
            
            # ESG category classification
            esg_scores = await self._classify_esg_categories(text)
            
            # Extract key themes
            themes = await self._extract_themes(text)
            
            # Identify risk indicators
            risk_indicators = await self._identify_risks(text)
            
            # Language detection (simplified)
            language = self._detect_language(text)
            
            return SentimentResult(
                overall_sentiment=sentiment_score,
                confidence=confidence,
                esg_scores=esg_scores,
                key_themes=themes,
                risk_indicators=risk_indicators,
                language=language
            )
            
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            # Return default result
            return SentimentResult(
                overall_sentiment=0.0,
                confidence=0.0,
                esg_scores={"environmental": 0.0, "social": 0.0, "governance": 0.0},
                key_themes=[],
                risk_indicators=[],
                language="en"
            )
    
    async def _analyze_sentiment(self, text: str) -> Tuple[float, float]:
        """Analyze overall sentiment of text"""
        if not self.sentiment_model:
            return 0.0, 0.0
        
        try:
            # Truncate text if too long
            max_length = 500  # Most models have token limits
            if len(text) > max_length:
                text = text[:max_length]
            
            results = self.sentiment_model(text)
            
            if isinstance(results, list) and len(results) > 0:
                # Handle different model outputs
                if isinstance(results[0], list):
                    # Multiple scores returned
                    results = results[0]
                
                # Convert to numerical score
                sentiment_score = 0.0
                confidence = 0.0
                
                for result in results:
                    label = result['label'].lower()
                    score = result['score']
                    
                    if 'positive' in label or label == 'pos':
                        sentiment_score = score
                        confidence = max(confidence, score)
                    elif 'negative' in label or label == 'neg':
                        sentiment_score = -score
                        confidence = max(confidence, score)
                    else:  # neutral
                        confidence = max(confidence, score)
                
                return sentiment_score, confidence
            
            return 0.0, 0.0
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return 0.0, 0.0
    
    async def _classify_esg_categories(self, text: str) -> Dict[str, float]:
        """Classify text into ESG categories"""
        if not self.esg_classifier:
            return {"environmental": 0.0, "social": 0.0, "governance": 0.0}
        
        try:
            # Define ESG labels for zero-shot classification
            esg_labels = [
                "environmental sustainability",
                "social responsibility", 
                "corporate governance"
            ]
            
            result = self.esg_classifier(text, esg_labels)
            
            scores = {}
            for label, score in zip(result['labels'], result['scores']):
                if 'environmental' in label.lower():
                    scores['environmental'] = score
                elif 'social' in label.lower():
                    scores['social'] = score
                elif 'governance' in label.lower():
                    scores['governance'] = score
            
            return scores
            
        except Exception as e:
            logger.error(f"Error in ESG classification: {e}")
            return self._keyword_based_esg_classification(text)
    
    def _keyword_based_esg_classification(self, text: str) -> Dict[str, float]:
        """Fallback keyword-based ESG classification"""
        text_lower = text.lower()
        scores = {"environmental": 0.0, "social": 0.0, "governance": 0.0}
        
        categories = ESGCategories.get_all_categories()
        
        for category_name, category_config in categories.items():
            keywords = category_config.get('keywords', [])
            matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            
            # Normalize score based on text length and keyword matches
            if len(text_lower) > 0:
                scores[category_name] = min(matches / len(keywords) * 2, 1.0)
        
        return scores
    
    async def _extract_themes(self, text: str) -> List[str]:
        """Extract key themes from text"""
        # Simple keyword-based theme extraction
        # TODO: Implement more sophisticated theme extraction using NLP
        
        themes = []
        text_lower = text.lower()
        
        # ESG theme keywords
        theme_keywords = {
            "sustainability": ["sustainability", "sustainable", "green", "eco-friendly"],
            "climate_change": ["climate change", "global warming", "carbon", "emissions"],
            "diversity": ["diversity", "inclusion", "equal", "equality"],
            "governance": ["governance", "board", "executive", "management"],
            "transparency": ["transparency", "disclosure", "reporting"],
            "innovation": ["innovation", "technology", "digital", "AI"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme.replace("_", " ").title())
        
        return themes
    
    async def _identify_risks(self, text: str) -> List[str]:
        """Identify potential risk indicators"""
        risks = []
        text_lower = text.lower()
        
        # Risk indicator keywords
        risk_keywords = {
            "regulatory_risk": ["fine", "penalty", "violation", "investigation", "lawsuit"],
            "reputational_risk": ["scandal", "controversy", "protest", "boycott", "criticism"],
            "operational_risk": ["disruption", "failure", "accident", "incident", "breach"],
            "environmental_risk": ["pollution", "contamination", "spill", "waste", "damage"],
            "financial_risk": ["loss", "deficit", "debt", "default", "bankruptcy"]
        }
        
        for risk_type, keywords in risk_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                risks.append(risk_type.replace("_", " ").title())
        
        return risks
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # TODO: Implement proper language detection using langdetect or similar
        # For now, assume English
        return "en"
    
    async def batch_analyze(self, texts: List[str], company_name: str = "") -> List[SentimentResult]:
        """Analyze multiple texts concurrently"""
        tasks = [self.analyze_text(text, company_name) for text in texts]
        results = await asyncio.gather(*tasks)
        return results
    
    async def analyze_with_llm(self, text: str, company_name: str) -> Optional[Dict]:
        """Analyze using LLM for advanced insights"""
        if not self.llm_chain:
            logger.warning("LLM chain not available")
            return None
        
        try:
            result = await self.llm_chain.arun(text=text, company=company_name)
            # TODO: Parse and structure the LLM response
            return {"llm_analysis": result}
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            return None


class ESGScorer:
    """ESG scoring engine that combines multiple analysis results"""
    
    def __init__(self):
        self.weights = {
            "environmental": settings.environmental_weight,
            "social": settings.social_weight,
            "governance": settings.governance_weight
        }
    
    def calculate_esg_score(self, sentiment_results: List[SentimentResult]) -> Dict[str, float]:
        """Calculate aggregated ESG scores from multiple sentiment results"""
        if not sentiment_results:
            return {
                "environmental": 0.0,
                "social": 0.0,
                "governance": 0.0,
                "overall": 0.0,
                "confidence": 0.0
            }
        
        # Aggregate scores
        total_weights = {"environmental": 0.0, "social": 0.0, "governance": 0.0}
        weighted_scores = {"environmental": 0.0, "social": 0.0, "governance": 0.0}
        total_confidence = 0.0
        
        for result in sentiment_results:
            weight = result.confidence  # Use confidence as weight
            total_confidence += weight
            
            for category in ["environmental", "social", "governance"]:
                score = result.esg_scores.get(category, 0.0)
                weighted_scores[category] += score * weight
                total_weights[category] += weight
        
        # Calculate final scores
        final_scores = {}
        for category in ["environmental", "social", "governance"]:
            if total_weights[category] > 0:
                final_scores[category] = weighted_scores[category] / total_weights[category]
            else:
                final_scores[category] = 0.0
        
        # Calculate overall score
        overall_score = sum(
            final_scores[category] * self.weights[category]
            for category in ["environmental", "social", "governance"]
        )
        
        final_scores["overall"] = overall_score
        final_scores["confidence"] = total_confidence / len(sentiment_results) if sentiment_results else 0.0
        
        return final_scores


# Usage example
async def main():
    """Example usage"""
    analyzer = ESGSentimentAnalyzer()
    
    sample_text = """
    Apple Inc. announced today a major commitment to carbon neutrality by 2030,
    including investments in renewable energy and sustainable manufacturing.
    The company also highlighted its diversity and inclusion programs,
    with improved board representation and employee satisfaction scores.
    """
    
    result = await analyzer.analyze_text(sample_text, "Apple Inc.")
    
    print("ESG Sentiment Analysis Results:")
    print(f"Overall Sentiment: {result.overall_sentiment:.2f}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"ESG Scores: {result.esg_scores}")
    print(f"Key Themes: {result.key_themes}")
    print(f"Risk Indicators: {result.risk_indicators}")


if __name__ == "__main__":
    asyncio.run(main())
