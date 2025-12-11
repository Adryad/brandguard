# brandguard/backend/app/services/data_collectors/financial_collector.py
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional
import os
from sqlalchemy.orm import Session
from app.models.sentiment import Article
import pandas as pd


class FinancialDataCollector:
    """
    Collect financial data using Alpha Vantage API
    Free tier: 5 calls per minute, 500 per day
    """

    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            logger.warning("Alpha Vantage API key not configured")

    async def collect_stock_news(self, company: object) -> List[Dict]:
        """Collect financial news for public companies"""
        if not self.api_key:
            return []

        if not company.tickers:
            return []

        articles = []
        for ticker in company.tickers.split(","):
            ticker = ticker.strip()
            news = await self._get_financial_news(ticker)
            articles.extend(news)

        return articles

    async def _get_financial_news(self, ticker: str) -> List[Dict]:
        """Get financial news from Alpha Vantage"""
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "apikey": self.api_key,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_financial_news(data, ticker)
        except Exception as e:
            logger.error(f"Alpha Vantage API error: {str(e)}")

        return []

    def _parse_financial_news(self, data: Dict, ticker: str) -> List[Dict]:
        """Parse Alpha Vantage financial news"""
        articles = []

        if "feed" in data:
            for item in data["feed"]:
                article = {
                    "title": item["title"],
                    "content": item.get("summary", ""),
                    "url": item["url"],
                    "published_date": datetime.strptime(
                        item["time_published"], "%Y%m%dT%H%M%S"
                    ),
                    "author": item.get("authors", [{}])[0].get("name", ""),
                    "source": "AlphaVantage",
                    "sentiment": self._map_sentiment(
                        item.get("overall_sentiment_label", "Neutral")
                    ),
                    "confidence_score": abs(item.get("overall_sentiment_score", 0))
                    / 1.0,
                    "relevance_score": 0.8,  # Higher relevance for ticker-specific news
                }
                articles.append(article)

        return articles

    def _map_sentiment(self, alpha_sentiment: str) -> str:
        """Map Alpha Vantage sentiment to our format"""
        mapping = {"Bullish": "positive", "Bearish": "negative", "Neutral": "neutral"}
        return mapping.get(alpha_sentiment, "neutral")
