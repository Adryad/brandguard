# brandguard/backend/tests/integration/test_companies.py
import pytest
from httpx import AsyncClient
from app.main import app
from tests.conftest import *
from sqlalchemy.ext.asyncio import AsyncSession

class TestCompaniesAPI:
    @pytest.mark.asyncio
    async def test_create_company(self, async_client: AsyncClient, db_session: AsyncSession):
        """Test creating a company via API"""
        company_data = {
            "name": "Test Corp",
            "industry": "technology",
            "country": "USA"
        }
        
        response = await async_client.post("/api/v1/companies", json=company_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Corp"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_companies(self, async_client: AsyncClient, test_company):
        """Test listing companies with pagination"""
        response = await async_client.get("/api/v1/companies?limit=10&skip=0")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10