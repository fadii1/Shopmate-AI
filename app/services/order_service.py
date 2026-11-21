"""Order management and courier tracking service for Khareed."""

from __future__ import annotations

import random
import hashlib
from datetime import datetime, timedelta, date, timezone
from typing import Dict, List, Optional, Any

from app.schemas.order import (
    CourierInfo,
    Order,
    OrderDashboard,
    OrderStatus,
)

# Pakistani cities used in mock tracking
_PK_CITIES = [
    "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad",
    "Multan", "Peshawar", "Quetta", "Sialkot", "Hyderabad",
]

# Courier configuration
_COURIERS: Dict[str, dict] = {
    "TCS": {
        "url_template": "https://track.tcs.com.pk/tracking?id={tracking_id}",
        "prefix": "TCS",
        "statuses": [
            "Shipment booked",
            "Picked up from seller",
            "In transit – {city} hub",
            "Out for delivery",
            "Delivered",
        ],
    },
    "Leopard": {
        "url_template": "https://leopardscourier.com/tracking?track={tracking_id}",
        "prefix": "LP",
        "statuses": [
            "Order received",
            "Package collected",
            "Arrived at {city} sorting facility",
            "With courier for delivery",
            "Delivered",
        ],
    },
    "Trax": {
        "url_template": "https://trax.pk/track/{tracking_id}",
        "prefix": "TRX",
        "statuses": [
            "Booked",
            "Picked up",
            "Reached {city} warehouse",
            "On the way",
            "Delivered",
        ],
    },
}


class OrderService:
    """In-memory order management with mock courier tracking."""

    def __init__(self) -> None:
        self._orders: Dict[str, Order] = {}

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_order(
        self,
        order_id: str,
        session_id: str,
        items: List[dict],
        total: float,
        payment_method: str,
        address: str,
    ) -> Order:
        now = datetime.now(timezone.utc)
        order = Order(
            order_id=order_id,
            session_id=session_id,
            items=items,
            total_pkr=total,
            payment_method=payment_method,
            delivery_address=address,
            status=OrderStatus.pending,
            created_at=now,
            updated_at=now,
        )
        self._orders[order_id] = order
        return order

    def get_order(self, order_id: str) -> Order:
        if order_id not in self._orders:
            raise ValueError(f"Order {order_id} not found")
        return self._orders[order_id]

    def list_orders(self, session_id: str) -> OrderDashboard:
        orders = [o for o in self._orders.values() if o.session_id == session_id]
        active = [
            o for o in orders
            if o.status not in (OrderStatus.delivered, OrderStatus.cancelled, OrderStatus.returned)
        ]
        delivered = [o for o in orders if o.status == OrderStatus.delivered]
        return OrderDashboard(
            orders=orders,
            total_orders=len(orders),
            active_orders=len(active),
            delivered_orders=len(delivered),
        )

    def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        courier_info: Optional[CourierInfo] = None,
    ) -> Order:
        order = self.get_order(order_id)
        order.status = status
        order.updated_at = datetime.now(timezone.utc)
        if courier_info is not None:
            order.courier = courier_info
        self._orders[order_id] = order
        return order

    # ------------------------------------------------------------------
    # Tracking
    # ------------------------------------------------------------------

    def track_order(self, order_id: str) -> CourierInfo:
        order = self.get_order(order_id)
        if order.courier:
            return order.courier
        # Pick a deterministic courier based on order_id hash
        idx = int(hashlib.md5(order_id.encode()).hexdigest(), 16) % len(_COURIERS)
        courier_name = list(_COURIERS.keys())[idx]
        tracking = self._generate_mock_tracking(order_id, courier_name)
        order.courier = tracking
        order.status = OrderStatus.in_transit
        order.updated_at = datetime.now(timezone.utc)
        self._orders[order_id] = order
        return tracking

    def _generate_mock_tracking(self, order_id: str, courier: str) -> CourierInfo:
        cfg = _COURIERS[courier]
        # Deterministic but varied tracking id
        digest = hashlib.md5(order_id.encode()).hexdigest()[:10].upper()
        tracking_id = f"{cfg['prefix']}{digest}"
        tracking_url = cfg["url_template"].format(tracking_id=tracking_id)

        # Pick a random-but-deterministic city and status
        rng = random.Random(order_id)
        city = rng.choice(_PK_CITIES)
        status_idx = rng.randint(1, len(cfg["statuses"]) - 2)  # not first, not delivered
        current_status = cfg["statuses"][status_idx].format(city=city)

        last_update = datetime.now(timezone.utc) - timedelta(hours=rng.randint(1, 12))
        eta = date.today() + timedelta(days=rng.randint(1, 4))

        return CourierInfo(
            courier_name=courier,
            tracking_id=tracking_id,
            tracking_url=tracking_url,
            current_status=current_status,
            last_update=last_update,
            estimated_delivery_date=eta,
        )

    # ------------------------------------------------------------------
    # Delay detection
    # ------------------------------------------------------------------

    def check_delivery_delays(self, session_id: str) -> List[dict]:
        delayed: List[dict] = []
        for order in self._orders.values():
            if order.session_id != session_id:
                continue
            if order.status in (OrderStatus.delivered, OrderStatus.cancelled, OrderStatus.returned):
                continue
            if order.courier and order.courier.estimated_delivery_date < date.today():
                delayed.append({
                    "order_id": order.order_id,
                    "courier": order.courier.courier_name,
                    "tracking_id": order.courier.tracking_id,
                    "estimated_delivery_date": str(order.courier.estimated_delivery_date),
                    "days_overdue": (date.today() - order.courier.estimated_delivery_date).days,
                    "current_status": order.courier.current_status,
                })
        return delayed


# Module-level singleton
order_service = OrderService()
