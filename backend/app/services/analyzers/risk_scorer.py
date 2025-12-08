# brandguard/backend/app/services/analyzers/risk_scorer.py
from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np
from sqlalchemy.orm import Session

from app.models.sentiment import Article, Review


class RiskScorer:
    """
    Calculate risk scores based on sentiment trends and patterns
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_risk_score(self, company_id: int) -> Dict:
        """
        Calculate comprehensive risk score for a company
        """
        # Get recent data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        articles = (
            self.db.query(Article) .filter(
                Article.company_id == company_id,
                Article.created_at >= start_date) .all())

        reviews = (
            self.db.query(Review) .filter(
                Review.company_id == company_id,
                Review.created_at >= start_date) .all())

        # Calculate risk factors
        sentiment_risk = self._calculate_sentiment_risk(articles, reviews)
        volume_risk = self._calculate_volume_risk(articles, reviews)
        velocity_risk = self._calculate_velocity_risk(articles, reviews)
        consistency_risk = self._calculate_consistency_risk(articles, reviews)

        # Weighted risk score
        risk_score = (
            sentiment_risk * 0.4
            + volume_risk * 0.2
            + velocity_risk * 0.2
            + consistency_risk * 0.2
        )

        # Ensure score is between 0 and 100
        risk_score = max(0, min(100, risk_score))

        return {
            "risk_score": risk_score,
            "risk_factors": [
                {
                    "type": "sentiment",
                    "score": sentiment_risk,
                    "description": "Negative sentiment trend",
                },
                {
                    "type": "volume",
                    "score": volume_risk,
                    "description": "Abnormal mention volume",
                },
                {
                    "type": "velocity",
                    "score": velocity_risk,
                    "description": "Rapid sentiment changes",
                },
                {
                    "type": "consistency",
                    "score": consistency_risk,
                    "description": "Inconsistent sentiment patterns",
                },
            ],
        }

    def _calculate_sentiment_risk(
        self, articles: List[Article], reviews: List[Review]
    ) -> float:
        """
        Calculate risk based on sentiment trends
        """
        if not articles and not reviews:
            return 0

        # Combine sentiment scores
        sentiment_scores = []

        for article in articles:
            score_map = {"positive": 1.0, "neutral": 0.5, "negative": 0.0}
            sentiment_scores.append(score_map.get(article.sentiment, 0.5))

        for review in reviews:
            sentiment_scores.append(review.rating / 5.0)

        # Calculate trend
        if len(sentiment_scores) < 5:
            return 0

        recent_scores = sentiment_scores[-10:]
        older_scores = sentiment_scores[:10]

        recent_avg = np.mean(recent_scores)
        older_avg = np.mean(older_scores)

        # Risk increases if sentiment is declining
        decline_risk = max(0, (older_avg - recent_avg) * 100)

        # Risk increases if recent sentiment is poor
        poor_sentiment_risk = max(0, (0.5 - recent_avg) * 100)

        return (decline_risk + poor_sentiment_risk) / 2

    def _calculate_volume_risk(
        self, articles: List[Article], reviews: List[Review]
    ) -> float:
        """
        Calculate risk based on mention volume anomalies
        """
        total_mentions = len(articles) + len(reviews)

        # Expected volume (based on historical average)
        expected_volume = 50  # This should be calculated from historical data

        if total_mentions < expected_volume * 0.5:
            return 30  # Low volume can indicate declining interest

        if total_mentions > expected_volume * 3:
            return 40  # High volume can indicate a crisis

        return 0

    def _calculate_velocity_risk(
        self, articles: List[Article], reviews: List[Review]
    ) -> float:
        """
        Calculate risk based on rapid sentiment changes
        """
        all_items = articles + reviews
        all_items.sort(key=lambda x: x.created_at)

        if len(all_items) < 7:
            return 0

        # Calculate sentiment changes between consecutive items
        sentiment_changes = []
        score_map = {"positive": 1.0, "neutral": 0.5, "negative": 0.0}

        for i in range(1, len(all_items)):
            prev_score = self._get_sentiment_score(all_items[i - 1], score_map)
            curr_score = self._get_sentiment_score(all_items[i], score_map)

            change = abs(curr_score - prev_score)
            sentiment_changes.append(change)

        # High frequency of large changes indicates instability
        large_changes = [c for c in sentiment_changes if c > 0.5]

        if len(large_changes) > len(sentiment_changes) * 0.3:
            return 50

        return len(large_changes) / len(sentiment_changes) * 100

    def _calculate_consistency_risk(
        self, articles: List[Article], reviews: List[Review]
    ) -> float:
        """
        Calculate risk based on sentiment consistency
        """
        all_items = articles + reviews
        score_map = {"positive": 1.0, "neutral": 0.5, "negative": 0.0}

        if len(all_items) < 10:
            return 0

        # Get sentiment scores
        scores = [
            self._get_sentiment_score(
                item,
                score_map) for item in all_items]

        # Calculate standard deviation (higher = more inconsistent)
        std_dev = np.std(scores)

        # Normalize to 0-100 scale
        return min(100, std_dev * 100)

    def _get_sentiment_score(self, item, score_map: Dict) -> float:
        """
        Get normalized sentiment score for an item
        """
        if isinstance(item, Article):
            return score_map.get(item.sentiment, 0.5)
        elif isinstance(item, Review):
            return item.rating / 5.0
        return 0.5
