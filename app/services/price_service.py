from typing import List, Dict, Any, Optional
from app.schemas.product import Product


class PriceService:
    """Handles price comparison, best-pick ranking, and 30/90-day sale authenticity analysis."""

    def compare_products(self, products: List[Product]) -> Dict[str, Any]:
        """Compare a list of products across stores and identify the best value option."""
        if not products:
            return {
                "best_pick": None,
                "comparison": [],
                "summary": "Koi product nahi mila."
            }

        comparison_list = []
        for p in products:
            comparison_list.append({
                "product_id": p.id,
                "title": p.title,
                "store": p.store,
                "seller": p.seller,
                "seller_trust_score": p.seller_trust_score,
                "item_price_pkr": p.price_pkr,
                "delivery_fee_pkr": p.delivery_fee_pkr,
                "total_price_pkr": p.total_price_pkr,
                "delivery_days": p.delivery_days,
                "rating": p.rating,
                "return_policy": p.return_policy,
                "url": p.url
            })

        # Rank by: total price + trust score + rating + delivery days
        # Score = (rating * 20 + trust_score) / (total_price / 1000 + 1)
        # Deduct penalty if delivery takes longer than 7 days
        def score_product(p: Product) -> float:
            base_score = (p.rating * 20.0 + p.seller_trust_score) / (p.total_price_pkr / 2000.0 + 1.0)
            if p.delivery_days > 7:
                base_score *= 0.8  # international delivery penalty
            if p.seller_trust_score < 60:
                base_score *= 0.5  # untrusted seller heavy penalty
            return base_score

        best = max(products, key=score_product)

        # Reasons why this is best
        reasons = []
        if best.total_price_pkr <= min(p.total_price_pkr for p in products):
            reasons.append("Sab se behtareen price")
        if best.seller_trust_score >= max(p.seller_trust_score for p in products):
            reasons.append(f"Aala seller trust ({best.seller_trust_score}/100)")
        if best.delivery_days <= min(p.delivery_days for p in products):
            reasons.append(f"Tez tareen delivery ({best.delivery_days} din)")
        if not reasons:
            reasons.append("Overall value aur rating ka behtareen balance")

        return {
            "best_pick": {
                "product": best,
                "reason": " • ".join(reasons)
            },
            "comparison": comparison_list,
            "total_options": len(products)
        }

    def evaluate_sale(self, product: Product, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare current price against 30/90-day price history.
        
        Classifies as:
        - 'Real deal': Price is >= 10% lower than 30-day average.
        - 'Fake sale': Item is marked on sale, but the regular price was artificially jacked up,
                      or current sale price is >= 30-day baseline.
        - 'Normal price': Within standard +/- 5% range of historical average.
        """
        if not history:
            return {
                "verdict": "Normal price",
                "details": "Naya product hai ya history abhi record ho rahi hai.",
                "history_points": 0
            }

        prices = [h["price_pkr"] for h in history if "price_pkr" in h]
        if not prices:
            return {
                "verdict": "Normal price",
                "details": "Historical price data na-kafi hai.",
                "history_points": 0
            }

        avg_price = sum(prices) / len(prices)
        current_price = product.price_pkr

        # Check for fake sale conditions
        has_fake_original = any(h.get("fake_original") for h in history)
        is_marked_on_sale = product.original_price_pkr is not None and product.original_price_pkr > product.price_pkr

        if has_fake_original or (is_marked_on_sale and current_price >= avg_price * 0.98):
            return {
                "verdict": "Fake sale",
                "badge": "⚠️ Fake sale",
                "details": (
                    f"Original price ko barha kar dikhaya gaya hai. "
                    f"Aam dino mein bhi ye Rs. {avg_price:,.0f} ka hi bikta hai."
                ),
                "avg_30_90_days": round(avg_price, 2),
                "current_price": current_price
            }

        # Real deal: at least 10% below average history
        if current_price <= avg_price * 0.90:
            savings = round(avg_price - current_price, 2)
            pct = round((savings / avg_price) * 100, 1)
            return {
                "verdict": "Real deal",
                "badge": "🔥 Real deal",
                "details": (
                    f"30/90 dino ki average price (Rs. {avg_price:,.0f}) se "
                    f"{pct}% sasta hai! Bachat: Rs. {savings:,.0f}."
                ),
                "avg_30_90_days": round(avg_price, 2),
                "current_price": current_price,
                "savings_pkr": savings
            }

        # Otherwise Normal price
        return {
            "verdict": "Normal price",
            "badge": "Normal price",
            "details": f"Price pichle 30-90 dino ki standard price (Rs. {avg_price:,.0f}) ke barabar hai.",
            "avg_30_90_days": round(avg_price, 2),
            "current_price": current_price
        }


price_service = PriceService()
