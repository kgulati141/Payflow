from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db

from app.schemas.order_schema import (
    OrderCreate,
    OrderResponse
)

from app.services.order_service import (
    get_all_orders,
    get_order_by_id,
    create_order,
    update_order,
    delete_order
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


# =========================================================
# GET ALL ORDERS
# =========================================================

@router.get(
    "",
    response_model=list[OrderResponse]
)
def get_orders(
    status: str | None = None,
    db: Session = Depends(get_db)
):
    return get_all_orders(
        db,
        status
    )


# =========================================================
# GET ORDER BY ID
# =========================================================

@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = get_order_by_id(
        db,
        order_id
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


# =========================================================
# CREATE ORDER
# =========================================================

@router.post(
    "",
    response_model=OrderResponse
)
def create_new_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    return create_order(
        db,
        order_data
    )


# =========================================================
# UPDATE ORDER
# =========================================================

@router.put(
    "/{order_id}",
    response_model=OrderResponse
)
def update_existing_order(
    order_id: int,
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    updated_order = update_order(
        db,
        order_id,
        order_data
    )

    if not updated_order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return updated_order


# =========================================================
# DELETE ORDER
# =========================================================

@router.delete(
    "/{order_id}"
)
def delete_existing_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    deleted_order = delete_order(
        db,
        order_id
    )

    if not deleted_order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return {
        "message": "Order deleted successfully",
        "order_id": order_id
    }