# backend/tests/test_sentiment_analyzer.py
import sys
from unittest.mock import Mock, patch

# Mock libraries before import
sys.modules['transformers'] = Mock()
sys.modules['transformers'].pipeline = Mock(return_value=Mock())

from app.services.analyzers.sentiment_analyzer import SentimentAnalyzer

def test_sentiment_analyzer_creation():
    """Test that SentimentAnalyzer can be created."""
    analyzer = SentimentAnalyzer()
    assert analyzer is not None
    assert hasattr(analyzer, 'analyze')

def test_analyze_empty_text():
    """Test analysis with empty text."""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("")
    assert result["sentiment"] == "NEUTRAL"
    assert result["confidence"] == 0.0
    assert "method" in result

def test_analyze_positive_text():
    """Test analysis with positive text."""
    analyzer = SentimentAnalyzer()
    
    # Mock the pipeline if it exists
    with patch.object(analyzer, 'pipeline', None):
        result = analyzer.analyze("This is good and great!")
    
    # Should be POSITIVE or NEUTRAL
    assert result["sentiment"] in ["POSITIVE", "NEUTRAL"]
    assert 0 <= result["confidence"] <= 1

def test_analyze_negative_text():
    """Test analysis with negative text."""
    analyzer = SentimentAnalyzer()
    
    with patch.object(analyzer, 'pipeline', None):
        result = analyzer.analyze("This is bad and terrible!")
    
    assert result["sentiment"] in ["NEGATIVE", "NEUTRAL"]
    assert 0 <= result["confidence"] <= 1

def test_batch_analyze():
    """Test batch analysis."""
    analyzer = SentimentAnalyzer()
    texts = ["Good news", "Bad situation", "Neutral report"]
    
    with patch.object(analyzer, 'pipeline', None):
        results = analyzer.batch_analyze(texts)
    
    assert len(results) == 3
    for result in results:
        assert "sentiment" in result
        assert "confidence" in result

class TestSentimentAnalyzerClass:
    """Test class for SentimentAnalyzer."""
    
    def setup_method(self):
        self.analyzer = SentimentAnalyzer()
    
    def test_initialization(self):
        assert self.analyzer.model_name is not None
    
    def test_analyze_method_exists(self):
        assert hasattr(self.analyzer, 'analyze')
        assert callable(self.analyzer.analyze)
    
    def test_batch_analyze_method_exists(self):
        assert hasattr(self.analyzer, 'batch_analyze')
        assert callable(self.analyzer.batch_analyze)