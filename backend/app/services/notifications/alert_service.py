# brandguard/backend/app/services/notifications/alert_service.py
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
from bs4 import BeautifulSoup


class AlertConfig(BaseModel):
    name: str
    condition: str  # e.g., "reputation_score < 60"
    severity: str  # low, medium, high, critical
    channels: List[str] = ["email"]
    cooldown_hours: int = 24


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    async def evaluate_alerts(self, company_id: int, new_data: Dict):
        """Evaluate all alert rules for company"""
        alerts = (
            self.db.query(Alert)
            .filter(Alert.company_id == company_id, Alert.is_active == True)
            .all()
        )

        for alert in alerts:
            if self._should_trigger(alert, new_data):
                await self._trigger_alert(alert, new_data)
