import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone

from app.schemas.cart import Cart, CartItem, CheckoutSummary, CheckoutApproval, OrderConfirmation
from app.adapters.registry import registry
from app.services.order_service import order_service


class CartService:
    """Manages unified multi-store cart, approval tokens, and approval-gated checkouts."""

    def __init__(self):
        self._carts: Dict[str, Dict[str, CartItem]] = {}
        self._approval_tokens: Dict[str, CheckoutSummary] = {}

    def get_cart(self, session_id: str) -> Cart:
        items_dict = self._carts.get(session_id, {})
        items = list(items_dict.values())
        items_total = sum(item.price_pkr * item.quantity for item in items)
        delivery_total = sum(item.delivery_fee_pkr for item in items)
        grand_total = items_total + delivery_total

        return Cart(
            session_id=session_id,
            items=items,
            total_items=sum(item.quantity for item in items),
            items_total_pkr=round(items_total, 2),
            delivery_total_pkr=round(delivery_total, 2),
            grand_total_pkr=round(grand_total, 2)
        )

    async def add_item(self, session_id: str, product_id: str, quantity: int = 1) -> Cart:
        product = await registry.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product '{product_id}' not found.")

        # Payment recommendation logic based on local Pakistani trust rules
        # Low trust seller (<70) or high price (>15,000 PKR) -> Recommend COD
        if product.seller_trust_score < 70 or product.price_pkr > 15000:
            payment_rec = "COD"
        else:
            payment_rec = "Online / JazzCash / Easypaisa"

        if session_id not in self._carts:
            self._carts[session_id] = {}

        if product_id in self._carts[session_id]:
            self._carts[session_id][product_id].quantity += quantity
        else:
            self._carts[session_id][product_id] = CartItem(
                product_id=product.id,
                title=product.title,
                store=product.store,
                seller=product.seller,
                seller_trust_score=product.seller_trust_score,
                price_pkr=product.price_pkr,
                delivery_fee_pkr=product.delivery_fee_pkr,
                quantity=quantity,
                url=product.url,
                image=product.image,
                payment_recommendation=payment_rec
            )

        return self.get_cart(session_id)

    def remove_item(self, session_id: str, product_id: str) -> Cart:
        if session_id in self._carts and product_id in self._carts[session_id]:
            del self._carts[session_id][product_id]
        return self.get_cart(session_id)

    def clear_cart(self, session_id: str):
        if session_id in self._carts:
            self._carts[session_id].clear()

    def find_coupons(self, store: str, cart_total: float) -> List[Dict]:
        """Discovers valid promotional coupons with actual savings."""
        coupons = []
        if cart_total >= 2000:
            coupons.append({
                "code": "DARAZ100",
                "discount_pkr": 100.0,
                "description": "Rs. 100 off on orders above Rs. 2,000",
                "is_valid": True
            })
        if cart_total >= 5000:
            coupons.append({
                "code": "KHAREED500",
                "discount_pkr": 500.0,
                "description": "Rs. 500 discount for Khareed AI shoppers",
                "is_valid": True
            })
        return coupons

    def request_checkout(
        self,
        session_id: str,
        payment_method: str = "COD",
        delivery_address: str = "Gulberg, Lahore, Pakistan",
        coupon_code: Optional[str] = None
    ) -> CheckoutSummary:
        cart = self.get_cart(session_id)
        if not cart.items:
            raise ValueError("Cart is empty. Pehle items add karein.")

        discount = 0.0
        if coupon_code:
            coupon_upper = coupon_code.strip().upper()
            if coupon_upper == "DARAZ100" and cart.grand_total_pkr >= 2000:
                discount = 100.0
            elif coupon_upper == "KHAREED500" and cart.grand_total_pkr >= 5000:
                discount = 500.0

        final_total = max(0.0, cart.grand_total_pkr - discount)
        token = str(uuid.uuid4())

        summary = CheckoutSummary(
            session_id=session_id,
            items=cart.items,
            items_total_pkr=cart.items_total_pkr,
            delivery_total_pkr=cart.delivery_total_pkr,
            coupon_code=coupon_code,
            discount_pkr=discount,
            final_total_pkr=final_total,
            payment_method=payment_method,
            delivery_address=delivery_address,
            approval_token=token,
            approved=False,
            requires_approval_prompt="Confirm karun? (Haan/Nahi)"
        )

        self._approval_tokens[token] = summary
        return summary

    def approve_and_place_order(self, approval_token: str, approved: bool) -> OrderConfirmation:
        """HARD RULE: Order cannot be completed without explicit stored user approval."""
        if approval_token not in self._approval_tokens:
            raise ValueError("Invalid or expired checkout approval token.")

        checkout = self._approval_tokens[approval_token]

        if not approved:
            del self._approval_tokens[approval_token]
            raise ValueError("Checkout cancelled by user (Nahi). No money spent.")

        checkout.approved = True
        order_id = f"KHD-{uuid.uuid4().hex[:6].upper()}"

        # Create live order in order_service
        created_order = order_service.create_order(
            order_id=order_id,
            session_id=checkout.session_id,
            items=[item.model_dump() for item in checkout.items],
            total=checkout.final_total_pkr,
            payment_method=checkout.payment_method,
            address=checkout.delivery_address,
        )
        courier_info = order_service.track_order(order_id)

        # Clear cart upon successful order
        self.clear_cart(checkout.session_id)
        del self._approval_tokens[approval_token]

        return OrderConfirmation(
            order_id=order_id,
            session_id=checkout.session_id,
            items_count=len(checkout.items),
            final_total_pkr=checkout.final_total_pkr,
            payment_method=checkout.payment_method,
            delivery_address=checkout.delivery_address,
            status="confirmed",
            courier=courier_info.courier_name,
            tracking_id=courier_info.tracking_id,
            estimated_delivery_days=3,
            message=f"Mubarak ho! Aapka order confirm ho chuka hai. {courier_info.courier_name} courier ke zariye deliver hoga."
        )


cart_service = CartService()
