"""
Pytest configuration and fixtures.
Uses an in-memory SQLite database and bypasses Google/Stripe externals where needed.
"""

import os
import pytest

# Must set before importing app modules
os.environ["DATABASE_URL"] = "sqlite:///./test_ecommerce.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["GOOGLE_CLIENT_ID"] = "test-google-client-id"
os.environ["FRONTEND_URL"] = "http://localhost:5173"
os.environ["ADMIN_EMAIL"] = "admin@test.local"
os.environ["AI_PROVIDER"] = "simple"
os.environ["STRIPE_SECRET_KEY"] = ""
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models import User, Product, UserRole, Cart, Order, OrderItem, OrderStatus, PaymentStatus
from dependencies import create_access_token


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def customer(db):
    user = User(
        email="customer@test.com",
        username="customer1",
        first_name="Cust",
        last_name="Omer",
        google_id="g_customer",
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db.add(user)
    db.flush()
    db.add(Cart(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def other_customer(db):
    user = User(
        email="other@test.com",
        username="customer2",
        first_name="Other",
        last_name="User",
        google_id="g_other",
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db.add(user)
    db.flush()
    db.add(Cart(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin(db):
    user = User(
        email="admin@test.local",
        username="admin",
        first_name="Admin",
        last_name="User",
        google_id="g_admin",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def product(db):
    p = Product(
        name="iPhone 15",
        description="Test phone",
        price=999.99,
        category="Electronics",
        stock_quantity=10,
        is_active=True,
        image_url="https://example.com/phone.jpg",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def auth_header(user: User) -> dict:
    token = create_access_token({"sub": user.email, "user_id": user.id})
    return {"Authorization": f"Bearer {token}"}
