"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, computed_field
from typing import Optional, List
from datetime import datetime
from models import UserRole, OrderStatus, PaymentStatus


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    """Base user schema."""
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserResponse(UserBase):
    """Schema for returning user data."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for Google OAuth login."""
    credential: str = Field(..., description="Google OAuth token/credential")


class DevLoginRequest(BaseModel):
    """Schema for development login (DEV_MODE only)."""
    email: str = Field(..., description="Email of the user to log in as")


# ==================== PRODUCT SCHEMAS ====================

class ProductBase(BaseModel):
    """Base product schema."""
    name: str
    description: Optional[str] = None
    price: float = Field(..., ge=0, description="Price must be >= 0")
    image_url: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: int = Field(default=0, ge=0, description="Stock cannot be negative")
    is_active: bool = True


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for returning product data."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockUpdate(BaseModel):
    """Schema for updating product stock."""
    stock_quantity: int = Field(..., ge=0, description="Stock cannot be negative")


# ==================== CART SCHEMAS ====================

class CartItemBase(BaseModel):
    """Base cart item schema."""
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be > 0")


class CartItemCreate(CartItemBase):
    """Schema for adding item to cart."""
    pass


class CartItemUpdate(BaseModel):
    """Schema for updating cart item."""
    quantity: int = Field(..., gt=0, description="Quantity must be > 0")


class CartItemResponse(BaseModel):
    """Schema for returning cart item data."""
    id: int
    product_id: int
    product: Optional[ProductResponse] = None
    quantity: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def subtotal(self) -> float:
        if self.product:
            return round(self.product.price * self.quantity, 2)
        return 0.0


class CartResponse(BaseModel):
    """Schema for returning cart data."""
    id: int
    user_id: int
    items: List[CartItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)

    @computed_field
    @property
    def total_price(self) -> float:
        return round(
            sum(
                item.product.price * item.quantity
                for item in self.items
                if item.product
            ),
            2,
        )


# ==================== ORDER SCHEMAS ====================

class OrderItemResponse(BaseModel):
    """Schema for returning order item data."""
    id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
    subtotal: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    """Base order schema."""
    pass


class OrderCreate(OrderBase):
    """Schema for creating an order."""
    pass


class OrderResponse(BaseModel):
    """Schema for returning order data."""
    id: int
    user_id: int
    total_amount: float
    status: OrderStatus
    payment_status: PaymentStatus
    stripe_session_id: Optional[str] = None
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderUpdateStatus(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus
    payment_status: Optional[PaymentStatus] = None


class OrderItemQuantityUpdate(BaseModel):
    """Schema for updating quantity on a pending order item."""
    quantity: int = Field(..., gt=0, description="Quantity must be > 0")


# ==================== PAYMENT SCHEMAS ====================

class PaymentResponse(BaseModel):
    """Schema for returning payment data."""
    id: int
    order_id: int
    stripe_payment_intent_id: Optional[str] = None
    stripe_session_id: Optional[str] = None
    amount: float
    currency: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckoutSessionRequest(BaseModel):
    """Optional: create checkout for a specific order."""
    order_id: Optional[int] = None


class CheckoutSessionResponse(BaseModel):
    """Schema for checkout session response."""
    session_id: str
    checkout_url: str
    order_id: int
    mock_mode: bool = False


class PaymentVerificationResponse(BaseModel):
    """Schema for payment verification / mock payment result."""
    session_id: str
    order_id: int
    payment_status: PaymentStatus
    order_status: OrderStatus
    verified: bool
    mock_mode: bool = False


class MockPaymentRequest(BaseModel):
    """Schema for mock payment actions in demo mode."""
    session_id: str = Field(..., min_length=1)


# ==================== AI SCHEMAS ====================

class AIMessage(BaseModel):
    """Schema for AI chat messages."""
    role: str  # "user" or "assistant"
    content: str


class AIChatRequest(BaseModel):
    """Schema for AI chat request."""
    message: str


class AIChatResponse(BaseModel):
    """Schema for AI chat response."""
    response: str
    conversation_id: Optional[str] = None


# ==================== TOKEN SCHEMA ====================

class TokenData(BaseModel):
    """Schema for token data."""
    email: Optional[str] = None
    user_id: Optional[int] = None


class Token(BaseModel):
    """Schema for returning authentication token."""
    access_token: str
    token_type: str
    user: UserResponse
