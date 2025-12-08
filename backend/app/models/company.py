# brandguard/backend/app/models/company.py
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String

from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    legal_name = Column(String, nullable=True)
    industry = Column(String, index=True)
    website = Column(String, nullable=True)
    country = Column(String, index=True)
    description = Column(String, nullable=True)

    # Reputation metrics
    reputation_score = Column(Float, default=0.0)  # 0-100
    reputation_trend = Column(Float, default=0.0)  # % change
    total_mentions = Column(Integer, default=0)
    positive_mentions = Column(Integer, default=0)
    negative_mentions = Column(Integer, default=0)
    neutral_mentions = Column(Integer, default=0)

    # Risk assessment
    risk_score = Column(Float, default=0.0)  # 0-100
    risk_factors = Column(JSON, default=list)

    # Metadata
    sources_config = Column(JSON, default=dict)  # Data source configurations
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)
    last_analyzed = Column(DateTime, nullable=True)


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # news, reviews, social, financial
    source_type = Column(String, index=True)
    url = Column(String, nullable=False)
    api_endpoint = Column(String, nullable=True)
    credibility_score = Column(Float, default=0.8)  # 0-1
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=100)
    last_accessed = Column(DateTime, nullable=True)
    api_key_required = Column(Boolean, default=False)

    # Compliance fields
    terms_accepted = Column(Boolean, default=False)
    privacy_compliant = Column(Boolean, default=True)
