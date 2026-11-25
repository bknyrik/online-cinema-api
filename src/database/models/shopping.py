from enum import StrEnum, auto

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.database.models.base import Base
from src.database.models.accounts import UserModel
from src.database.models.cinema import MovieModel


class CartModel(Base):
    __tablename__ = "carts"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    user = relationship(UserModel, back_populates="cart", single_parent=True)
    cart_items = relationship(
        "CartItemModel",
        back_populates="cart",
        cascade="all, delete-orphan"
    )


class CartItemModel(Base):
    __tablename__ = "cart_items"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    cart_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False
    )
    movie_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False
    )
    added_at = sa.Column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False
    )
    movie = relationship(
        MovieModel,
        back_populates="cart_items"
    )
    cart = relationship(
        CartModel,
        back_populates="cart_items"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "movie_id", "cart_id",
            name="movie_id_cart_id_unique"
        ),
    )


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
        server_default=OrderStatusEnum.PENDING.upper(),
        nullable=False
    )
    total_amount = sa.Column(
        sa.DECIMAL(10, 2),
        nullable=True
    )
    user = relationship("UserModel", back_populates="orders")
    order_items = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan"
    )


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    order_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    movie_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False
    )
    price_at_order = sa.Column(
        sa.DECIMAL(10, 2),
        nullable=False
    )
    order = relationship(
        OrderModel,
        back_populates="order_items"
    )
    movie = relationship(
        MovieModel,
        back_populates="order_items"
    )
