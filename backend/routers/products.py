"""
Products router — customer-facing product listing and details.
Admin product CRUD lives under /admin/products.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Product
from schemas import ProductResponse
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse], summary="List Products")
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query("", description="Search by product name"),
    category: str = Query("", description="Filter by category"),
    db: Session = Depends(get_db),
):
    """Return active products with pagination, search, and category filter."""
    query = db.query(Product).filter(Product.is_active == True)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category:
        query = query.filter(Product.category == category)

    skip = (page - 1) * limit
    return query.order_by(Product.id).offset(skip).limit(limit).all()


@router.get("/{product_id}", response_model=ProductResponse, summary="Get Product Details")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Return details for an active product."""
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product
