import pytest
from app.services.security_service import security_service
from app.services.recommendation_service import recommendation_service


def test_safe_link_detection():
    safe_daraz = security_service.check_link_safety("https://www.daraz.pk/products/running-shoes-i101.html")
    assert safe_daraz["safe"] is True
    assert safe_daraz["risk_level"] == "safe"


def test_scam_link_detection():
    fake_url = "https://daraz-sale.xyz/verify-otp?win=true"
    result = security_service.check_link_safety(fake_url)
    assert result["safe"] is False
    assert result["risk_level"] in ["warning", "danger"]
    assert len(result["reasons"]) >= 1


def test_ip_address_link_warning():
    ip_url = "http://192.168.1.100/checkout"
    result = security_service.check_link_safety(ip_url)
    assert result["safe"] is False
    assert any("IP address" in r for r in result["reasons"])


def test_seller_trust_scoring():
    # High trust seller
    high = security_service.compute_seller_score(
        rating=4.8,
        orders_count=350,
        complaints_count=0,
        account_age_months=24,
        return_acceptance_rate=0.98
    )
    assert high["trust_score"] >= 85
    assert high["verdict"] == "Trusted Seller"

    # Risky seller
    low = security_service.compute_seller_score(
        rating=2.8,
        orders_count=10,
        complaints_count=5,
        account_age_months=1,
        return_acceptance_rate=0.40
    )
    assert low["trust_score"] < 50
    assert "Low Trust" in low["verdict"]
    assert "COD" in low["payment_advice"]


def test_gift_suggestions():
    gifts = recommendation_service.suggest_gifts("Eid", "Brother", 5000.0)
    assert len(gifts) >= 2
    assert "idea" in gifts[0]
