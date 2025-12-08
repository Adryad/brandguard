# brandguard/backend/app/services/analyzers/trend_analyzer.py
import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.sentiment import Article, Review
import pandas as pd
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """
    Analyze trends in company reputation data
    """

    def __init__(self, db: Session):
        self.db = db

    def analyze_company_trends(self, company_id: int, days: int = 90) -> Dict:
        """
        Analyze trends for a specific company
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get articles and reviews
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

        # Combine data
        data_points = []

        for article in articles:
            data_points.append(
                {
                    "date": article.created_at.date(),
                    "sentiment_score": self._sentiment_to_score(article.sentiment),
                    "confidence": article.confidence_score,
                    "type": "article",
                }
            )

        for review in reviews:
            data_points.append(
                {
                    "date": review.created_at.date(),
                    "sentiment_score": review.rating / 5.0,  # Normalize to 0-1
                    "confidence": 0.8,
                    "type": "review",
                }
            )

        if not data_points:
            return {
                "trend": "stable",
                "momentum": 0.0,
                "predictions": [],
                "seasonal_patterns": [],
                "volatility": 0.0,
            }

        # Analyze trends
        trend_analysis = self._calculate_trend(data_points)
        seasonal_analysis = self._detect_seasonal_patterns(data_points)
        predictions = self._predict_future(data_points, days=30)
        volatility = self._calculate_volatility(data_points)

        return {
            "trend": trend_analysis["trend"],
            "momentum": trend_analysis["momentum"],
            "predictions": predictions,
            "seasonal_patterns": seasonal_analysis,
            "volatility": volatility,
            "data_points": len(data_points),
        }

    def _sentiment_to_score(self, sentiment: str) -> float:
        """
        Convert sentiment string to numeric score
        """
        mapping = {"positive": 1.0, "negative": 0.0, "neutral": 0.5}
        return mapping.get(sentiment, 0.5)

    def _calculate_trend(self, data_points: List[Dict]) -> Dict:
        """
        Calculate overall trend direction and momentum
        """
        if len(data_points) < 7:
            return {"trend": "stable", "momentum": 0.0}

        # Convert to DataFrame
        df = pd.DataFrame(data_points)
        df["date"] = pd.to_datetime(df["date"])
        df = df.groupby("date")["sentiment_score"].mean().reset_index()

        # Calculate moving averages
        df["ma_7"] = df["sentiment_score"].rolling(window=7).mean()
        df["ma_14"] = df["sentiment_score"].rolling(window=14).mean()
        df["ma_30"] = df["sentiment_score"].rolling(window=30).mean()

        # Determine trend
        recent_ma = (
            df["ma_7"].iloc[-1]
            if not pd.isna(df["ma_7"].iloc[-1])
            else df["sentiment_score"].iloc[-1]
        )
        older_ma = df["ma_7"].iloc[-8] if len(df) > 8 else df["sentiment_score"].iloc[0]

        momentum = recent_ma - older_ma

        if momentum > 0.1:
            trend = "improving"
        elif momentum < -0.1:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "momentum": momentum,
            "recent_score": recent_ma,
            "change_percentage": (momentum / older_ma) * 100 if older_ma > 0 else 0,
        }

    def _detect_seasonal_patterns(self, data_points: List[Dict]) -> List[Dict]:
        """
        Detect seasonal patterns in sentiment
        """
        if len(data_points) < 90:
            return []

        df = pd.DataFrame(data_points)
        df["date"] = pd.to_datetime(df["date"])
        df["day_of_week"] = df["date"].dt.dayofweek
        df["month"] = df["date"].dt.month

        # Weekly patterns
        weekly_pattern = df.groupby("day_of_week")["sentiment_score"].mean()

        # Monthly patterns
        monthly_pattern = df.groupby("month")["sentiment_score"].mean()

        patterns = []

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for i, score in weekly_pattern.items():
            if score > 0.6 or score < 0.4:
                patterns.append(
                    {
                        "type": "weekly",
                        "period": days[i],
                        "score": score,
                        "significance": "high" if abs(score - 0.5) > 0.2 else "medium",
                    }
                )

        months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        for i, score in monthly_pattern.items():
            if score > 0.6 or score < 0.4:
                patterns.append(
                    {
                        "type": "monthly",
                        "period": months[i - 1],
                        "score": score,
                        "significance": "high" if abs(score - 0.5) > 0.2 else "medium",
                    }
                )

        return patterns

    def _predict_future(self, data_points: List[Dict], days: int = 30) -> List[Dict]:
        """
        Predict future sentiment trends
        """
        if len(data_points) < 14:
            return []

        df = pd.DataFrame(data_points)
        df["date"] = pd.to_datetime(df["date"])
        df = df.groupby("date")["sentiment_score"].mean().reset_index()

        # Prepare data for linear regression
        X = np.arange(len(df)).reshape(-1, 1)
        y = df["sentiment_score"].values

        # Fit model
        model = LinearRegression()
        model.fit(X, y)

        # Generate predictions
        predictions = []
        last_date = df["date"].max()

        for i in range(1, days + 1):
            future_date = last_date + timedelta(days=i)
            X_future = np.array([[len(df) + i]])
            predicted_score = model.predict(X_future)[0]

            # Ensure score is between 0 and 1
            predicted_score = max(0, min(1, predicted_score))

            predictions.append(
                {
                    "date": future_date.strftime("%Y-%m-%d"),
                    "predicted_score": float(predicted_score),
                    "confidence": float(1 - abs(model.score(X, y))),
                }
            )

        return predictions[:7]  # Return only next 7 days

    def _calculate_volatility(self, data_points: List[Dict]) -> float:
        """
        Calculate sentiment volatility
        """
        if len(data_points) < 7:
            return 0.0

        scores = [dp["sentiment_score"] for dp in data_points]
        return float(np.std(scores))

    def generate_trend_summary(self, trends_data: Dict) -> str:
        """
        Generate human-readable trend summary
        """
        trend = trends_data["trend"]
        momentum = trends_data["momentum"]
        volatility = trends_data["volatility"]

        if trend == "improving":
            summary = f"Reputation is improving with a momentum of {momentum:.2%}. "
        elif trend == "declining":
            summary = (
                f"Reputation is declining with a momentum of {abs(momentum):.2%}. "
            )
        else:
            summary = "Reputation trend is stable. "

        if volatility > 0.2:
            summary += "High volatility detected in sentiment scores. "
        elif volatility > 0.1:
            summary += "Moderate volatility in sentiment scores. "
        else:
            summary += "Low volatility in sentiment scores. "

        if trends_data["predictions"]:
            avg_prediction = np.mean(
                [p["predicted_score"] for p in trends_data["predictions"]]
            )
            if avg_prediction > 0.6:
                summary += "Positive sentiment expected in the coming days."
            elif avg_prediction < 0.4:
                summary += "Negative sentiment expected in the coming days."
            else:
                summary += "Neutral sentiment expected in the coming days."

        return summary
