import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.schemas.alert import AlertCreate, AlertResponse


class AlertService:
    """Manages price-drop & back-in-stock alerts and triggers notifications."""

    def __init__(self):
        # In-memory alert store with persistence interface for Phase 1
        self._alerts: Dict[str, Dict[str, Any]] = {}
        self._notification_log: List[Dict[str, Any]] = []

    def create_alert(
        self,
        alert_in: AlertCreate,
        current_price: float
    ) -> AlertResponse:
        alert_id = f"alert-{uuid.uuid4().hex[:8]}"
        target = alert_in.target_price if alert_in.target_price is not None else round(current_price * 0.90, 2)

        record = {
            "id": alert_id,
            "product_id": alert_in.product_id,
            "product_title": alert_in.product_title,
            "store": alert_in.store,
            "alert_type": alert_in.alert_type,
            "target_price": target,
            "initial_price": current_price,
            "current_price": current_price,
            "status": "active",
            "user_contact": alert_in.user_contact,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "notified_at": None
        }
        self._alerts[alert_id] = record

        return AlertResponse(**record)

    def list_alerts(self) -> List[AlertResponse]:
        return [AlertResponse(**a) for a in self._alerts.values()]

    def get_alert(self, alert_id: str) -> Optional[AlertResponse]:
        data = self._alerts.get(alert_id)
        return AlertResponse(**data) if data else None

    def check_and_trigger_alerts(
        self,
        product_id: str,
        new_price: float,
        in_stock: bool = True
    ) -> List[Dict[str, Any]]:
        """Evaluate active alerts against updated price or stock, and dispatch notification."""
        triggered = []

        for alert in self._alerts.values():
            if alert["product_id"] != product_id or alert["status"] != "active":
                continue

            alert["current_price"] = new_price

            is_triggered = False
            message = ""

            if alert["alert_type"] == "price_drop":
                if alert["target_price"] and new_price <= alert["target_price"]:
                    is_triggered = True
                    message = (
                        f"🚨 Khareed Price-Drop Alert! '{alert['product_title']}' ki price "
                        f"Rs. {alert['initial_price']:,.0f} se gir kar Rs. {new_price:,.0f} ho gayi hai! "
                        f"Aapka target tha Rs. {alert['target_price']:,.0f}."
                    )
            elif alert["alert_type"] == "back_in_stock":
                if in_stock:
                    is_triggered = True
                    message = f"🎉 Back in Stock Alert! '{alert['product_title']}' ab stock mein wapis aa gaya hai!"

            if is_triggered:
                alert["status"] = "triggered"
                alert["notified_at"] = datetime.now(timezone.utc).isoformat()
                
                notif = {
                    "alert_id": alert["id"],
                    "contact": alert["user_contact"],
                    "message": message,
                    "timestamp": alert["notified_at"]
                }
                self._notification_log.append(notif)
                triggered.append(notif)

        return triggered

    @property
    def notification_history(self) -> List[Dict[str, Any]]:
        return list(self._notification_log)


alert_service = AlertService()
