# brandguard/backend/app/api/v1/endpoints/companies.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.analyzers.trend_analyzer import TrendAnalyzer
from app.services.data_collectors.news_collector import LegalNewsCollector

router = APIRouter()


@router.post("/", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new company for monitoring
    """
    # Check if company already exists
    existing = db.query(Company).filter(Company.name == company.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company already exists")

    # Create company
    db_company = Company(
        name=company.name,
        legal_name=company.legal_name,
        industry=company.industry,
        website=company.website,
        country=company.country,
        description=company.description,
        sources_config=company.sources_config or {},
    )

    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    # Trigger initial data collection
    collector = LegalNewsCollector(db)
    await collector.collect_company_news(db_company, days_back=7)

    return CompanyResponse.from_orm(db_company)


@router.get("/", response_model=List[CompanyResponse])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    industry: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    List all monitored companies with optional filters
    """
    query = db.query(Company).filter(Company.is_active)

    if industry:
        query = query.filter(Company.industry == industry)

    if search:
        query = query.filter(Company.name.contains(search))

    companies = query.offset(skip).limit(limit).all()

    return [CompanyResponse.from_orm(c) for c in companies]


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get detailed company information
    """
    company = (
        db.query(Company).filter(
            Company.id == company_id,
            Company.is_active).first())

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanyResponse.from_orm(company)


@router.get("/{company_id}/trends")
def get_company_trends(
    company_id: int,
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get trend analysis for a company
    """
    company = (
        db.query(Company).filter(
            Company.id == company_id,
            Company.is_active).first())

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    analyzer = TrendAnalyzer(db)
    trends = analyzer.analyze_company_trends(company_id, days)

    return {
        "company_id": company_id,
        "company_name": company.name,
        "analysis_period_days": days,
        "trends": trends,
        "summary": analyzer.generate_trend_summary(trends),
    }


@router.post("/{company_id}/refresh")
async def refresh_company_data(
    company_id: int,
    days_back: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Manually trigger data refresh for a company
    """
    company = (
        db.query(Company).filter(
            Company.id == company_id,
            Company.is_active).first())

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Collect fresh data
    collector = LegalNewsCollector(db)
    new_articles = await collector.collect_company_news(company, days_back)

    # Update company metrics
    company.last_analyzed = datetime.utcnow()
    company.total_mentions = len(new_articles)

    # Recalculate reputation score
    positive = sum(1 for a in new_articles if a.sentiment == "positive")
    negative = sum(1 for a in new_articles if a.sentiment == "negative")
    neutral = len(new_articles) - positive - negative

    if new_articles:
        company.reputation_score = (positive / len(new_articles)) * 100
        company.positive_mentions = positive
        company.negative_mentions = negative
        company.neutral_mentions = neutral

    db.commit()

    return {
        "message": f"Refreshed data for {company.name}",
        "new_articles": len(new_articles),
        "total_mentions": company.total_mentions,
    }


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update company information
    """
    company = (
        db.query(Company).filter(
            Company.id == company_id,
            Company.is_active).first())

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Update fields
    for field, value in company_update.dict(exclude_unset=True).items():
        setattr(company, field, value)

    company.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(company)

    return CompanyResponse.from_orm(company)


@router.delete("/{company_id}")
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Soft delete a company (set is_active to False)
    """
    company = (
        db.query(Company).filter(
            Company.id == company_id,
            Company.is_active).first())

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.is_active = False
    company.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Company {company.name} deleted successfully"}
