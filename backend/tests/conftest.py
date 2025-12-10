import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from fastapi import FastAPI


# Register markers
def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: async test")
    config.addinivalue_line("markers", "integration: integration test")
    config.addinivalue_line("markers", "unit: unit test")


# Test app
@pytest.fixture
def app():
    app = FastAPI(title="BrandGuard Test")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/api/v1/companies")
    async def get_companies():
        return [{"id": 1, "name": "Test Company", "industry": "tech"}]

    @app.post("/api/v1/companies")
    async def create_company():
        return {"id": 1, "status": "created"}

    return app


# Clients
@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Database mocks
@pytest.fixture
async def db_session():
    from unittest.mock import AsyncMock

    session = AsyncMock()
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock(return_value=AsyncMock())
    yield session


# Test data
@pytest.fixture
def test_company():
    return {"id": 1, "name": "Test Corp", "industry": "technology"}
