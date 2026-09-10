"""
Seed script — products + admin user for local development.

Usage:
  python seed.py
  python seed.py --promote-admin youremail@gmail.com
"""

from database import SessionLocal, engine, Base
from models import User, Product, UserRole, Cart
from config import settings
import sys


PRODUCTS = [
    {
        "name": "iPhone 15",
        "description": "Latest Apple smartphone with A16 Bionic chip and advanced camera system",
        "price": 999.99,
        "category": "Electronics",
        "stock_quantity": 50,
        "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400",
    },
    {
        "name": "Samsung Galaxy S24",
        "description": "Flagship Samsung Android phone with AI features",
        "price": 899.99,
        "category": "Electronics",
        "stock_quantity": 45,
        "image_url": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400",
    },
    {
        "name": "MacBook Air",
        "description": "Powerful Apple laptop with M2 chip for professionals",
        "price": 1299.99,
        "category": "Computers",
        "stock_quantity": 30,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
    },
    {
        "name": "Dell Laptop",
        "description": "High-performance Windows laptop for work and study",
        "price": 799.99,
        "category": "Computers",
        "stock_quantity": 35,
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=400",
    },
    {
        "name": "Sony Headphones",
        "description": "Premium noise-cancelling over-ear headphones",
        "price": 399.99,
        "category": "Audio",
        "stock_quantity": 60,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
    },
    {
        "name": "AirPods Pro",
        "description": "Apple wireless earbuds with active noise cancellation",
        "price": 249.99,
        "category": "Audio",
        "stock_quantity": 75,
        "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400",
    },
    {
        "name": "Mechanical Keyboard",
        "description": "RGB mechanical gaming keyboard with tactile switches",
        "price": 149.99,
        "category": "Accessories",
        "stock_quantity": 80,
        "image_url": "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?w=400",
    },
    {
        "name": "Gaming Mouse",
        "description": "High-precision gaming mouse with adjustable DPI",
        "price": 79.99,
        "category": "Accessories",
        "stock_quantity": 100,
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400",
    },
    {
        "name": "Monitor 4K",
        "description": "27-inch 4K display for creative work and gaming",
        "price": 599.99,
        "category": "Electronics",
        "stock_quantity": 25,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400",
    },
    {
        "name": "Smart Watch",
        "description": "Advanced fitness tracking smartwatch with heart-rate monitor",
        "price": 299.99,
        "category": "Wearables",
        "stock_quantity": 55,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
    },
]


def promote_admin(email: str) -> None:
    """Promote an existing user (by email) to ADMIN."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email.lower()).first()
        if not user:
            print(f"User not found: {email}. Sign in with Google first, then re-run.")
            sys.exit(1)
        user.role = UserRole.ADMIN
        db.commit()
        print(f"[OK] Promoted {email} to ADMIN")
    finally:
        db.close()


def seed_database(exit_on_error: bool = False) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Product).count() == 0:
            for product_data in PRODUCTS:
                db.add(Product(**product_data, is_active=True))
            db.commit()
            print(f"[OK] Created {len(PRODUCTS)} products")
        else:
            updated = 0
            product_map = {p["name"]: p for p in PRODUCTS}
            for product in db.query(Product).all():
                seed_data = product_map.get(product.name)
                if not seed_data:
                    continue
                needs_update = (
                    not product.image_url
                    or "via.placeholder.com" in (product.image_url or "")
                    or product.image_url != seed_data["image_url"]
                )
                if needs_update:
                    product.image_url = seed_data["image_url"]
                    product.description = seed_data["description"]
                    product.price = seed_data["price"]
                    product.category = seed_data["category"]
                    product.stock_quantity = seed_data["stock_quantity"]
                    updated += 1
            if updated:
                db.commit()
                print(f"[OK] Updated {updated} products (fixed placeholder/broken image URLs)")
            else:
                print("[OK] Products already present, skipping product seed")

        admin_email = settings.ADMIN_EMAIL.lower()
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                username="admin",
                first_name="Admin",
                last_name="User",
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)
            db.flush()
            db.add(Cart(user_id=admin_user.id))
            db.commit()
            print(f"[OK] Created admin placeholder user: {admin_email}")
            print("  Sign in with a Google account matching ADMIN_EMAIL,")
            print("  or run: python seed.py --promote-admin your@gmail.com")
        else:
            if admin_user.role != UserRole.ADMIN:
                admin_user.role = UserRole.ADMIN
                db.commit()
            print(f"[OK] Admin user ready: {admin_email}")

        customer_email = "customer@ecommerce.local"
        customer_user = db.query(User).filter(User.email == customer_email).first()
        if not customer_user:
            customer_user = User(
                email=customer_email,
                username="customer_dev",
                first_name="Demo",
                last_name="Customer",
                role=UserRole.CUSTOMER,
                is_active=True,
            )
            db.add(customer_user)
            db.flush()
            db.add(Cart(user_id=customer_user.id))
            db.commit()
            print(f"[OK] Created customer user: {customer_email}")
        else:
            print(f"[OK] Customer user ready: {customer_email}")

        print("\n[OK] Database seeding completed")
        print("Dev login: admin@ecommerce.local or customer@ecommerce.local (DEV_MODE=true)")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        if exit_on_error:
            sys.exit(1)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--promote-admin":
        promote_admin(sys.argv[2])
    else:
        seed_database(exit_on_error=True)
