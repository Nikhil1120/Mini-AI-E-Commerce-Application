"""
Payments router — Stripe Checkout session creation and webhook handling.

Business rules:
- Orders are created with payment_status=PENDING and status=PENDING.
- Stock is reduced ONLY after checkout.session.completed webhook (or mock-complete).
- Cart is cleared ONLY after successful payment.
- Frontend success redirect alone never marks an order as PAID.
- Failed payments set payment_status=FAILED; stock is not reduced.
- Cancelled checkout sets payment_status=CANCELLED; stock is not reduced.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
from models import User, Order, Payment, PaymentStatus, Product
from schemas import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PaymentVerificationResponse,
    MockPaymentRequest,
)
from dependencies import get_current_customer
from services.stripe_service import (
    create_checkout_session,
    construct_webhook_event,
    verify_checkout_session,
)
from services.payment_handlers import (
    process_checkout_completed,
    process_payment_failed,
    process_checkout_cancelled,
)
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])


def _ensure_mock_mode() -> None:
    if not settings.use_stripe_mock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mock payment endpoints are only available in Stripe mock mode",
        )


def _get_user_pending_order(
    db: Session,
    user: User,
    order_id: int | None = None,
) -> Order:
    query = db.query(Order).filter(
        Order.user_id == user.id,
        Order.payment_status == PaymentStatus.PENDING,
    )
    if order_id:
        query = query.filter(Order.id == order_id)
    order = query.order_by(Order.created_at.desc()).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending order found. Create an order first.",
        )
    if not order.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order has no items",
        )
    return order


def _validate_order_stock(db: Session, order: Order) -> None:
    for order_item in order.items:
        product = db.query(Product).filter(Product.id == order_item.product_id).first()
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{order_item.product_name}' is unavailable",
            )
        if order_item.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Insufficient stock for '{product.name}'. "
                    f"Available: {product.stock_quantity}"
                ),
            )


@router.post(
    "/create-checkout-session",
    response_model=CheckoutSessionResponse,
    summary="Create Stripe Checkout Session",
)
def create_checkout(
    body: CheckoutSessionRequest = CheckoutSessionRequest(),
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """
    Create a Stripe Checkout Session for a pending order.
    Uses mock checkout when dummy Stripe keys are configured.
    """
    order = _get_user_pending_order(db, current_user, body.order_id)
    _validate_order_stock(db, order)

    line_items = [
        {
            "price_data": {
                "currency": "usd",
                "unit_amount": int(round(item.price * 100)),
                "product_data": {"name": item.product_name},
            },
            "quantity": item.quantity,
        }
        for item in order.items
    ]

    session = create_checkout_session(
        order_id=order.id,
        user_id=current_user.id,
        customer_email=current_user.email,
        line_items=line_items,
    )

    order.stripe_session_id = session.id

    payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if not payment:
        payment = Payment(
            order_id=order.id,
            stripe_session_id=session.id,
            amount=order.total_amount,
            currency="USD",
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
    else:
        payment.stripe_session_id = session.id
        payment.status = PaymentStatus.PENDING

    db.commit()

    logger.info(f"Checkout session created: {session.id} for order {order.id}")

    return CheckoutSessionResponse(
        session_id=session.id,
        checkout_url=session.url,
        order_id=order.id,
        mock_mode=session.mock_mode,
    )


@router.get(
    "/verify-session/{session_id}",
    response_model=PaymentVerificationResponse,
    summary="Verify payment session status",
)
def verify_session(
    session_id: str,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Verify checkout/payment status for the current user's order."""
    order = (
        db.query(Order)
        .filter(
            Order.stripe_session_id == session_id,
            Order.user_id == current_user.id,
        )
        .first()
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found for this session",
        )

    verified = order.payment_status == PaymentStatus.PAID

    if not settings.use_stripe_mock and order.payment_status == PaymentStatus.PENDING:
        stripe_session = verify_checkout_session(session_id)
        if stripe_session.get("payment_status") == "paid" and not verified:
            meta_order_id = int((stripe_session.get("metadata") or {}).get("order_id", order.id))
            payment_intent = stripe_session.get("payment_intent")
            if isinstance(payment_intent, dict):
                payment_intent = payment_intent.get("id")
            order = process_checkout_completed(
                db,
                session_id,
                order_id=meta_order_id,
                payment_intent=payment_intent,
                currency=(stripe_session.get("currency") or "usd").upper(),
            )
            verified = order.payment_status == PaymentStatus.PAID

    return PaymentVerificationResponse(
        session_id=session_id,
        order_id=order.id,
        payment_status=order.payment_status,
        order_status=order.status,
        verified=verified,
        mock_mode=settings.use_stripe_mock,
    )


@router.post(
    "/mock-complete",
    response_model=PaymentVerificationResponse,
    summary="Simulate successful Stripe payment (mock mode)",
)
def mock_complete_payment(
    body: MockPaymentRequest,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Simulate checkout.session.completed webhook in mock/demo mode."""
    _ensure_mock_mode()

    order = (
        db.query(Order)
        .filter(
            Order.stripe_session_id == body.session_id,
            Order.user_id == current_user.id,
        )
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    _validate_order_stock(db, order)

    order = process_checkout_completed(
        db,
        body.session_id,
        order_id=order.id,
        payment_intent=f"pi_mock_{order.id}",
        currency="USD",
    )

    return PaymentVerificationResponse(
        session_id=body.session_id,
        order_id=order.id,
        payment_status=order.payment_status,
        order_status=order.status,
        verified=order.payment_status == PaymentStatus.PAID,
        mock_mode=True,
    )


@router.post(
    "/mock-fail",
    response_model=PaymentVerificationResponse,
    summary="Simulate failed Stripe payment (mock mode)",
)
def mock_fail_payment(
    body: MockPaymentRequest,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Simulate payment_intent.payment_failed in mock/demo mode."""
    _ensure_mock_mode()

    order = (
        db.query(Order)
        .filter(
            Order.stripe_session_id == body.session_id,
            Order.user_id == current_user.id,
        )
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order = process_payment_failed(db, body.session_id, order_id=order.id)

    return PaymentVerificationResponse(
        session_id=body.session_id,
        order_id=order.id,
        payment_status=order.payment_status,
        order_status=order.status,
        verified=False,
        mock_mode=True,
    )


@router.post(
    "/mock-cancel",
    response_model=PaymentVerificationResponse,
    summary="Simulate cancelled Stripe checkout (mock mode)",
)
def mock_cancel_payment(
    body: MockPaymentRequest,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Simulate checkout.session.expired in mock/demo mode."""
    _ensure_mock_mode()

    order = (
        db.query(Order)
        .filter(
            Order.stripe_session_id == body.session_id,
            Order.user_id == current_user.id,
        )
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order = process_checkout_cancelled(db, body.session_id, order_id=order.id)

    return PaymentVerificationResponse(
        session_id=body.session_id,
        order_id=order.id,
        payment_status=order.payment_status,
        order_status=order.status,
        verified=False,
        mock_mode=True,
    )


@router.post("/webhook", summary="Stripe Webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events with signature verification.
    Only the webhook confirms payment — never the frontend redirect.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = construct_webhook_event(payload, sig_header)

    event_type = event["type"]
    data_object = event["data"]["object"]

    if event_type == "checkout.session.completed":
        session_id = data_object["id"]
        meta_order_id = (data_object.get("metadata") or {}).get("order_id")
        order_id = int(meta_order_id) if meta_order_id else None
        payment_intent = data_object.get("payment_intent")
        if isinstance(payment_intent, dict):
            payment_intent = payment_intent.get("id")

        process_checkout_completed(
            db,
            session_id,
            order_id=order_id,
            payment_intent=payment_intent,
            currency=(data_object.get("currency") or "usd").upper(),
        )

    elif event_type in ("payment_intent.payment_failed", "checkout.session.async_payment_failed"):
        session_id = data_object.get("id")
        meta = data_object.get("metadata") or {}
        order_id = int(meta["order_id"]) if meta.get("order_id") else None
        process_payment_failed(db, session_id, order_id=order_id)

    elif event_type == "checkout.session.expired":
        session_id = data_object["id"]
        process_checkout_cancelled(db, session_id)

    return {"status": "success"}
