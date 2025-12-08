# brandguard/backend/tests/test_sentiment_analyzer.py

from app.services.analyzers.sentiment_analyzer import (
    analyze_sentiment,
    calculate_overall_sentiment,
)


class TestSentimentAnalyzer:
    def test_positive_sentiment(self):
        text = "This company is doing amazing work with their new products!"
        result = analyze_sentiment(text)
        assert result["sentiment"] == "positive"
        assert result["confidence"] > 0.7

    def test_negative_sentiment(self):
        text = "Terrible service and poor quality products from this company"
        result = analyze_sentiment(text)
        assert result["sentiment"] == "negative"
        assert result["confidence"] > 0.7

    def test_neutral_sentiment(self):
        text = "The company released a new product today"
        result = analyze_sentiment(text)
        assert result["sentiment"] == "neutral"

    def test_empty_text(self):
        result = analyze_sentiment("")
        assert result["sentiment"] == "neutral"
        assert result["confidence"] == 0.0

    def test_batch_sentiment_analysis(self):
        texts = ["Great product", "Bad service", "Kept neutral"]
        results = calculate_overall_sentiment([analyze_sentiment(t) for t in texts])
        assert "positive_ratio" in results
        assert "negative_ratio" in results
        assert "neutral_ratio" in results
