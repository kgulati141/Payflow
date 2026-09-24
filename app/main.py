from fastapi import FastAPI, Depends, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.websocket_manager import manager

from app.database.db import engine, Base, get_db

from app.models.order import Order
from app.models.user import User
from app.models.payment import Payment

from app.database.redis import get_redis

from app.services.redis_service import (
    set_value,
    get_value,
    delete_value,
    key_exists,
    set_expiry,
    set_json,
    get_json
)

from app.routes.order_routes import router as order_router
from app.routes.auth_routes import router as auth_router
from app.routes.payment_routes import router as payment_router


app = FastAPI(
    title="PayFlow API",
    description="Payment and Order Processing Platform",
    version="1.0.0"
)


# =========================================================
# Create Database Tables
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# Home
# =========================================================

@app.get("/")
def home():
    return {
        "message": "PayFlow API is running"
    }


# =========================================================
# WebSocket
# =========================================================

@app.websocket("/ws/payments/{payment_id}")
async def payment_websocket(
    websocket: WebSocket,
    payment_id: int
):
    await manager.connect(
        payment_id,
        websocket
    )

    try:
        while True:
            message = await websocket.receive_text()

            await manager.broadcast_to_payment(
                payment_id,
                f"Payment {payment_id}: {message}"
            )

    except WebSocketDisconnect:
        manager.disconnect(
            payment_id,
            websocket
        )


# =========================================================
# Redis Delete Test
# =========================================================

@app.get("/redis-delete-test")
def redis_delete_test():

    set_value(
        "payflow_test",
        "Hello Redis"
    )

    before_delete = get_value(
        "payflow_test"
    )

    delete_value(
        "payflow_test"
    )

    after_delete = get_value(
        "payflow_test"
    )

    return {
        "before_delete": before_delete,
        "after_delete": after_delete
    }


# =========================================================
# Redis JSON Test
# =========================================================

@app.get("/redis-json-test")
def redis_json_test():

    data = {
        "order_id": 101,
        "amount": 5000,
        "status": "PENDING"
    }

    set_json(
        "order:101",
        data,
        expiry=300
    )

    cached_data = get_json(
        "order:101"
    )

    return {
        "data": cached_data
    }


# =========================================================
# Test Database
# =========================================================

@app.get("/test-db")
def test_db(
    db=Depends(get_db)
):
    return {
        "message": "Database session created successfully"
    }


# =========================================================
# Routers
# =========================================================

app.include_router(order_router)
app.include_router(auth_router)
app.include_router(payment_router)