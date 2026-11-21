from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.cart_service import cart_service

router = APIRouter(prefix="/cart", tags=["Unified Cart & Checkout"])


class AddToCartBody(BaseModel):
    session_id: str = "default-session"
    product_id: str
    quantity: int = 1


class RemoveFromCartBody(BaseModel):
    session_id: str = "default-session"
    product_id: str


class CheckoutRequestBody(BaseModel):
    session_id: str = "default-session"
    payment_method: str = "COD"
    delivery_address: str = "Gulberg, Lahore, Pakistan"
    coupon_code: Optional[str] = None


class ApproveCheckoutBody(BaseModel):
    approval_token: str
    approved: bool


@router.get("")
async def get_cart(session_id: str = Query("default-session")):
    """Retrieve the unified multi-store cart."""
    return cart_service.get_cart(session_id).model_dump()


@router.post("/add")
async def add_item_to_cart(body: AddToCartBody):
    """Add a product from any store into the unified cart."""
    try:
        cart = await cart_service.add_item(body.session_id, body.product_id, body.quantity)
        return cart.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/remove")
async def remove_item_from_cart(body: RemoveFromCartBody):
    """Remove a product from the unified cart."""
    cart = cart_service.remove_item(body.session_id, body.product_id)
    return cart.model_dump()


@router.post("/checkout")
async def request_checkout(body: CheckoutRequestBody):
    """Step 1 of checkout: Generates summary & approval token. Does NOT complete order."""
    try:
        summary = cart_service.request_checkout(
            session_id=body.session_id,
            payment_method=body.payment_method,
            delivery_address=body.delivery_address,
            coupon_code=body.coupon_code
        )
        return summary.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/approve")
async def approve_and_place_order(body: ApproveCheckoutBody):
    """Step 2 of checkout: Gated by user approval. ONLY places order if approved is True."""
    try:
        confirmation = cart_service.approve_and_place_order(
            approval_token=body.approval_token,
            approved=body.approved
        )
        return confirmation.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/coupons")
async def find_coupons(store: str = Query("Daraz"), total_pkr: float = Query(2500.0)):
    """Search for valid coupons for store and cart value."""
    return cart_service.find_coupons(store, total_pkr)
