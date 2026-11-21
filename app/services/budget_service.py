"""In-memory budget management and wishlist service."""

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from app.schemas.budget import (
    BudgetStatus,
    SpendingCategory,
    SpendingReport,
    Wishlist,
    WishlistItem,
)


def _current_month() -> str:
    return datetime.now().strftime("%Y-%m")


class BudgetService:
    """Manages monthly budgets, spending records, and wishlists in memory."""

    def __init__(self):
        # session_id -> month -> limit
        self._budgets: Dict[str, Dict[str, float]] = {}
        # session_id -> month -> list of (amount, category)
        self._spending: Dict[str, Dict[str, List[tuple]]] = {}
        # session_id -> list of WishlistItem
        self._wishlists: Dict[str, List[WishlistItem]] = {}

    # ── Budget ──────────────────────────────────────────────────────────

    def set_budget(self, session_id: str, monthly_limit_pkr: float, month: Optional[str] = None) -> dict:
        month = month or _current_month()
        self._budgets.setdefault(session_id, {})[month] = monthly_limit_pkr
        # ensure spending bucket exists
        self._spending.setdefault(session_id, {}).setdefault(month, [])
        return {"session_id": session_id, "monthly_limit_pkr": monthly_limit_pkr, "month": month}

    def get_status(self, session_id: str) -> BudgetStatus:
        month = _current_month()
        limit = self._budgets.get(session_id, {}).get(month, 0)
        records = self._spending.get(session_id, {}).get(month, [])
        total_spent = sum(r[0] for r in records)
        remaining = max(limit - total_spent, 0)
        pct = (total_spent / limit * 100) if limit > 0 else 0.0

        warning = None
        if pct >= 100:
            warning = "⛔ Budget EXCEEDED! Aap ka monthly budget khatam ho chuka hai."
        elif pct >= 80:
            warning = "⚠️ Budget WARNING: Aap ne 80% se zyada budget use kar liya hai."

        return BudgetStatus(
            session_id=session_id,
            monthly_limit_pkr=limit,
            total_spent_pkr=total_spent,
            remaining_pkr=remaining,
            percentage_used=round(pct, 1),
            warning=warning,
            month=month,
        )

    def record_spending(self, session_id: str, amount_pkr: float, category: str) -> dict:
        month = _current_month()
        self._spending.setdefault(session_id, {}).setdefault(month, []).append((amount_pkr, category))
        return {"recorded": True, "amount_pkr": amount_pkr, "category": category, "month": month}

    def check_purchase_allowed(self, session_id: str, amount_pkr: float) -> dict:
        month = _current_month()
        limit = self._budgets.get(session_id, {}).get(month, 0)
        if limit == 0:
            return {"allowed": True, "warning": "No budget set for this month."}

        records = self._spending.get(session_id, {}).get(month, [])
        total_spent = sum(r[0] for r in records)
        new_total = total_spent + amount_pkr
        pct = new_total / limit * 100

        if pct > 100:
            return {
                "allowed": False,
                "warning": f"⛔ Yeh purchase Rs.{amount_pkr:,.0f} aap ke budget se zyada hai! "
                           f"Budget: Rs.{limit:,.0f}, Already spent: Rs.{total_spent:,.0f}."
            }
        elif pct >= 80:
            return {
                "allowed": True,
                "warning": f"⚠️ Is purchase ke baad aap budget ka {pct:.0f}% use kar chuke honge. Sochein!"
            }
        return {"allowed": True, "warning": ""}

    def get_spending_report(self, session_id: str, month: Optional[str] = None) -> SpendingReport:
        month = month or _current_month()
        limit = self._budgets.get(session_id, {}).get(month, 0)
        records = self._spending.get(session_id, {}).get(month, [])
        total_spent = sum(r[0] for r in records)

        # aggregate by category
        cat_data: Dict[str, dict] = {}
        for amount, cat in records:
            if cat not in cat_data:
                cat_data[cat] = {"amount_pkr": 0.0, "item_count": 0}
            cat_data[cat]["amount_pkr"] += amount
            cat_data[cat]["item_count"] += 1

        categories = []
        for cat_name, info in cat_data.items():
            pct = (info["amount_pkr"] / total_spent * 100) if total_spent > 0 else 0.0
            categories.append(SpendingCategory(
                category=cat_name,
                amount_pkr=info["amount_pkr"],
                percentage=round(pct, 1),
                item_count=info["item_count"],
            ))
        categories.sort(key=lambda c: c.amount_pkr, reverse=True)

        return SpendingReport(
            session_id=session_id,
            month=month,
            categories=categories,
            total_spent_pkr=total_spent,
            monthly_limit_pkr=limit,
        )

    # ── Wishlist ────────────────────────────────────────────────────────

    def add_to_wishlist(
        self,
        session_id: str,
        product_id: str,
        title: str,
        price_pkr: float,
        store: str,
        priority: int = 3,
    ) -> dict:
        item = WishlistItem(
            product_id=product_id,
            title=title,
            price_pkr=price_pkr,
            store=store,
            priority=priority,
        )
        self._wishlists.setdefault(session_id, []).append(item)
        return {"added": True, "product_id": product_id, "title": title}

    def get_wishlist(self, session_id: str) -> Wishlist:
        items = self._wishlists.get(session_id, [])
        sorted_items = sorted(items, key=lambda i: i.priority)
        total = sum(i.price_pkr for i in sorted_items)
        return Wishlist(session_id=session_id, items=sorted_items, total_value_pkr=total)

    def remove_from_wishlist(self, session_id: str, product_id: str) -> dict:
        items = self._wishlists.get(session_id, [])
        before = len(items)
        self._wishlists[session_id] = [i for i in items if i.product_id != product_id]
        removed = before - len(self._wishlists[session_id])
        return {"removed": removed > 0, "product_id": product_id}


# Singleton instance
budget_service = BudgetService()
