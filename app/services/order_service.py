from sqlalchemy.orm import Session

from app.models.order import Order
from app.schemas.order_schema import OrderCreate

from app.services.redis_service import (
    get_json,
    set_json,
    delete_value
)


def get_all_orders(
    db: Session,
    status: str | None = None
):
    query = db.query(Order)

    if status:
        query = query.filter(
            Order.status == status
        )

    return query.all()


def get_order_by_id(
    db: Session,
    order_id: int
):
    # =====================================================
    # 1. Check Redis cache
    # =====================================================

    cache_key = f"order:{order_id}"

    cached_order = get_json(cache_key)

    if cached_order:
        print("Order fetched from Redis")

        return cached_order

    # =====================================================
    # 2. Redis MISS → Fetch from Database
    # =====================================================

    order = (
        db.query(Order)
        .filter(Order.order_id == order_id)
        .first()
    )

    if not order:
        return None

    # =====================================================
    # 3. Store order in Redis
    # =====================================================

    order_data = {
        "order_id": order.order_id,
        "customer_name": order.customer_name,
        "product_name": order.product_name,
        "amount": order.amount,
        "coupon_code": order.coupon_code,
        "status": order.status
    }

    set_json(
        cache_key,
        order_data,
        expiry=300
    )

    print("Order fetched from Database and cached in Redis")

    return order


def create_order(
    db: Session,
    order_data: OrderCreate
):
    new_order = Order(
        customer_name=order_data.customer_name,
        product_name=order_data.product_name,
        amount=order_data.amount,
        coupon_code=order_data.coupon_code,
        status="created"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


def update_order(
    db: Session,
    order_id: int,
    order_data: OrderCreate
):
    existing_order = get_order_by_id(
        db,
        order_id
    )

    if not existing_order:
        return None

    # If Redis returned a dictionary,
    # we need the actual DB object for update.
    if isinstance(existing_order, dict):

        existing_order = (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )

        if not existing_order:
            return None

    existing_order.customer_name = order_data.customer_name
    existing_order.product_name = order_data.product_name
    existing_order.amount = order_data.amount
    existing_order.coupon_code = order_data.coupon_code

    db.commit()
    db.refresh(existing_order)

    # =====================================================
    # Invalidate old cache
    # =====================================================

    delete_value(
        f"order:{order_id}"
    )

    return existing_order


def delete_order(
    db: Session,
    order_id: int
):
    existing_order = get_order_by_id(
        db,
        order_id
    )

    if not existing_order:
        return None

    if isinstance(existing_order, dict):

        existing_order = (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )

        if not existing_order:
            return None

    db.delete(existing_order)
    db.commit()

    # =====================================================
    # Remove order from Redis
    # =====================================================

    delete_value(
        f"order:{order_id}"
    )

    return existing_order