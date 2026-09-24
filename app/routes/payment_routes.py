from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.tasks.payment_tasks import send_payment_notification
from app.database.db import get_db
from app.websocket_manager import manager
from app.models.webhook_event import WebhookEvent

from app.schemas.payment_schema import (
    PaymentResponse,
    PaymentWebhook
)

from app.services.payment_service import (
    create_payment,
    update_payment_status
)

from app.services.payment_gateway import (
    verify_webhook_signature
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


# =========================================================
# WEBHOOK
# =========================================================

@router.post("/webhook")
async def payment_webhook(
    webhook_data: PaymentWebhook,
    x_webhook_signature: str = Header(...),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # 1. Check if webhook event was already processed
    # -----------------------------------------------------

    existing_event = (
        db.query(WebhookEvent)
        .filter(
            WebhookEvent.event_id == webhook_data.event_id
        )
        .first()
    )

    if existing_event:
        return {
            "message": "Webhook already processed",
            "event_id": webhook_data.event_id
        }

    # -----------------------------------------------------
    # 2. Update payment status
    # -----------------------------------------------------

    payment, error = update_payment_status(
        db,
        webhook_data.payment_id,
        webhook_data.status
    )

    if error:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    # -----------------------------------------------------
    # 3. Create webhook event record
    # -----------------------------------------------------

    webhook_event = WebhookEvent(
        event_id=webhook_data.event_id,
        payment_id=webhook_data.payment_id,
        status=webhook_data.status
    )

    # -----------------------------------------------------
    # 4. Save webhook event
    # -----------------------------------------------------

    try:
        db.add(webhook_event)
        db.commit()

    except IntegrityError:
        db.rollback()

        return {
            "message": "Webhook already processed",
            "event_id": webhook_data.event_id
        }

    # -----------------------------------------------------
    # 5. Send real-time payment update via WebSocket
    # -----------------------------------------------------

    await manager.broadcast_to_payment(
        webhook_data.payment_id,
        f"Payment {webhook_data.payment_id}: "
        f"{webhook_data.status}"
    )

    # -----------------------------------------------------
    # 6. Successful response
    # -----------------------------------------------------

    return {
        "message": "Webhook processed successfully",
        "event_id": webhook_data.event_id,
        "payment_id": payment.payment_id,
        "status": payment.status
    }

def create_new_payment(
    order_id: int,
    idempotency_key: str = Header(...),
    db: Session = Depends(get_db)
):

    payment, error = create_payment(
        db,
        order_id,
        idempotency_key
    )

    if error:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    send_payment_notification.delay(
        payment.payment_id,
        payment.status
    )

    return payment

