# brandguard/load_tests/locustfile.py
from locust import HttpUser, task, between
import random

class BrandGuardUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_companies(self):
        self.client.get("/api/v1/companies?limit=10")
    
    @task(2)
    def get_company(self):
        company_id = random.randint(1, 100)
        with self.client.get(f"/api/v1/companies/{company_id}", catch_response=True) as response:
            if response.status_code == 404:
                response.success()
    
    @task(1)
    def create_company(self):
        self.client.post("/api/v1/companies", json={
            "name": f"Load Test Company {random.randint(1000, 9999)}",
            "industry": "technology"
        })