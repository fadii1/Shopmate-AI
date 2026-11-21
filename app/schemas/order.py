"""Order and courier tracking schemas for Khareed."""

from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"
    returned = "returned"


class CourierInfo(BaseModel):
    courier_name: str
    tracking_id: str
    tracking_url: str
    current_status: str
    last_update: datetime
    estimated_delivery_date: date


class Order(BaseModel):
    order_id: str
    session_id: str
    items: List[dict]
    total_pkr: float
    payment_method: str
    delivery_address: str
    status: OrderStatus = OrderStatus.pending
    courier: Optional[CourierInfo] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrderDashboard(BaseModel):
    orders: List[Order]
    total_orders: int
    active_orders: int
    delivered_orders: int
