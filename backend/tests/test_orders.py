"""Tests for order endpoints."""

from conftest import auth_header
from models import Cart, CartItem, Order


def _add_item_to_cart(db, customer_user, sample_product, quantity=1):
    cart = Cart(user_id=customer_user.id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    item = CartItem(cart_id=cart.id, product_id=sample_product.id, quantity=quantity)
    db.add(item)
    db.commit()
    return cart


def test_create_order(client, customer_user, sample_product, db):
    _add_item_to_cart(db, customer_user, sample_product, 2)

    response = client.post("/orders", headers=auth_header(customer_user))
    assert response.status_code == 200
    order = response.json()
    assert order["total_amount"] == 1999.98
    assert order["payment_status"] == "PENDING"


def test_customer_can_access_own_order(client, customer_user, sample_product, db):
    _add_item_to_cart(db, customer_user, sample_product)
    create_resp = client.post("/orders", headers=auth_header(customer_user))
    order_id = create_resp.json()["id"]

    response = client.get(f"/orders/{order_id}", headers=auth_header(customer_user))
    assert response.status_code == 200


def test_customer_cannot_access_other_order(client, customer_user, other_customer, sample_product, db):
    _add_item_to_cart(db, other_customer, sample_product)
    create_resp = client.post("/orders", headers=auth_header(other_customer))
    order_id = create_resp.json()["id"]

    response = client.get(f"/orders/{order_id}", headers=auth_header(customer_user))
    assert response.status_code == 403


def test_admin_can_access_all_orders(client, admin_user, customer_user, sample_product, db):
    _add_item_to_cart(db, customer_user, sample_product)
    create_resp = client.post("/orders", headers=auth_header(customer_user))
    order_id = create_resp.json()["id"]

    response = client.get(f"/admin/orders/{order_id}", headers=auth_header(admin_user))
    assert response.status_code == 200


def test_update_pending_order_item_quantity(client, customer_user, sample_product, db):
    _add_item_to_cart(db, customer_user, sample_product, 1)
    order = client.post("/orders", headers=auth_header(customer_user)).json()
    item_id = order["items"][0]["id"]

    response = client.put(
        f"/orders/{order['id']}/items/{item_id}",
        headers=auth_header(customer_user),
        json={"quantity": 3},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["items"][0]["quantity"] == 3
    assert updated["total_amount"] == 2999.97


def test_remove_pending_order(client, customer_user, sample_product, db):
    _add_item_to_cart(db, customer_user, sample_product)
    order = client.post("/orders", headers=auth_header(customer_user)).json()

    response = client.delete(
        f"/orders/{order['id']}",
        headers=auth_header(customer_user),
    )
    assert response.status_code == 200

    get_response = client.get(
        f"/orders/{order['id']}",
        headers=auth_header(customer_user),
    )
    assert get_response.status_code == 404
