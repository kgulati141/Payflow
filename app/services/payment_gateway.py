import os
import uuid
import hmac
import hashlib

from dotenv import load_dotenv


load_dotenv()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


def create_gateway_payment(
    amount: float,
    order_id: int
):
    gateway_payment_id = (
        f"GW_{uuid.uuid4().hex[:12]}"
    )

    return {
        "gateway_payment_id": gateway_payment_id,
        "status": "pending",
        "amount": amount,
        "order_id": order_id
    }


def verify_webhook_signature(
    payload: bytes,
    signature: str
):
    if not WEBHOOK_SECRET:
        return False

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature
    )