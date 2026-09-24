from pydantic import BaseModel


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    status: str
    provider: str
    transaction_id: str | None = None

    model_config = {
        "from_attributes": True
    }


class PaymentWebhook(BaseModel):
    event_id: str
    payment_id: int
    status: str