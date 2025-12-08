# brandguard/backend/app/models/sentiment.py
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)

    # Article data
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String, nullable=False)
    published_date = Column(DateTime, nullable=False)
    author = Column(String, nullable=True)

    # Analysis results
    sentiment = Column(String, default="neutral")  # positive, negative, neutral
    confidence_score = Column(Float, default=0.0)  # 0-1
    keywords = Column(JSON, default=list)
    entities = Column(JSON, default=list)
    relevance_score = Column(Float, default=0.0)  # 0-1

    # Compliance
    is_public = Column(Boolean, default=True)
    data_retention_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    platform = Column(String, nullable=False)  # trustpilot, google, etc.

    # Review data (public only)
    reviewer_id = Column(String, nullable=True)  # Anonymized
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    review_date = Column(DateTime, nullable=False)

    # Analysis
    sentiment = Column(String, default="neutral")
    verified = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)

    # Compliance
    platform_terms_compliant = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
