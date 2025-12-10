import pytest
import pytest_asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from fastapi import FastAPI


# Register marks
def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: async test")
    config.addinivalue_line("markers", "integration: integration test")


# Regular sync fixtures
@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI(title="BrandGuard Test")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/api/v1/companies")
    async def get_companies():
        return [{"id": 1, "name": "Test Company"}]

    @app.post("/api/v1/companies")
    async def create_company():
        return {"id": 1, "name": "Created Company"}

    return app


@pytest.fixture
def client(app):
    """Sync test client."""
    return TestClient(app)


# Async fixtures using pytest_asyncio
@pytest_asyncio.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """Async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session():
    """Mock database session."""
    from unittest.mock import AsyncMock

    session = AsyncMock()
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock(return_value=AsyncMock())
    yield session


@pytest.fixture
def test_company():
    return {"id": 1, "name": "Test Company"}
