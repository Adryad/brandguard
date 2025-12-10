import pytest
from unittest.mock import Mock, patch
from app.services.analyzers.sentiment_analyzer import SentimentAnalyzer


class TestSentimentAnalyzer:
    def setup_method(self):
        self.analyzer = SentimentAnalyzer()

    def test_positive_sentiment(self):
        with patch.object(
            self.analyzer.model,
            "__call__",
            return_value=[{"label": "POSITIVE", "score": 0.95}],
        ):
            result = self.analyzer.analyze("This is excellent!")
            assert result["sentiment"] == "POSITIVE"

    def test_neutral_sentiment(self):
        with patch.object(
            self.analyzer.model,
            "__call__",
            return_value=[{"label": "NEUTRAL", "score": 0.65}],
        ):
            result = self.analyzer.analyze("The company released a new product")
            assert result["sentiment"] == "NEUTRAL"

    def test_negative_sentiment(self):
        with patch.object(
            self.analyzer.model,
            "__call__",
            return_value=[{"label": "NEGATIVE", "score": 0.85}],
        ):
            result = self.analyzer.analyze("This is terrible!")
            assert result["sentiment"] == "NEGATIVE"

    def test_empty_text(self):
        result = self.analyzer.analyze("")
        assert result["sentiment"] == "NEUTRAL"
