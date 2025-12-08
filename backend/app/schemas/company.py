from typing import Optional
from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    reputation_score: float = 0.0
    total_mentions: int = 0
    
    class Config:
        from_attributes = True
