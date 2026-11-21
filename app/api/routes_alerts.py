from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.schemas.alert import AlertCreate, AlertResponse
from app.services.alert_service import alert_service
from app.adapters.registry import registry

router = APIRouter(prefix="/alerts", tags=["Price & Stock Alerts"])


@router.post("", response_model=AlertResponse)
async def create_price_alert(alert_in: AlertCreate):
    product = await registry.get_product_by_id(alert_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {alert_in.product_id} not found")

    created = alert_service.create_alert(alert_in, current_price=product.price_pkr)
    return created


@router.get("", response_model=List[AlertResponse])
async def list_alerts():
    return alert_service.list_alerts()


@router.post("/check")
async def check_alerts_now(
    product_id: str = Query(..., description="Product ID to simulate price change for"),
    new_price: float = Query(..., description="New price in PKR to test alert trigger")
):
    """Simulates background job check when store scrapers or APIs detect a price change."""
    triggered = alert_service.check_and_trigger_alerts(product_id=product_id, new_price=new_price)
    return {
        "status": "checked",
        "triggered_count": len(triggered),
        "notifications": triggered
    }
