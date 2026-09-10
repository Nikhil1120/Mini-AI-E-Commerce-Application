"""Tests for AI chat endpoint."""

from conftest import auth_header


def test_ai_requires_authentication(client):
    response = client.post("/ai/chat", json={"message": "What products are available?"})
    assert response.status_code in (401, 403)


def test_ai_chat_authenticated(client, customer_user, sample_product):
    response = client.post(
        "/ai/chat",
        json={"message": "What products are available?"},
        headers=auth_header(customer_user),
    )
    assert response.status_code == 200
    assert "response" in response.json()
    assert "Test Phone" in response.json()["response"] or "products" in response.json()["response"].lower()
