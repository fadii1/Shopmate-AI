import pytest
from app.services.alert_service import alert_service
from app.schemas.alert import AlertCreate


def test_alert_creation_and_trigger():
    alert_in = AlertCreate(
        product_id="daraz-shoe-01",
        product_title="Service Cheetah Running Shoes",
        store="Daraz",
        alert_type="price_drop",
        target_price=4000.0,
        user_contact="test@example.pk"
    )

    alert = alert_service.create_alert(alert_in, current_price=4499.0)
    assert alert.status == "active"
    assert alert.target_price == 4000.0

    # Test 1: Price still above target -> should not trigger
    triggered = alert_service.check_and_trigger_alerts("daraz-shoe-01", new_price=4200.0)
    assert len(triggered) == 0

    # Test 2: Price drops to or below target -> triggers!
    triggered = alert_service.check_and_trigger_alerts("daraz-shoe-01", new_price=3990.0)
    assert len(triggered) == 1
    assert "Rs. 3,990" in triggered[0]["message"]
    assert triggered[0]["contact"] == "test@example.pk"

    # Verify status changed
    updated = alert_service.get_alert(alert.id)
    assert updated.status == "triggered"
    assert updated.notified_at is not None
