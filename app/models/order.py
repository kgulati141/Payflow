from sqlalchemy import Column, Integer, String, Float

from app.database.db import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_name = Column(
        String(50),
        nullable=False
    )

    product_name = Column(
        String(100),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    coupon_code = Column(
        String(50),
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="created"
    )