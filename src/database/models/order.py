from enum import StrEnum, auto

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.database.models.base import Base


class OrderStatusEnum(StrEnum):
    PENDING = auto()
    PAID = auto()
    CANCELED = auto()


class OrderModel(Base):
    __tablename__ = "orders"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False
    )
    status = sa.Column(
        sa.Enum(OrderStatusEnum),
        server_default=OrderStatusEnum.PENDING,
        nullable=False
    )
    total_amount = sa.Column(
        sa.DECIMAL(10, 2),
        nullable=True
    )
    user = relationship("UserModel", back_populates="orders")
