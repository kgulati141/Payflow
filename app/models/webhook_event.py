from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.database.db import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    event_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    payment_id = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False
    )

    processed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )