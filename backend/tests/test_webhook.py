"""Tests for Stripe webhook handling."""

from conftest import auth_header
from models import Cart, CartItem, Order, PaymentStatus, OrderStatus


def _create_pending_order(db, customer_user, sample_product):
    cart = Cart(user_id=customer_user.id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    db.add(CartItem(cart_id=cart.id, product_id=sample_product.id, quantity=1))
    db.commit()

    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)
    response = client.post("/orders", headers=auth_header(customer_user))
    return response.json()


def test_webhook_rejects_missing_signature(client):
    response = client.post("/payments/webhook", content=b"{}")
    assert response.status_code in (400, 500)
