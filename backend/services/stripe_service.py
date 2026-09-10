"""Stripe Checkout and webhook helpers."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import uuid
import stripe
from fastapi import HTTPException, status
from config import settings
import logging

logger = logging.getLogger(__name__)


@dataclass
class CheckoutSessionResult:
    id: str
    url: str
    mock_mode: bool = False


def configure_stripe() -> None:
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe is not configured. Set STRIPE_SECRET_KEY.",
        )
    stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(
    order_id: int,
    user_id: int,
    customer_email: str,
    line_items: List[Dict[str, Any]],
) -> CheckoutSessionResult:
    """Create a Stripe Checkout Session, or a mock session in demo mode."""
    if settings.use_stripe_mock:
        session_id = f"cs_mock_{order_id}_{uuid.uuid4().hex[:10]}"
        checkout_url = (
            f"{settings.FRONTEND_URL}/checkout/mock"
            f"?session_id={session_id}&order_id={order_id}"
        )
        logger.info(f"Mock checkout session created: {session_id} for order {order_id}")
        return CheckoutSessionResult(id=session_id, url=checkout_url, mock_mode=True)

    configure_stripe()

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=(
                f"{settings.FRONTEND_URL}/orders"
                f"?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
            ),
            cancel_url=f"{settings.FRONTEND_URL}/checkout?payment=cancelled",
            customer_email=customer_email,
            metadata={
                "order_id": str(order_id),
                "user_id": str(user_id),
            },
        )
        return CheckoutSessionResult(id=session.id, url=session.url or "", mock_mode=False)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe session creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}",
        )


def verify_checkout_session(session_id: str) -> Dict[str, Any]:
    """Retrieve checkout session details from Stripe (real mode only)."""
    configure_stripe()
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            "id": session.id,
            "payment_status": session.payment_status,
            "status": session.status,
            "metadata": dict(session.metadata or {}),
            "payment_intent": session.payment_intent,
            "currency": session.currency,
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe session verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to verify checkout session: {str(e)}",
        )


def construct_webhook_event(payload: bytes, sig_header: Optional[str]):
    """Verify Stripe webhook signature and return the event."""
    if settings.use_stripe_mock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe webhooks are disabled in mock mode. Use /payments/mock-* endpoints.",
        )

    configure_stripe()

    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe webhook secret is not configured",
        )

    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header",
        )

    try:
        return stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )
