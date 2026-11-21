from typing import Optional, Literal
from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    product_id: str
    product_title: str
    store: str
    alert_type: Literal["price_drop", "back_in_stock"] = "price_drop"
    target_price: Optional[float] = Field(None, description="Target price threshold in PKR")
    user_contact: str = Field(
        "console",
        description="User contact destination (email, phone, or 'console')"
    )


class AlertResponse(BaseModel):
    id: str
    product_id: str
    product_title: str
    store: str
    alert_type: str
    target_price: Optional[float]
    initial_price: float
    current_price: float
    status: Literal["active", "triggered", "cancelled"]
    created_at: str
    notified_at: Optional[str] = None
