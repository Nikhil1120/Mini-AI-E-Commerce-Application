"""Tests for authentication endpoints."""

from conftest import auth_header


def test_dev_login_creates_customer(client, db):
    response = client.post("/auth/dev-login", json={"email": "newuser@test.com"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "CUSTOMER"
    assert data["user"]["email"] == "newuser@test.com"


def test_dev_login_existing_admin(client, admin_user):
    response = client.post("/auth/dev-login", json={"email": admin_user.email})
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "ADMIN"


def test_get_current_user(client, customer_user):
    response = client.get("/auth/me", headers=auth_header(customer_user))
    assert response.status_code == 200
    assert response.json()["email"] == customer_user.email


def test_unauthenticated_request_rejected(client):
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_invalid_token_rejected(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
