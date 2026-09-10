"""
Authentication router for Google OAuth and JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserRole, Cart
from schemas import UserLogin, UserResponse, Token, DevLoginRequest
from dependencies import create_access_token, get_current_user
from services.google_auth import verify_google_token
from config import settings
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _issue_token_response(user: User) -> dict:
    """Build JWT + user payload for authenticated session."""
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role.value},
        expires_delta=timedelta(hours=settings.JWT_EXPIRE_HOURS),
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }


@router.post("/google", response_model=Token, summary="Google OAuth Login")
def google_login(request: UserLogin, db: Session = Depends(get_db)):
    """
    Validate Google credential, create/find local user as CUSTOMER, return JWT.
    Role is never accepted from the client.
    """
    identity = verify_google_token(request.credential)

    email = identity["email"]
    google_id = identity["google_id"]
    first_name = identity.get("first_name")
    last_name = identity.get("last_name")

    user = (
        db.query(User)
        .filter((User.google_id == google_id) | (User.email == email))
        .first()
    )

    is_new_user = user is None

    if is_new_user:
        base_username = email.split("@")[0]
        username = f"{base_username}_{str(google_id)[:8]}"
        # Ensure unique username
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            username = f"{base_username}_{google_id}"

        # Promote to admin only if email matches configured ADMIN_EMAIL
        role = UserRole.ADMIN if email.lower() == settings.ADMIN_EMAIL.lower() else UserRole.CUSTOMER

        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            google_id=google_id,
            role=role,
            is_active=True,
        )
        db.add(user)
        db.flush()

        # Create empty cart for customers
        if user.role == UserRole.CUSTOMER:
            db.add(Cart(user_id=user.id))

        db.commit()
        db.refresh(user)
        logger.info(f"Google registration: {email} role={user.role.value}")
    else:
        # Link google_id if missing; never overwrite role from client
        if not user.google_id and google_id:
            user.google_id = google_id
        if first_name and not user.first_name:
            user.first_name = first_name
        if last_name and not user.last_name:
            user.last_name = last_name
        db.commit()
        db.refresh(user)
        logger.info(f"Google login: {email} role={user.role.value}")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    return _issue_token_response(user)


@router.post("/dev-login", response_model=Token, summary="Development Login")
def dev_login(request: DevLoginRequest, db: Session = Depends(get_db)):
    """
    Development-only login without Google OAuth.
    Only available when DEV_MODE=true.
    """
    if not settings.DEV_MODE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    email = request.email.lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        base_username = email.split("@")[0]
        role = UserRole.ADMIN if email == settings.ADMIN_EMAIL.lower() else UserRole.CUSTOMER
        user = User(
            email=email,
            username=f"{base_username}_dev",
            first_name=base_username,
            last_name="User",
            role=role,
            is_active=True,
        )
        db.add(user)
        db.flush()
        if user.role == UserRole.CUSTOMER:
            db.add(Cart(user_id=user.id))
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    logger.info(f"Dev login: {user.email} (role={user.role.value})")
    return _issue_token_response(user)


@router.get("/me", response_model=UserResponse, summary="Get Current User")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Return the authenticated user."""
    return current_user


@router.post("/logout", summary="Logout")
def logout(current_user: User = Depends(get_current_user)):
    """Invalidate client session by discarding JWT on the frontend."""
    logger.info(f"Logout: {current_user.email}")
    return {"message": "Logged out successfully"}
