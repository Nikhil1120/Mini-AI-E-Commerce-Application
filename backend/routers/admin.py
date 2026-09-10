"""
Admin router — dashboard, product CRUD, and order management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Order, Product, OrderStatus, PaymentStatus
from schemas import (
    UserResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    OrderResponse,
    OrderUpdateStatus,
    StockUpdate,
)
from dependencies import get_current_admin
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", summary="Admin Dashboard Statistics")
def get_dashboard_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Return product, order, and revenue statistics."""
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    confirmed_orders = db.query(Order).filter(Order.status == OrderStatus.CONFIRMED).count()
    shipped_orders = db.query(Order).filter(Order.status == OrderStatus.SHIPPED).count()
    pending_payment = db.query(Order).filter(Order.payment_status == PaymentStatus.PENDING).count()

    total_revenue_result = (
        db.query(func.sum(Order.total_amount))
        .filter(Order.payment_status == PaymentStatus.PAID)
        .scalar()
    )

    return {
        "products": {
            "total": total_products,
            "active": active_products,
            "inactive": total_products - active_products,
        },
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
            "confirmed": confirmed_orders,
            "shipped": shipped_orders,
            "pending_payment": pending_payment,
        },
        "revenue": {
            "total": float(total_revenue_result or 0.0),
            "currency": "USD",
        },
    }


@router.get("/me", response_model=UserResponse, summary="Get Current Admin Info")
def get_current_admin_info(current_user: User = Depends(get_current_admin)):
    return current_user


# ==================== ADMIN PRODUCTS ====================

@router.post("/products", response_model=ProductResponse, summary="Create Product")
def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create a new product. Admin only."""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    logger.info(f"Product created: {db_product.id} by admin {current_user.id}")
    return db_product


@router.put("/products/{product_id}", response_model=ProductResponse, summary="Update Product")
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update an existing product. Admin only."""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    for field, value in product_update.model_dump(exclude_unset=True).items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    logger.info(f"Product updated: {product_id}")
    return db_product


@router.delete("/products/{product_id}", summary="Delete Product")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Soft-delete (deactivate) a product. Admin only."""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db_product.is_active = False
    db.commit()
    logger.info(f"Product deactivated: {product_id}")
    return {"message": "Product deleted successfully"}


@router.put("/products/{product_id}/stock", response_model=ProductResponse, summary="Update Product Stock")
def update_product_stock(
    product_id: int,
    stock_update: StockUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update product stock quantity. Admin only."""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db_product.stock_quantity = stock_update.stock_quantity
    db.commit()
    db.refresh(db_product)
    logger.info(f"Product stock updated: {product_id} -> {stock_update.stock_quantity}")
    return db_product


# ==================== ADMIN ORDERS ====================

@router.get("/orders", response_model=List[OrderResponse], summary="Get All Orders")
def get_all_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status_filter: str = Query("", description="Filter by order status"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """List all orders. Admin only."""
    query = db.query(Order)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    skip = (page - 1) * limit
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/orders/{order_id}", response_model=OrderResponse, summary="Get Order Details")
def get_admin_order(
    order_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Get any order. Admin only."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.put("/orders/{order_id}/status", response_model=OrderResponse, summary="Update Order Status")
def update_order_status(
    order_id: int,
    status_update: OrderUpdateStatus,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update order status (and optional payment status). Admin only."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = status_update.status
    if status_update.payment_status is not None:
        order.payment_status = status_update.payment_status

    db.commit()
    db.refresh(order)
    logger.info(f"Order status updated: {order_id} -> {status_update.status}")
    return order
