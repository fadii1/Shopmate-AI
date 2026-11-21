from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    store = Column(String, nullable=False, index=True)  # Daraz, Amazon, etc.
    seller = Column(String, nullable=False)
    seller_trust_score = Column(Integer, default=80)
    price_pkr = Column(Float, nullable=False)
    original_price_pkr = Column(Float, nullable=True)
    delivery_fee_pkr = Column(Float, default=0.0)
    delivery_days = Column(Integer, default=3)
    rating = Column(Float, default=4.0)
    review_count = Column(Integer, default=0)
    url = Column(String, nullable=False)
    image = Column(String, nullable=True)
    in_stock = Column(Boolean, default=True)
    specs = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    price_history = relationship("PriceHistoryModel", back_populates="product", cascade="all, delete-orphan")


class PriceHistoryModel(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, ForeignKey("products.id"), index=True, nullable=False)
    price_pkr = Column(Float, nullable=False)
    original_price_pkr = Column(Float, nullable=True)
    is_sale = Column(Boolean, default=False)
    recorded_date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("ProductModel", back_populates="price_history")
