# brandguard/backend/tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.db.base import Base
from tests.factories import CompanyFactory, ArticleFactory

# Override test database
SQLALCHEMY_DATABASE_URL = (
    "postgresql://brandguard:password@localhost:5433/test_brandguard"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_company():
    return CompanyFactory()


@pytest.fixture
def test_articles():
    return ArticleFactory.create_batch(5)


@pytest.fixture
async def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
