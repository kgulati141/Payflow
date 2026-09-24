from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class OrderCreate(BaseModel):
    customer_name: str = Field(
        min_length=2,
        max_length=50
    )

    product_name: str = Field(
        min_length=2,
        max_length=100
    )

    amount: float = Field(
        gt=0
    )

    coupon_code: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: int
    customer_name: str
    product_name: str
    amount: float
    status: str

    model_config = ConfigDict(
        from_attributes=True
    )