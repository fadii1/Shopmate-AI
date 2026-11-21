import pytest
from app.services.cart_service import cart_service


@pytest.mark.asyncio
async def test_add_and_view_cart():
    session_id = "test-cart-session-1"
    cart = await cart_service.add_item(session_id, "daraz-shoe-01", quantity=1)

    assert cart.total_items == 1
    assert cart.items[0].product_id == "daraz-shoe-01"
    assert cart.grand_total_pkr > 4000.0


@pytest.mark.asyncio
async def test_remove_item():
    session_id = "test-cart-session-2"
    await cart_service.add_item(session_id, "daraz-shoe-01", quantity=1)
    cart = cart_service.remove_item(session_id, "daraz-shoe-01")

    assert cart.total_items == 0
    assert len(cart.items) == 0


@pytest.mark.asyncio
async def test_checkout_requires_approval():
    session_id = "test-cart-session-3"
    await cart_service.add_item(session_id, "daraz-shoe-01", quantity=1)

    # Calling approve with fake token must fail
    with pytest.raises(ValueError, match="Invalid or expired"):
        cart_service.approve_and_place_order("fake-token-xyz", approved=True)

    # Calling approve with approved=False cancels and places no order
    summary = cart_service.request_checkout(session_id)
    assert summary.approval_token is not None
    assert summary.approved is False

    with pytest.raises(ValueError, match="cancelled by user"):
        cart_service.approve_and_place_order(summary.approval_token, approved=False)


@pytest.mark.asyncio
async def test_full_checkout_flow():
    session_id = "test-cart-session-4"
    await cart_service.add_item(session_id, "daraz-shoe-01", quantity=1)

    # 1. Request checkout
    summary = cart_service.request_checkout(
        session_id=session_id,
        payment_method="COD",
        coupon_code="DARAZ100"
    )
    assert summary.discount_pkr == 100.0

    # 2. User approves (Haan)
    confirmation = cart_service.approve_and_place_order(summary.approval_token, approved=True)

    assert confirmation.order_id.startswith("KHD-")
    assert confirmation.status == "confirmed"
    assert confirmation.tracking_id != ""

    # Cart should be empty now
    cart = cart_service.get_cart(session_id)
    assert cart.total_items == 0


@pytest.mark.asyncio
async def test_cod_recommendation_for_untrusted_seller():
    session_id = "test-cart-session-5"
    # daraz-shoe-04 has low seller trust (48/100)
    cart = await cart_service.add_item(session_id, "daraz-shoe-04")
    assert cart.items[0].payment_recommendation == "COD"
