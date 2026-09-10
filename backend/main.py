"""
FastAPI main application entry point.
AI E-Commerce Application Backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI E-Commerce API",
    description="Mini AI-powered e-commerce API with Google OAuth, Stripe, and AI support",
    version="1.0.0",
)

# CORS from env + common local origins (Vite may use 5173, 5174, etc.)
origins = {
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
}
# Allow comma-separated extra origins via FRONTEND_URL if needed
extra = settings.FRONTEND_URL.split(",") if "," in settings.FRONTEND_URL else []
origins.update(o.strip() for o in extra if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(origins),
    # Allow any localhost port during local dev (e.g. when 5173 is already in use)
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()


@app.on_event("startup")
def startup_seed_database() -> None:
    """Seed products and demo users on deploy (Render free tier has no Shell)."""
    try:
        from seed import seed_database

        seed_database()
        logger.info("Database seed check completed")
    except Exception as exc:
        logger.warning("Database seed skipped or failed: %s", exc)


from routers import auth, products, cart, orders, payments, admin, ai

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(admin.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
def read_root():
    return {
        "message": "AI E-Commerce API",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "database": "sqlite" if settings.is_sqlite else "postgresql",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
