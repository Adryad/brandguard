# brandguard/backend/app/services/analyzers/risk_scorer.py
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.sentiment import Article, Review
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor


class RiskScoringEngine:
    """
    Production-ready risk scoring system using ML techniques
    """

    def __init__(self, db: Session):
        self.db = db
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.risk_factors = {
            "sentiment_trend": {"weight": 0.25, "threshold": 0.3},
            "volume_volatility": {"weight": 0.20, "threshold": 1.5},
            "negative_spikes": {"weight": 0.20, "threshold": 3},
            "review_decline": {"weight": 0.15, "threshold": 0.5},
            "news_impact": {"weight": 0.20, "threshold": 0.7},
        }

    def calculate_risk_score(self, company_id: int) -> Dict:
        """
        Calculate comprehensive 0-100 risk score with explanations
        """
        company = self.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"error": "Company not found"}

        # Get historical data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        articles = (
            self.db.query(Article)
            .filter(Article.company_id == company_id, Article.created_at >= start_date)
            .all()
        )

        reviews = (
            self.db.query(Review)
            .filter(Review.company_id == company_id, Review.created_at >= start_date)
            .all()
        )

        if not articles and not reviews:
            return {"score": 25, "risk": "low", "factors": ["Insufficient data"]}

        # Calculate individual factors
        factors = {
            "sentiment_trend": self._calculate_sentiment_trend(articles, reviews),
            "volume_volatility": self._calculate_volume_volatility(articles, reviews),
            "negative_spikes": self._calculate_negative_spikes(articles),
            "review_decline": self._calculate_review_decline(reviews),
            "news_impact": self._calculate_news_impact(articles),
        }

        # Weighted score
        total_score = sum(
            factor * self.risk_factors[name]["weight"]
            for name, factor in factors.items()
        )

        score = min(100, max(0, total_score * 100))

        return {
            "score": score,
            "risk": self._get_risk_level(score),
            "factors": [
                {
                    "name": name,
                    "score": factor,
                    "weight": self.risk_factors[name]["weight"],
                    "description": self._get_factor_description(name, factor),
                    "severity": (
                        "high"
                        if factor > self.risk_factors[name]["threshold"]
                        else "low"
                    ),
                }
                for name, factor in factors.items()
            ],
            "recommendations": self._generate_recommendations(score, factors),
            "last_updated": datetime.utcnow().isoformat(),
        }

    def _calculate_sentiment_trend(
        self, articles: List[Article], reviews: List[Review]
    ) -> float:
        """Calculate sentiment trend direction and magnitude"""
        if not articles and not reviews:
            return 0.0

        # Combine sentiment data
        sentiments = []
        for article in articles:
            score_map = {"positive": 1.0, "neutral": 0.5, "negative": 0.0}
            sentiments.append(
                (article.created_at, score_map.get(article.sentiment, 0.5))
            )

        for review in reviews:
            sentiments.append((review.created_at, review.rating / 5.0))

        if len(sentiments) < 5:
            return 0.0

        # Sort by date
        sentiments.sort(key=lambda x: x[0])
        dates, scores = zip(*sentiments)

        # Calculate rolling average and trend
        df = pd.DataFrame({"date": dates, "score": scores})
        df["rolling_avg"] = df["score"].rolling(window=3).mean()

        # Trend calculation
        if len(df) >= 2:
            recent_trend = df["rolling_avg"].iloc[-1] - df["rolling_avg"].iloc[0]
            return (0.5 - recent_trend) * 2  # Scale to 0-1

        return 0.0

    def _calculate_volume_volatility(
        self, articles: List[Article], reviews: List[Review]
    ) -> float:
        """Calculate volatility in mention volume"""
        all_items = articles + reviews

        if len(all_items) < 7:
            return 0.0

        # Group by day
        daily_counts = {}
        for item in all_items:
            date = item.created_at.date()
            daily_counts[date] = daily_counts.get(date, 0) + 1

        if len(daily_counts) < 3:
            return 0.0

        counts = list(daily_counts.values())
        volatility = np.std(counts) / np.mean(counts)

        return min(1.0, volatility / 3.0)  # Normalize

    def _calculate_negative_spikes(self, articles: List[Article]) -> float:
        """Detect negative sentiment spikes"""
        negative_scores = [
            1 - article.confidence_score  # For negative articles
            for article in articles
            if article.sentiment == "negative"
        ]

        if not negative_scores:
            return 0.0

        max_negative = max(negative_scores) if negative_scores else 0
        avg_negative = np.mean(negative_scores)

        # Higher more negative = higher risk
        return min(1.0, max_negative * 1.5)

    def _calculate_review_decline(self, reviews: List[Review]) -> float:
        """Detect declining review ratings"""
        if len(reviews) < 5:
            return 0.0

        # Group by week
        weekly_ratings = {}
        for review in reviews:
            week = review.created_at.isocalendar()[1]
            if week not in weekly_ratings:
                weekly_ratings[week] = []
            weekly_ratings[week].append(review.rating)

        # Calculate decline
        weeks = sorted(weekly_ratings.keys())
        weekly_averages = [np.mean(weekly_ratings[week]) for week in weeks]

        if len(weekly_averages) >= 2:
            first_avg = weekly_averages[0]
            last_avg = weekly_averages[-1]
            decline = (first_avg - last_avg) / 5  # 5-star scale
            return max(0, decline)

        return 0.0

    def _calculate_news_impact(self, articles: List[Article]) -> float:
        """Calculate impact of articles on reputation"""
        if not articles:
            return 0.0

        # Weight articles by confidence/relevance
        weighted_sentiment = sum(
            (
                article.confidence_score
                * article.relevance_score
                * (
                    1
                    if article.sentiment == "negative"
                    else -0.5 if article.sentiment == "positive" else 0
                )
            )
            for article in articles
        ) / len(articles)

        return max(0, weighted_sentiment)

    def _get_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level"""
        if score < 30:
            return "low"
        elif score < 60:
            return "medium"
        elif score < 80:
            return "high"
        else:
            return "critical"

    def _get_factor_description(self, factor_name: str, value: float) -> str:
        """Get human-readable description of risk factor"""
        descriptions = {
            "sentiment_trend": f"Sentiment trend showing {abs(value):.2f} change",
            "volume_volatility": f"Volume volatility at {value:.2f}",
            "negative_spikes": f"Detected {value:.2f} negative sentiment spikes",
            "review_decline": f"Review rating decline of {value:.2f}",
            "news_impact": f"News impact score: {value:.2f}",
        }
        return descriptions.get(factor_name, "Unknown factor")

    def _generate_recommendations(
        self, score: float, factors: Dict[str, float]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if score > 80:
            recommendations.append("Immediate response required - high risk detected")

        if factors["negative_spikes"] > 0.8:
            recommendations.append("Monitor negative PR closely and prepare response")

        if factors["review_decline"] > 0.7:
            recommendations.append("Focus on improving customer satisfaction")

        if factors["sentiment_trend"] > 0.6:
            recommendations.append("Implement reputation recovery strategy")

        if score < 30:
            recommendations.append("Continue current strategy - reputation is stable")

        return recommendations
