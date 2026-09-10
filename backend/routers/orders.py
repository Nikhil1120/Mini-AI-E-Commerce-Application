"""

Orders router for customer order operations.

Admin order endpoints live under /admin/orders.

"""



from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.orm import Session

from database import get_db

from models import (

    User,

    Order,

    OrderItem,

    Cart,

    Product,

    Payment,

    OrderStatus,

    PaymentStatus,

    UserRole,

)

from schemas import OrderResponse, OrderItemQuantityUpdate

from dependencies import get_current_customer

from typing import List

import logging



logger = logging.getLogger(__name__)



router = APIRouter(prefix="/orders", tags=["Orders"])





def _get_owned_order(db: Session, order_id: int, user: User) -> Order:

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Order not found",

        )

    if user.role != UserRole.ADMIN and order.user_id != user.id:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="You don't have permission to access this order",

        )

    return order





def _ensure_order_editable(order: Order) -> None:

    if order.payment_status != PaymentStatus.PENDING or order.status != OrderStatus.PENDING:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="Only pending unpaid orders can be modified",

        )





def _recalculate_order_total(order: Order) -> None:

    order.total_amount = round(sum(item.subtotal for item in order.items), 2)





@router.post("", response_model=OrderResponse, summary="Create Order")

def create_order(

    current_user: User = Depends(get_current_customer),

    db: Session = Depends(get_db),

):

    """

    Create an order from the user's cart.



    - Backend calculates totals from DB prices (never trusts frontend).

    - Stock is validated but NOT reduced until Stripe webhook confirms payment.

    - Cart is kept until payment succeeds so the user can retry checkout.

    """

    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()



    if not cart or not cart.items:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="Cart is empty",

        )



    total_amount = 0.0

    order_items_data = []



    for cart_item in cart.items:

        product = cart_item.product



        if not product or not product.is_active:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail=f"Product is no longer available",

            )



        if cart_item.quantity > product.stock_quantity:

            raise HTTPException(

                status_code=status.HTTP_409_CONFLICT,

                detail=f"Insufficient stock for '{product.name}'. Available: {product.stock_quantity}",

            )



        subtotal = round(product.price * cart_item.quantity, 2)

        total_amount += subtotal



        order_items_data.append(

            {

                "product_id": product.id,

                "product_name": product.name,

                "price": product.price,

                "quantity": cart_item.quantity,

                "subtotal": subtotal,

            }

        )



    try:

        order = Order(

            user_id=current_user.id,

            total_amount=round(total_amount, 2),

            status=OrderStatus.PENDING,

            payment_status=PaymentStatus.PENDING,

        )

        db.add(order)

        db.flush()



        for item_data in order_items_data:

            db.add(OrderItem(order_id=order.id, **item_data))



        db.commit()

        db.refresh(order)

        logger.info(f"Order created: {order.id} for user {current_user.id}")

        return order

    except HTTPException:

        db.rollback()

        raise

    except Exception as e:

        db.rollback()

        logger.error(f"Order creation failed: {e}")

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail="Failed to create order",

        )





@router.get("", response_model=List[OrderResponse], summary="Get User Orders")

def get_user_orders(

    page: int = Query(1, ge=1),

    limit: int = Query(10, ge=1, le=100),

    current_user: User = Depends(get_current_customer),

    db: Session = Depends(get_db),

):

    """Return only the authenticated customer's own orders."""

    query = db.query(Order).filter(Order.user_id == current_user.id)

    skip = (page - 1) * limit

    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()





@router.get("/{order_id}", response_model=OrderResponse, summary="Get Order Details")

def get_order_details(

    order_id: int,

    current_user: User = Depends(get_current_customer),

    db: Session = Depends(get_db),

):

    """Return order only if it belongs to the current user (or user is admin)."""

    return _get_owned_order(db, order_id, current_user)





@router.put(

    "/{order_id}/items/{item_id}",

    response_model=OrderResponse,

    summary="Update pending order item quantity",

)

def update_order_item_quantity(

    order_id: int,

    item_id: int,

    body: OrderItemQuantityUpdate,

    current_user: User = Depends(get_current_customer),

    db: Session = Depends(get_db),

):

    """Increase or decrease quantity on a pending unpaid order."""

    order = _get_owned_order(db, order_id, current_user)

    _ensure_order_editable(order)



    order_item = (

        db.query(OrderItem)

        .filter(OrderItem.id == item_id, OrderItem.order_id == order.id)

        .first()

    )

    if not order_item:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Order item not found",

        )



    product = db.query(Product).filter(Product.id == order_item.product_id).first()

    if not product or not product.is_active:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail=f"Product '{order_item.product_name}' is unavailable",

        )

    if body.quantity > product.stock_quantity:

        raise HTTPException(

            status_code=status.HTTP_409_CONFLICT,

            detail=f"Insufficient stock for '{product.name}'. Available: {product.stock_quantity}",

        )



    order_item.quantity = body.quantity

    order_item.subtotal = round(order_item.price * body.quantity, 2)

    _recalculate_order_total(order)



    payment = db.query(Payment).filter(Payment.order_id == order.id).first()

    if payment:

        payment.amount = order.total_amount



    db.commit()

    db.refresh(order)

    logger.info(f"Order {order.id} item {item_id} quantity updated to {body.quantity}")

    return order





@router.delete("/{order_id}", summary="Remove pending order")

def remove_order(

    order_id: int,

    current_user: User = Depends(get_current_customer),

    db: Session = Depends(get_db),

):

    """Remove a pending, failed, or cancelled order from the customer's list."""

    order = _get_owned_order(db, order_id, current_user)



    if order.payment_status == PaymentStatus.PAID:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="Paid orders cannot be removed",

        )



    db.delete(order)

    db.commit()

    logger.info(f"Order {order_id} removed by user {current_user.id}")

    return {"message": "Order removed successfully", "order_id": order_id}


