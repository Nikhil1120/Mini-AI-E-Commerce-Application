"""Backend API tests covering auth, products, cart, orders, RBAC, AI, payments."""

from unittest.mock import patch, MagicMock
from models import Order, OrderItem, OrderStatus, PaymentStatus, Product, CartItem, Cart
from tests.conftest import auth_header


def test_list_products(client, product):
    res = client.get("/products")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["name"] == "iPhone 15"


def test_get_product(client, product):
    res = client.get(f"/products/{product.id}")
    assert res.status_code == 200
    assert res.json()["price"] == 999.99


def test_customer_cannot_create_product(client, customer, product):
    res = client.post(
        "/admin/products",
        headers=auth_header(customer),
        json={
            "name": "Hack Product",
            "price": 1,
            "stock_quantity": 5,
        },
    )
    assert res.status_code == 403


def test_admin_can_create_product(client, admin):
    res = client.post(
        "/admin/products",
        headers=auth_header(admin),
        json={
            "name": "MacBook Air",
            "description": "Laptop",
            "price": 1299.99,
            "stock_quantity": 5,
            "category": "Computers",
            "is_active": True,
        },
    )
    assert res.status_code == 200
    assert res.json()["name"] == "MacBook Air"


def test_google_auth_flow(client, db):
    fake_identity = {
        "email": "newuser@gmail.com",
        "google_id": "google-sub-123",
        "first_name": "New",
        "last_name": "User",
    }
    with patch("routers.auth.verify_google_token", return_value=fake_identity):
        res = client.post("/auth/google", json={"credential": "fake-google-token"})
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert body["user"]["email"] == "newuser@gmail.com"
    assert body["user"]["role"] == "CUSTOMER"


def test_google_auth_cannot_set_admin_via_client(client):
    fake_identity = {
        "email": "sneaky@gmail.com",
        "google_id": "google-sub-999",
        "first_name": "Sneaky",
        "last_name": "User",
    }
    with patch("routers.auth.verify_google_token", return_value=fake_identity):
        res = client.post(
            "/auth/google",
            json={"credential": "token", "role": "ADMIN"},
        )
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "CUSTOMER"


def test_add_to_cart(client, customer, product):
    res = client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 2},
    )
    assert res.status_code == 200
    assert res.json()["quantity"] == 2


def test_invalid_quantity(client, customer, product):
    res = client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 0},
    )
    assert res.status_code == 422  # pydantic validation


def test_insufficient_stock(client, customer, product):
    res = client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 999},
    )
    assert res.status_code == 409


def test_order_creation(client, customer, product, db):
    client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 2},
    )
    res = client.post("/orders", headers=auth_header(customer))
    assert res.status_code == 200
    order = res.json()
    assert order["total_amount"] == 1999.98
    assert order["payment_status"] == "PENDING"
    assert order["status"] == "PENDING"
    assert len(order["items"]) == 1
    assert order["items"][0]["product_name"] == "iPhone 15"
    assert order["items"][0]["price"] == 999.99


def test_customer_can_access_own_order(client, customer, product):
    client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 1},
    )
    created = client.post("/orders", headers=auth_header(customer)).json()
    res = client.get(f"/orders/{created['id']}", headers=auth_header(customer))
    assert res.status_code == 200


def test_customer_cannot_access_other_order(client, customer, other_customer, product, db):
    client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 1},
    )
    created = client.post("/orders", headers=auth_header(customer)).json()
    res = client.get(f"/orders/{created['id']}", headers=auth_header(other_customer))
    assert res.status_code == 403


def test_admin_can_access_all_orders(client, admin, customer, product):
    client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 1},
    )
    created = client.post("/orders", headers=auth_header(customer)).json()
    res = client.get("/admin/orders", headers=auth_header(admin))
    assert res.status_code == 200
    assert any(o["id"] == created["id"] for o in res.json())


def test_ai_requires_authentication(client):
    res = client.post("/ai/chat", json={"message": "What products are available?"})
    assert res.status_code in (401, 403)


def test_ai_chat_uses_tools(client, customer, product):
    res = client.post(
        "/ai/chat",
        headers=auth_header(customer),
        json={"message": "What is the price of iPhone 15?"},
    )
    assert res.status_code == 200
    assert "999.99" in res.json()["response"]


def test_stripe_webhook_marks_paid(client, customer, product, db):
    client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 1},
    )
    order = client.post("/orders", headers=auth_header(customer)).json()

    # Attach a fake session id
    db_order = db.query(Order).filter(Order.id == order["id"]).first()
    db_order.stripe_session_id = "cs_test_123"
    db.commit()

    fake_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "payment_intent": "pi_test_123",
                "currency": "usd",
                "metadata": {"order_id": str(order["id"])},
            }
        },
    }

    with patch(
        "routers.payments.construct_webhook_event",
        return_value=fake_event,
    ):
        res = client.post(
            "/payments/webhook",
            content=b"{}",
            headers={"stripe-signature": "t=1,v1=fake"},
        )

    assert res.status_code == 200
    db.refresh(db_order)
    assert db_order.payment_status == PaymentStatus.PAID
    assert db_order.status == OrderStatus.CONFIRMED

    db.refresh(db.query(Product).get(product.id))
    updated = db.query(Product).filter(Product.id == product.id).first()
    assert updated.stock_quantity == 9


def test_mock_checkout_session(client, customer, product):
    client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 1},
    )
    order = client.post("/orders", headers=auth_header(customer)).json()

    res = client.post(
        "/payments/create-checkout-session",
        headers=auth_header(customer),
        json={"order_id": order["id"]},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["mock_mode"] is True
    assert "checkout/mock" in body["checkout_url"]
    assert body["order_id"] == order["id"]


def test_mock_complete_payment(client, customer, product, db):
    client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 1},
    )
    order = client.post("/orders", headers=auth_header(customer)).json()
    session = client.post(
        "/payments/create-checkout-session",
        headers=auth_header(customer),
        json={"order_id": order["id"]},
    ).json()

    res = client.post(
        "/payments/mock-complete",
        headers=auth_header(customer),
        json={"session_id": session["session_id"]},
    )
    assert res.status_code == 200
    assert res.json()["verified"] is True
    assert res.json()["payment_status"] == "PAID"

    db_order = db.query(Order).filter(Order.id == order["id"]).first()
    assert db_order.payment_status == PaymentStatus.PAID
    assert db_order.status == OrderStatus.CONFIRMED

    updated = db.query(Product).filter(Product.id == product.id).first()
    assert updated.stock_quantity == 9


def test_update_pending_order_item_quantity(client, customer, product):
    client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 1},
    )
    order = client.post("/orders", headers=auth_header(customer)).json()
    item_id = order["items"][0]["id"]

    res = client.put(
        f"/orders/{order['id']}/items/{item_id}",
        headers=auth_header(customer),
        json={"quantity": 3},
    )
    assert res.status_code == 200
    updated = res.json()
    assert updated["items"][0]["quantity"] == 3
    assert updated["total_amount"] == 2999.97


def test_remove_pending_order(client, customer, product):
    client.post(
        "/cart/items",
        headers=auth_header(customer),
        json={"product_id": product.id, "quantity": 1},
    )
    order = client.post("/orders", headers=auth_header(customer)).json()

    res = client.delete(f"/orders/{order['id']}", headers=auth_header(customer))
    assert res.status_code == 200

    get_res = client.get(f"/orders/{order['id']}", headers=auth_header(customer))
    assert get_res.status_code == 404
