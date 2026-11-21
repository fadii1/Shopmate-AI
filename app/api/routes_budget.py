"""FastAPI routes for budget management and wishlist."""

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.schemas.budget import BudgetSet
from app.services.budget_service import budget_service

router = APIRouter()


# ── Budget routes ───────────────────────────────────────────────────────

@router.post("/budget/set")
async def set_budget(body: BudgetSet):
    """Set monthly budget for a session."""
    result = budget_service.set_budget(
        session_id=body.session_id,
        monthly_limit_pkr=body.monthly_limit_pkr,
        month=body.get_month(),
    )
    return result


@router.get("/budget/status")
async def budget_status(session_id: str = Query(...)):
    """Get current budget status with warnings."""
    return budget_service.get_status(session_id)


@router.get("/budget/report")
async def spending_report(
    session_id: str = Query(...),
    month: Optional[str] = Query(None),
):
    """Get category-wise spending report."""
    return budget_service.get_spending_report(session_id, month)


# ── Wishlist routes ─────────────────────────────────────────────────────

class WishlistAddBody(BaseModel):
    session_id: str
    product_id: str
    title: str
    price_pkr: float
    store: str
    priority: int = 3


class WishlistRemoveBody(BaseModel):
    session_id: str
    product_id: str


@router.post("/wishlist/add")
async def add_to_wishlist(body: WishlistAddBody):
    """Add item to wishlist."""
    return budget_service.add_to_wishlist(
        session_id=body.session_id,
        product_id=body.product_id,
        title=body.title,
        price_pkr=body.price_pkr,
        store=body.store,
        priority=body.priority,
    )


@router.get("/wishlist")
async def view_wishlist(session_id: str = Query(...)):
    """View wishlist sorted by priority."""
    return budget_service.get_wishlist(session_id)


@router.delete("/wishlist/remove")
async def remove_from_wishlist(body: WishlistRemoveBody):
    """Remove item from wishlist."""
    return budget_service.remove_from_wishlist(body.session_id, body.product_id)
