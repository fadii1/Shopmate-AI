from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.database import Base


class CartModel(Base):
    __tablename__ = "carts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, unique=True, nullable=False, index=True)
    coupon_code = Column(String, nullable=True)
    discount_pkr = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    items = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan")


class CartItemModel(Base):
    __tablename__ = "cart_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cart_id = Column(String, ForeignKey("carts.id"), nullable=False, index=True)
    product_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    store = Column(String, nullable=False)
    seller = Column(String, nullable=False)
    seller_trust_score = Column(Integer, default=80)
    price_pkr = Column(Float, nullable=False)
    delivery_fee_pkr = Column(Float, default=0.0)
    quantity = Column(Integer, default=1)
    url = Column(String, nullable=False)
    image = Column(String, nullable=True)
    payment_recommendation = Column(String, default="COD")

    cart = relationship("CartModel", back_populates="items")
