"""Shared payment event handlers used by Stripe webhooks and mock checkout."""

from sqlalchemy.orm import Session
from models import Order, Payment, PaymentStatus, OrderStatus, Cart, CartItem, Product
import logging

logger = logging.getLogger(__name__)


def clear_user_cart(db: Session, user_id: int) -> None:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()


def reduce_stock(db: Session, order: Order) -> None:
    for order_item in order.items:
        product = db.query(Product).filter(Product.id == order_item.product_id).first()
        if product:
            product.stock_quantity = max(0, product.stock_quantity - order_item.quantity)


def find_order_by_session(
    db: Session,
    session_id: str,
    order_id: int | None = None,
) -> Order | None:
    order = db.query(Order).filter(Order.stripe_session_id == session_id).first()
    if order:
        return order
    if order_id:
        return db.query(Order).filter(Order.id == order_id).first()
    return None


def process_checkout_completed(
    db: Session,
    session_id: str,
    *,
    order_id: int | None = None,
    payment_intent: str | None = None,
    currency: str = "USD",
) -> Order | None:
    """Mark order paid, reduce stock, and clear cart."""
    order = find_order_by_session(db, session_id, order_id)
    if not order or order.payment_status == PaymentStatus.PAID:
        return order

    order.payment_status = PaymentStatus.PAID
    order.status = OrderStatus.CONFIRMED
    order.stripe_session_id = session_id

    reduce_stock(db, order)
    clear_user_cart(db, order.user_id)

    payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if not payment:
        payment = Payment(
            order_id=order.id,
            stripe_session_id=session_id,
            stripe_payment_intent_id=payment_intent,
            amount=order.total_amount,
            currency=currency.upper(),
            status=PaymentStatus.PAID,
        )
        db.add(payment)
    else:
        payment.status = PaymentStatus.PAID
        payment.stripe_session_id = session_id
        payment.stripe_payment_intent_id = payment_intent

    db.commit()
    db.refresh(order)
    logger.info(f"Payment confirmed for order {order.id}")
    return order


def process_payment_failed(
    db: Session,
    session_id: str,
    *,
    order_id: int | None = None,
) -> Order | None:
    order = find_order_by_session(db, session_id, order_id)
    if not order or order.payment_status != PaymentStatus.PENDING:
        return order

    order.payment_status = PaymentStatus.FAILED
    payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if payment:
        payment.status = PaymentStatus.FAILED
    db.commit()
    db.refresh(order)
    logger.info(f"Payment failed for order {order.id}")
    return order


def process_checkout_cancelled(
    db: Session,
    session_id: str,
    *,
    order_id: int | None = None,
) -> Order | None:
    order = find_order_by_session(db, session_id, order_id)
    if not order or order.payment_status != PaymentStatus.PENDING:
        return order

    order.payment_status = PaymentStatus.CANCELLED
    order.status = OrderStatus.CANCELLED
    payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if payment:
        payment.status = PaymentStatus.CANCELLED
    db.commit()
    db.refresh(order)
    logger.info(f"Checkout cancelled/expired for order {order.id}")
    return order
