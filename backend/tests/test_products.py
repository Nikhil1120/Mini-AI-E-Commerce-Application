"""Tests for product endpoints."""

from conftest import auth_header


def test_list_products(client, sample_product):
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "Test Phone"


def test_get_product_details(client, sample_product):
    response = client.get(f"/products/{sample_product.id}")
    assert response.status_code == 200
    assert response.json()["price"] == 999.99


def test_customer_cannot_create_product(client, customer_user):
    response = client.post(
        "/admin/products",
        json={
            "name": "Hacked Product",
            "price": 1.0,
            "stock_quantity": 1,
        },
        headers=auth_header(customer_user),
    )
    assert response.status_code == 403


def test_admin_can_create_product(client, admin_user):
    response = client.post(
        "/admin/products",
        json={
            "name": "Admin Product",
            "description": "Created by admin",
            "price": 49.99,
            "category": "Test",
            "stock_quantity": 5,
            "is_active": True,
        },
        headers=auth_header(admin_user),
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Admin Product"
