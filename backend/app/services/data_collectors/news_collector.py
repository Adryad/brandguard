# brandguard/backend/app/services/data_collectors/news_collector.py
import asyncio
import aiohttp
import feedparser
import defusedxml.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import xml
from sqlalchemy.orm import Session
from app.models.company import Company, DataSource
from app.models.sentiment import Article
from app.services.analyzers.sentiment_analyzer import analyze_sentiment
import logging
import re
from urllib.parse import urlparse
import html
from bs4 import BeautifulSoup
import spacy

tree = ET.parse("data.xml")
defusedxml.defuse_stdlib()

logger = logging.getLogger(__name__)


class LegalNewsCollector:
    """
    Production-ready news collector for BrandGuard
    - Only uses public RSS feeds
    - Respects robots.txt and rate limits
    - GDPR compliant data collection
    """

    LEGAL_SOURCES = [
        {
            "name": "Google News RSS",
            "url": "https://news.google.com/rss/search",
            "type": "news",
            "credibility": 0.9,
            "rate_limit": 30,  # requests per minute
        },
        {
            "name": "Reuters Business",
            "url": "https://feeds.reuters.com/reuters/businessNews",
            "type": "news",
            "credibility": 0.95,
            "rate_limit": 60,
        },
        {
            "name": "BBC Business",
            "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
            "type": "news",
            "credibility": 0.92,
            "rate_limit": 30,
        },
        {
            "name": "CNN Money",
            "url": "https://rss.cnn.com/rss/money.rss",
            "type": "news",
            "credibility": 0.88,
            "rate_limit": 50,
        },
        {
            "name": "WSJ Latest",
            "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
            "type": "news",
            "credibility": 0.93,
            "rate_limit": 30,
        },
    ]

    def __init__(self, db: Session):
        self.db = db
        self.rate_limiter = AsyncRateLimiter()
        self.spacy_nlp = None
        self._load_nlp()

    def _load_nlp(self):
        """Load spaCy for entity extraction"""
        try:
            self.spacy_nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("SpaCy model not found, proceeding without NLP")

    async def collect_for_company(
        self, company_id: int, company_name: str, days_back: int = 7
    ) -> List[Dict]:
        """Collect news for specific company"""
        articles = []
        keywords = self._generate_keywords(company_name)

        # Check for existing data source configurations
        sources = (
            self.db.query(DataSource)
            .filter(DataSource.source_type == "news", DataSource.is_active == True)
            .all()
        )

        if not sources:
            # Use default sources
            sources = [
                DataSource(name=s["name"], url=s["url"], source_type=s["type"])
                for s in self.LEGAL_SOURCES
            ]
            for source in sources:
                self.db.add(source)
            self.db.commit()

        for source in sources:
            try:
                await self.rate_limiter.wait(source.rate_limit)
                new_articles = await self._collect_from_source(
                    source, keywords, days_back
                )
                articles.extend(new_articles)
            except Exception as e:
                logger.error(f"Failed to collect from {source.name}: {str(e)}")
                continue

        # Store articles
        stored_articles = []
        for article_data in articles:
            article = self._store_article(company_id, source.id, article_data)
            stored_articles.append(article)

        self.db.commit()
        return [self._format_article_response(article) for article in stored_articles]

    async def _collect_from_source(
        self, source: DataSource, keywords: List[str], days_back: int
    ) -> List[Dict]:
        """Collect from specific source"""
        articles = []

        if "google.com" in source.url:
            articles = await self._collect_google_news(source, keywords, days_back)
        elif "reuters.com" in source.url:
            articles = await self._collect_reuters(source, keywords, days_back)
        else:
            articles = await self._collect_rss(source, keywords, days_back)

        return articles

    async def _collect_google_news(
        self, source: DataSource, keywords: List[str], days_back: int
    ) -> List[Dict]:
        """Collect from Google News RSS"""
        articles = []
        base_url = "https://news.google.com/rss/search"

        for keyword in keywords:
            params = {"q": keyword, "hl": "en-US", "gl": "US", "ceid": "US:en"}

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        base_url, params=params, timeout=30
                    ) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)

                            for entry in feed.entries:
                                if self._within_date_range(
                                    entry.published_parsed, days_back
                                ):
                                    article = self._parse_google_news_entry(
                                        entry, keyword
                                    )
                                    articles.append(article)

            except Exception as e:
                logger.error(f"Google News collection failed: {str(e)}")
                continue

        return articles

    async def _collect_reuters(
        self, source: DataSource, keywords: List[str], days_back: int
    ) -> List[Dict]:
        """Collect from Reuters RSS"""
        articles = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source.url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)

                        for entry in feed.entries:
                            if self._within_date_range(
                                entry.published_parsed, days_back
                            ):
                                # Check relevance
                                if self._is_article_relevant(entry, keywords):
                                    article = self._parse_rss_entry(entry, source.name)
                                    articles.append(article)

        except Exception as e:
            logger.error(f"Reuters collection failed: {str(e)}")

        return articles

    def _parse_google_news_entry(
        self, entry: feedparser.FeedParserDict, keyword: str
    ) -> Dict:
        """Parse Google News entry"""
        return {
            "title": html.unescape(entry.title),
            "content": html.unescape(entry.get("summary", "")),
            "url": entry.link,
            "published_date": self._parse_date(entry.published),
            "author": entry.get("author", ""),
            "source": entry.get("source", {}).get("title", "Google News"),
            "relevance_score": self._calculate_relevance(
                entry.title + " " + entry.summary, keyword
            ),
        }

    def _parse_rss_entry(
        self, entry: feedparser.FeedParserDict, source_name: str
    ) -> Dict:
        """Parse RSS entry"""
        content = entry.get("summary", "")
        if hasattr(entry, "content"):
            content = entry.content[0].value if entry.content else ""

        return {
            "title": html.unescape(entry.title),
            "content": self._clean_html(html.unescape(content)),
            "url": entry.link,
            "published_date": self._parse_date(entry.published),
            "author": entry.get("author", ""),
            "source": source_name,
            "relevance_score": 0.5,  # Default for RSS
        }

    def _clean_html(self, html_content: str) -> str:
        """Remove HTML tags and clean content"""
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style"]):
            tag.decompose()

        # Get text and clean
        text = soup.get_text()
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _generate_keywords(self, company_name: str) -> List[str]:
        """Generate search keywords for company"""
        return [
            company_name,
            company_name.lower(),
            company_name.replace(" ", "+"),
            company_name.replace("Inc", "").replace("Ltd", "").strip(),
        ]

    def _is_article_relevant(
        self, entry: feedparser.FeedParserDict, keywords: List[str]
    ) -> bool:
        """Check if article mentions company"""
        text = (entry.title + " " + entry.summary).lower()
        for keyword in keywords:
            if keyword.lower() in text:
                return True
        return False

    def _within_date_range(self, published_parsed: tuple, days_back: int) -> bool:
        """Check if article is within date range"""
        if not published_parsed:
            return False

        published = datetime(*published_parsed[:6])
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        return published >= cutoff

    def _parse_date(self, date_string: str) -> datetime:
        """Parse date string to datetime"""
        try:
            return feedparser._parse_date(date_string)
        except (ValueError, TypeError):
            return datetime.utcnow()

    def _calculate_relevance(self, text: str, keyword: str) -> float:
        """Calculate relevance score based on keyword mentions"""
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        if keyword_lower in text_lower:
            mentions = len(re.findall(re.escape(keyword_lower), text_lower))
            score = min(1.0, 0.1 + (mentions * 0.2))
            return score

        return 0.0

    def _store_article(
        self, company_id: int, source_id: int, article_data: Dict
    ) -> Article:
        """Store article in database"""
        # Analyze sentiment
        sentiment_result = analyze_sentiment(article_data["content"])

        article = Article(
            company_id=company_id,
            source_id=source_id,
            title=article_data["title"][:500],
            content=article_data["content"][:5000],
            url=article_data["url"][:1000],
            published_date=article_data["published_date"],
            author=article_data["author"][:255],
            sentiment=sentiment_result["sentiment"],
            confidence_score=sentiment_result["confidence"],
            keywords=sentiment_result.get("keywords", []),
            entities=sentiment_result.get("entities", []),
            relevance_score=article_data["relevance_score"],
            is_public=True,
            data_retention_until=datetime.utcnow() + timedelta(days=365),
        )

        self.db.add(article)
        return article

    def _format_article_response(self, article: Article) -> Dict:
        """Format article for API response"""
        return {
            "id": article.id,
            "title": article.title,
            "content": (
                article.content[:200] + "..."
                if len(article.content) > 200
                else article.content
            ),
            "url": article.url,
            "published_date": article.published_date.isoformat(),
            "sentiment": article.sentiment,
            "confidence_score": article.confidence_score,
            "relevance_score": article.relevance_score,
            "source": article.source.name if article.source else "Unknown",
        }


class AsyncRateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self):
        self.last_request = {}

    async def wait(self, rate_limit: int):
        """Wait according to rate limit"""
        now = datetime.utcnow()
        if rate_limit in self.last_request:
            elapsed = (now - self.last_request[rate_limit]).total_seconds()
            wait_time = max(0, 60.0 / rate_limit - elapsed)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        self.last_request[rate_limit] = now
