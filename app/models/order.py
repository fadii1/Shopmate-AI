from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
import uuid
from app.database import Base


class OrderModel(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    total_pkr = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # COD, JazzCash, Easypaisa, Card
    delivery_address = Column(String, nullable=False)
    status = Column(String, default="confirmed")  # confirmed, in_transit, delivered, cancelled
    courier_name = Column(String, default="TCS")  # TCS, Leopard, Trax
    tracking_id = Column(String, nullable=False)
    tracking_url = Column(String, nullable=False)
    items_json = Column(JSON, nullable=False)  # list of purchased items
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
