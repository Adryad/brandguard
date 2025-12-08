# brandguard/backend/app/services/data_collectors/news_collector.py
import asyncio
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.company import Company, DataSource
from app.models.sentiment import Article
from app.services.analyzers.sentiment_analyzer import analyze_sentiment

logger = logging.getLogger(__name__)


class LegalNewsCollector:
    """
    Collects news data from public RSS feeds and legal news sources
    """

    ALLOWED_DOMAINS = [
        "reuters.com",
        "bloomberg.com",
        "wsj.com",
        "ft.com",
        "cnbc.com",
        "marketwatch.com",
        "forbes.com",
        "bloomberg.com",
        "apnews.com",
        "upi.com",
        "afp.com",
    ]

    def __init__(self, db: Session):
        self.db = db
        self.session = None
        self.rate_limiter = RateLimiter(requests_per_minute=30)

    async def collect_company_news(
        self, company: Company, days_back: int = 30
    ) -> List[Dict]:
        """
        Collect public news articles about a company
        """
        articles = []
        company_keywords = self._extract_keywords(company.name, company.industry)

        # Get active news sources
        sources = (
            self.db.query(DataSource)
            .filter(
                DataSource.source_type == "news",
                DataSource.is_active == True,
                DataSource.terms_accepted == True,
            )
            .all()
        )

        for source in sources:
            try:
                await self.rate_limiter.wait()
                articles.extend(
                    await self._fetch_from_source(source, company_keywords, days_back)
                )
            except Exception as e:
                logger.error(f"Error fetching from {source.name}: {str(e)}")
                continue

        # Store articles
        stored_articles = []
        for article_data in articles:
            if self._is_compliant(article_data):
                article = self._store_article(company.id, source.id, article_data)
                stored_articles.append(article)

        return stored_articles

    async def _fetch_from_source(
        self, source: DataSource, keywords: List[str], days_back: int
    ) -> List[Dict]:
        """
        Fetch articles from a specific source
        """
        articles = []

        if "rss" in source.url.lower():
            articles = await self._fetch_rss_feed(source.url, keywords, days_back)
        elif "api" in source.url.lower() and source.api_endpoint:
            articles = await self._fetch_api_data(source, keywords, days_back)

        return articles

    async def _fetch_rss_feed(
        self, rss_url: str, keywords: List[str], days_back: int
    ) -> List[Dict]:
        """
        Fetch and parse RSS feed
        """
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(rss_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_rss_content(content, keywords, days_back)
        except Exception as e:
            logger.error(f"RSS fetch error: {str(e)}")

        return []

    def _parse_rss_content(
        self, content: str, keywords: List[str], days_back: int
    ) -> List[Dict]:
        """
        Parse RSS XML content
        """
        articles = []
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        try:
            root = ET.fromstring(content)
            channel = root.find("channel")

            if channel is None:
                return articles

            for item in channel.findall("item"):
                article_data = self._extract_article_data(item)

                if article_data["published_date"] >= cutoff_date:
                    # Check relevance
                    relevance = self._calculate_relevance(article_data, keywords)
                    if relevance > 0.3:  # 30% relevance threshold
                        article_data["relevance_score"] = relevance
                        articles.append(article_data)

        except ET.ParseError as e:
            logger.error(f"RSS parse error: {str(e)}")

        return articles

    def _extract_article_data(self, item: ET.Element) -> Dict:
        """
        Extract article data from RSS item
        """
        title = item.findtext("title", "")
        description = item.findtext("description", "")
        link = item.findtext("link", "")
        pub_date = item.findtext("pubDate", "")
        author = item.findtext("author", "")

        # Parse publication date
        pub_date_dt = self._parse_date(pub_date)

        # Clean HTML from description
        if description:
            soup = BeautifulSoup(description, "html.parser")
            description = soup.get_text()

        return {
            "title": title,
            "content": description,
            "url": link,
            "published_date": pub_date_dt or datetime.utcnow(),
            "author": author,
            "source_type": "rss",
        }

    def _calculate_relevance(self, article: Dict, keywords: List[str]) -> float:
        """
        Calculate article relevance to company
        """
        text = f"{article['title']} {article['content']}".lower()

        matches = 0
        for keyword in keywords:
            matches += text.count(keyword.lower())

        # Simple relevance calculation
        return min(matches / len(keywords), 1.0)

    def _extract_keywords(self, company_name: str, industry: str) -> List[str]:
        """
        Extract keywords for company matching
        """
        keywords = [company_name]

        # Add industry-specific terms
        industry_terms = {
            "technology": ["software", "tech", "digital", "innovation"],
            "finance": ["bank", "financial", "investment", "fintech"],
            "healthcare": ["medical", "health", "pharma", "hospital"],
            "retail": ["store", "retail", "ecommerce", "shopping"],
        }

        if industry.lower() in industry_terms:
            keywords.extend(industry_terms[industry.lower()])

        return keywords

    def _is_compliant(self, article: Dict) -> bool:
        """
        Check if article data is compliant with privacy rules
        """
        # Ensure no personal data is stored
        if article.get("content"):
            # Remove email addresses, phone numbers, etc.
            article["content"] = self._sanitize_content(article["content"])

        # Ensure source is public
        if article.get("source_type") == "private":
            return False

        return True

    def _sanitize_content(self, content: str) -> str:
        """
        Remove personal information from content
        """
        # Remove email addresses
        content = re.sub(r"\S+@\S+", "[EMAIL]", content)

        # Remove phone numbers
        content = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]", content)

        return content

    def _store_article(
        self, company_id: int, source_id: int, article_data: Dict
    ) -> Article:
        """
        Store article in database with sentiment analysis
        """
        # Analyze sentiment
        sentiment_result = analyze_sentiment(article_data["content"])

        article = Article(
            company_id=company_id,
            source_id=source_id,
            title=article_data["title"],
            content=article_data["content"],
            url=article_data["url"],
            published_date=article_data["published_date"],
            author=article_data.get("author"),
            sentiment=sentiment_result["sentiment"],
            confidence_score=sentiment_result["confidence"],
            keywords=sentiment_result.get("keywords", []),
            entities=sentiment_result.get("entities", []),
            relevance_score=article_data.get("relevance_score", 0),
            is_public=True,
            data_retention_until=datetime.utcnow()
            + timedelta(days=settings.DATA_RETENTION_DAYS),
        )

        self.db.add(article)
        return article

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse various date formats
        """
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None


class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request = None

    async def wait(self):
        if self.last_request:
            elapsed = (datetime.utcnow() - self.last_request).total_seconds()
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
        self.last_request = datetime.utcnow()
