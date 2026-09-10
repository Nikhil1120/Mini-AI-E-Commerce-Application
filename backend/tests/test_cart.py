"""Tests for cart endpoints."""

from conftest import auth_header
from models import Cart


def test_add_to_cart(client, customer_user, sample_product):
    response = client.post(
        "/cart/items",
        json={"product_id": sample_product.id, "quantity": 2},
        headers=auth_header(customer_user),
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 2


def test_invalid_quantity_rejected(client, customer_user, sample_product):
    response = client.post(
        "/cart/items",
        json={"product_id": sample_product.id, "quantity": 0},
        headers=auth_header(customer_user),
    )
    assert response.status_code == 422


def test_insufficient_stock_rejected(client, customer_user, sample_product):
    response = client.post(
        "/cart/items",
        json={"product_id": sample_product.id, "quantity": 100},
        headers=auth_header(customer_user),
    )
    assert response.status_code == 409


def test_get_cart(client, customer_user, sample_product, db):
    cart = Cart(user_id=customer_user.id)
    db.add(cart)
    db.commit()

    client.post(
        "/cart/items",
        json={"product_id": sample_product.id, "quantity": 1},
        headers=auth_header(customer_user),
    )

    response = client.get("/cart", headers=auth_header(customer_user))
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
