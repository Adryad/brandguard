# brandguard/backend/app/db/session.py (Updated)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import redis
from elasticsearch import Elasticsearch

# Create engine with connection pooling (configured via requirements.txt)
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,  # Set True for debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis client (from redis library in requirements.txt)
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_keepalive=True,
    socket_keepalive_options={
        "tcp_keepalive": 1,
        "tcp_keepalive_time": 300,
        "tcp_keepalive_interval": 10,
        "tcp_keepalive_probes": 5,
    },
)

# Elasticsearch client (from elasticsearch library in requirements.txt)
es_client = Elasticsearch(
    settings.ELASTICSEARCH_URL,
    verify_certs=False,
    ssl_show_warn=False,
    max_retries=3,
    retry_on_timeout=True,
)


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    """Redis client dependency"""
    return redis_client


def get_elasticsearch():
    """Elasticsearch client dependency"""
    return es_client
