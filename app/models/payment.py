from sqlalchemy import Column, Integer, String, Numeric

from app.database.db import Base


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="pending"
    )

    provider = Column(
        String(30),
        nullable=False,
        default="mock_gateway"
    )

    transaction_id = Column(
        String(100),
        nullable=True,
        unique=True
    )

    idempotency_key = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )