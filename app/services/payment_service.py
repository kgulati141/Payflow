from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment
from app.services.payment_gateway import create_gateway_payment


def create_payment(
    db: Session,
    order_id: int,
    idempotency_key: str
):
    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.idempotency_key == idempotency_key
        )
        .first()
    )

    if existing_payment:
        return existing_payment, None

    order = (
        db.query(Order)
        .filter(
            Order.order_id == order_id
        )
        .first()
    )

    if not order:
        return None, "Order not found"

    gateway_response = create_gateway_payment(
        amount=float(order.amount),
        order_id=order.order_id
    )

    payment = Payment(
        order_id=order.order_id,
        amount=order.amount,
        status=gateway_response["status"],
        provider="mock_gateway",
        transaction_id=gateway_response["gateway_payment_id"],
        idempotency_key=idempotency_key
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment, None

def update_payment_status(
    db: Session,
    payment_id: int,
    status: str
):
    payment = (
        db.query(Payment)
        .filter(
            Payment.payment_id == payment_id
        )
        .first()
    )

    if not payment:
        return None, "Payment not found"

    allowed_statuses = {
        "success",
        "failed"
    }

    if status not in allowed_statuses:
        return None, "Invalid payment status"

    payment.status = status

    db.commit()
    db.refresh(payment)

    return payment, None