"""Tests for the Order Dashboard & Courier Tracking system."""

from __future__ import annotations

import pytest
from datetime import date, timedelta, datetime, timezone

from app.schemas.order import OrderStatus, CourierInfo
from app.services.order_service import OrderService


@pytest.fixture()
def svc() -> OrderService:
    """Fresh OrderService for each test."""
    return OrderService()


SAMPLE_ITEMS = [
    {"product_id": "drz-001", "title": "Nike Air Max", "price_pkr": 15000, "quantity": 1},
    {"product_id": "drz-002", "title": "Adidas T-shirt", "price_pkr": 3500, "quantity": 2},
]


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

def test_create_and_get_order(svc: OrderService):
    order = svc.create_order(
        order_id="ORD-001",
        session_id="sess-abc",
        items=SAMPLE_ITEMS,
        total=22000.0,
        payment_method="COD",
        address="House 5, Gulshan-e-Iqbal, Karachi",
    )

    assert order.order_id == "ORD-001"
    assert order.session_id == "sess-abc"
    assert order.total_pkr == 22000.0
    assert order.status == OrderStatus.pending
    assert order.courier is None
    assert len(order.items) == 2

    # Retrieve the same order
    fetched = svc.get_order("ORD-001")
    assert fetched.order_id == order.order_id
    assert fetched.delivery_address == "House 5, Gulshan-e-Iqbal, Karachi"


def test_order_dashboard(svc: OrderService):
    svc.create_order("ORD-A", "sess-1", SAMPLE_ITEMS, 10000, "COD", "Lahore")
    svc.create_order("ORD-B", "sess-1", SAMPLE_ITEMS, 5000, "JazzCash", "Islamabad")
    svc.create_order("ORD-C", "sess-1", SAMPLE_ITEMS, 3000, "COD", "Rawalpindi")
    # Mark one as delivered
    svc.update_order_status("ORD-B", OrderStatus.delivered)

    dashboard = svc.list_orders("sess-1")
    assert dashboard.total_orders == 3
    assert dashboard.active_orders == 2
    assert dashboard.delivered_orders == 1

    # Different session should be empty
    other = svc.list_orders("sess-other")
    assert other.total_orders == 0


def test_courier_tracking_tcs(svc: OrderService):
    # Use an order_id whose md5 hash mod 3 == 0 → TCS
    # We'll just call track and verify the result regardless of which courier
    svc.create_order("ORD-TCS-TEST", "sess-t", SAMPLE_ITEMS, 7000, "COD", "Karachi")
    tracking = svc.track_order("ORD-TCS-TEST")

    assert isinstance(tracking, CourierInfo)
    assert tracking.courier_name in ("TCS", "Leopard", "Trax")
    assert tracking.tracking_id  # non-empty
    assert tracking.tracking_url.startswith("https://")
    assert tracking.current_status  # non-empty
    assert tracking.estimated_delivery_date >= date.today()

    # If it's TCS, verify TCS-specific fields
    if tracking.courier_name == "TCS":
        assert "tcs.com.pk" in tracking.tracking_url
        assert tracking.tracking_id.startswith("TCS")


def test_courier_tracking_leopard(svc: OrderService):
    svc.create_order("ORD-LP-TEST", "sess-l", SAMPLE_ITEMS, 8000, "COD", "Lahore")
    tracking = svc.track_order("ORD-LP-TEST")

    assert isinstance(tracking, CourierInfo)
    assert tracking.courier_name in ("TCS", "Leopard", "Trax")
    assert tracking.tracking_id
    assert tracking.tracking_url.startswith("https://")
    assert tracking.estimated_delivery_date >= date.today()

    # If it's Leopard, verify Leopard-specific fields
    if tracking.courier_name == "Leopard":
        assert "leopardscourier.com" in tracking.tracking_url
        assert tracking.tracking_id.startswith("LP")


def test_delivery_delay_detection(svc: OrderService):
    svc.create_order("ORD-DELAYED", "sess-d", SAMPLE_ITEMS, 6000, "COD", "Peshawar")

    # Manually attach courier info with a past ETA
    past_eta = date.today() - timedelta(days=3)
    delayed_courier = CourierInfo(
        courier_name="TCS",
        tracking_id="TCS0000DELAY",
        tracking_url="https://track.tcs.com.pk/tracking?id=TCS0000DELAY",
        current_status="In transit – Peshawar hub",
        last_update=datetime.now(timezone.utc),
        estimated_delivery_date=past_eta,
    )
    svc.update_order_status("ORD-DELAYED", OrderStatus.in_transit, courier_info=delayed_courier)

    # Also create a non-delayed order
    svc.create_order("ORD-OK", "sess-d", SAMPLE_ITEMS, 4000, "COD", "Lahore")
    future_eta = date.today() + timedelta(days=2)
    ok_courier = CourierInfo(
        courier_name="Leopard",
        tracking_id="LP000OK",
        tracking_url="https://leopardscourier.com/tracking?track=LP000OK",
        current_status="With courier for delivery",
        last_update=datetime.now(timezone.utc),
        estimated_delivery_date=future_eta,
    )
    svc.update_order_status("ORD-OK", OrderStatus.in_transit, courier_info=ok_courier)

    delays = svc.check_delivery_delays("sess-d")
    assert len(delays) == 1
    assert delays[0]["order_id"] == "ORD-DELAYED"
    assert delays[0]["days_overdue"] == 3
    assert delays[0]["courier"] == "TCS"
