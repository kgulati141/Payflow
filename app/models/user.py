from sqlalchemy import Column, Integer, String

from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    UserID = Column(
        Integer,
        primary_key=True,
        index=True
    )

    Username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    Password = Column(
        String(255),
        nullable=False
    )

    Role = Column(
        String(20),
        nullable=False,
        default="user"
    )