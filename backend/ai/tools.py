"""
AI tools for the support agent to access backend data.
"""

from sqlalchemy.orm import Session
from models import Product, Order, OrderStatus, PaymentStatus
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def search_products(query: str, db: Session) -> List[Dict[str, Any]]:
    """
    Search for products by name or description.
    
    Args:
        query: Search query string
        db: Database session
        
    Returns:
        List of products matching the query
    """
    products = db.query(Product).filter(
        Product.is_active == True,
        (Product.name.ilike(f"%{query}%") | Product.description.ilike(f"%{query}%"))
    ).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "stock": p.stock_quantity,
            "description": p.description[:100] if p.description else ""
        }
        for p in products
    ]


def get_product_by_name(product_name: str, db: Session) -> Dict[str, Any]:
    """
    Get a specific product by name.
    
    Args:
        product_name: Name of the product
        db: Database session
        
    Returns:
        Product details or None
    """
    product = db.query(Product).filter(
        Product.is_active == True,
        Product.name.ilike(f"%{product_name}%")
    ).first()
    
    if product:
        return {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock_quantity,
            "category": product.category,
            "description": product.description
        }
    return None


def get_product_stock(product_name: str, db: Session) -> Dict[str, Any]:
    """
    Get stock information for a product.
    
    Args:
        product_name: Name of the product
        db: Database session
        
    Returns:
        Stock information
    """
    product = db.query(Product).filter(
        Product.is_active == True,
        Product.name.ilike(f"%{product_name}%")
    ).first()
    
    if product:
        return {
            "product_name": product.name,
            "stock_quantity": product.stock_quantity,
            "in_stock": product.stock_quantity > 0,
            "price": product.price
        }
    return None


def get_all_products(db: Session) -> List[Dict[str, Any]]:
    """
    Get all available products.
    
    Args:
        db: Database session
        
    Returns:
        List of all active products
    """
    products = db.query(Product).filter(Product.is_active == True).limit(50).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "stock": p.stock_quantity,
            "category": p.category
        }
        for p in products
    ]


def get_my_orders(user_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    Get all orders for a user.
    
    Args:
        user_id: ID of the user
        db: Database session
        
    Returns:
        List of user's orders
    """
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    
    return [
        {
            "order_id": o.id,
            "total_amount": o.total_amount,
            "status": o.status.value,
            "payment_status": o.payment_status.value,
            "created_at": o.created_at.isoformat(),
            "item_count": len(o.items)
        }
        for o in orders
    ]


def get_order_status(order_id: int, user_id: int, db: Session) -> Dict[str, Any]:
    """
    Get status of a specific order (only for the owner).
    
    Args:
        order_id: ID of the order
        user_id: ID of the user requesting
        db: Database session
        
    Returns:
        Order status information
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()
    
    if order:
        return {
            "order_id": order.id,
            "total_amount": order.total_amount,
            "status": order.status.value,
            "payment_status": order.payment_status.value,
            "items": [
                {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "subtotal": item.subtotal
                }
                for item in order.items
            ],
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat()
        }
    return None
