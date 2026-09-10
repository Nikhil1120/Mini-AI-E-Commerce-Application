"""
AI chat router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import AIChatRequest, AIChatResponse
from dependencies import get_current_customer
from services.ai_service import chat
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat", response_model=AIChatResponse, summary="AI Chat")
def ai_chat(
    request: AIChatRequest,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """
    Authenticated AI support chat.

    Tools always use the authenticated user identity from JWT —
    never a client-supplied user_id.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    try:
        response = chat(
            message=request.message.strip(),
            user_id=current_user.id,
            db=db,
        )
        return AIChatResponse(response=response)
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )
