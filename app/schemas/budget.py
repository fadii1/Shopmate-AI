"""Pydantic schemas for budget management and wishlist."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


def _current_month() -> str:
    return datetime.now().strftime("%Y-%m")


class BudgetSet(BaseModel):
    session_id: str
    monthly_limit_pkr: float
    month: Optional[str] = None  # defaults to current YYYY-MM

    def get_month(self) -> str:
        return self.month or _current_month()


class BudgetStatus(BaseModel):
    session_id: str
    monthly_limit_pkr: float
    total_spent_pkr: float
    remaining_pkr: float
    percentage_used: float
    warning: Optional[str] = None
    month: str


class SpendingCategory(BaseModel):
    category: str
    amount_pkr: float
    percentage: float
    item_count: int


class SpendingReport(BaseModel):
    session_id: str
    month: str
    categories: List[SpendingCategory]
    total_spent_pkr: float
    monthly_limit_pkr: float


class WishlistItem(BaseModel):
    product_id: str
    title: str
    price_pkr: float
    store: str
    priority: int = Field(default=3, ge=1, le=5, description="1=highest priority")
    added_at: datetime = Field(default_factory=datetime.now)


class Wishlist(BaseModel):
    session_id: str
    items: List[WishlistItem]
    total_value_pkr: float
