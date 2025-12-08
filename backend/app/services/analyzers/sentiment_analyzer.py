# brandguard/backend/app/services/analyzers/sentiment_analyzer.py
import logging
import re
from collections import Counter
from typing import Dict, List

import spacy
from transformers import pipeline

logger = logging.getLogger(__name__)

# Load models (will be cached after first load)
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    return_all_scores=False,
)

# Load spacy model for entity recognition
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None
    logger.warning("Spacy model not found. Entity extraction disabled.")


def analyze_sentiment(text: str, confidence_threshold: float = 0.7) -> Dict:
    """
    Analyze sentiment of text using open-source models

    Args:
        text: Input text to analyze
        confidence_threshold: Minimum confidence score to accept result

    Returns:
        Dictionary with sentiment, confidence, keywords, and entities
    """
    if not text or len(text.strip()) == 0:
        return {
            "sentiment": "neutral",
            "confidence": 0.0,
            "keywords": [],
            "entities": [],
        }

    # Clean text
    clean_text = _clean_text(text)

    # Perform sentiment analysis
    try:
        result = sentiment_pipeline(clean_text[:512])[
            0]  # Truncate to model max length
        sentiment = result["label"].lower()
        confidence = result["score"]

        # If confidence is too low, classify as neutral
        if confidence < confidence_threshold:
            sentiment = "neutral"
            confidence = 1.0 - confidence

    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        sentiment = "neutral"
        confidence = 0.0

    # Extract keywords
    keywords = _extract_keywords(text)

    # Extract entities
    entities = _extract_entities(text) if nlp else []

    return {
        "sentiment": sentiment,
        "confidence": float(confidence),
        "keywords": keywords,
        "entities": entities,
    }


def _clean_text(text: str) -> str:
    """
    Clean text for analysis
    """
    # Remove URLs
    text = re.sub(r"http\S+|www.\S+", "", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", "", text)

    # Remove phone numbers
    text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "", text)

    # Remove special characters but keep spaces
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Remove extra whitespace
    text = " ".join(text.split())

    return text.strip()


def _extract_keywords(text: str, top_k: int = 10) -> List[str]:
    """
    Extract keywords from text
    """
    # Common stop words
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "up",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "among",
        "is",
        "was",
        "are",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "them",
        "their",
        "this",
        "that",
    }

    # Clean and tokenize
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    words = [w for w in words if w not in stop_words]

    # Count word frequencies
    word_freq = Counter(words)

    # Return top keywords
    return [word for word, _ in word_freq.most_common(top_k)]


def _extract_entities(text: str) -> List[Dict]:
    """
    Extract named entities from text
    """
    entities = []

    try:
        doc = nlp(text)

        for ent in doc.ents:
            entities.append(
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                }
            )

    except Exception as e:
        logger.error(f"Entity extraction error: {str(e)}")

    return entities


def analyze_batch_sentiments(texts: List[str]) -> List[Dict]:
    """
    Analyze sentiment for multiple texts
    """
    results = []

    for text in texts:
        result = analyze_sentiment(text)
        results.append(result)

    return results


def calculate_overall_sentiment(sentiments: List[Dict]) -> Dict:
    """
    Calculate overall sentiment from multiple analyses
    """
    if not sentiments:
        return {
            "sentiment": "neutral",
            "confidence": 0.0,
            "positive_ratio": 0.0,
            "negative_ratio": 0.0,
            "neutral_ratio": 0.0,
        }

    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    total_confidence = 0.0

    for sent in sentiments:
        sentiment_counts[sent["sentiment"]] += 1
        total_confidence += sent["confidence"]

    total = len(sentiments)
    positive_ratio = sentiment_counts["positive"] / total
    negative_ratio = sentiment_counts["negative"] / total
    neutral_ratio = sentiment_counts["neutral"] / total

    # Determine overall sentiment
    if positive_ratio > 0.6:
        overall_sentiment = "positive"
    elif negative_ratio > 0.6:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"

    avg_confidence = total_confidence / total

    return {
        "sentiment": overall_sentiment,
        "confidence": avg_confidence,
        "positive_ratio": positive_ratio,
        "negative_ratio": negative_ratio,
        "neutral_ratio": neutral_ratio,
    }
