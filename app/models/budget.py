from sqlalchemy import Column, String, Float, Integer, DateTime
from datetime import datetime, timezone
import uuid
from app.database import Base


class BudgetModel(Base):
    __tablename__ = "budgets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, index=True)
    month = Column(String, nullable=False, index=True)  # YYYY-MM
    monthly_limit_pkr = Column(Float, default=25000.0)
    total_spent_pkr = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SpendingRecordModel(Base):
    __tablename__ = "spendings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, index=True)
    month = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False)  # Electronics, Footwear, Fashion, Groceries
    amount_pkr = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class WishlistModel(Base):
    __tablename__ = "wishlist"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, index=True)
    product_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    price_pkr = Column(Float, nullable=False)
    store = Column(String, nullable=False)
    priority = Column(Integer, default=1)  # 1 = High, 2 = Medium, 3 = Low
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
