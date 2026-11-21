from typing import Dict, Any
from app.config import settings


class FXService:
    """Handles currency conversions and audit tracking for foreign stores (e.g. Amazon US)."""

    def __init__(self, usd_rate: float = None, rate_date: str = None):
        self.usd_rate = usd_rate or settings.usd_to_pkr_rate
        self.rate_date = rate_date or settings.fx_rate_date

    def usd_to_pkr(self, amount_usd: float) -> Dict[str, Any]:
        """Convert USD amount to PKR with transparent exchange rate disclosure."""
        converted = round(amount_usd * self.usd_rate, 2)
        return {
            "amount_pkr": converted,
            "original_amount": amount_usd,
            "original_currency": "USD",
            "rate_used": self.usd_rate,
            "rate_date": self.rate_date,
            "note": f"Converted at $1 = Rs. {self.usd_rate:.2f} (Rate date: {self.rate_date})"
        }

    def format_price_pkr(self, amount_pkr: float) -> str:
        """Format price in standard Pakistani format: Rs. 12,500"""
        return f"Rs. {amount_pkr:,.0f}"


fx_service = FXService()
