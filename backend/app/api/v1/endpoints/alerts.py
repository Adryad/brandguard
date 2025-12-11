# brandguard/backend/app/api/v1/endpoints/alerts.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.models.company import Alert
from app.services.notifications.alert_service import AlertService

router = APIRouter()


class AlertCreate(BaseModel):
    name: str
    condition: str
    severity: str = "medium"
    channels: List[str] = []
    cooldown_hours: int = 24


class AlertResponse(AlertCreate):
    id: int
    is_active: bool
    created_at: str


@router.post("/", response_model=AlertResponse)
async def create_alert(
    company_id: int, alert: AlertCreate, db: Session = Depends(get_db)
):
    """Create new alert rule for company"""
    db_alert = Alert(company_id=company_id, **alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    company_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """List company alerts"""
    return (
        db.query(Alert)
        .filter(Alert.company_id == company_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/{alert_id}/test")
async def test_alert(company_id: int, alert_id: int, db: Session = Depends(get_db)):
    """Test alert rule"""
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.company_id == company_id)
        .first()
    )

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    service = AlertService(db)
    await service.test_alert(alert)

    return {"message": "Test alert sent"}
