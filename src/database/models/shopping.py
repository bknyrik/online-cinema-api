import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.database.models.base import Base
from src.database.models.accounts import UserModel


class CartModel(Base):
    __tablename__ = "carts"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    user = relationship(UserModel, back_populates="cart", single_parent=True)


class CartItemModel(Base):
    __tablename__ = "cart_items"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    cart_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("carts.id", ondelete="CASCADE")
    )
    cart = relationship(
        CartModel,
        back_populates="cart_items"
    )
