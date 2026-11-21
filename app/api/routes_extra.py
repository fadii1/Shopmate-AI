from fastapi import APIRouter, Query
from app.services.security_service import security_service
from app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="", tags=["Security & Recommendations"])


@router.get("/security/check-link")
async def check_link(url: str = Query(...)):
    """Verifies link safety and flags phishing/scam lookalikes."""
    return security_service.check_link_safety(url)


@router.get("/security/seller-score")
async def get_seller_score(
    rating: float = Query(4.5),
    orders_count: int = Query(150),
    complaints_count: int = Query(0),
    account_age_months: int = Query(18),
    return_acceptance_rate: float = Query(0.95)
):
    """Computes transparent Seller Trust Score."""
    return security_service.compute_seller_score(
        rating=rating,
        orders_count=orders_count,
        complaints_count=complaints_count,
        account_age_months=account_age_months,
        return_acceptance_rate=return_acceptance_rate
    )


@router.get("/recommendations")
async def get_recommendations(category: str = Query("running shoes")):
    """Returns curated dashboard recommendations."""
    return recommendation_service.get_recommendations(category)


@router.get("/price-drops")
async def get_price_drops():
    """Returns top active price drop watch items."""
    return recommendation_service.get_price_drop_watch()


@router.get("/gifts")
async def suggest_gifts(
    occasion: str = Query("Eid"),
    recipient: str = Query("Friend"),
    budget_pkr: float = Query(5000.0)
):
    """Personalized gift ideas."""
    return recommendation_service.suggest_gifts(occasion, recipient, budget_pkr)
