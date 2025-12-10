import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
class TestCompaniesAPI:
    
    async def test_create_company(self, async_client, db_session):
        company_data = {"name": "Test Corp", "industry": "tech"}
        response = await async_client.post("/api/v1/companies", json=company_data)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "name" in data
    
    async def test_list_companies(self, async_client, test_company):
        response = await async_client.get("/api/v1/companies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
