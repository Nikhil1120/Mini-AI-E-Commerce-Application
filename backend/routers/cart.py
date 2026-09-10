"""
Shopping cart router for cart operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import User, Cart, CartItem, Product
from schemas import CartResponse, CartItemCreate, CartItemUpdate, CartItemResponse
from dependencies import get_current_customer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_or_create_cart(user: User, db: Session) -> Cart:
    """Get user's cart or create one if it doesn't exist."""
    cart = (
        db.query(Cart)
        .options(joinedload(Cart.items).joinedload(CartItem.product))
        .filter(Cart.user_id == user.id)
        .first()
    )
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        cart = (
            db.query(Cart)
            .options(joinedload(Cart.items).joinedload(CartItem.product))
            .filter(Cart.user_id == user.id)
            .first()
        )
    return cart


@router.get("", response_model=CartResponse, summary="Get User Cart")
def get_cart(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Get the current user's shopping cart with all items and totals."""
    return get_or_create_cart(current_user, db)


@router.post("/items", response_model=CartItemResponse, summary="Add to Cart")
def add_to_cart(
    item: CartItemCreate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Add a product to the user's cart with stock validation."""
    cart = get_or_create_cart(current_user, db)

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not available",
        )

    if item.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0",
        )

    if item.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Insufficient stock. Available: {product.stock_quantity}",
        )

    cart_item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_id == item.product_id)
        .first()
    )

    if cart_item:
        new_quantity = cart_item.quantity + item.quantity
        if new_quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insufficient stock. Available: {product.stock_quantity}",
            )
        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity,
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    _ = cart_item.product
    logger.info(f"Item added to cart - User: {current_user.id}, Product: {item.product_id}")
    return cart_item


@router.put("/items/{item_id}", response_model=CartItemResponse, summary="Update Cart Item")
def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Update quantity of a cart item."""
    cart = get_or_create_cart(current_user, db)

    cart_item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
        .first()
    )

    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    if item_update.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0",
        )

    product = cart_item.product
    if item_update.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Insufficient stock. Available: {product.stock_quantity}",
        )

    cart_item.quantity = item_update.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.delete("/items/{item_id}", summary="Remove from Cart")
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Remove an item from the user's cart."""
    cart = get_or_create_cart(current_user, db)

    cart_item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
        .first()
    )

    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("", summary="Clear Cart")
def clear_cart(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Clear all items from the user's cart."""
    cart = get_or_create_cart(current_user, db)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return {"message": "Cart cleared successfully"}
