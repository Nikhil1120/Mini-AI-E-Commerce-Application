"""AI support service wrapper."""

from sqlalchemy.orm import Session
from ai.agent import get_ai_response


def chat(message: str, user_id: int, db: Session) -> str:
    """Process a customer support chat message using backend tools."""
    return get_ai_response(message=message, user_id=user_id, db=db)
