from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime, timezone
import uuid
from app.database import Base


class AlertModel(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, nullable=False, index=True)
    product_title = Column(String, nullable=False)
    store = Column(String, nullable=False)
    alert_type = Column(String, default="price_drop")  # price_drop, back_in_stock
    target_price = Column(Float, nullable=True)
    initial_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    status = Column(String, default="active")  # active, triggered, cancelled
    user_contact = Column(String, default="console")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notified_at = Column(DateTime, nullable=True)
