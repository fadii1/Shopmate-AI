"""Tests for budget management and wishlist features."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.budget_service import BudgetService, budget_service


@pytest.fixture(autouse=True)
def fresh_budget_service(monkeypatch):
    """Reset the budget service singleton before each test."""
    fresh = BudgetService()
    monkeypatch.setattr("app.services.budget_service.budget_service", fresh)
    monkeypatch.setattr("app.api.routes_budget.budget_service", fresh)
    return fresh


client = TestClient(app)
SID = "test-session-budget"


# ── Budget tests ────────────────────────────────────────────────────────

def test_set_and_get_budget(fresh_budget_service):
    """Set a budget and verify status returns correct values."""
    svc = fresh_budget_service
    svc.set_budget(SID, 50000)
    status = svc.get_status(SID)

    assert status.monthly_limit_pkr == 50000
    assert status.total_spent_pkr == 0
    assert status.remaining_pkr == 50000
    assert status.percentage_used == 0.0
    assert status.warning is None


def test_budget_80_percent_warning(fresh_budget_service):
    """Warning should trigger when spending reaches 80%."""
    svc = fresh_budget_service
    svc.set_budget(SID, 10000)
    svc.record_spending(SID, 8500, "Electronics")

    status = svc.get_status(SID)
    assert status.percentage_used == 85.0
    assert status.warning is not None
    assert "80%" in status.warning or "WARNING" in status.warning

    # Also test check_purchase_allowed near threshold
    result = svc.check_purchase_allowed(SID, 500)
    assert result["allowed"] is True
    assert result["warning"] != ""


def test_budget_exceeded_block(fresh_budget_service):
    """Purchases should be blocked when budget is exceeded."""
    svc = fresh_budget_service
    svc.set_budget(SID, 10000)
    svc.record_spending(SID, 9000, "Clothing")

    # This purchase would bring total to 11000 (110%)
    result = svc.check_purchase_allowed(SID, 2000)
    assert result["allowed"] is False
    assert "budget" in result["warning"].lower() or "⛔" in result["warning"]

    # Status should show exceeded
    status = svc.get_status(SID)
    svc.record_spending(SID, 2000, "Misc")
    status = svc.get_status(SID)
    assert status.percentage_used >= 100
    assert status.warning is not None
    assert "EXCEEDED" in status.warning or "⛔" in status.warning


def test_spending_report_categories(fresh_budget_service):
    """Spending report should correctly aggregate by category."""
    svc = fresh_budget_service
    svc.set_budget(SID, 50000)
    svc.record_spending(SID, 5000, "Electronics")
    svc.record_spending(SID, 3000, "Clothing")
    svc.record_spending(SID, 2000, "Electronics")
    svc.record_spending(SID, 1000, "Food")

    report = svc.get_spending_report(SID)
    assert report.total_spent_pkr == 11000
    assert report.monthly_limit_pkr == 50000
    assert len(report.categories) == 3

    # Categories should be sorted by amount descending
    assert report.categories[0].category == "Electronics"
    assert report.categories[0].amount_pkr == 7000
    assert report.categories[0].item_count == 2

    assert report.categories[1].category == "Clothing"
    assert report.categories[1].amount_pkr == 3000

    # Percentages should add up close to 100
    total_pct = sum(c.percentage for c in report.categories)
    assert abs(total_pct - 100.0) < 0.5


# ── Wishlist tests ──────────────────────────────────────────────────────

def test_wishlist_priority_ordering(fresh_budget_service):
    """Wishlist items should be sorted by priority (1=highest first)."""
    svc = fresh_budget_service
    svc.add_to_wishlist(SID, "p3", "Low Priority Item", 1000, "Daraz", priority=5)
    svc.add_to_wishlist(SID, "p1", "High Priority Item", 5000, "Amazon", priority=1)
    svc.add_to_wishlist(SID, "p2", "Medium Priority Item", 3000, "Daraz", priority=3)

    wishlist = svc.get_wishlist(SID)
    assert len(wishlist.items) == 3
    assert wishlist.items[0].product_id == "p1"
    assert wishlist.items[0].priority == 1
    assert wishlist.items[1].product_id == "p2"
    assert wishlist.items[2].product_id == "p3"
    assert wishlist.total_value_pkr == 9000


def test_wishlist_add_remove(fresh_budget_service):
    """Adding and removing items from wishlist."""
    svc = fresh_budget_service
    svc.add_to_wishlist(SID, "p1", "Test Item 1", 2000, "Daraz")
    svc.add_to_wishlist(SID, "p2", "Test Item 2", 3000, "Amazon")

    wishlist = svc.get_wishlist(SID)
    assert len(wishlist.items) == 2
    assert wishlist.total_value_pkr == 5000

    # Remove one
    result = svc.remove_from_wishlist(SID, "p1")
    assert result["removed"] is True

    wishlist = svc.get_wishlist(SID)
    assert len(wishlist.items) == 1
    assert wishlist.items[0].product_id == "p2"
    assert wishlist.total_value_pkr == 3000

    # Remove non-existent
    result = svc.remove_from_wishlist(SID, "nonexistent")
    assert result["removed"] is False
