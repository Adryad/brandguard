"""
Sentiment Analyzer Module
تحليل المشاعر للنصوص الإنجليزية
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    محلل المشاعر الذي يستخدم transformers إذا كان متاحاً،
    وإلا يستخدم تحليلاً بسيطاً.
    """

    def __init__(
        self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
    ):
        """تهيئة محلل المشاعر."""
        self.model_name = model_name
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        """تحميل نموذج تحليل المشاعر."""
        try:
            from transformers import pipeline

            self.pipeline = pipeline("sentiment-analysis", model=self.model_name)
            logger.info(f"Loaded sentiment analysis model: {self.model_name}")
        except ImportError as e:
            logger.warning(f"Transformers not available: {e}. Using simple analyzer.")
            self.pipeline = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.pipeline = None

    def analyze(self, text: str) -> Dict[str, any]:
        """
        تحليل مشاعر النص.

        Args:
            text: النص المراد تحليله (يجب أن يكون بالإنجليزية)

        Returns:
            dict: {
                "sentiment": "POSITIVE" | "NEGATIVE" | "NEUTRAL",
                "confidence": float between 0 and 1,
                "method": "transformers" | "simple" | "fallback"
            }
        """
        if not text or not isinstance(text, str):
            return self._fallback_result("empty")

        text = text.strip()
        if not text:
            return self._fallback_result("empty")

        # محاولة استخدام transformers
        if self.pipeline:
            try:
                # تقييد طول النص
                truncated_text = text[:512]
                result = self.pipeline(truncated_text)

                if result and len(result) > 0:
                    sentiment = result[0]["label"].upper()
                    confidence = float(result[0]["score"])

                    return {
                        "sentiment": sentiment,
                        "confidence": confidence,
                        "method": "transformers",
                    }
            except Exception as e:
                logger.warning(f"Transformers analysis failed: {e}")

        # استخدام تحليل بسيط
        return self._simple_analyze(text)

    def _simple_analyze(self, text: str) -> Dict[str, any]:
        """تحليل مشاعر بسيط باستخدام قوائم الكلمات."""
        text_lower = text.lower()

        # قوائم الكلمات (يمكن توسيعها)
        positive_words = {
            "good",
            "great",
            "excellent",
            "awesome",
            "fantastic",
            "amazing",
            "wonderful",
            "perfect",
            "best",
            "love",
            "like",
            "happy",
            "positive",
            "success",
            "successful",
            "win",
            "winner",
            "profit",
            "growth",
            "improve",
            "improvement",
            "better",
            "strong",
            "stable",
        }

        negative_words = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "worst",
            "hate",
            "dislike",
            "sad",
            "negative",
            "failure",
            "fail",
            "problem",
            "issue",
            "error",
            "crash",
            "loss",
            "decline",
            "drop",
            "weak",
            "poor",
            "terrible",
            "disappoint",
            "disappointment",
        }

        neutral_words = {
            "company",
            "release",
            "announce",
            "report",
            "today",
            "yesterday",
            "week",
            "month",
            "year",
            "quarter",
            "results",
        }

        # حساب التكرارات
        words = text_lower.split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        neutral_count = sum(1 for word in words if word in neutral_words)

        # تحديد المشاعر
        total = positive_count + negative_count + neutral_count

        if total == 0:
            return self._fallback_result("no_keywords")

        positive_score = positive_count / total
        negative_score = negative_count / total

        if positive_score > negative_score and positive_score > 0.3:
            sentiment = "POSITIVE"
            confidence = min(positive_score, 0.9)
        elif negative_score > positive_score and negative_score > 0.3:
            sentiment = "NEGATIVE"
            confidence = min(negative_score, 0.9)
        else:
            sentiment = "NEUTRAL"
            confidence = 0.5

        return {"sentiment": sentiment, "confidence": confidence, "method": "simple"}

    def _fallback_result(self, reason: str = "unknown") -> Dict[str, any]:
        """نتيجة افتراضية عند الفشل."""
        return {
            "sentiment": "NEUTRAL",
            "confidence": 0.0,
            "method": f"fallback ({reason})",
        }

    def batch_analyze(self, texts: List[str]) -> List[Dict[str, any]]:
        """تحليل مجموعة من النصوص."""
        return [self.analyze(text) for text in texts]


# تصدير الفئة للاستيراد
__all__ = ["SentimentAnalyzer"]
