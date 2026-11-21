"""FastAPI routes for order dashboard and courier tracking."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.schemas.order import OrderStatus
from app.services.order_service import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


# ---- request bodies ----

class StatusUpdateBody(BaseModel):
    status: OrderStatus
    courier_name: Optional[str] = None
    tracking_id: Optional[str] = None
    tracking_url: Optional[str] = None


# ---- routes ----

@router.get("")
async def order_dashboard(session_id: str = Query(...)):
    """Return full order dashboard for a session."""
    dashboard = order_service.list_orders(session_id)
    return dashboard.model_dump()


@router.get("/delays")
async def delayed_orders(session_id: str = Query(...)):
    """Return orders past their estimated delivery date."""
    delays = order_service.check_delivery_delays(session_id)
    return {"delayed_orders": delays, "count": len(delays)}


@router.get("/{order_id}")
async def get_order(order_id: str):
    """Get single order details."""
    try:
        order = order_service.get_order(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return order.model_dump()


@router.get("/{order_id}/track")
async def track_order(order_id: str):
    """Get courier tracking info for an order."""
    try:
        tracking = order_service.track_order(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return tracking.model_dump()


@router.post("/{order_id}/status")
async def update_status(order_id: str, body: StatusUpdateBody):
    """Update order status (for testing / admin)."""
    try:
        order = order_service.update_order_status(order_id, body.status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return order.model_dump()
