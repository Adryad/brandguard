# brandguard/backend/app/api/v1/endpoints/billing.py
import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanResponse(BaseModel):
    id: str
    name: str
    price: float
    features: List[str]
    usage_limit: Dict[str, int]


class SubscriptionCreate(BaseModel):
    plan_id: str
    payment_method: str


router = APIRouter()


@router.get("/plans", response_model=List[PlanResponse])
async def get_pricing_plans():
    """Get available pricing plans"""
    plans = [
        {
            "id": "starter",
            "name": "Starter",
            "price": 49,
            "features": ["Monitor 10 companies", "Email alerts", "Basic analytics"],
            "usage_limit": {"companies": 10, "metrics": 1000},
        },
        {
            "id": "professional",
            "name": "Professional",
            "price": 129,
            "features": [
                "Monitor 50 companies",
                "Multi-channel alerts",
                "Advanced analytics",
                "API access",
            ],
            "usage_limit": {"companies": 50, "metrics": 10000},
        },
        {
            "id": "enterprise",
            "name": "Enterprise",
            "price": 299,
            "features": [
                "Unlimited companies",
                "Custom integrations",
                "Dedicated support",
                "White-label",
            ],
            "usage_limit": {"companies": None, "metrics": None},
        },
    ]
    return plans


@router.post("/subscribe")
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create new subscription"""
    try:
        customer = stripe.Customer.create(
            email=get_user_email(db, current_user_id),
            payment_method=subscription.payment_method,
            invoice_settings={"default_payment_method": subscription.payment_method},
        )

        stripe_subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": subscription.plan_id}],
            expand=["latest_invoice.payment_intent"],
        )

        # Store subscription in database
        db_subscription = Subscription(
            user_id=current_user_id,
            stripe_subscription_id=stripe_subscription.id,
            plan_id=subscription.plan_id,
            status="active",
        )
        db.add(db_subscription)
        db.commit()

        return {"subscription": stripe_subscription}

    except stripe.error.CardError as e:
        raise HTTPException(status_code=400, detail=str(e))
