"""
Configuration module for the AI E-Commerce application.
Loads environment variables and provides configuration.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from environment variables."""

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "your-secret-key-change-in-production",
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_MOCK_MODE: str = os.getenv("STRIPE_MOCK_MODE", "auto").lower()

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")  # gemini | openai | simple
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@ecommerce.local")

    DEV_MODE: bool = os.getenv("DEV_MODE", "false").lower() in ("true", "1", "yes")

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_postgresql(self) -> bool:
        return self.DATABASE_URL.startswith("postgresql")

    @property
    def use_stripe_mock(self) -> bool:
        """Use simulated Stripe checkout when real keys are not configured."""
        if self.STRIPE_MOCK_MODE in ("true", "1", "yes"):
            return True
        if self.STRIPE_MOCK_MODE in ("false", "0", "no"):
            return False

        placeholder_markers = (
            "your_stripe",
            "dummy",
            "placeholder",
            "changeme",
        )
        key = (self.STRIPE_SECRET_KEY or "").lower()
        return not key or any(marker in key for marker in placeholder_markers)


settings = Settings()
