from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import uuid


class CartItem(BaseModel):
    product_id: str
    title: str
    store: str
    seller: str
    seller_trust_score: int
    price_pkr: float
    delivery_fee_pkr: float = 0.0
    quantity: int = 1
    url: str
    image: Optional[str] = None
    payment_recommendation: str = "COD"  # COD or Online

    @property
    def subtotal_pkr(self) -> float:
        return (self.price_pkr + self.delivery_fee_pkr) * self.quantity


class Cart(BaseModel):
    session_id: str
    items: List[CartItem] = Field(default_factory=list)
    total_items: int = 0
    items_total_pkr: float = 0.0
    delivery_total_pkr: float = 0.0
    grand_total_pkr: float = 0.0


class CheckoutSummary(BaseModel):
    session_id: str
    items: List[CartItem]
    items_total_pkr: float
    delivery_total_pkr: float
    coupon_code: Optional[str] = None
    discount_pkr: float = 0.0
    final_total_pkr: float
    payment_method: str = "COD"
    delivery_address: str = "Gulberg, Lahore, Pakistan"
    approval_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    approved: bool = False
    requires_approval_prompt: str = "Confirm karun? (Haan/Nahi)"


class CheckoutApproval(BaseModel):
    approval_token: str
    approved: bool


class OrderConfirmation(BaseModel):
    order_id: str
    session_id: str
    items_count: int
    final_total_pkr: float
    payment_method: str
    delivery_address: str
    status: str = "confirmed"
    courier: str = "TCS"
    tracking_id: str
    estimated_delivery_days: int = 3
    message: str
