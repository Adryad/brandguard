# brandguard/backend/app/services/payment/stripe_service.py
import stripe
from datetime import datetime
from typing import Dict, Optional
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class StripePaymentService:
    """Complete Stripe integration for subscriptions"""

    PRICING_PLANS = {
        "starter": {
            "price_id": "price_starter_monthly",
            "amount": 4900,  # $49/month
            "features": ["monitor_10_companies", "email_alerts", "basic_analytics"],
        },
        "professional": {
            "price_id": "price_professional_monthly",
            "amount": 12900,  # $129/month
            "features": ["monitor_50_companies", "multi_channel_alerts", "api_access"],
        },
        "enterprise": {
            "price_id": "price_enterprise_monthly",
            "amount": 29900,  # $299/month
            "features": ["unlimited_companies", "custom_integrations", "white_label"],
        },
    }

    async def create_checkout_session(
        self, user_email: str, plan_id: str, success_url: str, cancel_url: str
    ) -> Dict:
        """Create Stripe checkout session"""
        plan = self.PRICING_PLANS.get(plan_id)
        if not plan:
            raise ValueError("Invalid plan")

        session = stripe.checkout.Session.create(
            customer_email=user_email,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": plan["price_id"],
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            metadata={"plan_id": plan_id},
        )

        return {"session_id": session.id, "url": session.url}

    async def handle_webhook(self, payload: bytes, sig_header: str) -> bool:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
            )

            if event["type"] == "customer.subscription.updated":
                subscription = event["data"]["object"]
                await self._update_subscription(subscription)

            elif event["type"] == "customer.subscription.deleted":
                subscription = event["data"]["object"]
                await self._cancel_subscription(subscription)

            elif event["type"] == "invoice.payment_succeeded":
                invoice = event["data"]["object"]
                await self._handle_payment_success(invoice)

            return True

        except ValueError:
            return False

    async def generate_usage_report(self, subscription_id: str, usage: Dict) -> Dict:
        """Generate usage-based billing report"""
        subscription = stripe.Subscription.retrieve(subscription_id)

        report = {
            "subscription_id": subscription_id,
            "period_start": datetime.fromtimestamp(subscription.current_period_start),
            "period_end": datetime.fromtimestamp(subscription.current_period_end),
            "plan": subscription.items.data[0].price.nickname,
            "usage_breakdown": usage,
            "estimated_cost": self._calculate_usage_cost(usage),
        }

        return report
